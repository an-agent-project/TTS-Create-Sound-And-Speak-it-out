import asyncio

from app.services import tts
from app.services.text_processing import (
    PARAGRAPH_PAUSE_MS,
    WORD_BOUNDARY_PAUSE_MS,
    split_segments,
)
from app.work_schemas import TextSegment


def test_split_segments_preserves_paragraph_boundaries():
    segments = split_segments(
        "第一段第一句。第一段第二句。\n\n第二段只有一句。",
        max_length=40,
    )

    assert [segment.text for segment in segments] == [
        "第一段第一句。第一段第二句。",
        "第二段只有一句。",
    ]
    assert [segment.pauseMs for segment in segments] == [
        PARAGRAPH_PAUSE_MS,
        PARAGRAPH_PAUSE_MS,
    ]


def test_split_segments_limits_very_long_sentences():
    segments = split_segments("这是一个没有标点的超长句子" * 20, max_length=50)

    assert len(segments) > 1
    assert all(0 < len(segment.text) <= 50 for segment in segments)
    assert [segment.index for segment in segments] == list(range(len(segments)))


def test_split_segments_respects_chinese_word_boundaries():
    text = "人工智能技术正在改变有声读物的制作方式并提升内容生产效率" * 4
    protected_words = ["人工智能", "有声读物", "制作方式", "生产效率"]

    segments = split_segments(text, max_length=24)

    assert "".join(segment.text for segment in segments) == text
    boundaries = []
    consumed = 0
    for segment in segments[:-1]:
        consumed += len(segment.text)
        boundaries.append(consumed)

    for word in protected_words:
        start = 0
        while (index := text.find(word, start)) != -1:
            assert not any(index < boundary < index + len(word) for boundary in boundaries)
            start = index + len(word)

    assert all(segment.pauseMs == WORD_BOUNDARY_PAUSE_MS for segment in segments[:-1])


def test_split_segments_keeps_closing_punctuation_with_previous_words():
    text = "这是用于验证中文词语边界的较长内容，后面还有补充说明。"

    segments = split_segments(text, max_length=18)

    assert "".join(segment.text for segment in segments) == text
    assert all(not segment.text.startswith(("，", "。")) for segment in segments)


def test_segment_synthesis_keeps_order_and_pauses(monkeypatch, tmp_path):
    synthesized = []
    concatenated = {}

    async def fake_synthesize_with_retry(
        text,
        voice,
        speed,
        pitch,
        emotion,
        output_path,
        attempts=3,
    ):
        synthesized.append((output_path.name, text, speed, pitch, emotion))
        output_path.write_bytes(text.encode("utf-8"))

    async def fake_concat_segments(segment_paths, pauses_ms, output_path, temp_path):
        concatenated["names"] = [path.name for path in segment_paths]
        concatenated["pauses"] = list(pauses_ms)
        output_path.write_bytes(b"combined mp3")
        return 12.6

    monkeypatch.setattr(tts, "_synthesize_with_retry", fake_synthesize_with_retry)
    monkeypatch.setattr(tts, "_concat_segments", fake_concat_segments)
    monkeypatch.setattr(tts, "_has_media_tools", lambda: True)

    segments = [
        TextSegment(index=0, text="第一段。", pauseMs=700),
        TextSegment(index=1, text="第二段？", pauseMs=750),
        TextSegment(index=2, text="第三段。", pauseMs=900),
    ]
    output_path = tmp_path / "result.mp3"

    duration = asyncio.run(
        tts.synthesize_segments_to_file(
            segments=segments,
            voice="zh-CN-XiaoxiaoNeural",
            speed=1.1,
            pitch=10,
            emotion="calm",
            output_path=output_path,
        )
    )

    assert sorted(synthesized) == [
        ("segment-0000.mp3", "第一段。", 1.1, 10, "calm"),
        ("segment-0001.mp3", "第二段？", 1.1, 10, "calm"),
        ("segment-0002.mp3", "第三段。", 1.1, 10, "calm"),
    ]
    assert concatenated == {
        "names": ["segment-0000.mp3", "segment-0001.mp3", "segment-0002.mp3"],
        "pauses": [700, 750, 900],
    }
    assert duration == 13
    assert output_path.read_bytes() == b"combined mp3"


def test_segment_synthesis_falls_back_when_ffmpeg_is_missing(monkeypatch, tmp_path):
    synthesized = []

    monkeypatch.setattr(tts, "_has_media_tools", lambda: False)

    async def fake_synthesize_with_retry(
        text,
        voice,
        speed,
        pitch,
        emotion,
        output_path,
        attempts=3,
    ):
        synthesized.append((text, voice, speed, pitch, emotion))
        output_path.write_bytes(b"fallback mp3")

    monkeypatch.setattr(tts, "_synthesize_with_retry", fake_synthesize_with_retry)

    segments = [
        TextSegment(index=0, text="第一段。", pauseMs=700),
        TextSegment(index=1, text="第二段。", pauseMs=900),
    ]
    output_path = tmp_path / "fallback.mp3"

    duration = asyncio.run(
        tts.synthesize_segments_to_file(
            segments=segments,
            voice="zh-CN-XiaoxiaoNeural",
            speed=1.0,
            pitch=0,
            emotion="calm",
            output_path=output_path,
        )
    )

    assert synthesized == [("第一段。\n\n第二段。", "zh-CN-XiaoxiaoNeural", 1.0, 0, "calm")]
    assert duration >= 1
    assert output_path.read_bytes() == b"fallback mp3"


def test_media_tool_lookup_uses_configured_ffmpeg_dir(monkeypatch, tmp_path):
    bin_dir = tmp_path / "ffmpeg" / "bin"
    bin_dir.mkdir(parents=True)
    ffmpeg = bin_dir / "ffmpeg.exe"
    ffmpeg.write_text("", encoding="utf-8")

    monkeypatch.setattr(tts.shutil, "which", lambda name: None)
    monkeypatch.setenv("TTS_FFMPEG_DIR", str(bin_dir))

    assert tts._media_command("ffmpeg") == str(ffmpeg)
