from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.auth import create_access_token, hash_password
from app.models import Base, User, Voice, VoicePreviewAudio, VoiceProviderProfile
from app.crud.tts_preview import hash_sample_text


def make_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    voice = Voice(
        voice_key="xiaoxiao",
        display_name="晓晓",
        gender="female",
        style="温柔",
        category="知识类",
        description="温柔知性的女声，适合知识讲解、课程录制",
        is_recommended=True,
        is_active=True,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider="edge_tts",
            provider_voice_id="zh-CN-XiaoxiaoNeural",
            locale="zh-CN",
            supports_wav=False,
            supports_mp3=True,
            is_default=True,
            is_active=True,
        )
    )
    db.add(voice)
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def test_preview_tts_generates_audio_and_stores_cache_record(monkeypatch, tmp_path):
    calls = []

    async def fake_synthesize_preview(text, provider_profile, output_filename=None):
        calls.append((text, provider_profile.provider_voice_id))
        output_path = tmp_path / "preview-test.mp3"
        output_path.write_bytes(b"fake mp3")
        return {
            "filename": "preview-test.mp3",
            "path": output_path,
            "duration": 5,
        }

    monkeypatch.setattr("app.api.tts.synthesize_preview", fake_synthesize_preview)

    client, SessionLocal = make_client()
    response = client.post(
        "/api/tts/preview",
        json={
            "text": "大家好，欢迎收听本期节目。",
            "voiceId": "zh-CN-XiaoxiaoNeural",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "audioUrl": "/static/previews/preview-test.mp3",
        "duration": 5,
    }
    assert calls == [("大家好，欢迎收听本期节目。", "zh-CN-XiaoxiaoNeural")]

    db = SessionLocal()
    cache_record = db.query(VoicePreviewAudio).one()
    db.close()

    assert cache_record.audio_url == "/static/previews/preview-test.mp3"
    assert cache_record.audio_path.endswith("preview-test.mp3")
    assert cache_record.file_size_bytes == 8
    assert cache_record.status == "ready"


def test_preview_tts_uses_cached_audio_without_regenerating(monkeypatch, tmp_path):
    calls = []

    async def fake_synthesize_preview(text, provider_profile, output_filename=None):
        calls.append((text, provider_profile.provider_voice_id))
        output_path = tmp_path / "preview-test.mp3"
        output_path.write_bytes(b"fake mp3")
        return {
            "filename": "preview-test.mp3",
            "path": output_path,
            "duration": 5,
        }

    monkeypatch.setattr("app.api.tts.synthesize_preview", fake_synthesize_preview)

    client, _ = make_client()
    payload = {"text": "大家好，欢迎收听本期节目。", "voiceId": "zh-CN-XiaoxiaoNeural"}

    first_response = client.post("/api/tts/preview", json=payload)
    second_response = client.post("/api/tts/preview", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json() == first_response.json()
    assert len(calls) == 1


def test_preview_tts_regenerates_when_cached_file_is_missing(monkeypatch, tmp_path):
    calls = []

    async def fake_synthesize_preview(text, provider_profile, output_filename=None):
        calls.append((text, provider_profile.provider_voice_id, output_filename))
        output_path = tmp_path / output_filename
        output_path.write_bytes(b"new fake mp3")
        return {
            "filename": output_filename,
            "path": output_path,
            "duration": 7,
        }

    monkeypatch.setattr("app.api.tts.synthesize_preview", fake_synthesize_preview)

    client, SessionLocal = make_client()
    sample_text = "hello preview"

    db = SessionLocal()
    provider_profile = db.query(VoiceProviderProfile).one()
    provider_profile_id = provider_profile.id
    db.add(
        VoicePreviewAudio(
            voice_provider_profile_id=provider_profile_id,
            sample_text_hash=hash_sample_text(sample_text),
            sample_text=sample_text,
            format="mp3",
            audio_path=str(tmp_path / "missing-preview.mp3"),
            audio_url="/static/previews/missing-preview.mp3",
            duration_seconds=3,
            status="ready",
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/api/tts/preview",
        json={"text": sample_text, "voiceId": "zh-CN-XiaoxiaoNeural"},
    )

    expected_filename = f"preview-{provider_profile_id}-{hash_sample_text(sample_text)[:16]}.mp3"
    assert response.status_code == 200
    assert response.json() == {
        "audioUrl": f"/static/previews/{expected_filename}",
        "duration": 7,
    }
    assert calls == [(sample_text, "zh-CN-XiaoxiaoNeural", expected_filename)]

    db = SessionLocal()
    cache_records = db.query(VoicePreviewAudio).order_by(VoicePreviewAudio.id).all()
    db.close()

    assert len(cache_records) == 1
    assert cache_records[0].audio_url == f"/static/previews/{expected_filename}"
    assert cache_records[0].audio_path.endswith(expected_filename)
    assert cache_records[0].file_size_bytes == 12
    assert cache_records[0].status == "ready"
    assert cache_records[0].error_message is None


def test_preview_tts_rejects_unknown_voice_id():
    client, _ = make_client()
    response = client.post(
        "/api/tts/preview",
        json={"text": "大家好，欢迎收听本期节目。", "voiceId": "unknown-voice"},
    )

    assert response.status_code == 404
    assert "voice provider not found" in response.text


def test_preview_tts_rejects_empty_text():
    client, _ = make_client()
    response = client.post(
        "/api/tts/preview",
        json={"text": "   ", "voiceId": "zh-CN-XiaoxiaoNeural"},
    )

    assert response.status_code == 422
    assert "text" in response.text


def test_preview_tts_rejects_other_users_personal_voice(monkeypatch):
    calls = []

    async def fake_synthesize_preview(text, provider_profile, output_filename=None):
        calls.append((text, provider_profile.provider_voice_id))
        return {"filename": "should-not-run.mp3", "path": None, "duration": 1}

    monkeypatch.setattr("app.api.tts.synthesize_preview", fake_synthesize_preview)

    client, SessionLocal = make_client()
    db = SessionLocal()
    owner = User(username="owner", password_hash=hash_password("pass1234"), is_active=True)
    other = User(username="other", password_hash=hash_password("pass1234"), is_active=True)
    db.add_all([owner, other])
    db.flush()
    voice = Voice(
        voice_key="owner-private",
        display_name="Owner Private",
        gender="female",
        category="personal",
        is_active=True,
        owner_id=owner.id,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider="bailian_tts",
            provider_voice_id="bailian:qwen3-tts-flash:private-owner",
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

    response = client.post(
        "/api/tts/preview",
        json={"text": "hello", "voiceId": "bailian:qwen3-tts-flash:private-owner"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
    assert calls == []
def test_preview_tts_supports_bailian_provider(monkeypatch, tmp_path):
    calls = []

    async def fake_synthesize_preview(text, provider_profile, output_filename=None):
        calls.append((text, provider_profile.provider, provider_profile.provider_voice_id))
        output_path = tmp_path / "bailian-preview.mp3"
        output_path.write_bytes(b"fake bailian mp3")
        return {
            "filename": "bailian-preview.mp3",
            "path": output_path,
            "duration": 6,
        }

    monkeypatch.setattr("app.api.tts.synthesize_preview", fake_synthesize_preview)

    client, SessionLocal = make_client()
    db = SessionLocal()
    voice = Voice(
        voice_key="bailian-qwen-cherry",
        display_name="Bailian Cherry",
        gender="female",
        style="general",
        category="knowledge",
        description="Bailian fixed voice",
        is_recommended=True,
        is_active=True,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider="bailian_tts",
            provider_voice_id="bailian:qwen3-tts-flash:Cherry",
            locale="zh-CN",
            supports_wav=False,
            supports_mp3=True,
            is_default=True,
            is_active=True,
        )
    )
    db.add(voice)
    db.commit()
    db.close()

    response = client.post(
        "/api/tts/preview",
        json={"text": "你好，欢迎使用百炼语音合成。", "voiceId": "bailian:qwen3-tts-flash:Cherry"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "audioUrl": "/static/previews/bailian-preview.mp3",
        "duration": 6,
    }
    assert calls == [("你好，欢迎使用百炼语音合成。", "bailian_tts", "bailian:qwen3-tts-flash:Cherry")]