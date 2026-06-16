from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.tts import router as tts_router
from app.api.voices import router as voices_router


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
PREVIEW_DIR = STATIC_DIR / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="TTS Podcast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(tts_router)
app.include_router(voices_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
