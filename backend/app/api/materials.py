from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.material_defaults import seed_default_materials
from app.models import Material, User
from app.schemas import MaterialRead
from app.storage import MEDIA_DIR

router = APIRouter(prefix="/api/materials", tags=["materials"])

MATERIAL_DIR = MEDIA_DIR / "materials"
MATERIAL_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/ogg", "audio/wav", "audio/x-wav", "audio/flac", "audio/mp4"}


@router.get("", response_model=list[MaterialRead])
def list_materials(category: str | None = None, db: Session = Depends(get_db)) -> list[Material]:
    seed_default_materials(db)
    query = db.query(Material).filter(Material.is_active.is_(True))
    if category:
        query = query.filter(Material.category == category)
    return query.order_by(Material.id.asc()).all()


@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
async def upload_material(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Material:
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="unsupported audio file type")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio file cannot be empty")

    original = Path(file.filename or "audio.mp3")
    ext = original.suffix.lower() or ".mp3"
    material_key = f"upload-{uuid4().hex[:12]}"
    filename = f"{material_key}{ext}"
    output_path = MATERIAL_DIR / filename
    output_path.write_bytes(audio_bytes)

    material = Material(
        material_key=material_key,
        filename=original.name,
        title=original.stem,
        category="bgm",
        format=ext.lstrip("."),
        file_size_bytes=len(audio_bytes),
        uploader=current_user.username,
        audio_path=str(output_path),
        audio_url=f"/media/materials/{filename}",
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material
