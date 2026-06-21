import asyncio
import shutil
import tempfile
from pathlib import Path
from collections.abc import Sequence

import edge_tts

from app.work_schemas import TextSegment

EMOTION_RATE_MAP = {
    "calm": 0,
    "happy": 8,
    "sad": -10,
    "excited": 16,
}

EMOTION_PITCH_MAP = {
    "calm": 0,
    "happy": 8,
    "sad": -12,
    "excited": 18,
}


async def synthesize_to_file(
    text: str,
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    output_path: Path,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await _synthesize_text(
        text=text,
        voice=voice,
        speed=speed,
        pitch=pitch,
        emotion=emotion,
        output_path=output_path,
    )
    return max(1, round(await _probe_duration(output_path)))


async def synthesize_segments_to_file(
    segments: Sequence[TextSegment],
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    output_path: Path,
    max_concurrency: int = 3,
) -> int:
    if not segments:
        raise ValueError("没有可合成的文本分段")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(max_concurrency)

    with tempfile.TemporaryDirectory(prefix="tts-segments-", dir=output_path.parent) as temp_dir:
        temp_path = Path(temp_dir)
        segment_paths = [temp_path / f"segment-{index:04d}.mp3" for index in range(len(segments))]

        async def synthesize_one(index: int, segment: TextSegment) -> None:
            async with semaphore:
                await _synthesize_with_retry(
                    text=segment.text,
                    voice=voice,
                    speed=speed,
                    pitch=pitch,
                    emotion=emotion,
                    output_path=segment_paths[index],
                )

        await asyncio.gather(
            *(synthesize_one(index, segment) for index, segment in enumerate(segments))
        )
        duration = await _concat_segments(
            segment_paths=segment_paths,
            pauses_ms=[segment.pauseMs for segment in segments],
            output_path=output_path,
            temp_path=temp_path,
        )

    return max(1, round(duration))


async def _synthesize_with_retry(
    text: str,
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    output_path: Path,
    attempts: int = 3,
) -> None:
    for attempt in range(attempts):
        try:
            await _synthesize_text(text, voice, speed, pitch, emotion, output_path)
            return
        except Exception:
            output_path.unlink(missing_ok=True)
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(0.5 * (2**attempt))


async def _synthesize_text(
    text: str,
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    output_path: Path,
) -> None:
    rate_percent = int(round((speed - 1.0) * 100)) + EMOTION_RATE_MAP.get(emotion, 0)
    rate_percent = max(-50, min(100, rate_percent))
    pitch_hz = pitch + EMOTION_PITCH_MAP.get(emotion, 0)
    pitch_hz = max(-100, min(100, pitch_hz))

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate_percent:+d}%",
        pitch=f"{pitch_hz:+d}Hz",
    )
    await communicate.save(str(output_path))


async def _concat_segments(
    segment_paths: Sequence[Path],
    pauses_ms: Sequence[int],
    output_path: Path,
    temp_path: Path,
) -> float:
    if len(segment_paths) == 1:
        shutil.copyfile(segment_paths[0], output_path)
        return await _probe_duration(output_path)

    silence_paths: dict[int, Path] = {}
    for pause_ms in sorted(set(pauses_ms[:-1])):
        silence_path = temp_path / f"silence-{pause_ms}.mp3"
        await _create_silence(silence_path, pause_ms)
        silence_paths[pause_ms] = silence_path

    manifest_path = temp_path / "concat.txt"
    manifest_lines: list[str] = []
    for index, segment_path in enumerate(segment_paths):
        manifest_lines.append(f"file '{_escape_concat_path(segment_path)}'")
        if index < len(segment_paths) - 1:
            manifest_lines.append(f"file '{_escape_concat_path(silence_paths[pauses_ms[index]])}'")
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    await _run_command(
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(manifest_path),
        "-ar",
        "24000",
        "-ac",
        "1",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "48k",
        str(output_path),
    )
    return await _probe_duration(output_path)


async def _create_silence(output_path: Path, pause_ms: int) -> None:
    await _run_command(
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=24000:cl=mono",
        "-t",
        f"{pause_ms / 1000:.3f}",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "48k",
        str(output_path),
    )


async def _probe_duration(path: Path) -> float:
    output = await _run_command(
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    )
    return float(output.strip())


async def _run_command(*command: str) -> str:
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        message = stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"命令执行失败: {command[0]}")
    return stdout.decode("utf-8", errors="replace")


def _escape_concat_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "'\\''")
