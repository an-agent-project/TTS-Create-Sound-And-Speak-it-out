from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Base, Material, User


def test_list_materials_returns_seeded_bgm(monkeypatch, tmp_path):
    material_dir = tmp_path / "materials"
    material_dir.mkdir()
    (material_dir / "soft-corporate.ogg").write_bytes(b"ogg")
    (material_dir / "liftoff.ogg").write_bytes(b"ogg")
    (material_dir / "samedi-deconfine.ogg").write_bytes(b"ogg")
    monkeypatch.setattr("app.material_defaults.MEDIA_DIR", tmp_path)

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
    try:
        response = TestClient(app).get("/api/materials?category=bgm")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    keys = {item["materialKey"] for item in response.json()}
    assert {"soft-corporate", "liftoff", "samedi-deconfine"} <= keys


def test_list_materials_returns_public_and_current_user_only(monkeypatch, tmp_path):
    monkeypatch.setattr("app.material_defaults.MEDIA_DIR", tmp_path)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    user_a = User(username="user-a", password_hash=hash_password("secret"))
    user_b = User(username="user-b", password_hash=hash_password("secret"))
    db.add_all([user_a, user_b])
    db.flush()
    db.add_all(
        [
            Material(
                material_key="public-bgm",
                filename="public.ogg",
                title="Public",
                category="bgm",
                format="ogg",
                audio_path="/tmp/public.ogg",
                audio_url="/media/materials/public.ogg",
            ),
            Material(
                material_key="user-a-bgm",
                filename="a.ogg",
                title="A",
                category="bgm",
                format="ogg",
                uploader=user_a.username,
                owner_id=user_a.id,
                audio_path="/tmp/a.ogg",
                audio_url="/media/materials/a.ogg",
            ),
            Material(
                material_key="user-b-bgm",
                filename="b.ogg",
                title="B",
                category="bgm",
                format="ogg",
                uploader=user_b.username,
                owner_id=user_b.id,
                audio_path="/tmp/b.ogg",
                audio_url="/media/materials/b.ogg",
            ),
        ]
    )
    db.commit()
    token = create_access_token(user_a.id)
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get(
            "/api/materials?category=bgm",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    keys = {item["materialKey"] for item in response.json()}
    assert keys == {"public-bgm", "user-a-bgm"}
