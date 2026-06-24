from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from huggingface_hub import snapshot_download

# Downloads Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice when no local snapshot exists.
from app.database import SessionLocal
from app.qwen_defaults import (
    QWEN_06B_CACHE_MODEL_DIR,
    QWEN_06B_MODEL_ID,
    QWEN_VIVIAN_VOICE_KEY,
    seed_system_qwen_vivian,
)


def find_existing_snapshot() -> Path | None:
    snapshots_dir = QWEN_06B_CACHE_MODEL_DIR / "snapshots"
    if not snapshots_dir.exists():
        return None
    snapshots = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
    return snapshots[-1] if snapshots else None


def ensure_qwen_model() -> Path:
    existing = find_existing_snapshot()
    if existing:
        return existing

    downloaded = snapshot_download(
        repo_id=QWEN_06B_MODEL_ID,
        cache_dir=str(ROOT_DIR / ".hf-cache" / "qwen-tts"),
        local_dir_use_symlinks=False,
    )
    return Path(downloaded)


def main() -> None:
    snapshot_path = ensure_qwen_model()
    db = SessionLocal()
    try:
        seed_system_qwen_vivian(db, artifact_path=str(snapshot_path))
    finally:
        db.close()
    print(f"Qwen model ready: {snapshot_path}")
    print(f"System voice ready: {QWEN_VIVIAN_VOICE_KEY}")


if __name__ == "__main__":
    main()
