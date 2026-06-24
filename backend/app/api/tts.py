from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_optional_user
from app.crud import tts_preview as tts_preview_crud
from app.database import get_db
from app.models import User
from app.schemas import TtsPreviewRequest, TtsPreviewResponse
from app.services.qwen_tts import synthesize_qwen_to_file
from app.services.tts_service import synthesize_preview
from app.services.voice_provider import resolve_provider_by_voice_or_provider_id


router = APIRouter(prefix="/api/tts", tags=["tts"])


async def synthesize_provider_preview(text, provider_profile, output_filename: str) -> dict:
    if provider_profile.provider == "edge_tts":
        return await synthesize_preview(
            text=text,
            voice_id=provider_profile.provider_voice_id,
            output_filename=output_filename,
        )
    if provider_profile.provider == "qwen3_tts":
        from app.services.tts_service import PREVIEW_DIR

        output_path = PREVIEW_DIR / output_filename
        duration = await synthesize_qwen_to_file(
            text=text,
            provider_profile=provider_profile,
            output_path=output_path,
        )
        return {"filename": output_filename, "path": output_path, "duration": duration}
    raise RuntimeError(f"Unsupported TTS provider: {provider_profile.provider}")


@router.post("/preview", response_model=TtsPreviewResponse)
async def preview_tts(
    payload: TtsPreviewRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> TtsPreviewResponse:
    resolved = resolve_provider_by_voice_or_provider_id(
        db,
        payload.voice_id,
        user_id=current_user.id if current_user else None,
    )
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="voice provider not found",
        )
    provider_profile = resolved.provider

    sample_text_hash = tts_preview_crud.hash_sample_text(payload.text)
    cached_preview = tts_preview_crud.get_ready_preview_cache(
        db,
        provider_profile_id=provider_profile.id,
        sample_text_hash=sample_text_hash,
    )
    if cached_preview:
        if Path(cached_preview.audio_path).exists():
            return TtsPreviewResponse(
                audioUrl=cached_preview.audio_url,
                duration=int(cached_preview.duration_seconds or 0),
            )
        tts_preview_crud.mark_preview_cache_missing(db, cached_preview)

    output_filename = tts_preview_crud.build_preview_filename(
        provider_profile_id=provider_profile.id,
        sample_text_hash=sample_text_hash,
    )
    result = await synthesize_provider_preview(
        payload.text,
        provider_profile,
        output_filename=output_filename,
    )
    audio_url = f"/static/previews/{result['filename']}"
    tts_preview_crud.create_ready_preview_cache(
        db,
        provider_profile_id=provider_profile.id,
        sample_text=payload.text,
        audio_url=audio_url,
        audio_path=result["path"],
        duration_seconds=result["duration"],
    )
    return TtsPreviewResponse(
        audioUrl=audio_url,
        duration=result["duration"],
    )
