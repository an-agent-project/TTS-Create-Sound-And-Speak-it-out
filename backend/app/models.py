from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120))
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Voice(Base):
    __tablename__ = "voices"

    id = Column(Integer, primary_key=True, index=True)
    voice_key = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(50), nullable=False)
    gender = Column(String(20), nullable=False)
    style = Column(String(50))
    category = Column(String(50), index=True)
    description = Column(String(255))
    is_recommended = Column(Boolean, nullable=False, default=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    providers = relationship(
        "VoiceProviderProfile",
        back_populates="voice",
        cascade="all, delete-orphan",
    )


class VoiceProviderProfile(Base):
    __tablename__ = "voice_provider_profiles"

    id = Column(Integer, primary_key=True, index=True)
    voice_id = Column(Integer, ForeignKey("voices.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    provider_voice_id = Column(String(120), nullable=False, unique=True)
    locale = Column(String(20))
    supports_wav = Column(Boolean, nullable=False, default=False)
    supports_mp3 = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    voice = relationship("Voice", back_populates="providers")
    preview_audios = relationship("VoicePreviewAudio", back_populates="provider_profile")


class VoicePreviewAudio(Base):
    __tablename__ = "voice_preview_audios"

    id = Column(Integer, primary_key=True, index=True)
    voice_provider_profile_id = Column(
        Integer,
        ForeignKey("voice_provider_profiles.id"),
        nullable=False,
        index=True,
    )
    sample_text_hash = Column(String(64), nullable=False)
    sample_text = Column(String(1000), nullable=False)
    format = Column(String(10), nullable=False, default="mp3")
    audio_path = Column(String(500), nullable=False)
    audio_url = Column(String(500))
    duration_seconds = Column(Numeric(8, 2))
    file_size_bytes = Column(Integer)
    status = Column(String(20), nullable=False, default="ready", index=True)
    error_message = Column(Text)
    generated_at = Column(DateTime, nullable=False, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    provider_profile = relationship("VoiceProviderProfile", back_populates="preview_audios")
