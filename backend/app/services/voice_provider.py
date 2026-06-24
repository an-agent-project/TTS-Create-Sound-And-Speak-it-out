from dataclasses import dataclass

from sqlalchemy.orm import Session, selectinload

from app import models


@dataclass(frozen=True)
class ResolvedVoice:
    voice: models.Voice
    provider: models.VoiceProviderProfile


def resolve_voice(db: Session, voice_id: str, user_id: int | None = None) -> ResolvedVoice | None:
    query = (
        db.query(models.Voice)
        .options(
            selectinload(models.Voice.providers).selectinload(
                models.VoiceProviderProfile.model_artifact
            )
        )
        .filter(models.Voice.is_active.is_(True))
    )

    if voice_id.isdigit():
        query = query.filter(models.Voice.id == int(voice_id))
    else:
        query = query.filter(models.Voice.voice_key == voice_id)

    if user_id is not None:
        query = query.filter(
            (models.Voice.owner_id.is_(None)) | (models.Voice.owner_id == user_id)
        )
    else:
        query = query.filter(models.Voice.owner_id.is_(None))

    voice = query.first()
    if not voice:
        return None

    provider = next(
        (item for item in voice.providers if item.is_active and item.is_default),
        None,
    ) or next((item for item in voice.providers if item.is_active), None)

    if not provider:
        return None

    return ResolvedVoice(voice=voice, provider=provider)


def resolve_provider_by_voice_or_provider_id(
    db: Session,
    voice_id: str,
    user_id: int | None = None,
) -> ResolvedVoice | None:
    resolved = resolve_voice(db, voice_id=voice_id, user_id=user_id)
    if resolved:
        return resolved

    provider = (
        db.query(models.VoiceProviderProfile)
        .options(
            selectinload(models.VoiceProviderProfile.voice),
            selectinload(models.VoiceProviderProfile.model_artifact),
        )
        .filter(
            models.VoiceProviderProfile.provider_voice_id == voice_id,
            models.VoiceProviderProfile.is_active.is_(True),
        )
        .first()
    )
    if not provider or not provider.voice or not provider.voice.is_active:
        return None
    if provider.voice.owner_id is not None and provider.voice.owner_id != user_id:
        return None
    return ResolvedVoice(voice=provider.voice, provider=provider)
