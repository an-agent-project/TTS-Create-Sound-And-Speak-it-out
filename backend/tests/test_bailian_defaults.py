from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.bailian_defaults import deactivate_legacy_local_qwen_voices, seed_bailian_default_voice
from app.models import Base, Voice, VoiceProviderProfile


def _make_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def test_deactivate_legacy_local_qwen_voices():
    db = _make_session()
    legacy = Voice(
        voice_key="qwen-vivian",
        display_name="Qwen Vivian",
        gender="female",
        is_active=True,
    )
    legacy.providers.append(
        VoiceProviderProfile(
            provider="qwen3_tts",
            provider_voice_id="qwen3:qwen-vivian",
            locale="zh-CN",
            is_active=True,
        )
    )
    db.add(legacy)
    db.commit()

    changed = deactivate_legacy_local_qwen_voices(db)

    db.refresh(legacy)
    assert changed == 1
    assert legacy.is_active is False
    assert legacy.providers[0].is_active is False


def test_seed_bailian_default_voice_deactivates_legacy_qwen():
    db = _make_session()
    legacy = Voice(
        voice_key="qwen-0-6b-vivian-u10",
        display_name="Qwen Vivian",
        gender="female",
        is_active=True,
    )
    legacy.providers.append(
        VoiceProviderProfile(
            provider="qwen3_tts",
            provider_voice_id="qwen3:qwen-0-6b-vivian-u10",
            locale="zh-CN",
            is_active=True,
        )
    )
    db.add(legacy)
    db.commit()

    seed_bailian_default_voice(db)

    db.refresh(legacy)
    bailian = db.query(Voice).filter(Voice.voice_key == "bailian-qwen-cherry").one()
    assert legacy.is_active is False
    assert legacy.providers[0].is_active is False
    assert bailian.is_active is True
    assert bailian.providers[0].provider == "bailian_tts"

def test_seed_bailian_default_voice_creates_multiple_presets():
    db = _make_session()

    seed_bailian_default_voice(db)

    voices = db.query(Voice).filter(Voice.voice_key.like("bailian-qwen-%")).all()
    voice_keys = {voice.voice_key for voice in voices}
    assert {
        "bailian-qwen-cherry",
        "bailian-qwen-serena",
        "bailian-qwen-ethan",
        "bailian-qwen-chelsie",
        "bailian-qwen-moon",
        "bailian-qwen-maia",
        "bailian-qwen-kai",
        "bailian-qwen-neil",
    }.issubset(voice_keys)
    providers = {
        provider.provider_voice_id
        for voice in voices
        for provider in voice.providers
        if provider.provider == "bailian_tts"
    }
    assert "bailian:qwen3-tts-flash:Serena" in providers
    assert "bailian:qwen3-tts-flash:Neil" in providers
