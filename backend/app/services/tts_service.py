from pathlib import Path

import edge_tts

from app.models import VoiceProviderProfile
from app.services.bailian_tts import BAILIAN_TTS_PROVIDER, synthesize_bailian_to_file


PREVIEW_DIR = Path(__file__).resolve().parents[2] / "static" / "previews"


async def synthesize_preview(
    text: str,
    provider_profile: VoiceProviderProfile,
    output_filename: str,
) -> dict:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREVIEW_DIR / output_filename

    if provider_profile.provider == BAILIAN_TTS_PROVIDER:
        await synthesize_bailian_to_file(
            text=text,
            provider_voice_id=provider_profile.provider_voice_id,
            output_path=output_path,
        )
    elif provider_profile.provider == "edge_tts":
        communicate = edge_tts.Communicate(
            text=text,
            voice=provider_profile.provider_voice_id,
        )
        await communicate.save(str(output_path))
    else:
        raise RuntimeError(f"Unsupported TTS provider: {provider_profile.provider}")

    return {
        "filename": output_filename,
        "path": output_path,
        "duration": max(1, round(len(text) / 5)),
    }