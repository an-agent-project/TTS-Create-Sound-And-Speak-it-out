from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.tts import router as tts_router
from app.api.voices import router as voices_router
from app.data import SCENE_BY_ID, SCENES, VOICE_BY_ID
from app.database import engine
from app.models import Base
from app.services.text_processing import preprocess_text
from app.services.tts import synthesize_segments_to_file
from app.storage import MEDIA_DIR, delete_work, ensure_storage, get_work, list_works, save_work
from app.work_schemas import GenerateRequest, PreprocessRequest, Work


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
PREVIEW_DIR = STATIC_DIR / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
ensure_storage()

# Create SQL tables on startup for the auth and voice-library APIs.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TTS Podcast API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.include_router(auth_router)
app.include_router(tts_router)
app.include_router(voices_router)


@app.get("/health")
@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "audiobook-generator-backend"}


@app.get("/api/scenes")
def get_scenes() -> list[dict]:
    return SCENES


@app.post("/api/text/preprocess")
def preprocess(payload: PreprocessRequest):
    return preprocess_text(payload.content, payload.maxSegmentLength)


@app.post("/api/tts/generate", response_model=Work)
async def generate_tts(payload: GenerateRequest, request: Request) -> Work:
    voice = VOICE_BY_ID.get(payload.voiceId)
    if voice is None:
        raise HTTPException(status_code=400, detail="unsupported voice id")

    scene = SCENE_BY_ID.get(payload.sceneId or "")
    processed = preprocess_text(payload.content)
    if not processed.cleanedText:
        raise HTTPException(status_code=400, detail="text content cannot be empty")
    if processed.sensitiveWords:
        words = ", ".join(sorted({hit.word for hit in processed.sensitiveWords}))
        raise HTTPException(status_code=400, detail=f"text contains sensitive words: {words}")

    work_id = uuid4().hex
    output_path = MEDIA_DIR / f"{work_id}.mp3"
    try:
        duration = await synthesize_segments_to_file(
            segments=processed.segments,
            voice=payload.voiceId,
            speed=payload.speed,
            pitch=payload.pitch,
            emotion=payload.emotion,
            output_path=output_path,
        )
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc

    scene_name = scene["name"] if scene else "通用"
    work = Work(
        id=work_id,
        title=payload.title or _build_title(scene_name, processed.cleanedText),
        content=processed.cleanedText,
        sceneId=payload.sceneId or "",
        sceneName=scene_name,
        voiceId=payload.voiceId,
        voiceName=voice["name"],
        speed=payload.speed,
        pitch=payload.pitch,
        emotion=payload.emotion,
        bgmType=payload.bgmType,
        bgmVolume=payload.bgmVolume,
        duration=duration,
        audioUrl=f"{str(request.base_url).rstrip('/')}/media/{output_path.name}",
        createdAt=datetime.now(timezone.utc).isoformat(),
        segmentCount=len(processed.segments),
    )
    return save_work(work)


@app.get("/api/works", response_model=list[Work])
def get_works() -> list[Work]:
    return list_works()


@app.get("/api/works/{work_id}", response_model=Work)
def get_work_detail(work_id: str) -> Work:
    work = get_work(work_id)
    if work is None:
        raise HTTPException(status_code=404, detail="work not found")
    return work


@app.delete("/api/works/{work_id}")
def remove_work(work_id: str) -> dict[str, bool]:
    if not delete_work(work_id):
        raise HTTPException(status_code=404, detail="work not found")
    return {"ok": True}


def _build_title(scene_name: str, text: str) -> str:
    excerpt = text[:20].strip()
    suffix = "..." if len(text) > 20 else ""
    return f"《{scene_name}》{excerpt}{suffix}"
