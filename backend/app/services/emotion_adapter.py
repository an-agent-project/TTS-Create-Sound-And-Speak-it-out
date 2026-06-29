from dataclasses import dataclass


@dataclass(frozen=True)
class EmotionProfile:
    rate_delta: int
    pitch_delta: int
    instruction: str


EMOTION_PROFILES = {
    "calm": EmotionProfile(0, 0, "用平稳、自然、清晰的语气朗读，吐字清楚，节奏适中。"),
    "happy": EmotionProfile(8, 8, "用开朗、轻快、有亲和力的语气朗读，语调略微上扬。"),
    "sad": EmotionProfile(-10, -12, "用低缓、克制、略带忧伤的语气朗读，节奏放慢。"),
    "excited": EmotionProfile(16, 18, "用兴奋、有感染力、节奏更强的语气朗读，表达更有能量。"),
}


@dataclass(frozen=True)
class AdaptedEmotion:
    rate_percent: int
    pitch_hz: int
    instruction: str


INTENSITY_SCALE = {
    "light": 0.6,
    "normal": 1.0,
    "strong": 1.5,
}

INTENSITY_PREFIX = {
    "light": "轻微地",
    "normal": "",
    "strong": "明显地",
}


def adapt_emotion(
    provider: str,
    emotion: str,
    speed: float,
    pitch: int,
    intensity: str = "normal",
) -> AdaptedEmotion:
    profile = EMOTION_PROFILES.get(emotion, EMOTION_PROFILES["calm"])
    scale = INTENSITY_SCALE.get(intensity, INTENSITY_SCALE["normal"])

    # ponytail: only Edge consumes numeric emotion today; prompt providers can reuse instruction later.
    if provider == "edge_tts":
        rate_percent = int(round((speed - 1.0) * 100)) + round(profile.rate_delta * scale)
        pitch_hz = pitch + round(profile.pitch_delta * scale)
    else:
        rate_percent = int(round((speed - 1.0) * 100))
        pitch_hz = pitch

    prefix = INTENSITY_PREFIX.get(intensity, "")
    instruction = f"{prefix}{profile.instruction}" if prefix else profile.instruction

    return AdaptedEmotion(
        rate_percent=max(-50, min(100, rate_percent)),
        pitch_hz=max(-100, min(100, pitch_hz)),
        instruction=instruction,
    )
