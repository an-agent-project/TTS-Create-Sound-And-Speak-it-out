from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.data import SCENE_BY_ID, SCENES, VOICE_BY_ID, VOICES
from app.models import GenerateRequest, PreprocessRequest, Work
from app.services.text_processing import preprocess_text
from app.services.tts import synthesize_to_file
from app.storage import MEDIA_DIR, delete_work, ensure_storage, get_work, list_works, save_work

app = FastAPI(title="有声读物智能生成系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_storage()
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "audiobook-generator-backend"}


@app.get("/api/scenes")
def get_scenes() -> list[dict]:
    return SCENES


@app.get("/api/voices")
def get_voices() -> list[dict]:
    return VOICES


@app.post("/api/text/preprocess")
def preprocess(payload: PreprocessRequest):
    return preprocess_text(payload.content, payload.maxSegmentLength)


@app.post("/api/tts/generate", response_model=Work)
async def generate_tts(payload: GenerateRequest, request: Request) -> Work:
    voice = VOICE_BY_ID.get(payload.voiceId)
    if voice is None:
        raise HTTPException(status_code=400, detail="不支持的音色 ID")

    scene = SCENE_BY_ID.get(payload.sceneId or "")
    processed = preprocess_text(payload.content)
    if not processed.cleanedText:
        raise HTTPException(status_code=400, detail="文本内容不能为空")
    if processed.sensitiveWords:
        words = "、".join(sorted({hit.word for hit in processed.sensitiveWords}))
        raise HTTPException(status_code=400, detail=f"文本包含敏感词：{words}")

    work_id = uuid4().hex
    output_path = MEDIA_DIR / f"{work_id}.mp3"

    try:
        await synthesize_to_file(
            text=processed.cleanedText,
            voice=payload.voiceId,
            speed=payload.speed,
            pitch=payload.pitch,
            emotion=payload.emotion,
            output_path=output_path,
        )
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=502, detail=f"TTS 合成失败：{exc}") from exc

    title = payload.title or _build_title(scene["name"] if scene else "通用", processed.cleanedText)
    audio_url = _public_media_url(request, output_path)
    work = Work(
        id=work_id,
        title=title,
        content=processed.cleanedText,
        sceneId=scene["id"] if scene else "",
        sceneName=scene["name"] if scene else "通用",
        voiceId=payload.voiceId,
        voiceName=voice["name"],
        speed=payload.speed,
        pitch=payload.pitch,
        emotion=payload.emotion,
        bgmType=payload.bgmType,
        bgmVolume=payload.bgmVolume,
        duration=max(1, round(len(processed.cleanedText) / 4)),
        audioUrl=audio_url,
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
        raise HTTPException(status_code=404, detail="作品不存在")
    return work


@app.delete("/api/works/{work_id}")
def remove_work(work_id: str) -> dict[str, bool]:
    if not delete_work(work_id):
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"ok": True}


def _build_title(scene_name: str, text: str) -> str:
    excerpt = text[:20].strip()
    suffix = "..." if len(text) > 20 else ""
    return f"【{scene_name}】{excerpt}{suffix}"


def _public_media_url(request: Request, path: Path) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/media/{path.name}"
