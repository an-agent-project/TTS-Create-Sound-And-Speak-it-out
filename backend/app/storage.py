import json
from pathlib import Path

from app.work_schemas import Work

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = BASE_DIR / "media"
WORKS_FILE = DATA_DIR / "works.json"


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    if not WORKS_FILE.exists():
        WORKS_FILE.write_text("[]\n", encoding="utf-8")


def list_works(owner_id: int | None = None) -> list[Work]:
    ensure_storage()
    raw = json.loads(WORKS_FILE.read_text(encoding="utf-8"))
    works = []
    visible_works = []
    stale_ids = []
    for item in raw:
        work = Work(**item)
        media_path = MEDIA_DIR / f"{work.id}.mp3"
        if media_path.exists():
            works.append(work)
            if owner_id is None or work.ownerId == owner_id:
                visible_works.append(work)
        else:
            stale_ids.append(work.id)
    if stale_ids:
        _write_works(works)
    return visible_works


def save_work(work: Work) -> Work:
    works = list_works()
    works.insert(0, work)
    _write_works(works)
    return work


def get_work(work_id: str, owner_id: int | None = None) -> Work | None:
    for work in list_works(owner_id):
        if work.id == work_id:
            media_path = MEDIA_DIR / f"{work.id}.mp3"
            if not media_path.exists():
                return None
            return work
    return None


def delete_work(work_id: str, owner_id: int | None = None) -> bool:
    works = list_works()
    work = next((item for item in works if item.id == work_id and (owner_id is None or item.ownerId == owner_id)), None)
    if work is None:
        return False

    _write_works([item for item in works if item.id != work_id])
    media_path = MEDIA_DIR / f"{work_id}.mp3"
    if media_path.exists():
        media_path.unlink()
    return True


def _write_works(works: list[Work]) -> None:
    WORKS_FILE.write_text(
        json.dumps([work.model_dump() for work in works], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
