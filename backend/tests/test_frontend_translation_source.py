from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_PATH = ROOT_DIR / "src" / "views" / "Workspace.vue"
API_PATH = ROOT_DIR / "src" / "services" / "api.js"


def test_workspace_supports_translation_preview_and_editable_translated_text():
    workspace_source = WORKSPACE_PATH.read_text(encoding="utf-8")
    api_source = API_PATH.read_text(encoding="utf-8")

    assert "translateText" in api_source
    assert 'request("/text/translate"' in api_source
    assert "translatedContent" in workspace_source
    assert "previewTranslation" in workspace_source
    assert "translationStatus" in workspace_source
    assert "generateContent" in workspace_source
    assert "v-model=\"translatedContent\"" in workspace_source
    assert "翻译预览" in workspace_source


def test_workspace_exposes_advanced_tts_parameters_in_generate_payload():
    workspace_source = WORKSPACE_PATH.read_text(encoding="utf-8")
    store_source = (ROOT_DIR / "src" / "stores" / "app.js").read_text(encoding="utf-8")

    for field in ("voiceVolume", "maxSegmentLength", "pauseScale"):
        assert field in workspace_source
        assert field in store_source
    assert "settings.value.voiceVolume" in workspace_source
    assert "settings.value.maxSegmentLength" in workspace_source
    assert "settings.value.pauseScale" in workspace_source