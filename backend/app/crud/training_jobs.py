from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.schemas import VoiceTrainingJobCreate, VoiceTrainingJobUpdate


def list_jobs(db: Session, owner_id: int) -> list[models.VoiceTrainingJob]:
    return (
        db.query(models.VoiceTrainingJob)
        .filter(models.VoiceTrainingJob.owner_id == owner_id)
        .order_by(models.VoiceTrainingJob.id.desc())
        .all()
    )


def get_job(db: Session, job_id: int, owner_id: int) -> models.VoiceTrainingJob | None:
    return (
        db.query(models.VoiceTrainingJob)
        .filter(
            models.VoiceTrainingJob.id == job_id,
            models.VoiceTrainingJob.owner_id == owner_id,
        )
        .first()
    )


def create_job(
    db: Session,
    payload: VoiceTrainingJobCreate,
    owner_id: int,
) -> models.VoiceTrainingJob:
    job = models.VoiceTrainingJob(
        owner_id=owner_id,
        material_asset_id=payload.material_asset_id,
        result_model_artifact_id=payload.result_model_artifact_id,
        job_name=payload.job_name,
        provider=payload.provider,
        base_model=payload.base_model,
        status=payload.status,
        config_json=payload.config_json,
        error_message=payload.error_message,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(
    db: Session,
    job: models.VoiceTrainingJob,
    payload: VoiceTrainingJobUpdate,
) -> models.VoiceTrainingJob:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    if job.status == "running" and job.started_at is None:
        job.started_at = datetime.now(timezone.utc)
    if job.status in {"succeeded", "failed", "canceled"} and job.completed_at is None:
        job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job


def cancel_job(db: Session, job: models.VoiceTrainingJob) -> models.VoiceTrainingJob:
    job.status = "canceled"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
