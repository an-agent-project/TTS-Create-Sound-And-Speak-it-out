from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Material


def test_generate_tts_mixes_selected_bgm(monkeypatch, tmp_path):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    bgm_path = tmp_path / "bgm.ogg"
    bgm_path.write_bytes(b"bgm")
    db = TestingSessionLocal()
    db.add(
        Material(
            material_key="test-bgm",
            filename="bgm.ogg",
            title="Test BGM",
            category="bgm",
            format="ogg",
            file_size_bytes=3,
            audio_path=str(bgm_path),
            audio_url="/media/materials/bgm.ogg",
        )
    )
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def fake_synthesize(**kwargs):
        kwargs["output_path"].write_bytes(b"voice")
        return 1

    calls = []

    async def fake_mix(voice_path: Path, bgm_path_arg: Path | None, output_path: Path, bgm_volume: int):
        calls.append((bgm_path_arg, bgm_volume))
        output_path.write_bytes(b"mixed")
        return 2.0

    monkeypatch.setattr("app.main.synthesize_segments_to_file", fake_synthesize)
    monkeypatch.setattr("app.main.mix_bgm_to_file", fake_mix)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/api/tts/generate",
            json={
                "content": "你好，测试背景音乐。",
                "voiceId": "zh-CN-XiaoxiaoNeural",
                "bgmType": "test-bgm",
                "bgmVolume": 40,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert calls == [(bgm_path, 40)]
