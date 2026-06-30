"""Admin API endpoints: materials/voices/works management, reports review, health."""
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.crud import voices as voice_crud
from app.database import engine, get_db
from app.models import Material, MaterialReport, User, Voice, VoicePreviewAudio
from app.storage import MEDIA_DIR, delete_work, list_works

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/health")
def admin_health(_admin: User = Depends(get_current_admin)) -> dict:
    checks = {}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as exc:
        checks["database"] = {"status": "error", "detail": str(exc)}

    try:
        usage = shutil.disk_usage(MEDIA_DIR)
        checks["disk"] = {
            "status": "ok",
            "free_gb": round(usage.free / (1024**3), 1),
            "total_gb": round(usage.total / (1024**3), 1),
        }
    except Exception as exc:
        checks["disk"] = {"status": "error", "detail": str(exc)}

    try:
        import edge_tts

        checks["edge_tts"] = {"status": "ok", "note": "module available"}
    except ImportError:
        checks["edge_tts"] = {"status": "not_installed"}

    try:
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("BAILIAN_API_KEY")
        if api_key:
            try:
                import dashscope

                checks["bailian_tts"] = {"status": "configured"}
            except ImportError:
                checks["bailian_tts"] = {"status": "not_installed", "detail": "dashscope package missing"}
        else:
            checks["bailian_tts"] = {"status": "not_configured"}
    except Exception as exc:
        checks["bailian_tts"] = {"status": "error", "detail": str(exc)}

    all_ok = all(c.get("status") in ("ok", "configured") for c in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}


@router.get("/materials")
def list_all_materials(
    category: str | None = Query(default=None),
    uploader: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    query = db.query(Material)
    if not include_inactive:
        query = query.filter(Material.is_active.is_(True))
    if category:
        query = query.filter(Material.category == category)
    if uploader:
        query = query.filter(Material.uploader == uploader)
    total = query.count()
    items = query.order_by(Material.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "pageSize": page_size,
        "items": [
            {
                "id": m.id,
                "materialKey": m.material_key,
                "filename": m.filename,
                "title": m.title,
                "category": m.category,
                "format": m.format,
                "duration": m.duration_seconds,
                "fileSize": m.file_size_bytes,
                "uploader": m.uploader,
                "audioUrl": m.audio_url,
                "isActive": m.is_active,
                "createdAt": m.created_at.isoformat() if m.created_at else None,
            }
            for m in items
        ],
    }


def _hard_delete_material_record(db: Session, material: Material) -> None:
    Path(material.audio_path).unlink(missing_ok=True)
    db.delete(material)


@router.delete("/materials/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material not found")
    _hard_delete_material_record(db, material)
    db.commit()
    return {"detail": "material deleted"}


@router.delete("/materials/{material_id}/permanent")
def hard_delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="material not found")
    _hard_delete_material_record(db, material)
    db.commit()
    return {"detail": "material deleted"}


@router.get("/voices")
def list_all_voices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    total = db.query(Voice).count()
    voices = db.query(Voice).order_by(Voice.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for v in voices:
        providers = [
            {
                "id": p.id,
                "provider": p.provider,
                "providerVoiceId": p.provider_voice_id,
                "isActive": p.is_active,
            }
            for p in v.providers
        ]
        result.append(
            {
                "id": v.id,
                "voiceKey": v.voice_key,
                "displayName": v.display_name,
                "gender": v.gender,
                "style": v.style,
                "category": v.category,
                "description": v.description,
                "isRecommended": v.is_recommended,
                "isActive": v.is_active,
                "ownerId": v.owner_id,
                "providers": providers,
            }
        )
    return {"total": total, "page": page, "pageSize": page_size, "items": result}


@router.put("/voices/{voice_id}")
def update_voice(
    voice_id: int,
    display_name: str | None = Query(default=None, alias="displayName"),
    category: str | None = Query(default=None),
    description: str | None = Query(default=None),
    is_active: bool | None = Query(default=None, alias="isActive"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    if display_name is not None:
        voice.display_name = display_name
    if category is not None:
        voice.category = category
    if description is not None:
        voice.description = description
    if is_active is not None:
        voice.is_active = is_active
    db.commit()
    db.refresh(voice)
    return {"detail": "voice updated", "id": voice.id}


@router.delete("/voices/{voice_id}")
def delete_voice(
    voice_id: int,
    permanent: bool = Query(default=False, description="cascade delete all cloned copies"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="voice not found")
    if permanent and voice.owner_id is None:
        clones_deleted = voice_crud.cascade_delete_public_voice(db, voice)
        return {"detail": f"voice and {clones_deleted} cloned copies soft-deleted"}
    for provider in voice.providers:
        for preview in db.query(VoicePreviewAudio).filter(VoicePreviewAudio.voice_provider_profile_id == provider.id).all():
            Path(preview.audio_path).unlink(missing_ok=True)
            db.delete(preview)
        db.delete(provider)
    db.delete(voice)
    db.commit()
    return {"detail": "voice deleted"}


@router.get("/works")
def list_all_works(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    _admin: User = Depends(get_current_admin),
) -> dict:
    works = list_works()
    total = len(works)
    start = (page - 1) * page_size
    items = [w.model_dump() for w in works[start:start + page_size]]
    return {"total": total, "page": page, "pageSize": page_size, "items": items}


@router.delete("/works/{work_id}")
def remove_work_admin(
    work_id: str,
    _admin: User = Depends(get_current_admin),
) -> dict:
    if not delete_work(work_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="work not found")
    return {"detail": "work deleted"}


@router.get("/reports")
def list_reports(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    query = db.query(MaterialReport)
    if status_filter:
        query = query.filter(MaterialReport.status == status_filter)
    total = query.count()
    reports = query.order_by(MaterialReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in reports:
        material = db.query(Material).filter(Material.id == r.material_id).first()
        reporter = db.query(User).filter(User.id == r.reporter_id).first()
        result.append(
            {
                "id": r.id,
                "materialId": r.material_id,
                "materialTitle": material.title if material else "(deleted)",
                "materialIsActive": material.is_active if material else False,
                "reporterId": r.reporter_id,
                "reporterName": reporter.username if reporter else "(unknown)",
                "reasonCategory": r.reason_category,
                "reasonDetail": r.reason_detail,
                "status": r.status,
                "reviewNote": r.review_note,
                "createdAt": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return {"total": total, "page": page, "pageSize": page_size, "items": result}


@router.post("/reports/{report_id}/review")
def review_report(
    report_id: int,
    action: str = Query(description="'delete_material' or 'dismiss'"),
    note: str = Query(default=""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    if action not in ("delete_material", "dismiss"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action must be 'delete_material' or 'dismiss'",
        )

    report = db.query(MaterialReport).filter(MaterialReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="report not found")

    if action == "delete_material":
        material = db.query(Material).filter(Material.id == report.material_id).first()
        if material:
            _hard_delete_material_record(db, material)

    report.status = "reviewed" if action == "delete_material" else "dismissed"
    report.reviewed_by = admin.id
    report.review_note = note[:500] if note else None
    db.commit()
    return {"detail": f"report {report.status}"}