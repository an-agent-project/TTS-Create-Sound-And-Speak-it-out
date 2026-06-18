import hashlib
import secrets
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_hex(16)
        h = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${h}", salt

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            salt, _ = password_hash.split("$", 1)
            hashed, _ = User.hash_password(password, salt)
            return hashed == password_hash
        except (ValueError, AttributeError):
            return False


class Voice(Base):
    __tablename__ = "voices"

    id = Column(Integer, primary_key=True, index=True)
    voice_key = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(50), nullable=False)
    gender = Column(String(20), nullable=False)
    style = Column(String(50))
    category = Column(String(100), index=True)
    description = Column(String(255))
    is_recommended = Column(Boolean, nullable=False, default=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
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
