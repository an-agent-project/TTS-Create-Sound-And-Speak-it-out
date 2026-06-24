import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf
import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Qwen3-TTS CustomVoice inference once.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provider-voice-id", default="")
    parser.add_argument("--speed", default="1.0")
    parser.add_argument("--pitch", default="0")
    parser.add_argument("--emotion", default="calm")
    parser.add_argument("--runtime-config-json", default="")
    parser.add_argument("--artifact-runtime-config-json", default="")
    return parser.parse_args()


def load_json(value: str) -> dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in [
        os.getenv("TTS_FFMPEG_DIR"),
        os.getenv("FFMPEG_DIR"),
        r"D:\ffmpeg-master-latest-win64-gpl\bin",
        r"D:\ffmpeg-master-latest-win64-gpl",
    ]:
        if not candidate:
            continue
        path = Path(candidate) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if path.exists():
            return str(path)
    return None


def write_audio(output_path: Path, wav, sample_rate: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() != ".mp3":
        sf.write(output_path, wav, sample_rate)
        return

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to write mp3 output for Qwen3-TTS.")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    try:
        sf.write(temp_path, wav, sample_rate)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(temp_path),
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "96k",
                str(output_path),
            ],
            check=True,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def build_model_kwargs(runtime: dict, cache_dir: Path, device: str, dtype) -> dict:
    kwargs = {
        "dtype": dtype,
        "device_map": device,
        "cache_dir": str(cache_dir),
        "attn_implementation": "flash_attention_2" if runtime.get("flash_attn", False) else None,
    }
    if "local_files_only" in runtime:
        kwargs["local_files_only"] = bool(runtime["local_files_only"])
    return kwargs


def main() -> None:
    args = parse_args()
    runtime = {
        **load_json(args.artifact_runtime_config_json),
        **load_json(args.runtime_config_json),
    }
    cache_dir = Path(
        runtime.get("cache_dir")
        or os.getenv("QWEN_TTS_CACHE_DIR")
        or Path(__file__).resolve().parents[2] / ".hf-cache" / "qwen-tts"
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["HUGGINGFACE_HUB_CACHE"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)

    from qwen_tts import Qwen3TTSModel

    device = runtime.get("device") or ("cuda:0" if torch.cuda.is_available() else "cpu")
    dtype_name = str(runtime.get("dtype") or "float32").lower()
    dtype = {
        "bf16": torch.bfloat16,
        "bfloat16": torch.bfloat16,
        "fp16": torch.float16,
        "float16": torch.float16,
        "fp32": torch.float32,
        "float32": torch.float32,
    }.get(dtype_name, torch.float32)

    model = Qwen3TTSModel.from_pretrained(
        args.model_path,
        **build_model_kwargs(runtime, cache_dir, device, dtype),
    )

    wavs, sample_rate = model.generate_custom_voice(
        text=args.text,
        speaker=runtime.get("speaker", "Vivian"),
        language=runtime.get("language", "Auto"),
        instruct=runtime.get("instruct") or None,
        max_new_tokens=runtime.get("max_new_tokens"),
        temperature=runtime.get("temperature"),
        top_k=runtime.get("top_k"),
        top_p=runtime.get("top_p"),
    )

    write_audio(Path(args.output), wavs[0], sample_rate)


if __name__ == "__main__":
    main()
