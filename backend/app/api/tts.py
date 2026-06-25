from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import tts_preview as tts_preview_crud
from app.database import get_db
from app.schemas import TtsPreviewRequest, TtsPreviewResponse
from app.services.tts_service import synthesize_preview


router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.post("/preview", response_model=TtsPreviewResponse)
async def preview_tts(
    payload: TtsPreviewRequest,
    db: Session = Depends(get_db),
) -> TtsPreviewResponse:
    provider_profile = tts_preview_crud.get_provider_profile_by_voice_id(db, payload.voice_id)
    if not provider_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="voice provider not found",
        )

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
    result = await synthesize_preview(
        payload.text,
        provider_profile=provider_profile,
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
