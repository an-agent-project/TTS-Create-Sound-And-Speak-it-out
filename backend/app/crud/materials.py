from sqlalchemy.orm import Session, selectinload

from app import models
from app.schemas import UserMaterialAssetCreate, UserMaterialAssetUpdate


def list_assets(db: Session, owner_id: int) -> list[models.UserMaterialAsset]:
    return (
        db.query(models.UserMaterialAsset)
        .options(selectinload(models.UserMaterialAsset.items))
        .filter(
            models.UserMaterialAsset.owner_id == owner_id,
            models.UserMaterialAsset.is_active.is_(True),
        )
        .order_by(models.UserMaterialAsset.id.desc())
        .all()
    )


def get_asset(db: Session, asset_id: int, owner_id: int) -> models.UserMaterialAsset | None:
    return (
        db.query(models.UserMaterialAsset)
        .options(selectinload(models.UserMaterialAsset.items))
        .filter(
            models.UserMaterialAsset.id == asset_id,
            models.UserMaterialAsset.owner_id == owner_id,
            models.UserMaterialAsset.is_active.is_(True),
        )
        .first()
    )


def create_asset(
    db: Session,
    payload: UserMaterialAssetCreate,
    owner_id: int,
) -> models.UserMaterialAsset:
    asset = models.UserMaterialAsset(
        owner_id=owner_id,
        name=payload.name,
        description=payload.description,
        asset_type=payload.asset_type,
        source_format=payload.source_format,
        original_filename=payload.original_filename,
        storage_path=payload.storage_path,
        status=payload.status,
        metadata_json=payload.metadata_json,
        is_active=True,
    )
    for item in payload.items:
        asset.items.append(
            models.UserMaterialItem(
                filename=item.filename,
                media_type=item.media_type,
                storage_path=item.storage_path,
                transcript=item.transcript,
                duration_seconds=item.duration_seconds,
                file_size_bytes=item.file_size_bytes,
                status=item.status,
            )
        )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return get_asset(db, asset.id, owner_id=owner_id)


def update_asset(
    db: Session,
    asset: models.UserMaterialAsset,
    payload: UserMaterialAssetUpdate,
) -> models.UserMaterialAsset:
    update_data = payload.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_data.items():
        setattr(asset, field, value)

    if payload.items is not None:
        asset.items.clear()
        for item in payload.items:
            asset.items.append(
                models.UserMaterialItem(
                    filename=item.filename,
                    media_type=item.media_type,
                    storage_path=item.storage_path,
                    transcript=item.transcript,
                    duration_seconds=item.duration_seconds,
                    file_size_bytes=item.file_size_bytes,
                    status=item.status,
                )
            )

    db.commit()
    db.refresh(asset)
    return get_asset(db, asset.id, owner_id=asset.owner_id)


def soft_delete_asset(db: Session, asset: models.UserMaterialAsset) -> None:
    asset.is_active = False
    asset.status = "deleted"
    db.commit()
