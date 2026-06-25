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

def test_workspace_loads_voices_from_voice_api():
    source = WORKSPACE_PATH.read_text(encoding="utf-8")

    assert 'import { fetchVoices, generateTts }' in source
    assert 'await fetchVoices()' in source
    assert 'const availableVoices = ref' in source
    assert 'const availableVoices = [' not in source

def test_extraction_page_exposes_bailian_clone_upload_not_voice_library():
    api_source = API_PATH.read_text(encoding="utf-8")
    library_source = (ROOT_DIR / "src" / "views" / "VoiceLibrary.vue").read_text(encoding="utf-8")
    extraction_source = (ROOT_DIR / "src" / "views" / "ExtractionPage.vue").read_text(encoding="utf-8")

    assert "export async function createVoiceClone" in api_source
    assert 'fetch(`${API_BASE}/voice-clones`' in api_source
    assert 'localStorage.getItem("auth_token")' in api_source
    assert 'createVoiceClone(formData)' in extraction_source
    assert 'cloneVoice' in extraction_source
    assert '克隆音色' in extraction_source
    assert 'createVoiceClone(formData)' not in library_source
    assert 'cloneVoice' not in library_source
def test_extraction_page_generates_preview_for_cloned_voice_result():
    api_source = API_PATH.read_text(encoding="utf-8")
    extraction_source = (ROOT_DIR / "src" / "views" / "ExtractionPage.vue").read_text(encoding="utf-8")

    assert "export function synthesizeVoicePreview" in api_source
    assert 'request("/tts/preview"' in api_source
    assert 'synthesizeVoicePreview({' in extraction_source
    assert 'voiceId: clonedVoice.providers?.[0]?.providerVoiceId' in extraction_source
    assert 'src: preview.audioUrl' in extraction_source
    assert 'URL.createObjectURL(uploadedFile.value)' not in extraction_source
