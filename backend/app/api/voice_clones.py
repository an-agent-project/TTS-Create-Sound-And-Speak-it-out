from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import SessionLocal, get_db
from app.job_queue import create_job, update_job
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
    audio_bytes, content_type = await _read_clone_audio(file)
    return await _create_voice_clone_from_audio(
        name=name,
        preferred_name=preferredName,
        audio_bytes=audio_bytes,
        content_type=content_type,
        current_user=current_user,
        db=db,
    )


@router.post("/jobs")
async def create_voice_clone_job(
    background_tasks: BackgroundTasks,
    name: str = Form(..., min_length=1, max_length=50),
    preferredName: str | None = Form(default=None, max_length=64),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    audio_bytes, content_type = await _read_clone_audio(file)
    job = await create_job("voice_clone", owner_id=current_user.id, message="音色克隆任务已创建")
    background_tasks.add_task(
        _run_voice_clone_job,
        job.id,
        name,
        preferredName,
        audio_bytes,
        content_type,
        current_user.id,
    )
    return {"jobId": job.id}


async def _read_clone_audio(file: UploadFile) -> tuple[bytes, str]:
    content_type = (file.content_type or "").lower()
    if content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="unsupported audio file type")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio file cannot be empty")
    if len(audio_bytes) > MAX_CLONE_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="audio file is too large")
    return audio_bytes, content_type


async def _run_voice_clone_job(
    job_id: str,
    name: str,
    preferred_name: str | None,
    audio_bytes: bytes,
    content_type: str,
    user_id: int,
) -> None:
    db = SessionLocal()
    try:
        current_user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if not current_user:
            raise RuntimeError("user not found")

        async def report(progress: int, message: str) -> None:
            await update_job(job_id, status="running", progress=progress, message=message)

        await report(8, "正在校验源音频")
        voice = await _create_voice_clone_from_audio(
            name=name,
            preferred_name=preferred_name,
            audio_bytes=audio_bytes,
            content_type=content_type,
            current_user=current_user,
            db=db,
            progress=report,
        )
        await update_job(
            job_id,
            status="completed",
            progress=100,
            message="音色克隆完成",
            result={"voice": VoiceRead.model_validate(voice).model_dump(by_alias=True)},
        )
    except Exception as exc:
        await update_job(
            job_id,
            status="failed",
            progress=100,
            message="音色克隆失败",
            error=str(exc),
        )
    finally:
        db.close()


async def _create_voice_clone_from_audio(
    name: str,
    preferred_name: str | None,
    audio_bytes: bytes,
    content_type: str,
    current_user: User,
    db: Session,
    progress=None,
) -> Voice:
    async def report(value: int, message: str) -> None:
        if progress:
            await progress(value, message)

    normalized_preferred_name = _normalize_preferred_name(preferred_name)
    await report(20, "正在提交音色克隆请求")
    try:
        cloned_voice_id = await create_qwen_voice_clone(
            audio_bytes=audio_bytes,
            mime_type=content_type,
            preferred_name=normalized_preferred_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bailian voice cloning failed: {exc}") from exc

    await report(82, "正在写入个人音色库")
    voice = Voice(
        voice_key=f"clone-{current_user.id}-{uuid4().hex[:12]}",
        display_name=name.strip(),
        gender="female",
        style="cloned",
        category="personal voice",
        description="Bailian Qwen-TTS cloned voice.",
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


def _normalize_preferred_name(value: str | None) -> str:
    cleaned = "".join(ch if ch.isascii() and (ch.isalnum() or ch in {"_", "-"}) else "_" for ch in (value or "").strip())
    cleaned = cleaned.strip("_-")
    return (cleaned or f"voice_{uuid4().hex[:8]}")[:64]