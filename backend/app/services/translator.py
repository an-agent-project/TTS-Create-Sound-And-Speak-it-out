from deep_translator import GoogleTranslator

# Language code -> display name
LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
}

# Output language -> recommended Edge-TTS voice
LANG_VOICE_MAP = {
    "zh": "zh-CN-XiaoxiaoNeural",
    "en": "en-US-JennyNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
}


def translate_text(text: str, target_lang: str) -> str:
    if target_lang == "zh":
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as exc:
        raise RuntimeError(f"Translation failed: {exc}") from exc
