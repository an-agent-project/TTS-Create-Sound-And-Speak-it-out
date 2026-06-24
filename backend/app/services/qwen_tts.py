import asyncio
import os
import shlex
import sys
from pathlib import Path

from app.models import VoiceProviderProfile
from app.services.tts import _estimate_duration_seconds, _has_media_tools, _probe_duration

REPO_DIR = Path(__file__).resolve().parents[3]
DEFAULT_QWEN_RUNNER = REPO_DIR / "backend" / "scripts" / "qwen_custom_voice_runner.py"
DEFAULT_QWEN_PYTHON_CANDIDATES = (
    REPO_DIR / ".venv-gpu" / "Scripts" / "python.exe",
    REPO_DIR / ".venv" / "Scripts" / "python.exe",
) if sys.platform == "win32" else (
    REPO_DIR / ".venv-gpu" / "bin" / "python",
    REPO_DIR / ".venv" / "bin" / "python",
)
DEFAULT_QWEN_PYTHON = DEFAULT_QWEN_PYTHON_CANDIDATES[-1]


def resolve_qwen_command() -> list[str]:
    command = os.getenv("QWEN3_TTS_COMMAND")
    if command:
        parts = shlex.split(command, posix=os.name != "nt")
        resolved_parts = []
        for part in parts:
            path = Path(part.strip('"'))
            if not path.is_absolute():
                repo_path = REPO_DIR / path
                if repo_path.exists():
                    resolved_parts.append(str(repo_path))
                    continue
            resolved_parts.append(str(path) if path.is_absolute() else part)
        return resolved_parts
    if DEFAULT_QWEN_RUNNER.exists():
        for python_path in DEFAULT_QWEN_PYTHON_CANDIDATES:
            if python_path.exists():
                return [str(python_path), str(DEFAULT_QWEN_RUNNER)]
    raise RuntimeError(
        "QWEN3_TTS_COMMAND is not configured and the default Qwen3-TTS runner was not found."
    )


async def synthesize_qwen_to_file(
    text: str,
    provider_profile: VoiceProviderProfile,
    output_path: Path,
    speed: float = 1.0,
    pitch: int = 0,
    emotion: str = "calm",
) -> int:
    artifact = provider_profile.model_artifact
    if not artifact or not artifact.artifact_path:
        raise RuntimeError("Qwen3-TTS voice is missing model artifact path.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    args = [
        *resolve_qwen_command(),
        "--model-path",
        artifact.artifact_path,
        "--text",
        text,
        "--output",
        str(output_path),
        "--provider-voice-id",
        provider_profile.provider_voice_id,
        "--speed",
        str(speed),
        "--pitch",
        str(pitch),
        "--emotion",
        emotion,
    ]
    if provider_profile.runtime_config_json:
        args.extend(["--runtime-config-json", provider_profile.runtime_config_json])
    if artifact.runtime_config_json:
        args.extend(["--artifact-runtime-config-json", artifact.runtime_config_json])

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        message = stderr.decode("utf-8", errors="replace").strip()
        detail = message or stdout.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "Qwen3-TTS inference command failed.")

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("Qwen3-TTS inference did not create an audio file.")

    if _has_media_tools():
        return max(1, round(await _probe_duration(output_path)))
    return _estimate_duration_seconds(text, speed)
