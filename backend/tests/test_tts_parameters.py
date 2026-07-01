import asyncio

from app.services import tts
from app.services.azure_tts import _build_ssml
from app.services.bailian_tts import _instruction_model
from app.services.emotion_adapter import adapt_emotion
from app.work_schemas import GenerateRequest


def test_generate_request_accepts_numeric_pitch():
    payload = GenerateRequest(
        content="测试参数",
        voiceId="zh-CN-XiaoxiaoNeural",
        speed=1.5,
        pitch=25,
        voiceVolume=85,
        maxSegmentLength=80,
        pauseScale=1.5,
    )

    assert payload.speed == 1.5
    assert payload.pitch == 25
    assert payload.voiceVolume == 85
    assert payload.maxSegmentLength == 80
    assert payload.pauseScale == 1.5


def test_synthesize_passes_speed_and_pitch_to_edge_tts(monkeypatch, tmp_path):
    captured = {}

    class FakeCommunicate:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        async def save(self, path):
            captured["output_path"] = path

    monkeypatch.setattr(tts.edge_tts, "Communicate", FakeCommunicate)

    async def fake_probe_duration(path):
        return 2.4

    monkeypatch.setattr(tts, "_probe_duration", fake_probe_duration)

    asyncio.run(
        tts.synthesize_to_file(
            text="测试参数",
            voice="zh-CN-XiaoxiaoNeural",
            speed=1.5,
            pitch=25,
            emotion="calm",
            output_path=tmp_path / "result.mp3",
            voice_volume=85,
        )
    )

    assert captured["rate"] == "+50%"
    assert captured["pitch"] == "+25Hz"
    assert captured["volume"] == "-15%"


def test_synthesize_strips_personal_clone_suffix_for_edge_tts(monkeypatch, tmp_path):
    captured = {}

    class FakeCommunicate:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        async def save(self, path):
            captured["output_path"] = path

    monkeypatch.setattr(tts.edge_tts, "Communicate", FakeCommunicate)
    async def fake_probe_duration(path):
        return 1.0

    monkeypatch.setattr(tts, "_probe_duration", fake_probe_duration)

    asyncio.run(
        tts.synthesize_to_file(
            text="测试",
            voice="zh-CN-XiaoyiNeural_u2",
            speed=1.0,
            pitch=0,
            emotion="calm",
            output_path=tmp_path / "result.mp3",
        )
    )

    assert captured["voice"] == "zh-CN-XiaoyiNeural"


def test_emotion_adapter_maps_edge_emotion_to_voice_params():
    adapted = adapt_emotion("edge_tts", "happy", speed=1.0, pitch=0)

    assert adapted.rate_percent == 8
    assert adapted.pitch_hz == 8
    assert "开朗" in adapted.instruction


def test_emotion_adapter_scales_strong_intensity():
    adapted = adapt_emotion("edge_tts", "happy", speed=1.0, pitch=0, intensity="strong")

    assert adapted.rate_percent == 12
    assert adapted.pitch_hz == 12
    assert adapted.instruction.startswith("明显地")


def test_emotion_adapter_leaves_unknown_provider_numeric_params_neutral():
    adapted = adapt_emotion("prompt_tts", "excited", speed=1.2, pitch=5)

    assert adapted.rate_percent == 20
    assert adapted.pitch_hz == 5
    assert "兴奋" in adapted.instruction


def test_azure_ssml_maps_emotion_to_style_and_prosody():
    ssml = _build_ssml(
        text="你好 <测试>",
        voice="zh-CN-XiaoxiaoNeural",
        speed=1.2,
        pitch=5,
        emotion="happy",
    )

    assert 'voice name="zh-CN-XiaoxiaoNeural"' in ssml
    assert 'style="cheerful"' in ssml
    assert 'rate="+20%"' in ssml
    assert 'pitch="+5Hz"' in ssml
    assert "你好 &lt;测试&gt;" in ssml


def test_synthesize_routes_azure_provider(monkeypatch, tmp_path):
    captured = {}

    async def fake_synthesize_azure_to_file(**kwargs):
        captured.update(kwargs)
        kwargs["output_path"].write_bytes(b"mp3")

    async def fake_probe_duration(path):
        return 1.0

    monkeypatch.setattr(tts, "synthesize_azure_to_file", fake_synthesize_azure_to_file)
    monkeypatch.setattr(tts, "_probe_duration", fake_probe_duration)

    asyncio.run(
        tts.synthesize_to_file(
            text="测试",
            voice="zh-CN-XiaoxiaoNeural",
            speed=1.0,
            pitch=0,
            emotion="happy",
            output_path=tmp_path / "azure.mp3",
            provider="azure_tts",
        )
    )

    assert captured["emotion"] == "happy"
    assert captured["voice"] == "zh-CN-XiaoxiaoNeural"


def test_bailian_default_model_uses_instruction_model():
    assert _instruction_model("qwen3-tts-flash") == "qwen3-tts-instruct-flash"
