from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_optional_user
from app.bailian_defaults import seed_bailian_default_voice
from app.crud import voices as voice_crud
from app.database import get_db
from app.models import User
from app.schemas import VoiceCreate, VoiceRead, VoiceUpdate

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("", response_model=list[VoiceRead])
def list_voices(
    category: str | None = None,
    gender: str | None = None,
    recommendedOnly: bool = False,
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
    db: Session = Depends(get_db),
) -> list[VoiceRead]:
    seed_bailian_default_voice(db)
    return voice_crud.list_voices(
        db,
        category=category,
        gender=gender,
        recommended_only=recommendedOnly,
        user_id=current_user.id if current_user else None,
    )


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
