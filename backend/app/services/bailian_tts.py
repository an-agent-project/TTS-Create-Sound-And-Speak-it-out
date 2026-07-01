import asyncio
import base64
import os
from pathlib import Path

import httpx

from app.env import load_env
from app.services.emotion_adapter import adapt_emotion

load_env()

BAILIAN_TTS_PROVIDER = "bailian_tts"
BAILIAN_TTS_DEFAULT_MODEL = "qwen3-tts-flash"
BAILIAN_TTS_INSTRUCT_MODEL = "qwen3-tts-instruct-flash"
BAILIAN_TTS_DEFAULT_VOICE = "Cherry"
BAILIAN_TTS_DEFAULT_LANGUAGE = "Chinese"
BAILIAN_LANGUAGE_TYPE_BY_OUTPUT_LANG = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
}
BAILIAN_VOICE_CLONE_MODEL = "qwen-voice-enrollment"
BAILIAN_VOICE_CLONE_TARGET_MODEL = "qwen3-tts-vc-2026-01-22"
BAILIAN_TTS_DEFAULT_PROVIDER_VOICE_ID = (
    f"bailian:{BAILIAN_TTS_DEFAULT_MODEL}:{BAILIAN_TTS_DEFAULT_VOICE}"
)


def _language_type_for_output_lang(output_lang: str | None) -> str:
    return BAILIAN_LANGUAGE_TYPE_BY_OUTPUT_LANG.get(output_lang or "zh", BAILIAN_TTS_DEFAULT_LANGUAGE)


def parse_bailian_provider_voice_id(provider_voice_id: str) -> tuple[str, str]:
    """Return (model, voice) from our stored provider voice id."""
    provider_voice_id = (provider_voice_id or "").split("#public-", 1)[0]
    if provider_voice_id.startswith("bailian:"):
        parts = provider_voice_id.split(":", 2)
        if len(parts) == 3 and parts[1] and parts[2]:
            return parts[1], parts[2]
    return (
        os.getenv("BAILIAN_TTS_MODEL", BAILIAN_TTS_DEFAULT_MODEL),
        provider_voice_id or os.getenv("BAILIAN_TTS_VOICE", BAILIAN_TTS_DEFAULT_VOICE),
    )


async def synthesize_bailian_to_file(
    text: str,
    provider_voice_id: str,
    output_path: Path,
    output_lang: str = "zh",
    speed: float = 1.0,
    pitch: int = 0,
    emotion: str = "calm",
    emotion_intensity: str = "normal",
) -> None:
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("BAILIAN_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not configured")

    model, voice = parse_bailian_provider_voice_id(provider_voice_id)
    language_type = os.getenv("BAILIAN_TTS_LANGUAGE") or _language_type_for_output_lang(output_lang)
    adapted = adapt_emotion(BAILIAN_TTS_PROVIDER, emotion, speed, pitch, emotion_intensity)
    workspace = os.getenv("DASHSCOPE_WORKSPACE") or os.getenv("BAILIAN_WORKSPACE")

    response = await _call_qwen_tts(
        text=text,
        model=_instruction_model(model),
        voice=voice,
        language_type=language_type,
        instructions=adapted.instruction,
        api_key=api_key,
        workspace=workspace,
    )
    audio_url = _extract_audio_url(response)
    if not audio_url:
        raise RuntimeError(_format_bailian_error(response))
    await _download_audio(audio_url, output_path)


async def create_qwen_voice_clone(
    audio_bytes: bytes,
    mime_type: str,
    preferred_name: str,
) -> str:
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("BAILIAN_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not configured")

    data_uri = f"data:{mime_type};base64,{base64.b64encode(audio_bytes).decode('ascii')}"
    payload = {
        "model": BAILIAN_VOICE_CLONE_MODEL,
        "input": {
            "action": "create",
            "target_model": BAILIAN_VOICE_CLONE_TARGET_MODEL,
            "preferred_name": preferred_name,
            "audio": {"data": data_uri},
        },
    }

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            _voice_clone_url(),
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
    if response.status_code >= 400:
        raise RuntimeError(
            f"Bailian voice cloning failed: status={response.status_code}; body={response.text[:500]}"
        )
    data = response.json()
    voice = _nested_get(data, "output", "voice") or data.get("voice")
    if not voice:
        raise RuntimeError(_format_bailian_error(data))
    return str(voice)


async def _call_qwen_tts(
    text: str,
    model: str,
    voice: str,
    language_type: str,
    instructions: str,
    api_key: str,
    workspace: str | None,
):
    try:
        import dashscope
    except ImportError as exc:
        raise RuntimeError(
            "dashscope is not installed; run `pip install -r backend/requirements.txt`"
        ) from exc

    def run_call():
        kwargs = {
            "api_key": api_key,
            "model": model,
            "text": text,
            "voice": voice,
            "language_type": language_type,
            "instructions": instructions,
            "optimize_instructions": True,
            "stream": False,
        }
        if workspace:
            kwargs["workspace"] = workspace
        return dashscope.MultiModalConversation.call(**kwargs)

    return await asyncio.to_thread(run_call)


def _instruction_model(model: str) -> str:
    return os.getenv("BAILIAN_TTS_INSTRUCT_MODEL") or (
        BAILIAN_TTS_INSTRUCT_MODEL if model == BAILIAN_TTS_DEFAULT_MODEL else model
    )


def _voice_clone_url() -> str:
    explicit_url = os.getenv("BAILIAN_TTS_CUSTOMIZATION_URL")
    if explicit_url:
        return explicit_url
    workspace = os.getenv("DASHSCOPE_WORKSPACE") or os.getenv("BAILIAN_WORKSPACE")
    if not workspace:
        raise RuntimeError("DASHSCOPE_WORKSPACE is required for Bailian voice cloning")
    region = os.getenv("DASHSCOPE_REGION", "cn-beijing")
    return f"https://{workspace}.{region}.maas.aliyuncs.com/api/v1/services/audio/tts/customization"


def _extract_audio_url(response) -> str | None:
    if isinstance(response, dict):
        candidates = [
            response.get("audio_url"),
            response.get("url"),
            _nested_get(response, "output", "audio", "url"),
            _nested_get(response, "output", "url"),
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate:
                return candidate

    output = getattr(response, "output", None)
    if isinstance(output, dict):
        return _extract_audio_url({"output": output})
    return None


def _format_bailian_error(response) -> str:
    if isinstance(response, dict):
        code = response.get("code") or response.get("status_code")
        message = response.get("message") or response.get("msg")
        request_id = response.get("request_id") or response.get("requestId")
        parts = ["Bailian Qwen-TTS response did not contain audio URL"]
        if code:
            parts.append(f"code={code}")
        if message:
            parts.append(f"message={message}")
        if request_id:
            parts.append(f"request_id={request_id}")
        return "; ".join(parts)

    status_code = getattr(response, "status_code", None)
    code = getattr(response, "code", None)
    message = getattr(response, "message", None)
    request_id = getattr(response, "request_id", None)
    parts = ["Bailian Qwen-TTS response did not contain audio URL"]
    if status_code:
        parts.append(f"status_code={status_code}")
    if code:
        parts.append(f"code={code}")
    if message:
        parts.append(f"message={message}")
    if request_id:
        parts.append(f"request_id={request_id}")
    return "; ".join(parts)


def _nested_get(data: dict, *keys: str):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


async def _download_audio(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(url)
        response.raise_for_status()
        output_path.write_bytes(response.content)
