from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Base, Material, User, Voice, VoiceProviderProfile


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
    user = User(username="bgm-user", password_hash=hash_password("secret"))
    db.add(user)
    db.flush()
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
    token = create_access_token(user.id)
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    synthesize_calls = []

    async def fake_synthesize(**kwargs):
        synthesize_calls.append(kwargs)
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
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "你好，测试背景音乐。",
                "voiceId": "zh-CN-XiaoxiaoNeural",
                "bgmType": "test-bgm",
                "bgmVolume": 40,
                "voiceVolume": 85,
                "maxSegmentLength": 80,
                "pauseScale": 1.5,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert calls == [(bgm_path, 40)]
    assert synthesize_calls[0]["voice_volume"] == 85
    assert all(len(segment.text) <= 80 for segment in synthesize_calls[0]["segments"])
    assert all(segment.pauseMs >= 180 for segment in synthesize_calls[0]["segments"])


def test_generate_tts_rejects_other_users_personal_voice(monkeypatch, tmp_path):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    owner = User(username="owner", password_hash=hash_password("pass1234"), is_active=True)
    other = User(username="other", password_hash=hash_password("pass1234"), is_active=True)
    db.add_all([owner, other])
    db.flush()
    voice = Voice(
        voice_key="owner-generate-private",
        display_name="Owner Generate Private",
        gender="female",
        category="personal",
        is_active=True,
        owner_id=owner.id,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider="bailian_tts",
            provider_voice_id="bailian:qwen3-tts-flash:private-generate-owner",
            locale="zh-CN",
            supports_wav=False,
            supports_mp3=True,
            is_default=True,
            is_active=True,
        )
    )
    other_token = create_access_token(other.id, other.role or "user")
    db.add(voice)
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    synthesize_calls = []

    async def fake_synthesize(**kwargs):
        synthesize_calls.append(kwargs)
        kwargs["output_path"].write_bytes(b"voice")
        return 1

    async def fake_mix(voice_path: Path, bgm_path_arg: Path | None, output_path: Path, bgm_volume: int):
        output_path.write_bytes(b"mixed")
        return 2.0

    monkeypatch.setattr("app.main.synthesize_segments_to_file", fake_synthesize)
    monkeypatch.setattr("app.main.mix_bgm_to_file", fake_mix)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/api/tts/generate",
            json={
                "content": "hello",
                "voiceId": "bailian:qwen3-tts-flash:private-generate-owner",
            },
            headers={"Authorization": f"Bearer {other_token}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "unsupported voice id" in response.text
    assert synthesize_calls == []
