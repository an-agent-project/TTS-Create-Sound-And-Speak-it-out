from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Voice, VoiceProviderProfile


def _make_client():
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
    return TestClient(app), TestingSessionLocal


def _register_and_token(client):
    response = client.post("/api/auth/register", json={"username": "clone-user", "password": "pass1234"})
    assert response.status_code == 201, response.text
    return response.json()["access_token"], response.json()["user"]["id"]


def test_create_voice_clone_requires_authentication():
    client, _ = _make_client()

    response = client.post(
        "/api/voice-clones",
        data={"name": "我的克隆音色", "preferredName": "my_clone"},
        files={"file": ("voice.mp3", b"abc", "audio/mpeg")},
    )

    assert response.status_code == 422


def test_create_voice_clone_creates_user_owned_bailian_voice(monkeypatch):
    async def fake_trim(audio_bytes, filename):
        return audio_bytes

    async def fake_clone(audio_bytes, mime_type, preferred_name):
        assert audio_bytes == b"abc"
        assert mime_type == "audio/mpeg"
        assert preferred_name == "my_clone"
        return "voice-clone-123"

    monkeypatch.setattr("app.api.voice_clones._trim_clone_audio_to_30s", fake_trim)
    monkeypatch.setattr("app.api.voice_clones.create_qwen_voice_clone", fake_clone)

    client, SessionLocal = _make_client()
    token, user_id = _register_and_token(client)

    response = client.post(
        "/api/voice-clones",
        data={"name": "我的克隆音色", "preferredName": "my_clone"},
        files={"file": ("voice.mp3", b"abc", "audio/mpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["displayName"] == "我的克隆音色"
    assert body["ownerId"] == user_id
    assert body["providers"][0]["provider"] == "bailian_tts"
    assert body["providers"][0]["providerVoiceId"] == "bailian:qwen3-tts-vc-2026-01-22:voice-clone-123"

    db = SessionLocal()
    voice = db.query(Voice).filter(Voice.owner_id == user_id).one()
    provider = db.query(VoiceProviderProfile).filter(VoiceProviderProfile.voice_id == voice.id).one()
    db.close()
    assert voice.display_name == "我的克隆音色"
    assert provider.provider_voice_id == "bailian:qwen3-tts-vc-2026-01-22:voice-clone-123"


def test_create_voice_clone_sends_trimmed_audio_to_bailian(monkeypatch):
    async def fake_trim(audio_bytes, filename):
        assert audio_bytes == b"full-audio"
        assert filename == "voice.mp3"
        return b"first-30s"

    async def fake_clone(audio_bytes, mime_type, preferred_name):
        assert audio_bytes == b"first-30s"
        return "voice-clone-trimmed"

    monkeypatch.setattr("app.api.voice_clones._trim_clone_audio_to_30s", fake_trim)
    monkeypatch.setattr("app.api.voice_clones.create_qwen_voice_clone", fake_clone)

    client, _ = _make_client()
    token, _ = _register_and_token(client)

    response = client.post(
        "/api/voice-clones",
        data={"name": "我的克隆音色"},
        files={"file": ("voice.mp3", b"full-audio", "audio/mpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, response.text


def test_create_voice_clone_generates_ascii_preferred_name_when_blank(monkeypatch):
    calls = []

    async def fake_trim(audio_bytes, filename):
        return audio_bytes

    async def fake_clone(audio_bytes, mime_type, preferred_name):
        calls.append(preferred_name)
        return "voice-clone-blank"

    monkeypatch.setattr("app.api.voice_clones._trim_clone_audio_to_30s", fake_trim)
    monkeypatch.setattr("app.api.voice_clones.create_qwen_voice_clone", fake_clone)

    client, _ = _make_client()
    token, _ = _register_and_token(client)

    response = client.post(
        "/api/voice-clones",
        data={"name": "我的克隆音色"},
        files={"file": ("voice.mp3", b"abc", "audio/mpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, response.text
    assert calls[0].startswith("voice_")
