from sqlalchemy.orm import Session

from app import models
from app.schemas import VoiceModelArtifactCreate, VoiceModelArtifactUpdate


def list_artifacts(db: Session, owner_id: int) -> list[models.VoiceModelArtifact]:
    return (
        db.query(models.VoiceModelArtifact)
        .filter(
            models.VoiceModelArtifact.owner_id == owner_id,
            models.VoiceModelArtifact.is_active.is_(True),
        )
        .order_by(models.VoiceModelArtifact.id.desc())
        .all()
    )


def get_artifact(db: Session, artifact_id: int, owner_id: int) -> models.VoiceModelArtifact | None:
    return (
        db.query(models.VoiceModelArtifact)
        .filter(
            models.VoiceModelArtifact.id == artifact_id,
            models.VoiceModelArtifact.owner_id == owner_id,
            models.VoiceModelArtifact.is_active.is_(True),
        )
        .first()
    )


def create_artifact(
    db: Session,
    payload: VoiceModelArtifactCreate,
    owner_id: int,
) -> models.VoiceModelArtifact:
    artifact = models.VoiceModelArtifact(
        owner_id=owner_id,
        training_job_id=payload.training_job_id,
        display_name=payload.display_name,
        provider=payload.provider,
        model_version=payload.model_version,
        artifact_path=payload.artifact_path,
        config_path=payload.config_path,
        tokenizer_path=payload.tokenizer_path,
        runtime_config_json=payload.runtime_config_json,
        status=payload.status,
        file_size_bytes=payload.file_size_bytes,
        is_active=True,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def update_artifact(
    db: Session,
    artifact: models.VoiceModelArtifact,
    payload: VoiceModelArtifactUpdate,
) -> models.VoiceModelArtifact:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(artifact, field, value)
    db.commit()
    db.refresh(artifact)
    return artifact


def soft_delete_artifact(db: Session, artifact: models.VoiceModelArtifact) -> None:
    artifact.is_active = False
    artifact.status = "deleted"
    db.commit()
