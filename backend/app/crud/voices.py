from pathlib import Path

from sqlalchemy.orm import Session, selectinload

from app import models
from app.schemas import VoiceCreate, VoiceUpdate


def list_voices(
    db: Session,
    category: str | None = None,
    gender: str | None = None,
    recommended_only: bool = False,
    user_id: int | None = None,
    scope: str | None = None,
) -> list[models.Voice]:
    query = (
        db.query(models.Voice)
        .options(selectinload(models.Voice.providers))
        .filter(models.Voice.is_active.is_(True))
    )
    if scope == "public":
        query = query.filter(models.Voice.owner_id.is_(None))
    elif scope == "personal" and user_id is not None:
        query = query.filter(models.Voice.owner_id == user_id)
    elif user_id is not None:
        query = query.filter(
            (models.Voice.owner_id.is_(None)) | (models.Voice.owner_id == user_id)
        )
    else:
        query = query.filter(models.Voice.owner_id.is_(None))
    if category:
        query = query.filter(models.Voice.category == category)
    if gender:
        query = query.filter(models.Voice.gender == gender)
    if recommended_only:
        query = query.filter(models.Voice.is_recommended.is_(True))
    return query.order_by(models.Voice.id.asc()).all()


def get_voice(
    db: Session,
    voice_id: int,
    user_id: int | None = None,
) -> models.Voice | None:
    query = (
        db.query(models.Voice)
        .options(selectinload(models.Voice.providers))
        .filter(
            models.Voice.id == voice_id,
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


def get_voice_by_key(db: Session, voice_key: str) -> models.Voice | None:
    return db.query(models.Voice).filter(models.Voice.voice_key == voice_key).first()


def create_voice(
    db: Session,
    payload: VoiceCreate,
    owner_id: int,
    source_voice_id: int | None = None,
) -> models.Voice:
    voice = models.Voice(
        voice_key=payload.voice_key,
        display_name=payload.display_name,
        gender=payload.gender,
        style=payload.style,
        category=payload.category,
        description=payload.description,
        is_recommended=payload.is_recommended,
        is_active=True,
        owner_id=owner_id,
        source_voice_id=source_voice_id,
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
    return get_voice(db, voice.id, user_id=owner_id)


def update_voice(
    db: Session,
    voice: models.Voice,
    payload: VoiceUpdate,
    user_id: int,
) -> models.Voice | None:
    if voice.owner_id != user_id:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voice, field, value)
    db.commit()
    db.refresh(voice)
    return get_voice(db, voice.id, user_id=user_id)


def hard_delete_voice(
    db: Session,
    voice: models.Voice,
    user_id: int,
) -> bool:
    if voice.owner_id != user_id:
        return False

    for provider in voice.providers:
        for preview in list(provider.preview_audios):
            Path(preview.audio_path).unlink(missing_ok=True)
            db.delete(preview)
        db.delete(provider)
    db.delete(voice)
    db.commit()
    return True


def clone_voice(
    db: Session,
    source_voice: models.Voice,
    owner_id: int,
) -> models.Voice:
    already = (
        db.query(models.Voice)
        .filter(
            models.Voice.source_voice_id == source_voice.id,
            models.Voice.owner_id == owner_id,
            models.Voice.is_active.is_(True),
        )
        .first()
    )
    if already:
        return already
    new_key = f"{source_voice.voice_key}_u{owner_id}"
    existing = get_voice_by_key(db, new_key)
    if existing:
        return existing
    voice = models.Voice(
        voice_key=new_key,
        display_name=source_voice.display_name,
        gender=source_voice.gender,
        style=source_voice.style,
        category=source_voice.category,
        description=source_voice.description,
        is_recommended=False,
        is_active=True,
        owner_id=owner_id,
        source_voice_id=source_voice.id,
    )
    for src_provider in source_voice.providers:
        voice.providers.append(
            models.VoiceProviderProfile(
                provider=src_provider.provider,
                provider_voice_id=f"{src_provider.provider_voice_id}_u{owner_id}",
                locale=src_provider.locale,
                supports_wav=src_provider.supports_wav,
                supports_mp3=src_provider.supports_mp3,
                is_default=src_provider.is_default,
                is_active=True,
            )
        )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    return get_voice(db, voice.id, user_id=owner_id)


def cascade_delete_public_voice(db: Session, voice: models.Voice) -> int:
    clones = (
        db.query(models.Voice)
        .filter(models.Voice.source_voice_id == voice.id)
        .all()
    )
    count = 0
    for clone in clones:
        clone.is_active = False
        for provider in clone.providers:
            provider.is_active = False
        count += 1
    voice.is_active = False
    for provider in voice.providers:
        provider.is_active = False
    db.commit()
    return count