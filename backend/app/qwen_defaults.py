from pathlib import Path

from sqlalchemy.orm import Session

from app import models

QWEN_06B_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
QWEN_06B_MODEL_VERSION = "qwen3-tts-0.6b-customvoice"
QWEN_06B_RUNTIME_CONFIG = '{"speaker":"Vivian","language":"Auto","dtype":"float32","flash_attn":false,"local_files_only":true}'
QWEN_VIVIAN_VOICE_KEY = "qwen-vivian"
QWEN_VIVIAN_PROVIDER_VOICE_ID = "qwen3:qwen-vivian"
REPO_DIR = Path(__file__).resolve().parents[2]
QWEN_06B_CACHE_MODEL_DIR = REPO_DIR / ".hf-cache" / "qwen-tts" / "models--Qwen--Qwen3-TTS-12Hz-0.6B-CustomVoice"


def resolve_qwen_06b_artifact_path() -> str:
    snapshots_dir = QWEN_06B_CACHE_MODEL_DIR / "snapshots"
    if snapshots_dir.exists():
        snapshots = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
        if snapshots:
            return str(snapshots[-1])
    return QWEN_06B_MODEL_ID


def seed_system_qwen_vivian(db: Session, artifact_path: str | None = None) -> models.Voice:
    resolved_artifact_path = artifact_path or resolve_qwen_06b_artifact_path()
    artifact = (
        db.query(models.VoiceModelArtifact)
        .filter(
            models.VoiceModelArtifact.owner_id.is_(None),
            models.VoiceModelArtifact.provider == "qwen3_tts",
            models.VoiceModelArtifact.model_version == QWEN_06B_MODEL_VERSION,
            models.VoiceModelArtifact.is_active.is_(True),
        )
        .first()
    )
    if artifact is None:
        artifact = models.VoiceModelArtifact(
            owner_id=None,
            display_name="Qwen 0.6B CustomVoice",
            provider="qwen3_tts",
            model_version=QWEN_06B_MODEL_VERSION,
            artifact_path=resolved_artifact_path,
            runtime_config_json=QWEN_06B_RUNTIME_CONFIG,
            status="ready",
            is_active=True,
        )
        db.add(artifact)
        db.flush()
    else:
        artifact.artifact_path = resolved_artifact_path
        artifact.runtime_config_json = QWEN_06B_RUNTIME_CONFIG
        artifact.status = "ready"
        artifact.is_active = True

    voice = db.query(models.Voice).filter(models.Voice.voice_key == QWEN_VIVIAN_VOICE_KEY).first()
    if voice is None:
        voice = models.Voice(
            voice_key=QWEN_VIVIAN_VOICE_KEY,
            display_name="Qwen Vivian",
            gender="female",
            style="custom",
            category="system",
            description="Qwen3-TTS 0.6B CustomVoice preset voice",
            is_recommended=True,
            is_active=True,
            owner_id=None,
        )
        db.add(voice)
        db.flush()
    else:
        voice.display_name = "Qwen Vivian"
        voice.gender = "female"
        voice.style = "custom"
        voice.category = "system"
        voice.description = "Qwen3-TTS 0.6B CustomVoice preset voice"
        voice.is_recommended = True
        voice.is_active = True
        voice.owner_id = None

    provider = (
        db.query(models.VoiceProviderProfile)
        .filter(models.VoiceProviderProfile.provider_voice_id == QWEN_VIVIAN_PROVIDER_VOICE_ID)
        .first()
    )
    if provider is None:
        provider = models.VoiceProviderProfile(
            voice_id=voice.id,
            provider="qwen3_tts",
            provider_voice_id=QWEN_VIVIAN_PROVIDER_VOICE_ID,
            provider_kind="local_model",
            model_artifact_id=artifact.id,
            runtime_config_json=QWEN_06B_RUNTIME_CONFIG,
            supports_wav=True,
            supports_mp3=True,
            is_default=True,
            is_active=True,
        )
        db.add(provider)
    else:
        provider.voice_id = voice.id
        provider.provider = "qwen3_tts"
        provider.provider_kind = "local_model"
        provider.model_artifact_id = artifact.id
        provider.runtime_config_json = QWEN_06B_RUNTIME_CONFIG
        provider.supports_wav = True
        provider.supports_mp3 = True
        provider.is_default = True
        provider.is_active = True

    db.commit()
    db.refresh(voice)
    return voice
