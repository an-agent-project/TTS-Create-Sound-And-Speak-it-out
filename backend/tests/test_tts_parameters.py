import asyncio

from app.services import tts
from app.work_schemas import GenerateRequest


def test_generate_request_accepts_numeric_pitch():
    payload = GenerateRequest(
        content="测试参数",
        voiceId="zh-CN-XiaoxiaoNeural",
        speed=1.5,
        pitch=25,
    )

    assert payload.speed == 1.5
    assert payload.pitch == 25


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
        )
    )

    assert captured["rate"] == "+50%"
    assert captured["pitch"] == "+25Hz"
