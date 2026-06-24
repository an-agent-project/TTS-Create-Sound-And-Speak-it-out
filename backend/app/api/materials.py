from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.crud import materials as material_crud
from app.database import get_db
from app.models import User
from app.schemas import UserMaterialAssetCreate, UserMaterialAssetRead, UserMaterialAssetUpdate

router = APIRouter(prefix="/api/material-assets", tags=["material-assets"])


@router.get("", response_model=list[UserMaterialAssetRead])
def list_material_assets(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[UserMaterialAssetRead]:
    return material_crud.list_assets(db, owner_id=current_user.id)


@router.get("/{asset_id}", response_model=UserMaterialAssetRead)
def get_material_asset(
    asset_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserMaterialAssetRead:
    asset = material_crud.get_asset(db, asset_id, owner_id=current_user.id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material asset not found")
    return asset


@router.post("", response_model=UserMaterialAssetRead, status_code=status.HTTP_201_CREATED)
def create_material_asset(
    payload: UserMaterialAssetCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserMaterialAssetRead:
    return material_crud.create_asset(db, payload, owner_id=current_user.id)


@router.put("/{asset_id}", response_model=UserMaterialAssetRead)
def update_material_asset(
    asset_id: int,
    payload: UserMaterialAssetUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserMaterialAssetRead:
    asset = material_crud.get_asset(db, asset_id, owner_id=current_user.id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material asset not found")
    return material_crud.update_asset(db, asset, payload)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_asset(
    asset_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Response:
    asset = material_crud.get_asset(db, asset_id, owner_id=current_user.id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material asset not found")
    material_crud.soft_delete_asset(db, asset)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
