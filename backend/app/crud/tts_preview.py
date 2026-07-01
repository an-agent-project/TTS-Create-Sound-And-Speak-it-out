from hashlib import sha256
from pathlib import Path

from sqlalchemy.orm import Session

from app import models


def hash_sample_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def get_provider_profile_by_voice_id(
    db: Session,
    provider_voice_id: str,
    user_id: int | None = None,
) -> models.VoiceProviderProfile | None:
    query = (
        db.query(models.VoiceProviderProfile)
        .join(models.Voice)
        .filter(
            models.VoiceProviderProfile.provider_voice_id == provider_voice_id,
            models.VoiceProviderProfile.is_active.is_(True),
            models.Voice.is_active.is_(True),
        )
    )
    if user_id is not None:
        query = query.filter(
            (models.Voice.owner_id.is_(None)) | (models.Voice.owner_id == user_id)
        )
    else:
        query = query.filter(models.Voice.owner_id.is_(None))
    return query.first()


def get_ready_preview_cache(
    db: Session,
    provider_profile_id: int,
    sample_text_hash: str,
    audio_format: str = "mp3",
) -> models.VoicePreviewAudio | None:
    return (
        db.query(models.VoicePreviewAudio)
        .filter(
            models.VoicePreviewAudio.voice_provider_profile_id == provider_profile_id,
            models.VoicePreviewAudio.sample_text_hash == sample_text_hash,
            models.VoicePreviewAudio.format == audio_format,
            models.VoicePreviewAudio.status == "ready",
        )
        .first()
    )


def build_preview_filename(
    provider_profile_id: int,
    sample_text_hash: str,
    audio_format: str = "mp3",
) -> str:
    return f"preview-{provider_profile_id}-{sample_text_hash[:16]}.{audio_format}"


def get_preview_cache_by_key(
    db: Session,
    provider_profile_id: int,
    sample_text_hash: str,
    audio_format: str = "mp3",
) -> models.VoicePreviewAudio | None:
    return (
        db.query(models.VoicePreviewAudio)
        .filter(
            models.VoicePreviewAudio.voice_provider_profile_id == provider_profile_id,
            models.VoicePreviewAudio.sample_text_hash == sample_text_hash,
            models.VoicePreviewAudio.format == audio_format,
        )
        .first()
    )


def mark_preview_cache_missing(
    db: Session,
    cache_record: models.VoicePreviewAudio,
) -> models.VoicePreviewAudio:
    cache_record.status = "missing"
    cache_record.error_message = "Cached audio file is missing from storage."
    db.commit()
    db.refresh(cache_record)
    return cache_record


def create_ready_preview_cache(
    db: Session,
    provider_profile_id: int,
    sample_text: str,
    audio_url: str,
    audio_path: Path,
    duration_seconds: int,
    audio_format: str = "mp3",
) -> models.VoicePreviewAudio:
    sample_text_hash = hash_sample_text(sample_text)
    cache_record = get_preview_cache_by_key(
        db,
        provider_profile_id=provider_profile_id,
        sample_text_hash=sample_text_hash,
        audio_format=audio_format,
    )
    if not cache_record:
        cache_record = models.VoicePreviewAudio(
            voice_provider_profile_id=provider_profile_id,
            sample_text_hash=sample_text_hash,
            format=audio_format,
        )
        db.add(cache_record)

    cache_record.sample_text = sample_text
    cache_record.audio_path = str(audio_path)
    cache_record.audio_url = audio_url
    cache_record.duration_seconds = duration_seconds
    cache_record.file_size_bytes = audio_path.stat().st_size if audio_path.exists() else None
    cache_record.status = "ready"
    cache_record.error_message = None
    db.add(cache_record)
    db.commit()
    db.refresh(cache_record)
    return cache_record
