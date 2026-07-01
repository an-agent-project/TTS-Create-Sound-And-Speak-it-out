from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.materials import router as materials_router
from app.api.tts import router as tts_router
from app.api.voices import router as voices_router
from app.api.admin import router as admin_router
from app.api.reports import router as reports_router
from app.api.voice_clones import router as voice_clones_router
from app.api.jobs import router as jobs_router
from app.crud import tts_preview as tts_preview_crud
from app.data import SCENE_BY_ID, SCENES, VOICE_BY_ID
from app.auth import get_current_user, get_optional_user
from app.database import SessionLocal, engine, ensure_legacy_schema, get_db
from app.job_queue import create_job, update_job
from app.models import Base, User
from app.schema_migrations import ensure_runtime_schema
from app.models import Material
from sqlalchemy.orm import Session
from app.services.text_processing import preprocess_text
from app.services.bailian_tts import BAILIAN_TTS_PROVIDER
from app.services.translator import LANGUAGES, LANG_VOICE_MAP, translate_text
from app.services.tts import mix_bgm_to_file, synthesize_segments_to_file
from app.storage import MEDIA_DIR, delete_work, ensure_storage, get_work, list_works, save_work
from app.work_schemas import GenerateRequest, PreprocessRequest, TranslateRequest, TranslateResponse, Work


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
PREVIEW_DIR = STATIC_DIR / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
ensure_storage()

# Create SQL tables on startup for the auth and voice-library APIs.
Base.metadata.create_all(bind=engine)
ensure_legacy_schema()
ensure_runtime_schema(engine)

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
app.include_router(jobs_router)
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


@app.post("/api/text/translate", response_model=TranslateResponse)
def translate_preview(payload: TranslateRequest) -> TranslateResponse:
    target_lang = payload.targetLang or "zh"
    if target_lang not in LANGUAGES:
        raise HTTPException(status_code=400, detail="unsupported target language")
    try:
        translated_text = translate_text(payload.content, target_lang)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Translation failed: {exc}") from exc
    return TranslateResponse(
        sourceText=payload.content,
        targetLang=target_lang,
        translatedText=translated_text,
    )


@app.post("/api/tts/generate", response_model=Work)
async def generate_tts(
    payload: GenerateRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> Work:
    return await _generate_tts_work(
        payload=payload,
        base_url=str(request.base_url),
        current_user=current_user,
        db=db,
    )


@app.post("/api/tts/generate-jobs")
async def create_generate_tts_job(
    payload: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User | None = Depends(get_optional_user),
) -> dict[str, str]:
    job = await create_job("tts_generate", owner_id=current_user.id if current_user else None, message="配音任务已创建")
    background_tasks.add_task(
        _run_generate_tts_job,
        job.id,
        payload,
        str(request.base_url),
        current_user.id if current_user else None,
    )
    return {"jobId": job.id}


async def _run_generate_tts_job(
    job_id: str,
    payload: GenerateRequest,
    base_url: str,
    user_id: int | None,
) -> None:
    db = SessionLocal()
    try:
        current_user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first() if user_id else None

        async def report(progress: int, message: str) -> None:
            await update_job(job_id, status="running", progress=progress, message=message)

        await report(3, "正在准备配音任务")
        work = await _generate_tts_work(
            payload=payload,
            base_url=base_url,
            current_user=current_user,
            db=db,
            progress=report,
        )
        await update_job(
            job_id,
            status="completed",
            progress=100,
            message="配音生成完成",
            result={"work": work.model_dump()},
        )
    except Exception as exc:
        await update_job(
            job_id,
            status="failed",
            progress=100,
            message="配音生成失败",
            error=str(exc),
        )
    finally:
        db.close()


async def _generate_tts_work(
    payload: GenerateRequest,
    base_url: str,
    current_user: User | None,
    db: Session,
    progress=None,
) -> Work:
    async def report(value: int, message: str) -> None:
        if progress:
            await progress(value, message)

    output_lang = payload.outputLang or "zh"
    await report(8, "正在校验音色")

    selected_voice_id = payload.voiceId
    provider_profile = tts_preview_crud.get_provider_profile_by_voice_id(
        db,
        selected_voice_id,
        user_id=current_user.id if current_user else None,
    )
    voice = VOICE_BY_ID.get(selected_voice_id)
    provider = provider_profile.provider if provider_profile else "edge_tts"

    if output_lang != "zh" and provider != BAILIAN_TTS_PROVIDER:
        selected_voice_id = LANG_VOICE_MAP.get(output_lang, selected_voice_id)
        provider_profile = tts_preview_crud.get_provider_profile_by_voice_id(
            db,
            selected_voice_id,
            user_id=current_user.id if current_user else None,
        )
        voice = VOICE_BY_ID.get(selected_voice_id)
        provider = provider_profile.provider if provider_profile else "edge_tts"

    voice_id_for_tts = selected_voice_id
    voice_name = provider_profile.voice.display_name if provider_profile else (voice["name"] if voice else voice_id_for_tts)
    if provider_profile is None and voice is None and output_lang == "zh":
        raise HTTPException(status_code=400, detail="unsupported voice id")

    scene = SCENE_BY_ID.get(payload.sceneId or "")
    content_to_speak = payload.content
    if output_lang != "zh":
        if payload.translatedContent and payload.translatedContent.strip():
            content_to_speak = payload.translatedContent
        else:
            await report(15, "正在翻译文本")
            try:
                content_to_speak = translate_text(payload.content, output_lang)
            except Exception as exc:
                raise HTTPException(status_code=502, detail=f"Translation failed: {exc}") from exc
    await report(22, "正在预处理文本")
    processed = preprocess_text(content_to_speak, payload.maxSegmentLength, payload.pauseScale)
    if not processed.cleanedText:
        raise HTTPException(status_code=400, detail="text content cannot be empty")
    if processed.sensitiveWords:
        words = ", ".join(sorted({hit.word for hit in processed.sensitiveWords}))
        raise HTTPException(status_code=400, detail=f"text contains sensitive words: {words}")

    work_id = uuid4().hex
    output_path = MEDIA_DIR / f"{work_id}.mp3"
    dry_output_path = MEDIA_DIR / f"{work_id}-voice.mp3"
    try:
        total_segments = max(1, len(processed.segments))

        async def synthesis_progress(done: int, total: int) -> None:
            percent = 30 + round((done / max(1, total)) * 45)
            await report(percent, f"正在合成第 {done}/{total} 段音频")

        await report(28, f"开始合成 {total_segments} 段音频")
        await synthesize_segments_to_file(
            segments=processed.segments,
            voice=voice_id_for_tts,
            speed=payload.speed,
            pitch=payload.pitch,
            emotion=payload.emotion,
            emotion_intensity=payload.emotionIntensity,
            output_path=dry_output_path,
            provider=provider,
            output_lang=output_lang,
            voice_volume=payload.voiceVolume,
            progress_callback=synthesis_progress,
        )
        await report(82, "正在混合背景音乐")
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

    await report(92, "正在保存作品")
    scene_name = scene["name"] if scene else "General"
    work = Work(
        id=work_id,
        ownerId=current_user.id if current_user else None,
        title=payload.title or _build_title(scene_name, processed.cleanedText),
        content=processed.cleanedText,
        sceneId=payload.sceneId or "",
        sceneName=scene_name,
        voiceId=voice_id_for_tts,
        voiceName=voice_name or voice_id_for_tts,
        speed=payload.speed,
        pitch=payload.pitch,
        emotion=payload.emotion,
        emotionIntensity=payload.emotionIntensity,
        bgmType=payload.bgmType,
        bgmVolume=payload.bgmVolume,
        duration=duration,
        audioUrl=f"{base_url.rstrip('/')}/media/{output_path.name}",
        createdAt=datetime.now(timezone.utc).isoformat(),
        segmentCount=len(processed.segments),
    )
    return save_work(work)

@app.get("/api/works", response_model=list[Work])
def get_works(current_user: User = Depends(get_current_user)) -> list[Work]:
    return list_works(current_user.id)


@app.get("/api/works/{work_id}", response_model=Work)
def get_work_detail(work_id: str, current_user: User = Depends(get_current_user)) -> Work:
    work = get_work(work_id, current_user.id)
    if work is None:
        raise HTTPException(status_code=404, detail="work not found")
    return work


@app.delete("/api/works/{work_id}")
def remove_work(work_id: str, current_user: User = Depends(get_current_user)) -> dict[str, bool]:
    if not delete_work(work_id, current_user.id):
        raise HTTPException(status_code=404, detail="work not found")
    return {"ok": True}


def _build_title(scene_name: str, text: str) -> str:
    excerpt = text[:20].strip()
    suffix = "..." if len(text) > 20 else ""
    return f"[{scene_name}] {excerpt}{suffix}"


def _find_bgm_path(db: Session, bgm_type: str) -> Path | None:
    if not bgm_type or bgm_type == "none":
        return None
    material = db.query(Material).filter(Material.material_key == bgm_type, Material.is_active.is_(True)).first()
    if not material:
        return None
    path = Path(material.audio_path)
    return path if path.exists() else None
