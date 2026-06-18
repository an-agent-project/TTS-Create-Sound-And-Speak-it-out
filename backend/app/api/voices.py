from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import voices as voice_crud
from app.database import get_db
from app.schemas import VoiceCreate, VoiceRead, VoiceUpdate


router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("", response_model=list[VoiceRead])
def list_voices(
    category: str | None = None,
    gender: str | None = None,
    recommendedOnly: bool = False,
    db: Session = Depends(get_db),
) -> list[VoiceRead]:
    return voice_crud.list_voices(
        db,
        category=category,
        gender=gender,
        recommended_only=recommendedOnly,
    )


@router.get("/{voice_id}", response_model=VoiceRead)
def get_voice(voice_id: int, db: Session = Depends(get_db)) -> VoiceRead:
    voice = voice_crud.get_voice(db, voice_id)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    return voice


@router.post("", response_model=VoiceRead, status_code=status.HTTP_201_CREATED)
def create_voice(payload: VoiceCreate, db: Session = Depends(get_db)) -> VoiceRead:
    if voice_crud.get_voice_by_key(db, payload.voice_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="voiceKey already exists")
    try:
        return voice_crud.create_voice(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="voice provider already exists") from exc


@router.put("/{voice_id}", response_model=VoiceRead)
def update_voice(voice_id: int, payload: VoiceUpdate, db: Session = Depends(get_db)) -> VoiceRead:
    voice = voice_crud.get_voice(db, voice_id)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    return voice_crud.update_voice(db, voice, payload)


@router.delete("/{voice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voice(voice_id: int, db: Session = Depends(get_db)) -> Response:
    voice = voice_crud.get_voice(db, voice_id)
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    voice_crud.soft_delete_voice(db, voice)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
