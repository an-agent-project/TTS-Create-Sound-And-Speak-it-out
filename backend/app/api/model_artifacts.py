from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.crud import model_artifacts as artifact_crud
from app.crud import training_jobs as job_crud
from app.database import get_db
from app.models import User
from app.schemas import VoiceModelArtifactCreate, VoiceModelArtifactRead, VoiceModelArtifactUpdate

router = APIRouter(prefix="/api/model-artifacts", tags=["model-artifacts"])


@router.get("", response_model=list[VoiceModelArtifactRead])
def list_model_artifacts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[VoiceModelArtifactRead]:
    return artifact_crud.list_artifacts(db, owner_id=current_user.id)


@router.get("/{artifact_id}", response_model=VoiceModelArtifactRead)
def get_model_artifact(
    artifact_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceModelArtifactRead:
    artifact = artifact_crud.get_artifact(db, artifact_id, owner_id=current_user.id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model artifact not found")
    return artifact


@router.post("", response_model=VoiceModelArtifactRead, status_code=status.HTTP_201_CREATED)
def create_model_artifact(
    payload: VoiceModelArtifactCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceModelArtifactRead:
    if payload.training_job_id and not job_crud.get_job(db, payload.training_job_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="training job not found")
    return artifact_crud.create_artifact(db, payload, owner_id=current_user.id)


@router.put("/{artifact_id}", response_model=VoiceModelArtifactRead)
def update_model_artifact(
    artifact_id: int,
    payload: VoiceModelArtifactUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceModelArtifactRead:
    artifact = artifact_crud.get_artifact(db, artifact_id, owner_id=current_user.id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model artifact not found")
    if payload.training_job_id and not job_crud.get_job(db, payload.training_job_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="training job not found")
    return artifact_crud.update_artifact(db, artifact, payload)


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_artifact(
    artifact_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Response:
    artifact = artifact_crud.get_artifact(db, artifact_id, owner_id=current_user.id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model artifact not found")
    artifact_crud.soft_delete_artifact(db, artifact)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
