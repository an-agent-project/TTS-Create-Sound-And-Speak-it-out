from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    material_assets = relationship("UserMaterialAsset", back_populates="owner")
    training_jobs = relationship("VoiceTrainingJob", back_populates="owner")
    model_artifacts = relationship("VoiceModelArtifact", back_populates="owner")


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
    provider_kind = Column(String(50), nullable=False, default="external_tts")
    model_artifact_id = Column(Integer, ForeignKey("voice_model_artifacts.id"), nullable=True, index=True)
    runtime_config_json = Column(Text)
    locale = Column(String(20))
    supports_wav = Column(Boolean, nullable=False, default=False)
    supports_mp3 = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    voice = relationship("Voice", back_populates="providers")
    model_artifact = relationship("VoiceModelArtifact", back_populates="provider_profiles")
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


class UserMaterialAsset(Base):
    __tablename__ = "user_material_assets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    asset_type = Column(String(50), nullable=False, default="audio_dataset")
    source_format = Column(String(20), nullable=False, default="audio")
    original_filename = Column(String(255))
    storage_path = Column(String(500))
    status = Column(String(30), nullable=False, default="ready", index=True)
    metadata_json = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="material_assets")
    items = relationship(
        "UserMaterialItem",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
    training_jobs = relationship("VoiceTrainingJob", back_populates="material_asset")


class UserMaterialItem(Base):
    __tablename__ = "user_material_items"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("user_material_assets.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False, default="audio")
    storage_path = Column(String(500), nullable=False)
    transcript = Column(Text)
    duration_seconds = Column(Numeric(8, 2))
    file_size_bytes = Column(Integer)
    status = Column(String(30), nullable=False, default="ready", index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    asset = relationship("UserMaterialAsset", back_populates="items")


class VoiceTrainingJob(Base):
    __tablename__ = "voice_training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_asset_id = Column(Integer, ForeignKey("user_material_assets.id"), nullable=True, index=True)
    result_model_artifact_id = Column(Integer, ForeignKey("voice_model_artifacts.id"), nullable=True, index=True)
    job_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False, default="qwen3_tts")
    base_model = Column(String(120), nullable=False, default="qwen3-tts-1.7b")
    status = Column(String(30), nullable=False, default="queued", index=True)
    config_json = Column(Text)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="training_jobs")
    material_asset = relationship("UserMaterialAsset", back_populates="training_jobs")
    result_model_artifact = relationship(
        "VoiceModelArtifact",
        foreign_keys=[result_model_artifact_id],
        post_update=True,
    )


class VoiceModelArtifact(Base):
    __tablename__ = "voice_model_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    training_job_id = Column(Integer, ForeignKey("voice_training_jobs.id"), nullable=True, index=True)
    display_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False, default="qwen3_tts", index=True)
    model_version = Column(String(120))
    artifact_path = Column(String(500), nullable=False)
    config_path = Column(String(500))
    tokenizer_path = Column(String(500))
    runtime_config_json = Column(Text)
    status = Column(String(30), nullable=False, default="ready", index=True)
    file_size_bytes = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="model_artifacts")
    training_job = relationship("VoiceTrainingJob", foreign_keys=[training_job_id])
    provider_profiles = relationship("VoiceProviderProfile", back_populates="model_artifact")
