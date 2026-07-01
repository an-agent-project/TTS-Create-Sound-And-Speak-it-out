from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Base, User, Voice, VoiceProviderProfile, VoicePublishRequest


def make_client_and_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def create_user(db, username: str, role: str = "user") -> User:
    user = User(
        username=username,
        password_hash=hash_password("pass1234"),
        email=f"{username}@example.com",
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


def create_personal_voice(db, owner: User) -> Voice:
    voice = Voice(
        voice_key=f"personal-{owner.id}",
        display_name="Personal Voice",
        gender="female",
        style="warm",
        category="personal",
        description="Owned voice",
        is_active=True,
        owner_id=owner.id,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider="bailian_tts",
            provider_voice_id=f"bailian:qwen3-tts-vc-2026-01-22:voice-{owner.id}",
            locale="zh-CN",
            supports_mp3=True,
            supports_wav=False,
            is_default=True,
            is_active=True,
        )
    )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    return voice


def test_user_can_submit_own_voice_for_public_review():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        user = create_user(db, "alice")
        voice = create_personal_voice(db, user)
        voice_id = voice.id
        headers = auth_headers(user)

    response = client.post(f"/api/voices/{voice_id}/publish-requests", headers=headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert body["sourceVoiceId"] == voice_id
    with SessionLocal() as db:
        request = db.query(VoicePublishRequest).one()
        assert request.requester_id == user.id
        assert request.source_voice_id == voice_id


def test_user_cannot_submit_other_users_voice_for_public_review():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        owner = create_user(db, "owner")
        other = create_user(db, "other")
        voice = create_personal_voice(db, owner)
        voice_id = voice.id
        headers = auth_headers(other)

    response = client.post(f"/api/voices/{voice_id}/publish-requests", headers=headers)

    assert response.status_code == 404


def test_duplicate_pending_publish_request_is_rejected():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        user = create_user(db, "alice")
        voice = create_personal_voice(db, user)
        voice_id = voice.id
        headers = auth_headers(user)

    first = client.post(f"/api/voices/{voice_id}/publish-requests", headers=headers)
    second = client.post(f"/api/voices/{voice_id}/publish-requests", headers=headers)

    assert first.status_code == 201
    assert second.status_code == 409


def test_admin_approves_publish_request_and_creates_public_voice():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        admin = create_user(db, "admin", role="admin")
        user = create_user(db, "alice")
        voice = create_personal_voice(db, user)
        voice_id = voice.id
        user_headers = auth_headers(user)
        admin_headers = auth_headers(admin)

    submitted = client.post(f"/api/voices/{voice_id}/publish-requests", headers=user_headers)
    request_id = submitted.json()["id"]
    response = client.post(
        f"/api/admin/voice-publish-requests/{request_id}/review?action=approve",
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "approved"
    assert body["publicVoiceId"]
    with SessionLocal() as db:
        public_voice = db.get(Voice, body["publicVoiceId"])
        assert public_voice.owner_id is None
        assert public_voice.source_voice_id == voice_id
        assert public_voice.providers[0].provider_voice_id.endswith(f"#public-{request_id}")

    public_list = client.get("/api/voices?scope=public")
    assert any(item["id"] == body["publicVoiceId"] for item in public_list.json())


def test_admin_rejects_publish_request_without_creating_public_voice():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        admin = create_user(db, "admin", role="admin")
        user = create_user(db, "alice")
        voice = create_personal_voice(db, user)
        voice_id = voice.id
        user_headers = auth_headers(user)
        admin_headers = auth_headers(admin)

    submitted = client.post(f"/api/voices/{voice_id}/publish-requests", headers=user_headers)
    request_id = submitted.json()["id"]
    response = client.post(
        f"/api/admin/voice-publish-requests/{request_id}/review?action=reject&note=no",
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "rejected"
    with SessionLocal() as db:
        request = db.get(VoicePublishRequest, request_id)
        assert request.public_voice_id is None
        assert request.review_note == "no"
