from pathlib import Path


PREVIEW_DIR = Path(__file__).resolve().parents[2] / "static" / "previews"


async def synthesize_preview(text: str, voice_id: str, output_filename: str) -> dict:
    import edge_tts

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREVIEW_DIR / output_filename

    communicate = edge_tts.Communicate(text=text, voice=voice_id)
    await communicate.save(str(output_path))

    return {
        "filename": output_filename,
        "path": output_path,
        "duration": max(1, round(len(text) / 5)),
    }
