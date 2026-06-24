from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.crud import materials as material_crud
from app.crud import model_artifacts as artifact_crud
from app.crud import training_jobs as job_crud
from app.database import get_db
from app.models import User
from app.schemas import VoiceTrainingJobCreate, VoiceTrainingJobRead, VoiceTrainingJobUpdate

router = APIRouter(prefix="/api/training-jobs", tags=["training-jobs"])


@router.get("", response_model=list[VoiceTrainingJobRead])
def list_training_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[VoiceTrainingJobRead]:
    return job_crud.list_jobs(db, owner_id=current_user.id)


@router.get("/{job_id}", response_model=VoiceTrainingJobRead)
def get_training_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceTrainingJobRead:
    job = job_crud.get_job(db, job_id, owner_id=current_user.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="training job not found")
    return job


@router.post("", response_model=VoiceTrainingJobRead, status_code=status.HTTP_201_CREATED)
def create_training_job(
    payload: VoiceTrainingJobCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceTrainingJobRead:
    if payload.material_asset_id and not material_crud.get_asset(
        db,
        payload.material_asset_id,
        owner_id=current_user.id,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="material asset not found")
    if payload.result_model_artifact_id and not artifact_crud.get_artifact(
        db,
        payload.result_model_artifact_id,
        owner_id=current_user.id,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="model artifact not found")
    return job_crud.create_job(db, payload, owner_id=current_user.id)


@router.put("/{job_id}", response_model=VoiceTrainingJobRead)
def update_training_job(
    job_id: int,
    payload: VoiceTrainingJobUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceTrainingJobRead:
    job = job_crud.get_job(db, job_id, owner_id=current_user.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="training job not found")
    if payload.material_asset_id and not material_crud.get_asset(
        db,
        payload.material_asset_id,
        owner_id=current_user.id,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="material asset not found")
    if payload.result_model_artifact_id and not artifact_crud.get_artifact(
        db,
        payload.result_model_artifact_id,
        owner_id=current_user.id,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="model artifact not found")
    return job_crud.update_job(db, job, payload)


@router.post("/{job_id}/cancel", response_model=VoiceTrainingJobRead)
def cancel_training_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> VoiceTrainingJobRead:
    job = job_crud.get_job(db, job_id, owner_id=current_user.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="training job not found")
    return job_crud.cancel_job(db, job)
