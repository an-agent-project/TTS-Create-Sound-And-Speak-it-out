from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
VOICE_PREVIEW_PATH = ROOT_DIR / "src" / "components" / "VoicePreview.vue"
VITE_CONFIG_PATH = ROOT_DIR / "vite.config.js"


def test_voice_preview_calls_tts_preview_api_and_plays_audio():
    source = VOICE_PREVIEW_PATH.read_text(encoding="utf-8")

    assert 'fetch("/api/tts/preview"' in source
    assert 'voiceId: props.voice.id' in source
    assert "new Audio(audioUrl.value)" in source
    assert "@toggle-play=\"togglePreview\"" in source
    assert ":audio-url=\"audioUrl\"" in source


def test_vite_proxies_api_and_static_audio_to_backend():
    source = VITE_CONFIG_PATH.read_text(encoding="utf-8")

    assert '"/api"' in source
    assert '"/static"' in source
    assert '"http://127.0.0.1:8000"' in source
