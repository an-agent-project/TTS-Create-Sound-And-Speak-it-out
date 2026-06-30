from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Base, Material, User, Voice


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


def test_admin_endpoints_reject_non_admin_users():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        user = create_user(db, "regular-user")

    response = client.get("/api/admin/voices", headers=auth_headers(user))

    assert response.status_code == 403
    assert response.json()["detail"] == "admin access required"


def test_admin_can_update_voice_with_frontend_query_aliases():
    client, SessionLocal = make_client_and_session()
    with SessionLocal() as db:
        admin = create_user(db, "admin-user", role="admin")
        voice = Voice(
            voice_key="admin-edit-voice",
            display_name="Old Voice",
            gender="female",
            category="Old Category",
            is_active=True,
        )
        db.add(voice)
        db.commit()
        db.refresh(voice)
        voice_id = voice.id

    response = client.put(
        f"/api/admin/voices/{voice_id}?displayName=New Voice&category=New Category&isActive=false",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        updated = db.query(Voice).filter(Voice.id == voice_id).one()
        assert updated.display_name == "New Voice"
        assert updated.category == "New Category"
        assert updated.is_active is False

def test_admin_material_delete_removes_database_row(tmp_path):
    client, SessionLocal = make_client_and_session()
    audio_path = tmp_path / "admin-material.mp3"
    audio_path.write_bytes(b"audio")
    with SessionLocal() as db:
        admin = create_user(db, "material-admin", role="admin")
        material = Material(
            material_key="admin-delete-material",
            filename="admin-material.mp3",
            title="Admin Material",
            category="bgm",
            format="mp3",
            duration_seconds=1,
            file_size_bytes=5,
            uploader="admin",
            audio_path=str(audio_path),
            audio_url="/media/admin-material.mp3",
            is_active=True,
        )
        db.add(material)
        db.commit()
        db.refresh(material)
        material_id = material.id

    response = client.delete(f"/api/admin/materials/{material_id}", headers=auth_headers(admin))

    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        assert db.query(Material).filter(Material.id == material_id).first() is None
    assert not audio_path.exists()
