from fastapi.testclient import TestClient

from app.main import app


def test_translate_preview_returns_translated_text(monkeypatch):
    def fake_translate(text: str, target_lang: str) -> str:
        assert text == "你好，世界"
        assert target_lang == "en"
        return "Hello, world"

    monkeypatch.setattr("app.main.translate_text", fake_translate)

    response = TestClient(app).post(
        "/api/text/translate",
        json={"content": "你好，世界", "targetLang": "en"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "sourceText": "你好，世界",
        "targetLang": "en",
        "translatedText": "Hello, world",
    }


def test_translate_preview_rejects_unsupported_language():
    response = TestClient(app).post(
        "/api/text/translate",
        json={"content": "hello", "targetLang": "nl"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported target language"


def test_generate_tts_uses_edited_translated_content_without_retranslating(monkeypatch, tmp_path):
    from pathlib import Path

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.database import get_db
    from app.models import Base

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

    def fail_translate(text: str, target_lang: str) -> str:
        raise AssertionError("translate_text should not be called when translatedContent is supplied")

    async def fake_synthesize(**kwargs):
        joined_text = " ".join(segment.text for segment in kwargs["segments"])
        assert "Edited English text" in joined_text
        kwargs["output_path"].write_bytes(b"voice")
        return 1

    async def fake_mix(voice_path: Path, bgm_path_arg: Path | None, output_path: Path, bgm_volume: int):
        output_path.write_bytes(b"mixed")
        return 2.0

    monkeypatch.setattr("app.main.translate_text", fail_translate)
    monkeypatch.setattr("app.main.synthesize_segments_to_file", fake_synthesize)
    monkeypatch.setattr("app.main.mix_bgm_to_file", fake_mix)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/api/tts/generate",
            json={
                "content": "你好，世界",
                "translatedContent": "Edited English text",
                "voiceId": "zh-CN-XiaoxiaoNeural",
                "outputLang": "en",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert response.json()["content"] == "Edited English text"
    assert response.json()["voiceId"] == "en-US-JennyNeural"

def test_generate_tts_keeps_bailian_voice_for_non_chinese_output(monkeypatch, tmp_path):
    from pathlib import Path

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.database import get_db
    from app.models import Base, Voice, VoiceProviderProfile

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    voice = Voice(voice_key="bailian-qwen-test", display_name="Qwen Test", gender="female", is_active=True)
    db.add(voice)
    db.flush()
    db.add(
        VoiceProviderProfile(
            voice_id=voice.id,
            provider="bailian_tts",
            provider_voice_id="bailian:qwen3-tts-flash:Cherry",
            locale="zh-CN",
            is_active=True,
            is_default=True,
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
        assert kwargs["voice"] == "bailian:qwen3-tts-flash:Cherry"
        assert kwargs["provider"] == "bailian_tts"
        assert kwargs["output_lang"] == "en"
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
                "content": "source text",
                "translatedContent": "Edited English text",
                "voiceId": "bailian:qwen3-tts-flash:Cherry",
                "outputLang": "en",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert response.json()["voiceId"] == "bailian:qwen3-tts-flash:Cherry"
    assert response.json()["voiceName"] == "Qwen Test"