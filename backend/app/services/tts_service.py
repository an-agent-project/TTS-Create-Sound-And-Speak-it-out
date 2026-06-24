from pathlib import Path

from app.models import VoiceProviderProfile
from app.services.qwen_tts import synthesize_qwen_to_file


PREVIEW_DIR = Path(__file__).resolve().parents[2] / "static" / "previews"


async def synthesize_preview(text: str, voice_id: str, output_filename: str) -> dict:
    import edge_tts

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREVIEW_DIR / output_filename

    communicate = edge_tts.Communicate(text=text, voice=voice_id)
    await communicate.save(str(output_path))

    return {
        "filename": output_filename,
        "path": output_path,
        "duration": max(1, round(len(text) / 5)),
    }


async def synthesize_provider_preview(
    text: str,
    provider_profile: VoiceProviderProfile,
    output_filename: str,
) -> dict:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREVIEW_DIR / output_filename

    if provider_profile.provider == "edge_tts":
        return await synthesize_preview(
            text=text,
            voice_id=provider_profile.provider_voice_id,
            output_filename=output_filename,
        )

    if provider_profile.provider == "qwen3_tts":
        duration = await synthesize_qwen_to_file(
            text=text,
            provider_profile=provider_profile,
            output_path=output_path,
        )
        return {
            "filename": output_filename,
            "path": output_path,
            "duration": duration,
        }

    raise RuntimeError(f"Unsupported TTS provider: {provider_profile.provider}")
