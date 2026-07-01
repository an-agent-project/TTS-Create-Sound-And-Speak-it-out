import html
import os
from pathlib import Path

import httpx

from app.services.emotion_adapter import adapt_emotion


AZURE_TTS_PROVIDER = "azure_tts"
AZURE_OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3"
AZURE_STYLE_MAP = {
    "calm": "calm",
    "happy": "cheerful",
    "sad": "sad",
    "excited": "excited",
}


async def synthesize_azure_to_file(
    text: str,
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    emotion_intensity: str,
    output_path: Path,
) -> None:
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    if not key or not region:
        raise RuntimeError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION are required")

    response = await _call_azure_tts(
        key=key,
        region=region,
        ssml=_build_ssml(
            text=text,
            voice=voice,
            speed=speed,
            pitch=pitch,
            emotion=emotion,
            emotion_intensity=emotion_intensity,
        ),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response)


def _build_ssml(
    text: str,
    voice: str,
    speed: float,
    pitch: int,
    emotion: str,
    emotion_intensity: str = "normal",
) -> str:
    adapted = adapt_emotion(AZURE_TTS_PROVIDER, emotion, speed, pitch, emotion_intensity)
    style = AZURE_STYLE_MAP.get(emotion, "general")
    rate = f"{adapted.rate_percent:+d}%"
    pitch_value = f"{adapted.pitch_hz:+d}Hz"
    escaped_text = html.escape(text, quote=False)

    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="{html.escape(voice)}">
    <mstts:express-as style="{style}">
      <prosody rate="{rate}" pitch="{pitch_value}">{escaped_text}</prosody>
    </mstts:express-as>
  </voice>
</speak>"""


async def _call_azure_tts(key: str, region: str, ssml: str) -> bytes:
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": AZURE_OUTPUT_FORMAT,
        "User-Agent": "tts-podcast",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, content=ssml.encode("utf-8"))
    if response.status_code >= 400:
        raise RuntimeError(f"Azure TTS failed: status={response.status_code}; body={response.text[:500]}")
    return response.content
