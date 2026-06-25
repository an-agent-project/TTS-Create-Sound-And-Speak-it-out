from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models
from app.services.bailian_tts import BAILIAN_TTS_PROVIDER

LEGACY_LOCAL_QWEN_PROVIDERS = {"qwen_tts", "qwen3_tts"}
BAILIAN_TTS_MODEL = "qwen3-tts-flash"


@dataclass(frozen=True)
class BailianPresetVoice:
    key: str
    voice: str
    display_name: str
    gender: str
    style: str
    category: str
    description: str

    @property
    def provider_voice_id(self) -> str:
        return f"bailian:{BAILIAN_TTS_MODEL}:{self.voice}"


BAILIAN_PRESET_VOICES = [
    BailianPresetVoice("cherry", "Cherry", "芊悦", "female", "阳光", "知识类", "阳光积极、亲切自然的百炼 Qwen-TTS 女声。"),
    BailianPresetVoice("serena", "Serena", "苏瑶", "female", "温柔", "情感类", "温柔细腻的百炼 Qwen-TTS 女声。"),
    BailianPresetVoice("ethan", "Ethan", "晨煦", "male", "温暖", "播客类", "阳光温暖的百炼 Qwen-TTS 男声。"),
    BailianPresetVoice("chelsie", "Chelsie", "千雪", "female", "二次元", "故事类", "二次元风格的百炼 Qwen-TTS 女性音色。"),
    BailianPresetVoice("moon", "Moon", "月白", "male", "率性", "播客类", "率性帅气的百炼 Qwen-TTS 男声。"),
    BailianPresetVoice("maia", "Maia", "四月", "female", "知性", "知识类", "知性温柔的百炼 Qwen-TTS 女声。"),
    BailianPresetVoice("kai", "Kai", "凯", "male", "低沉", "故事类", "低沉舒适的百炼 Qwen-TTS 男声。"),
    BailianPresetVoice("neil", "Neil", "阿闻", "male", "新闻", "知识类", "新闻主持风格的百炼 Qwen-TTS 男声。"),
]


def deactivate_legacy_local_qwen_voices(db: Session) -> int:
    legacy_providers = (
        db.query(models.VoiceProviderProfile)
        .join(models.Voice)
        .filter(
            models.VoiceProviderProfile.provider.in_(LEGACY_LOCAL_QWEN_PROVIDERS),
            models.VoiceProviderProfile.is_active.is_(True),
        )
        .all()
    )
    changed_voice_ids: set[int] = set()
    for provider in legacy_providers:
        provider.is_active = False
        if provider.voice and provider.voice.is_active:
            provider.voice.is_active = False
        if provider.voice:
            changed_voice_ids.add(provider.voice.id)

    if legacy_providers:
        db.commit()
    return len(changed_voice_ids)


def seed_bailian_default_voice(db: Session) -> models.Voice:
    deactivate_legacy_local_qwen_voices(db)
    first_voice: models.Voice | None = None
    for preset in BAILIAN_PRESET_VOICES:
        voice = _upsert_preset_voice(db, preset)
        if first_voice is None:
            first_voice = voice
    db.commit()
    db.refresh(first_voice)
    return first_voice


def _upsert_preset_voice(db: Session, preset: BailianPresetVoice) -> models.Voice:
    voice_key = f"bailian-qwen-{preset.key}"
    voice = db.query(models.Voice).filter(models.Voice.voice_key == voice_key).first()
    if voice is None:
        voice = models.Voice(
            voice_key=voice_key,
            display_name=preset.display_name,
            gender=preset.gender,
        )
        db.add(voice)
        db.flush()

    voice.display_name = preset.display_name
    voice.gender = preset.gender
    voice.style = preset.style
    voice.category = preset.category
    voice.description = preset.description
    voice.is_recommended = preset.key in {"cherry", "serena", "ethan", "maia"}
    voice.is_active = True
    voice.owner_id = None

    provider = (
        db.query(models.VoiceProviderProfile)
        .filter(
            models.VoiceProviderProfile.provider == BAILIAN_TTS_PROVIDER,
            models.VoiceProviderProfile.provider_voice_id == preset.provider_voice_id,
        )
        .first()
    )
    if provider is None:
        provider = models.VoiceProviderProfile(
            provider=BAILIAN_TTS_PROVIDER,
            provider_voice_id=preset.provider_voice_id,
        )
        db.add(provider)

    provider.voice_id = voice.id
    provider.locale = "zh-CN"
    provider.supports_wav = False
    provider.supports_mp3 = True
    provider.is_default = True
    provider.is_active = True
    return voice