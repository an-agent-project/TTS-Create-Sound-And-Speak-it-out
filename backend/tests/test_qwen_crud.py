import sys
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


def _make_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _register(client: TestClient, username: str = "alice") -> str:
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "pass1234"},
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_material_asset_lifecycle():
    client = _make_client()
    token = _register(client)

    response = client.post(
        "/api/material-assets",
        json={
            "name": "demo dataset",
            "assetType": "audio_dataset",
            "sourceFormat": "zip",
            "originalFilename": "demo.zip",
            "storagePath": "storage/materials/demo.zip",
            "items": [
                {
                    "filename": "sample.wav",
                    "mediaType": "audio",
                    "storagePath": "storage/materials/sample.wav",
                    "transcript": "hello",
                    "durationSeconds": 2.5,
                    "fileSizeBytes": 1024,
                }
            ],
        },
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    asset = response.json()
    assert asset["name"] == "demo dataset"
    assert asset["items"][0]["filename"] == "sample.wav"

    response = client.put(
        f"/api/material-assets/{asset['id']}",
        json={"name": "renamed dataset", "status": "ready"},
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "renamed dataset"

    response = client.delete(f"/api/material-assets/{asset['id']}", headers=_headers(token))
    assert response.status_code == 204

    response = client.get(f"/api/material-assets/{asset['id']}", headers=_headers(token))
    assert response.status_code == 404


def test_training_job_lifecycle_with_material_asset():
    client = _make_client()
    token = _register(client)

    asset_response = client.post(
        "/api/material-assets",
        json={"name": "dataset", "storagePath": "storage/materials/dataset.zip"},
        headers=_headers(token),
    )
    assert asset_response.status_code == 201, asset_response.text
    asset_id = asset_response.json()["id"]

    response = client.post(
        "/api/training-jobs",
        json={
            "jobName": "clone voice",
            "materialAssetId": asset_id,
            "baseModel": "qwen3-tts-1.7b",
            "configJson": "{\"epochs\":1}",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    job = response.json()
    assert job["status"] == "queued"
    assert job["materialAssetId"] == asset_id

    response = client.put(
        f"/api/training-jobs/{job['id']}",
        json={"status": "running"},
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "running"
    assert response.json()["startedAt"] is not None

    response = client.post(f"/api/training-jobs/{job['id']}/cancel", headers=_headers(token))
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "canceled"
    assert response.json()["completedAt"] is not None


def test_model_artifact_can_back_qwen_voice_provider():
    client = _make_client()
    token = _register(client)

    response = client.post(
        "/api/model-artifacts",
        json={
            "displayName": "Alice Qwen Voice",
            "provider": "qwen3_tts",
            "modelVersion": "qwen3-tts-1.7b",
            "artifactPath": "D:/models/alice",
            "runtimeConfigJson": "{\"speaker\":\"alice\"}",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    artifact = response.json()

    response = client.post(
        "/api/voices",
        json={
            "voiceKey": "alice-qwen",
            "displayName": "Alice Qwen",
            "gender": "female",
            "style": "custom",
            "category": "personal",
            "providers": [
                {
                    "provider": "qwen3_tts",
                    "providerVoiceId": "artifact:alice-qwen",
                    "providerKind": "local_model",
                    "modelArtifactId": artifact["id"],
                    "runtimeConfigJson": "{\"speaker\":\"alice\"}",
                    "supportsWav": True,
                    "supportsMp3": True,
                    "isDefault": True,
                }
            ],
        },
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    voice = response.json()
    assert voice["providers"][0]["providerKind"] == "local_model"
    assert voice["providers"][0]["modelArtifactId"] == artifact["id"]


def test_user_cannot_reference_other_users_model_artifact():
    client = _make_client()
    alice_token = _register(client, "alice")
    bob_token = _register(client, "bob")

    response = client.post(
        "/api/model-artifacts",
        json={"displayName": "Alice Model", "artifactPath": "D:/models/alice"},
        headers=_headers(alice_token),
    )
    assert response.status_code == 201, response.text
    artifact_id = response.json()["id"]

    response = client.post(
        "/api/voices",
        json={
            "voiceKey": "bob-qwen",
            "displayName": "Bob Qwen",
            "gender": "male",
            "providers": [
                {
                    "provider": "qwen3_tts",
                    "providerVoiceId": "artifact:bob-qwen",
                    "providerKind": "local_model",
                    "modelArtifactId": artifact_id,
                }
            ],
        },
        headers=_headers(bob_token),
    )
    assert response.status_code == 400


def test_imported_qwen_voice_can_preview_and_generate(monkeypatch, tmp_path):
    client = _make_client()
    token = _register(client)

    runner = tmp_path / "fake_qwen_runner.py"
    runner.write_text(
        "\n".join(
            [
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--model-path')",
                "parser.add_argument('--text')",
                "parser.add_argument('--output')",
                "parser.add_argument('--provider-voice-id')",
                "parser.add_argument('--speed')",
                "parser.add_argument('--pitch')",
                "parser.add_argument('--emotion')",
                "parser.add_argument('--runtime-config-json', default='')",
                "parser.add_argument('--artifact-runtime-config-json', default='')",
                "args = parser.parse_args()",
                "with open(args.output, 'wb') as f:",
                "    f.write(b'fake-qwen-audio')",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("QWEN3_TTS_COMMAND", f'"{sys.executable}" "{runner}"')
    monkeypatch.setattr("app.services.qwen_tts._has_media_tools", lambda: False)

    artifact_response = client.post(
        "/api/model-artifacts",
        json={
            "displayName": "Qwen Demo",
            "provider": "qwen3_tts",
            "modelVersion": "0.6B-CustomVoice",
            "artifactPath": str(tmp_path / "Qwen3-TTS-0.6B-CustomVoice"),
        },
        headers=_headers(token),
    )
    assert artifact_response.status_code == 201, artifact_response.text
    artifact_id = artifact_response.json()["id"]

    voice_response = client.post(
        "/api/voices",
        json={
            "voiceKey": "qwen-demo",
            "displayName": "Qwen Demo",
            "gender": "female",
            "style": "custom",
            "category": "personal",
            "providers": [
                {
                    "provider": "qwen3_tts",
                    "providerVoiceId": "qwen3:qwen-demo",
                    "providerKind": "local_model",
                    "modelArtifactId": artifact_id,
                    "supportsWav": True,
                    "supportsMp3": True,
                    "isDefault": True,
                }
            ],
        },
        headers=_headers(token),
    )
    assert voice_response.status_code == 201, voice_response.text

    preview_response = client.post(
        "/api/tts/preview",
        json={"text": "hello qwen", "voiceId": "qwen-demo"},
        headers=_headers(token),
    )
    assert preview_response.status_code == 200, preview_response.text
    assert preview_response.json()["audioUrl"].startswith("/static/previews/")

    generate_response = client.post(
        "/api/tts/generate",
        json={
            "content": "hello qwen",
            "voiceId": "qwen-demo",
            "speed": 1.0,
            "pitch": 0,
            "emotion": "calm",
        },
        headers=_headers(token),
    )
    assert generate_response.status_code == 200, generate_response.text
    body = generate_response.json()
    assert body["voiceName"] == "Qwen Demo"
    assert body["audioUrl"].endswith(".mp3")



def test_tts_generate_job_reports_progress_and_completed_work(monkeypatch, tmp_path):
    client = _make_client()
    token = _register(client)

    runner = tmp_path / "fake_qwen_runner.py"
    runner.write_text(
        "\n".join(
            [
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--model-path')",
                "parser.add_argument('--text')",
                "parser.add_argument('--output')",
                "parser.add_argument('--provider-voice-id')",
                "parser.add_argument('--speed')",
                "parser.add_argument('--pitch')",
                "parser.add_argument('--emotion')",
                "parser.add_argument('--runtime-config-json', default='')",
                "parser.add_argument('--artifact-runtime-config-json', default='')",
                "args = parser.parse_args()",
                "with open(args.output, 'wb') as f:",
                "    f.write(b'fake-qwen-audio')",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("QWEN3_TTS_COMMAND", f'"{sys.executable}" "{runner}"')
    monkeypatch.setattr("app.services.qwen_tts._has_media_tools", lambda: False)

    artifact_response = client.post(
        "/api/model-artifacts",
        json={"displayName": "Qwen Demo", "provider": "qwen3_tts", "artifactPath": str(tmp_path / "model")},
        headers=_headers(token),
    )
    assert artifact_response.status_code == 201, artifact_response.text

    voice_response = client.post(
        "/api/voices",
        json={
            "voiceKey": "qwen-job-demo",
            "displayName": "Qwen Job Demo",
            "gender": "female",
            "providers": [
                {
                    "provider": "qwen3_tts",
                    "providerVoiceId": "qwen3:qwen-job-demo",
                    "providerKind": "local_model",
                    "modelArtifactId": artifact_response.json()["id"],
                    "isDefault": True,
                }
            ],
        },
        headers=_headers(token),
    )
    assert voice_response.status_code == 201, voice_response.text

    create_response = client.post(
        "/api/tts/jobs",
        json={"content": "hello qwen job", "voiceId": "qwen-job-demo"},
        headers=_headers(token),
    )
    assert create_response.status_code == 202, create_response.text
    created = create_response.json()
    assert created["jobId"]
    assert created["status"] in {"queued", "preprocessing", "synthesizing", "writing", "completed"}
    assert 0 <= created["progress"] <= 100

    status_response = client.get(f"/api/tts/jobs/{created['jobId']}", headers=_headers(token))
    assert status_response.status_code == 200, status_response.text
    status_body = status_response.json()
    assert status_body["status"] == "completed"
    assert status_body["progress"] == 100
    assert status_body["stage"] == "配音生成完成"
    assert status_body["work"]["voiceName"] == "Qwen Job Demo"
    assert status_body["work"]["audioUrl"].endswith(".mp3")
    assert status_body["errorMessage"] is None

def test_system_qwen_vivian_voice_is_seeded_for_all_users():
    client = _make_client()

    response = client.get("/api/voices")
    assert response.status_code == 200, response.text
    voices = response.json()
    qwen_voice = next((voice for voice in voices if voice["voiceKey"] == "qwen-vivian"), None)
    assert qwen_voice is not None
    assert qwen_voice["ownerId"] is None
    assert qwen_voice["displayName"] == "Qwen Vivian"
    assert qwen_voice["providers"][0]["provider"] == "qwen3_tts"
    assert qwen_voice["providers"][0]["providerKind"] == "local_model"
    assert qwen_voice["providers"][0]["modelArtifactId"] is not None
def test_qwen_preset_import_creates_personal_voice_and_reuses_it():
    client = _make_client()
    token = _register(client)

    first_response = client.post(
        "/api/voices/qwen-presets/0-6b-customvoice/import",
        headers=_headers(token),
    )
    assert first_response.status_code == 201, first_response.text
    first_voice = first_response.json()
    assert first_voice["voiceKey"].startswith("qwen-0-6b-vivian-u")
    assert first_voice["displayName"] == "Qwen Vivian"
    assert first_voice["ownerId"] is not None
    assert first_voice["providers"][0]["provider"] == "qwen3_tts"
    assert first_voice["providers"][0]["providerKind"] == "local_model"
    assert first_voice["providers"][0]["modelArtifactId"] is not None
    assert first_voice["providers"][0]["runtimeConfigJson"] == (
        '{"speaker":"Vivian","language":"Auto","dtype":"float32","flash_attn":false,"local_files_only":true}'
    )

    second_response = client.post(
        "/api/voices/qwen-presets/0-6b-customvoice/import",
        headers=_headers(token),
    )
    assert second_response.status_code == 201, second_response.text
    assert second_response.json()["id"] == first_voice["id"]

    list_response = client.get("/api/voices", headers=_headers(token))
    assert list_response.status_code == 200, list_response.text
    assert any(voice["id"] == first_voice["id"] for voice in list_response.json())


def test_qwen_command_uses_project_runner_when_env_is_missing(monkeypatch, tmp_path):
    from app.services import qwen_tts

    python_path = tmp_path / ("python.exe" if sys.platform == "win32" else "python")
    runner_path = tmp_path / "qwen_custom_voice_runner.py"
    python_path.write_text("", encoding="utf-8")
    runner_path.write_text("", encoding="utf-8")

    monkeypatch.delenv("QWEN3_TTS_COMMAND", raising=False)
    monkeypatch.setattr(qwen_tts, "DEFAULT_QWEN_PYTHON_CANDIDATES", (python_path,))
    monkeypatch.setattr(qwen_tts, "DEFAULT_QWEN_RUNNER", runner_path)

    assert qwen_tts.resolve_qwen_command() == [str(python_path), str(runner_path)]


def test_qwen_command_prefers_gpu_venv_when_available(monkeypatch, tmp_path):
    from app.services import qwen_tts

    gpu_python = tmp_path / ".venv-gpu" / "Scripts" / "python.exe"
    cpu_python = tmp_path / ".venv" / "Scripts" / "python.exe"
    runner_path = tmp_path / "qwen_custom_voice_runner.py"
    gpu_python.parent.mkdir(parents=True)
    cpu_python.parent.mkdir(parents=True)
    gpu_python.write_text("", encoding="utf-8")
    cpu_python.write_text("", encoding="utf-8")
    runner_path.write_text("", encoding="utf-8")

    monkeypatch.delenv("QWEN3_TTS_COMMAND", raising=False)
    monkeypatch.setattr(qwen_tts, "DEFAULT_QWEN_PYTHON_CANDIDATES", (gpu_python, cpu_python))
    monkeypatch.setattr(qwen_tts, "DEFAULT_QWEN_RUNNER", runner_path)

    assert qwen_tts.resolve_qwen_command() == [str(gpu_python), str(runner_path)]


def test_qwen_command_resolves_relative_env_paths_from_project_root(monkeypatch, tmp_path):
    from app.services import qwen_tts

    python_path = tmp_path / ".venv" / "Scripts" / "python.exe"
    runner_path = tmp_path / "backend" / "scripts" / "qwen_custom_voice_runner.py"
    python_path.parent.mkdir(parents=True)
    runner_path.parent.mkdir(parents=True)
    python_path.write_text("", encoding="utf-8")
    runner_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(qwen_tts, "REPO_DIR", tmp_path)
    monkeypatch.setenv(
        "QWEN3_TTS_COMMAND",
        ".\\.venv\\Scripts\\python.exe backend\\scripts\\qwen_custom_voice_runner.py",
    )

    assert qwen_tts.resolve_qwen_command() == [str(python_path), str(runner_path)]


def test_qwen_runner_passes_local_files_only_to_model_loader():
    runner_path = Path(__file__).resolve().parents[1] / "scripts" / "qwen_custom_voice_runner.py"
    spec = importlib.util.spec_from_file_location("qwen_custom_voice_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(runner)

    kwargs = runner.build_model_kwargs(
        runtime={"flash_attn": False, "local_files_only": True},
        cache_dir=Path("cache"),
        device="cpu",
        dtype=object(),
    )

    assert kwargs["local_files_only"] is True


def test_qwen_runner_defaults_to_float32_dtype(monkeypatch):
    runner_path = Path(__file__).resolve().parents[1] / "scripts" / "qwen_custom_voice_runner.py"
    spec = importlib.util.spec_from_file_location("qwen_custom_voice_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(runner)

    monkeypatch.setattr(runner.torch.cuda, "is_available", lambda: True)
    runtime = {}
    dtype_name = str(runtime.get("dtype") or "float32").lower()
    dtype = {
        "bf16": runner.torch.bfloat16,
        "bfloat16": runner.torch.bfloat16,
        "fp16": runner.torch.float16,
        "float16": runner.torch.float16,
        "fp32": runner.torch.float32,
        "float32": runner.torch.float32,
    }.get(dtype_name, runner.torch.float32)

    assert dtype is runner.torch.float32


def test_qwen_preset_prefers_local_cached_snapshot(monkeypatch, tmp_path):
    from app import qwen_defaults

    cache_root = tmp_path / "models--Qwen--Qwen3-TTS-12Hz-0.6B-CustomVoice"
    first_snapshot = cache_root / "snapshots" / "111"
    second_snapshot = cache_root / "snapshots" / "222"
    first_snapshot.mkdir(parents=True)
    second_snapshot.mkdir(parents=True)

    monkeypatch.setattr(qwen_defaults, "QWEN_06B_CACHE_MODEL_DIR", cache_root)

    assert qwen_defaults.resolve_qwen_06b_artifact_path() == str(second_snapshot)
