from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_optional_user
from app.bailian_defaults import seed_bailian_default_voice
from app.crud import voices as voice_crud
from app.database import get_db
from app.models import User, Voice, VoicePublishRequest
from app.schemas import VoiceCreate, VoiceRead, VoiceUpdate

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("", response_model=list[VoiceRead])
def list_voices(
    category: str | None = None,
    gender: str | None = None,
    recommendedOnly: bool = False,
    scope: str | None = Query(default=None, description="'public' | 'personal'"),
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
    db: Session = Depends(get_db),
) -> list[VoiceRead]:
    seed_bailian_default_voice(db)
    voices = voice_crud.list_voices(
        db,
        category=category,
        gender=gender,
        recommended_only=recommendedOnly,
        user_id=current_user.id if current_user else None,
        scope=scope,
    )
    if current_user and voices:
        voice_ids = [voice.id for voice in voices if voice.owner_id == current_user.id]
        if voice_ids:
            requests = (
                db.query(VoicePublishRequest)
                .filter(
                    VoicePublishRequest.source_voice_id.in_(voice_ids),
                    VoicePublishRequest.requester_id == current_user.id,
                    VoicePublishRequest.status.in_(["pending", "approved"]),
                )
                .order_by(VoicePublishRequest.created_at.desc())
                .all()
            )
            status_by_voice_id = {}
            for item in requests:
                status_by_voice_id.setdefault(item.source_voice_id, item.status)
            for voice in voices:
                voice.publish_status = status_by_voice_id.get(voice.id)
    return voices


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



@router.post("/{voice_id}/publish-requests", status_code=status.HTTP_201_CREATED)
def create_voice_publish_request(
    voice_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    request_note: str | None = Query(default=None, alias="note"),
    db: Session = Depends(get_db),
) -> dict:
    voice = (
        db.query(Voice)
        .filter(
            Voice.id == voice_id,
            Voice.owner_id == current_user.id,
            Voice.is_active.is_(True),
        )
        .first()
    )
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="personal voice not found")

    existing = (
        db.query(VoicePublishRequest)
        .filter(
            VoicePublishRequest.source_voice_id == voice.id,
            VoicePublishRequest.requester_id == current_user.id,
            VoicePublishRequest.status == "pending",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="publish request already pending")

    publish_request = VoicePublishRequest(
        source_voice_id=voice.id,
        requester_id=current_user.id,
        status="pending",
        request_note=request_note[:500] if request_note else None,
    )
    db.add(publish_request)
    db.commit()
    db.refresh(publish_request)
    return {
        "id": publish_request.id,
        "status": publish_request.status,
        "sourceVoiceId": publish_request.source_voice_id,
        "createdAt": publish_request.created_at.isoformat() if publish_request.created_at else None,
    }
@router.post("/{voice_id}/clone", response_model=VoiceRead)
def clone_voice_to_personal(
    voice_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceRead:
    source = db.query(Voice).filter(Voice.id == voice_id, Voice.owner_id.is_(None), Voice.is_active.is_(True)).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="public voice not found")
    return voice_crud.clone_voice(db, source, owner_id=current_user.id)


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
    ok = voice_crud.hard_delete_voice(db, voice, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot delete a system voice")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
