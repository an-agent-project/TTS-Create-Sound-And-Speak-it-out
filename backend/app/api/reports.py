from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Material, MaterialReport, User

router = APIRouter(tags=["reports"])

REPORT_CATEGORIES = ["pornography", "violence", "political", "copyright", "other"]


@router.post("/api/materials/{material_id}/report", status_code=status.HTTP_200_OK)
def report_material(
    material_id: int,
    reason_category: str = Form(default="other"),
    reason_detail: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if reason_category not in REPORT_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid reason category, must be one of: {', '.join(REPORT_CATEGORIES)}",
        )

    material = db.query(Material).filter(
        Material.id == material_id, Material.is_active.is_(True)
    ).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material not found")

    existing = (
        db.query(MaterialReport)
        .filter(
            MaterialReport.material_id == material_id,
            MaterialReport.reporter_id == current_user.id,
            MaterialReport.status == "pending",
        )
        .first()
    )
    if existing:
        return {"detail": "already reported"}

    report = MaterialReport(
        material_id=material_id,
        reporter_id=current_user.id,
        reason_category=reason_category,
        reason_detail=reason_detail[:500] if reason_detail else None,
        status="pending",
    )
    db.add(report)
    db.commit()
    return {"detail": "report submitted"}
