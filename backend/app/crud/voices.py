from sqlalchemy.orm import Session, selectinload

from app import models
from app.schemas import VoiceCreate, VoiceUpdate


def list_voices(
    db: Session,
    category: str | None = None,
    gender: str | None = None,
    recommended_only: bool = False,
) -> list[models.Voice]:
    query = (
        db.query(models.Voice)
        .options(selectinload(models.Voice.providers))
        .filter(models.Voice.is_active.is_(True))
    )
    if category:
        query = query.filter(models.Voice.category == category)
    if gender:
        query = query.filter(models.Voice.gender == gender)
    if recommended_only:
        query = query.filter(models.Voice.is_recommended.is_(True))
    return query.order_by(models.Voice.id.asc()).all()


def get_voice(db: Session, voice_id: int) -> models.Voice | None:
    return (
        db.query(models.Voice)
        .options(selectinload(models.Voice.providers))
        .filter(models.Voice.id == voice_id, models.Voice.is_active.is_(True))
        .first()
    )


def get_voice_by_key(db: Session, voice_key: str) -> models.Voice | None:
    return db.query(models.Voice).filter(models.Voice.voice_key == voice_key).first()


def create_voice(db: Session, payload: VoiceCreate) -> models.Voice:
    voice = models.Voice(
        voice_key=payload.voice_key,
        display_name=payload.display_name,
        gender=payload.gender,
        style=payload.style,
        category=payload.category,
        description=payload.description,
        is_recommended=payload.is_recommended,
        is_active=True,
    )
    for provider in payload.providers:
        voice.providers.append(
            models.VoiceProviderProfile(
                provider=provider.provider,
                provider_voice_id=provider.provider_voice_id,
                locale=provider.locale,
                supports_wav=provider.supports_wav,
                supports_mp3=provider.supports_mp3,
                is_default=provider.is_default,
                is_active=True,
            )
        )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    return get_voice(db, voice.id)


def update_voice(db: Session, voice: models.Voice, payload: VoiceUpdate) -> models.Voice:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voice, field, value)
    db.commit()
    db.refresh(voice)
    return get_voice(db, voice.id)


def soft_delete_voice(db: Session, voice: models.Voice) -> None:
    voice.is_active = False
    for provider in voice.providers:
        provider.is_active = False
    db.commit()
