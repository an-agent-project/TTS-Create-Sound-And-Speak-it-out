from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


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
