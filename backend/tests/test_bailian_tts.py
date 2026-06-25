import asyncio
from types import SimpleNamespace

from app.services import bailian_tts


def test_qwen_tts_call_uses_multimodal_conversation(monkeypatch):
    captured = {}

    class FakeMultiModalConversation:
        @staticmethod
        def call(**kwargs):
            captured.update(kwargs)
            return {"output": {"audio": {"url": "https://example.test/audio.mp3"}}}

    fake_dashscope = SimpleNamespace(MultiModalConversation=FakeMultiModalConversation)
    monkeypatch.setitem(__import__("sys").modules, "dashscope", fake_dashscope)

    response = asyncio.run(
        bailian_tts._call_qwen_tts(
            text="你好",
            model="qwen3-tts-flash",
            voice="Cherry",
            language_type="Chinese",
            api_key="sk-test",
            workspace=None,
        )
    )

    assert response["output"]["audio"]["url"] == "https://example.test/audio.mp3"
    assert captured == {
        "api_key": "sk-test",
        "model": "qwen3-tts-flash",
        "text": "你好",
        "voice": "Cherry",
        "language_type": "Chinese",
        "stream": False,
    }


def test_extract_audio_url_from_dashscope_response_object():
    response = SimpleNamespace(output={"audio": {"url": "https://example.test/audio.mp3"}})

    assert bailian_tts._extract_audio_url(response) == "https://example.test/audio.mp3"

def test_create_qwen_voice_clone_posts_data_uri(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200
        text = "ok"

        def json(self):
            return {"output": {"voice": "voice-test-123"}}

    class FakeClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, json, headers):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test")
    monkeypatch.setenv("DASHSCOPE_WORKSPACE", "ws-test")
    monkeypatch.setattr(bailian_tts.httpx, "AsyncClient", FakeClient)

    voice = asyncio.run(
        bailian_tts.create_qwen_voice_clone(
            audio_bytes=b"abc",
            mime_type="audio/mpeg",
            preferred_name="my_voice",
        )
    )

    assert voice == "voice-test-123"
    assert captured["url"] == "https://ws-test.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/customization"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["json"]["model"] == "qwen-voice-enrollment"
    assert captured["json"]["input"]["target_model"] == "qwen3-tts-vc-2026-01-22"
    assert captured["json"]["input"]["preferred_name"] == "my_voice"
    assert captured["json"]["input"]["audio"]["data"] == "data:audio/mpeg;base64,YWJj"
