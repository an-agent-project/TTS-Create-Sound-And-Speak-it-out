from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.materials import router as materials_router
from app.api.model_artifacts import router as model_artifacts_router
from app.api.tts import router as tts_router
from app.api.training_jobs import router as training_jobs_router
from app.api.voices import router as voices_router
from app.auth import get_optional_user
from app.data import SCENE_BY_ID, SCENES, VOICE_BY_ID
from app.database import engine, get_db
from app.models import Base
from app.models import User
from app.services.text_processing import preprocess_text
from app.services.qwen_tts import synthesize_qwen_to_file
from app.services.tts import synthesize_segments_to_file
from app.services.voice_provider import resolve_provider_by_voice_or_provider_id
from app.storage import MEDIA_DIR, delete_work, ensure_storage, get_work, list_works, save_work
from app.work_schemas import GenerateRequest, PreprocessRequest, TtsJobStatus, Work


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
app.include_router(materials_router)
app.include_router(training_jobs_router)
app.include_router(model_artifacts_router)

TTS_JOBS: dict[str, dict] = {}


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_response(job: dict) -> TtsJobStatus:
    return TtsJobStatus(
        jobId=job["jobId"],
        status=job["status"],
        progress=job["progress"],
        stage=job["stage"],
        work=job.get("work"),
        errorMessage=job.get("errorMessage"),
        createdAt=job["createdAt"],
        updatedAt=job["updatedAt"],
    )


def _update_job(job_id: str, *, status: str, progress: int, stage: str, **extra) -> None:
    job = TTS_JOBS[job_id]
    job.update(
        {
            "status": status,
            "progress": max(0, min(100, progress)),
            "stage": stage,
            "updatedAt": _utc_now(),
            **extra,
        }
    )


async def _generate_tts_work(
    payload: GenerateRequest,
    base_url: str,
    current_user: User | None,
    db,
    progress_callback=None,
) -> Work:
    if progress_callback:
        progress_callback("preprocessing", 12, "解析音色与预处理文本")

    resolved_voice = resolve_provider_by_voice_or_provider_id(
        db,
        payload.voiceId,
        user_id=current_user.id if current_user else None,
    )
    static_voice = VOICE_BY_ID.get(payload.voiceId)
    if resolved_voice:
        voice_name = resolved_voice.voice.display_name
    elif static_voice:
        voice_name = static_voice["name"]
    else:
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
        if resolved_voice and resolved_voice.provider.provider == "qwen3_tts":
            if progress_callback:
                progress_callback("synthesizing", 35, "调用本地 Qwen 模型合成")
            combined_text = "\n\n".join(segment.text for segment in processed.segments)
            duration = await synthesize_qwen_to_file(
                text=combined_text,
                provider_profile=resolved_voice.provider,
                speed=payload.speed,
                pitch=payload.pitch,
                emotion=payload.emotion,
                output_path=output_path,
            )
        else:
            if progress_callback:
                progress_callback("synthesizing", 35, "调用 TTS 服务合成")
            edge_voice_id = (
                resolved_voice.provider.provider_voice_id
                if resolved_voice and resolved_voice.provider.provider == "edge_tts"
                else payload.voiceId
            )
            duration = await synthesize_segments_to_file(
                segments=processed.segments,
                voice=edge_voice_id,
                speed=payload.speed,
                pitch=payload.pitch,
                emotion=payload.emotion,
                output_path=output_path,
            )
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc

    if progress_callback:
        progress_callback("writing", 92, "写入作品信息")

    scene_name = scene["name"] if scene else "通用"
    work = Work(
        id=work_id,
        title=payload.title or _build_title(scene_name, processed.cleanedText),
        content=processed.cleanedText,
        sceneId=payload.sceneId or "",
        sceneName=scene_name,
        voiceId=payload.voiceId,
        voiceName=voice_name,
        speed=payload.speed,
        pitch=payload.pitch,
        emotion=payload.emotion,
        bgmType=payload.bgmType,
        bgmVolume=payload.bgmVolume,
        duration=duration,
        audioUrl=f"{base_url.rstrip('/')}/media/{output_path.name}",
        createdAt=_utc_now(),
        segmentCount=len(processed.segments),
    )
    return save_work(work)


@app.post("/api/tts/generate", response_model=Work)
async def generate_tts(
    payload: GenerateRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_user),
    db=Depends(get_db),
) -> Work:
    return await _generate_tts_work(
        payload=payload,
        base_url=str(request.base_url),
        current_user=current_user,
        db=db,
    )


@app.post("/api/tts/jobs", response_model=TtsJobStatus, status_code=status.HTTP_202_ACCEPTED)
async def create_tts_job(
    payload: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User | None = Depends(get_optional_user),
    db=Depends(get_db),
) -> TtsJobStatus:
    job_id = uuid4().hex
    now = _utc_now()
    TTS_JOBS[job_id] = {
        "jobId": job_id,
        "ownerId": current_user.id if current_user else None,
        "status": "queued",
        "progress": 5,
        "stage": "任务已进入队列",
        "work": None,
        "errorMessage": None,
        "createdAt": now,
        "updatedAt": now,
    }

    async def run_job() -> None:
        def set_progress(next_status: str, progress: int, stage: str) -> None:
            _update_job(job_id, status=next_status, progress=progress, stage=stage)

        try:
            work = await _generate_tts_work(
                payload=payload,
                base_url=str(request.base_url),
                current_user=current_user,
                db=db,
                progress_callback=set_progress,
            )
            _update_job(
                job_id,
                status="completed",
                progress=100,
                stage="配音生成完成",
                work=work,
                errorMessage=None,
            )
        except HTTPException as exc:
            _update_job(
                job_id,
                status="failed",
                progress=100,
                stage="配音生成失败",
                errorMessage=str(exc.detail),
            )
        except Exception as exc:
            _update_job(
                job_id,
                status="failed",
                progress=100,
                stage="配音生成失败",
                errorMessage=str(exc),
            )

    background_tasks.add_task(run_job)
    return _job_response(TTS_JOBS[job_id])


@app.get("/api/tts/jobs/{job_id}", response_model=TtsJobStatus)
def get_tts_job(
    job_id: str,
    current_user: User | None = Depends(get_optional_user),
) -> TtsJobStatus:
    job = TTS_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="tts job not found")
    if job.get("ownerId") is not None and (current_user is None or current_user.id != job["ownerId"]):
        raise HTTPException(status_code=404, detail="tts job not found")
    return _job_response(job)


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
