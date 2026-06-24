from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user, get_optional_user
from app.crud import model_artifacts as artifact_crud
from app.crud import voices as voice_crud
from app.database import get_db
from app.models import User
from app.qwen_defaults import QWEN_06B_MODEL_ID, QWEN_06B_RUNTIME_CONFIG, resolve_qwen_06b_artifact_path, seed_system_qwen_vivian
from app.schemas import VoiceCreate, VoiceModelArtifactCreate, VoiceRead, VoiceUpdate

router = APIRouter(prefix="/api/voices", tags=["voices"])

def _validate_provider_artifacts(payload: VoiceCreate | VoiceUpdate, db: Session, user_id: int) -> None:
    providers = payload.providers or []
    for provider in providers:
        if provider.model_artifact_id and not artifact_crud.get_artifact(
            db,
            provider.model_artifact_id,
            owner_id=user_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="model artifact not found",
            )


@router.get("", response_model=list[VoiceRead])
def list_voices(
    category: str | None = None,
    gender: str | None = None,
    recommendedOnly: bool = False,
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
    db: Session = Depends(get_db),
) -> list[VoiceRead]:
    seed_system_qwen_vivian(db)
    return voice_crud.list_voices(
        db,
        category=category,
        gender=gender,
        recommended_only=recommendedOnly,
        user_id=current_user.id if current_user else None,
    )


@router.post("/qwen-presets/0-6b-customvoice/import", response_model=VoiceRead, status_code=status.HTTP_201_CREATED)
def import_qwen_06b_custom_voice(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceRead:
    voice_key = f"qwen-0-6b-vivian-u{current_user.id}"
    provider_voice_id = f"qwen3:{voice_key}"
    artifact_path = resolve_qwen_06b_artifact_path()

    existing_voice = voice_crud.get_voice_by_key(db, voice_key)
    artifact = (
        db.query(models.VoiceModelArtifact)
        .filter(
            models.VoiceModelArtifact.owner_id == current_user.id,
            models.VoiceModelArtifact.provider == "qwen3_tts",
            models.VoiceModelArtifact.artifact_path.in_([artifact_path, QWEN_06B_MODEL_ID]),
            models.VoiceModelArtifact.is_active.is_(True),
        )
        .first()
    )
    if artifact is None:
        artifact = artifact_crud.create_artifact(
            db,
            VoiceModelArtifactCreate(
                displayName="Qwen 0.6B CustomVoice",
                provider="qwen3_tts",
                modelVersion="qwen3-tts-0.6b-customvoice",
                artifactPath=artifact_path,
                runtimeConfigJson=QWEN_06B_RUNTIME_CONFIG,
                status="ready",
            ),
            owner_id=current_user.id,
        )
    else:
        artifact.artifact_path = artifact_path
        artifact.runtime_config_json = QWEN_06B_RUNTIME_CONFIG
        artifact.status = "ready"

    if existing_voice and existing_voice.owner_id == current_user.id:
        existing_voice.is_active = True
        existing_voice.display_name = "Qwen Vivian"
        existing_voice.gender = "female"
        existing_voice.style = "custom"
        existing_voice.category = "personal"
        existing_voice.description = "Qwen3-TTS 0.6B CustomVoice preset voice"
        if not any(provider.provider_voice_id == provider_voice_id for provider in existing_voice.providers):
            existing_voice.providers.append(
                models.VoiceProviderProfile(
                    provider="qwen3_tts",
                    provider_voice_id=provider_voice_id,
                    provider_kind="local_model",
                    model_artifact_id=artifact.id,
                    runtime_config_json=QWEN_06B_RUNTIME_CONFIG,
                    supports_wav=True,
                    supports_mp3=True,
                    is_default=True,
                    is_active=True,
                )
            )
        for provider in existing_voice.providers:
            if provider.provider_voice_id == provider_voice_id:
                provider.is_active = True
                provider.is_default = True
                provider.model_artifact_id = artifact.id
                provider.runtime_config_json = QWEN_06B_RUNTIME_CONFIG
        db.commit()
        voice = voice_crud.get_voice(db, existing_voice.id, user_id=current_user.id)
        if voice:
            return voice

    try:
        return voice_crud.create_voice(
            db,
            VoiceCreate(
                voiceKey=voice_key,
                displayName="Qwen Vivian",
                gender="female",
                style="custom",
                category="personal",
                description="Qwen3-TTS 0.6B CustomVoice preset voice",
                providers=[
                    {
                        "provider": "qwen3_tts",
                        "providerVoiceId": provider_voice_id,
                        "providerKind": "local_model",
                        "modelArtifactId": artifact.id,
                        "runtimeConfigJson": QWEN_06B_RUNTIME_CONFIG,
                        "supportsWav": True,
                        "supportsMp3": True,
                        "isDefault": True,
                    }
                ],
            ),
            owner_id=current_user.id,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="qwen preset voice already exists") from exc


@router.get("/{voice_id}", response_model=VoiceRead)
def get_voice(
    voice_id: int,
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
    db: Session = Depends(get_db),
) -> VoiceRead:
    voice = voice_crud.get_voice(db, voice_id, user_id=current_user.id if current_user else None)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    return voice


@router.post("", response_model=VoiceRead, status_code=status.HTTP_201_CREATED)
def create_voice(
    payload: VoiceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceRead:
    if voice_crud.get_voice_by_key(db, payload.voice_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="voiceKey already exists")
    _validate_provider_artifacts(payload, db, current_user.id)
    try:
        return voice_crud.create_voice(db, payload, owner_id=current_user.id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="voice provider already exists") from exc


@router.put("/{voice_id}", response_model=VoiceRead)
def update_voice(
    voice_id: int,
    payload: VoiceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceRead:
    voice = voice_crud.get_voice(db, voice_id, user_id=current_user.id)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    _validate_provider_artifacts(payload, db, current_user.id)
    result = voice_crud.update_voice(db, voice, payload, user_id=current_user.id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot edit a system voice")
    return result


@router.delete("/{voice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voice(
    voice_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Response:
    voice = voice_crud.get_voice(db, voice_id, user_id=current_user.id)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    ok = voice_crud.soft_delete_voice(db, voice, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot delete a system voice")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
