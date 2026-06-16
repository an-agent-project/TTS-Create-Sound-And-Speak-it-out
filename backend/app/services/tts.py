from pathlib import Path

import edge_tts

PITCH_MAP = {
    "low": -20,
    "normal": 0,
    "high": 20,
}

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
    pitch: str,
    emotion: str,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rate_percent = int(round((speed - 1.0) * 100)) + EMOTION_RATE_MAP.get(emotion, 0)
    rate_percent = max(-50, min(100, rate_percent))
    pitch_hz = PITCH_MAP.get(pitch, 0) + EMOTION_PITCH_MAP.get(emotion, 0)

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate_percent:+d}%",
        pitch=f"{pitch_hz:+d}Hz",
    )
    await communicate.save(str(output_path))
