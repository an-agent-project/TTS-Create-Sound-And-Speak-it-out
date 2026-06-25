from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User, Voice, VoiceProviderProfile
from app.schemas import VoiceRead
from app.services.bailian_tts import (
    BAILIAN_TTS_PROVIDER,
    BAILIAN_VOICE_CLONE_TARGET_MODEL,
    create_qwen_voice_clone,
)

router = APIRouter(prefix="/api/voice-clones", tags=["voice-clones"])

SUPPORTED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/wave"}
MAX_CLONE_AUDIO_BYTES = 10 * 1024 * 1024


@router.post("", response_model=VoiceRead, status_code=status.HTTP_201_CREATED)
async def create_voice_clone(
    name: str = Form(..., min_length=1, max_length=50),
    preferredName: str | None = Form(default=None, max_length=64),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoiceRead:
    content_type = (file.content_type or "").lower()
    if content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="unsupported audio file type")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio file cannot be empty")
    if len(audio_bytes) > MAX_CLONE_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="audio file is too large")

    preferred_name = _normalize_preferred_name(preferredName or name)
    try:
        cloned_voice_id = await create_qwen_voice_clone(
            audio_bytes=audio_bytes,
            mime_type=content_type,
            preferred_name=preferred_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bailian voice cloning failed: {exc}") from exc

    voice = Voice(
        voice_key=f"clone-{current_user.id}-{uuid4().hex[:12]}",
        display_name=name.strip(),
        gender="female",
        style="克隆",
        category="个人音色",
        description="百炼 Qwen-TTS 声音复刻音色。",
        is_recommended=False,
        is_active=True,
        owner_id=current_user.id,
    )
    voice.providers.append(
        VoiceProviderProfile(
            provider=BAILIAN_TTS_PROVIDER,
            provider_voice_id=f"bailian:{BAILIAN_VOICE_CLONE_TARGET_MODEL}:{cloned_voice_id}",
            locale="zh-CN",
            supports_wav=False,
            supports_mp3=True,
            is_default=True,
            is_active=True,
        )
    )
    db.add(voice)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="cloned voice already exists") from exc
    db.refresh(voice)
    return voice


def _normalize_preferred_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value.strip())
    cleaned = cleaned.strip("_-")
    return (cleaned or f"voice_{uuid4().hex[:8]}")[:64]