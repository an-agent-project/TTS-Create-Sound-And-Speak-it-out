from typing import Literal

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    title: str | None = None
    content: str = Field(..., min_length=1, max_length=20000)
    sceneId: str | None = None
    voiceId: str
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: int = Field(0, ge=-50, le=50)
    emotion: Literal["calm", "happy", "sad", "excited"] = "calm"
    emotionIntensity: Literal["light", "normal", "strong"] = "normal"
    bgmType: str = "none"
    outputLang: str = Field("zh", alias="outputLang")
    bgmVolume: int = Field(30, ge=0, le=100)


class PreprocessRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=20000)
    maxSegmentLength: int = Field(120, ge=40, le=300)


class TextSegment(BaseModel):
    index: int
    text: str
    pauseMs: int


class SensitiveHit(BaseModel):
    word: str
    index: int


class PreprocessResponse(BaseModel):
    cleanedText: str
    segments: list[TextSegment]
    sensitiveWords: list[SensitiveHit]


class Work(BaseModel):
    id: str
    title: str
    content: str
    sceneId: str = ""
    sceneName: str = "通用"
    voiceId: str
    voiceName: str
    speed: float
    pitch: int | Literal["low", "normal", "high"]
    emotion: str
    emotionIntensity: str = "normal"
    bgmType: str
    bgmVolume: int
    duration: int
    audioUrl: str
    status: str = "completed"
    createdAt: str
    segmentCount: int = 0
