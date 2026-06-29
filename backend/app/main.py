from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.materials import router as materials_router
from app.api.tts import router as tts_router
from app.api.voices import router as voices_router
from app.api.admin import router as admin_router
from app.api.reports import router as reports_router
from app.api.voice_clones import router as voice_clones_router
from app.crud import tts_preview as tts_preview_crud
from app.data import SCENE_BY_ID, SCENES, VOICE_BY_ID
from app.auth import get_current_user
from app.database import engine, get_db
from app.models import Base, User
from app.models import Material
from sqlalchemy.orm import Session
from app.services.text_processing import preprocess_text
from app.services.translator import LANG_VOICE_MAP, translate_text
from app.services.tts import mix_bgm_to_file, synthesize_segments_to_file
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
app.include_router(materials_router)
app.include_router(tts_router)
app.include_router(voices_router)
app.include_router(voice_clones_router)
app.include_router(admin_router)
app.include_router(reports_router)


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
async def generate_tts(payload: GenerateRequest, request: Request, db: Session = Depends(get_db)) -> Work:
    output_lang = payload.outputLang or "zh"

    voice_id_for_tts = payload.voiceId if output_lang == "zh" else LANG_VOICE_MAP.get(output_lang, payload.voiceId)
    provider_profile = tts_preview_crud.get_provider_profile_by_voice_id(db, voice_id_for_tts)
    voice = VOICE_BY_ID.get(voice_id_for_tts)
    provider = provider_profile.provider if provider_profile else "edge_tts"
    voice_name = provider_profile.voice.display_name if provider_profile else (voice["name"] if voice else voice_id_for_tts)
    if provider_profile is None and voice is None and output_lang == "zh":
        raise HTTPException(status_code=400, detail="unsupported voice id")

    scene = SCENE_BY_ID.get(payload.sceneId or "")
    content_to_speak = payload.content
    if output_lang != "zh":
        try:
            content_to_speak = translate_text(payload.content, output_lang)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Translation failed: {exc}") from exc
    processed = preprocess_text(content_to_speak)
    if not processed.cleanedText:
        raise HTTPException(status_code=400, detail="text content cannot be empty")
    if processed.sensitiveWords:
        words = ", ".join(sorted({hit.word for hit in processed.sensitiveWords}))
        raise HTTPException(status_code=400, detail=f"text contains sensitive words: {words}")

    work_id = uuid4().hex
    output_path = MEDIA_DIR / f"{work_id}.mp3"
    dry_output_path = MEDIA_DIR / f"{work_id}-voice.mp3"
    try:
        await synthesize_segments_to_file(
            segments=processed.segments,
            voice=voice_id_for_tts,
            speed=payload.speed,
            pitch=payload.pitch,
            emotion=payload.emotion,
            output_path=dry_output_path,
            provider=provider,
        )
        bgm_path = _find_bgm_path(db, payload.bgmType)
        duration = round(await mix_bgm_to_file(dry_output_path, bgm_path, output_path, payload.bgmVolume))
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        if dry_output_path.exists():
            dry_output_path.unlink()
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc
    finally:
        dry_output_path.unlink(missing_ok=True)

    scene_name = scene["name"] if scene else "通用"
    work = Work(
        id=work_id,
        title=payload.title or _build_title(scene_name, processed.cleanedText),
        content=processed.cleanedText,
        sceneId=payload.sceneId or "",
        sceneName=scene_name,
        voiceId=voice_id_for_tts,
        voiceName=voice_name or voice_id_for_tts,
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
def get_works(current_user: User = Depends(get_current_user)) -> list[Work]:
    return list_works()


@app.get("/api/works/{work_id}", response_model=Work)
def get_work_detail(work_id: str, current_user: User = Depends(get_current_user)) -> Work:
    work = get_work(work_id)
    if work is None:
        raise HTTPException(status_code=404, detail="work not found")
    return work


@app.delete("/api/works/{work_id}")
def remove_work(work_id: str, current_user: User = Depends(get_current_user)) -> dict[str, bool]:
    if not delete_work(work_id):
        raise HTTPException(status_code=404, detail="work not found")
    return {"ok": True}


def _build_title(scene_name: str, text: str) -> str:
    excerpt = text[:20].strip()
    suffix = "..." if len(text) > 20 else ""
    return f"《{scene_name}》{excerpt}{suffix}"


def _find_bgm_path(db: Session, bgm_type: str) -> Path | None:
    if not bgm_type or bgm_type == "none":
        return None
    material = db.query(Material).filter(Material.material_key == bgm_type, Material.is_active.is_(True)).first()
    if not material:
        return None
    path = Path(material.audio_path)
    return path if path.exists() else None
