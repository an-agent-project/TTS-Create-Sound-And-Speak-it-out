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



def test_voice_preview_shows_generation_progress_and_resets_audio_state():
    source = VOICE_PREVIEW_PATH.read_text(encoding="utf-8")

    assert "previewProgress" in source
    assert "startPreviewProgress" in source
    assert "finishPreviewProgress" in source
    assert "resetAudioState" in source
    assert "audio.removeEventListener" in source
    assert "audio = null" in source


def test_workspace_shows_generation_progress_while_waiting_for_tts():
    source = WORKSPACE_PATH.read_text(encoding="utf-8")

    assert "generationProgress" in source
    assert "generationStage" in source
    assert "startGenerationProgress" in source
    assert "finishGenerationProgress" in source
    assert "resetGenerationProgress" in source

def test_workspace_uses_tts_job_polling_for_generation():
    api_source = API_PATH.read_text(encoding="utf-8")
    workspace_source = WORKSPACE_PATH.read_text(encoding="utf-8")

    assert "createTtsJob" in api_source
    assert "fetchTtsJob" in api_source
    assert "createTtsJob" in workspace_source
    assert "fetchTtsJob" in workspace_source
    assert "pollGenerationJob" in workspace_source
    assert "/tts/jobs" in api_source

VOICE_LIBRARY_PATH = ROOT_DIR / "src" / "views" / "VoiceLibrary.vue"
ENSURE_QWEN_MODEL_SCRIPT = ROOT_DIR / "backend" / "scripts" / "ensure_qwen_model.py"


def test_voice_library_does_not_expose_qwen_one_click_import():
    source = VOICE_LIBRARY_PATH.read_text(encoding="utf-8")
    api_source = API_PATH.read_text(encoding="utf-8")

    assert "importQwenPresetVoice" not in source
    assert "importPresetQwenVoice" not in source
    assert "qwen-presets/0-6b-customvoice/import" not in api_source


def test_qwen_model_initializer_script_exists():
    source = ENSURE_QWEN_MODEL_SCRIPT.read_text(encoding="utf-8")

    assert "snapshot_download" in source
    assert "seed_system_qwen_vivian" in source
    assert "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice" in source
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
