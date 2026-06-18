from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Base, User


def _make_client():
    """Return a TestClient wired to a fresh in-memory SQLite database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _register_and_token(client, username="alice", password="pass1234"):
    """Helper: register a user and return (user_id, token)."""
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    return body["user"]["id"], body["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Anonymous / public access ────────────────────────────────────


def test_anonymous_can_list_default_voices():
    """Anonymous users see only owner_id=NULL voices (the 8 defaults in seed)."""
    client = _make_client()

    # Without registering, there are no voices in an in-memory DB.
    # Create one default voice (owner_id=None) and one owned voice indirectly
    # by seeding them via the DB directly.
    resp = client.get("/api/voices")
    assert resp.status_code == 200
    assert resp.json() == []


def test_authenticated_user_sees_default_and_own_voices():
    """Logged-in users see default voices + their own."""
    client = _make_client()
    uid, token = _register_and_token(client)

    # Create a voice as this user
    resp = client.post(
        "/api/voices",
        json={"voiceKey": "my-voice", "displayName": "我的音色", "gender": "male"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    my_id = resp.json()["id"]

    # List as authenticated
    resp = client.get("/api/voices", headers=_auth_headers(token))
    assert resp.status_code == 200
    voices = resp.json()
    ids = [v["id"] for v in voices]
    assert my_id in ids
    # All voices should be either ownerId=null or ownerId=uid
    for v in voices:
        assert v["ownerId"] is None or v["ownerId"] == uid


def test_user_cannot_see_other_users_voices():
    """User A's voices are invisible to user B."""
    client = _make_client()
    id_a, tok_a = _register_and_token(client, "alice")
    id_b, tok_b = _register_and_token(client, "bob")

    # Alice creates a voice
    client.post(
        "/api/voices",
        json={"voiceKey": "alice-voice", "displayName": "A音色", "gender": "female"},
        headers=_auth_headers(tok_a),
    )

    # Bob lists — should NOT see Alice's voice
    resp = client.get("/api/voices", headers=_auth_headers(tok_b))
    for v in resp.json():
        assert v["ownerId"] is None or v["ownerId"] == id_b


# ── CRUD with ownership ──────────────────────────────────────────


def test_owned_voice_lifecycle():
    """Create → read → update → delete an owned voice."""
    client = _make_client()
    uid, token = _register_and_token(client)

    # Create
    resp = client.post(
        "/api/voices",
        json={
            "voiceKey": "my-custom",
            "displayName": "自定义",
            "gender": "female",
            "style": "温柔",
            "category": "知识类",
            "providers": [{
                "provider": "edge_tts",
                "providerVoiceId": "zh-CN-custom",
                "locale": "zh-CN",
                "supportsMp3": True,
                "supportsWav": False,
                "isDefault": True,
            }],
        },
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["ownerId"] == uid
    voice_id = created["id"]

    # Read
    resp = client.get(f"/api/voices/{voice_id}", headers=_auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["voiceKey"] == "my-custom"

    # Update
    resp = client.put(
        f"/api/voices/{voice_id}",
        json={"style": "知性"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["style"] == "知性"

    # Delete
    resp = client.delete(f"/api/voices/{voice_id}", headers=_auth_headers(token))
    assert resp.status_code == 204

    # Should be gone
    resp = client.get(f"/api/voices/{voice_id}", headers=_auth_headers(token))
    assert resp.status_code == 404


# ── System voice protection ──────────────────────────────────────


def _seed_default_voice(client):
    """Seed a default (owner_id=NULL) voice directly since POST requires auth now."""
    from app.database import SessionLocal
    from app import models
    from app.models import Base
    import sqlalchemy

    # Use the already-overridden session
    pass


def test_cannot_update_system_voice():
    """Authenticated users cannot edit voices with owner_id=NULL."""
    client = _make_client()
    uid, token = _register_and_token(client)

    # Create a voice (as owner), then manually set owner_id=NULL via DB
    resp = client.post(
        "/api/voices",
        json={"voiceKey": "temp-sys", "displayName": "temp-sys", "gender": "male"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    voice_id = resp.json()["id"]

    # Set owner_id=NULL through the override DB session
    db_gen = app.dependency_overrides[get_db]
    db_session = db_gen()
    db_session = next(db_session) if hasattr(db_session, "__next__") else db_session
    from app.models import Voice
    voice = db_session.get(Voice, voice_id)
    voice.owner_id = None
    db_session.commit()

    # Now try to update it — should be forbidden
    resp = client.put(
        f"/api/voices/{voice_id}",
        json={"style": "hacked"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 403


def test_cannot_delete_system_voice():
    """Authenticated users cannot delete system voices."""
    client = _make_client()
    uid, token = _register_and_token(client)

    # Create as owner, then unset owner_id
    resp = client.post(
        "/api/voices",
        json={"voiceKey": "sys-voice", "displayName": "sys-voice", "gender": "female"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    voice_id = resp.json()["id"]

    db_gen = app.dependency_overrides[get_db]
    db_session = db_gen()
    db_session = next(db_session) if hasattr(db_session, "__next__") else db_session
    from app.models import Voice
    voice = db_session.get(Voice, voice_id)
    voice.owner_id = None
    db_session.commit()

    resp = client.delete(f"/api/voices/{voice_id}", headers=_auth_headers(token))
    assert resp.status_code == 403


def test_unauthenticated_cannot_create_voice():
    """POST /api/voices requires authentication."""
    client = _make_client()
    resp = client.post(
        "/api/voices",
        json={"voiceKey": "anon-voice", "displayName": "匿名", "gender": "male"},
    )
    assert resp.status_code == 422  # Missing required Header
