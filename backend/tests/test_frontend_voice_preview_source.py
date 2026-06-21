from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
VOICE_PREVIEW_PATH = ROOT_DIR / "src" / "components" / "VoicePreview.vue"
API_PATH = ROOT_DIR / "src" / "services" / "api.js"
TEXT_EDITOR_PATH = ROOT_DIR / "src" / "components" / "TextEditor.vue"
WORKSPACE_PATH = ROOT_DIR / "src" / "views" / "Workspace.vue"
VITE_CONFIG_PATH = ROOT_DIR / "vite.config.js"


def test_voice_preview_calls_tts_preview_api_and_plays_audio():
    source = VOICE_PREVIEW_PATH.read_text(encoding="utf-8")

    assert 'fetch("/api/tts/preview"' in source
    assert 'voiceId: props.voice.providerVoiceId || props.voice.id' in source
    assert "new Audio(audioUrl.value)" in source
    assert "@toggle-play=\"togglePreview\"" in source
    assert ":audio-url=\"audioUrl\"" in source


def test_voice_api_maps_active_provider_voice_id():
    source = API_PATH.read_text(encoding="utf-8")

    assert "item.isActive && item.isDefault" in source
    assert "providerVoiceId: provider?.providerVoiceId" in source


def test_workspace_clear_speed_and_pitch_controls_are_wired():
    editor_source = TEXT_EDITOR_PATH.read_text(encoding="utf-8")
    workspace_source = WORKSPACE_PATH.read_text(encoding="utf-8")

    assert 'emit("update:modelValue", "")' in editor_source
    assert 'v-model.number="settings.speed"' in workspace_source
    assert 'v-model.number="settings.pitch"' in workspace_source
    assert 'min="-50" max="50" step="5"' in workspace_source


def test_vite_proxies_api_and_static_audio_to_backend():
    source = VITE_CONFIG_PATH.read_text(encoding="utf-8")

    assert '"/api"' in source
    assert '"/static"' in source
    assert '"http://127.0.0.1:8000"' in source
