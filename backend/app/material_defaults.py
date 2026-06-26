from pathlib import Path

from sqlalchemy.orm import Session

from app import models
from app.storage import MEDIA_DIR


MATERIALS = [
    {
        "material_key": "soft-corporate",
        "filename": "soft-corporate.ogg",
        "title": "Soft Corporate",
        "duration_seconds": 170,
        "uploader": "MusicLFiles",
        "license": "CC BY 4.0",
        "source_url": "https://commons.wikimedia.org/wiki/File:Soft_Corporate_by_MusicLFiles.ogg",
    },
    {
        "material_key": "liftoff",
        "filename": "liftoff.ogg",
        "title": "Liftoff",
        "duration_seconds": 117,
        "uploader": "Florian CUNY",
        "license": "CC BY 4.0",
        "source_url": "https://commons.wikimedia.org/wiki/File:Background_music_-_Liftoff.ogg",
    },
    {
        "material_key": "samedi-deconfine",
        "filename": "samedi-deconfine.ogg",
        "title": "Samedi déconfiné",
        "duration_seconds": 70,
        "uploader": "Florian CUNY",
        "license": "CC BY 4.0",
        "source_url": "https://commons.wikimedia.org/wiki/File:Background_music_-_Samedi_d%C3%A9confin%C3%A9.ogg",
    },
]


def seed_default_materials(db: Session) -> None:
    for item in MATERIALS:
        path = MEDIA_DIR / "materials" / item["filename"]
        if not path.exists():
            continue

        material = db.query(models.Material).filter(models.Material.material_key == item["material_key"]).first()
        if material is None:
            material = models.Material(material_key=item["material_key"])
            db.add(material)

        material.filename = item["filename"]
        material.title = item["title"]
        material.category = "bgm"
        material.format = Path(item["filename"]).suffix.lstrip(".")
        material.duration_seconds = item["duration_seconds"]
        material.file_size_bytes = path.stat().st_size
        material.uploader = item["uploader"]
        material.audio_path = str(path)
        material.audio_url = f"/media/materials/{item['filename']}"
        material.license = item["license"]
        material.source_url = item["source_url"]
        material.is_active = True
    db.commit()
