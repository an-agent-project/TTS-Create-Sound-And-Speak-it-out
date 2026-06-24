import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().lower()
    if not value:
        return None
    if not EMAIL_RE.match(value):
        raise ValueError("email format is invalid")
    return value


# ---------- TTS ----------

class TtsPreviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    voice_id: str = Field(..., alias="voiceId", min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value.strip()


class TtsPreviewResponse(BaseModel):
    audio_url: str = Field(..., alias="audioUrl")
    duration: int


# ---------- Voice Provider ----------

class VoiceProviderProfileBase(CamelModel):
    provider: str = Field(..., min_length=1, max_length=50)
    provider_voice_id: str = Field(..., alias="providerVoiceId", min_length=1, max_length=120)
    provider_kind: str = Field(default="external_tts", alias="providerKind", min_length=1, max_length=50)
    model_artifact_id: int | None = Field(default=None, alias="modelArtifactId")
    runtime_config_json: str | None = Field(default=None, alias="runtimeConfigJson")
    locale: str | None = Field(default=None, max_length=20)
    supports_wav: bool = Field(default=False, alias="supportsWav")
    supports_mp3: bool = Field(default=True, alias="supportsMp3")
    is_default: bool = Field(default=False, alias="isDefault")


class VoiceProviderProfileCreate(VoiceProviderProfileBase):
    pass


class VoiceProviderProfileRead(VoiceProviderProfileBase):
    id: int
    is_active: bool = Field(alias="isActive")


# ---------- Voice ----------

class VoiceBase(CamelModel):
    voice_key: str = Field(..., alias="voiceKey", min_length=1, max_length=100)
    display_name: str = Field(..., alias="displayName", min_length=1, max_length=50)
    gender: str = Field(..., min_length=1, max_length=20)
    style: str | None = Field(default=None, max_length=50)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_recommended: bool = Field(default=False, alias="isRecommended")


class VoiceCreate(VoiceBase):
    providers: list[VoiceProviderProfileCreate] = Field(default_factory=list)


class VoiceUpdate(CamelModel):
    display_name: str | None = Field(default=None, alias="displayName", min_length=1, max_length=50)
    gender: str | None = Field(default=None, min_length=1, max_length=20)
    style: str | None = Field(default=None, max_length=50)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_recommended: bool | None = Field(default=None, alias="isRecommended")
    voice_key: str | None = Field(default=None, alias="voiceKey", min_length=1, max_length=100)
    providers: list[VoiceProviderProfileCreate] | None = None


class VoiceRead(VoiceBase):
    id: int
    is_active: bool = Field(alias="isActive")
    owner_id: int | None = Field(default=None, alias="ownerId")
    providers: list[VoiceProviderProfileRead] = Field(default_factory=list)


# ---------- Auth ----------

class SendCodeRequest(CamelModel):
    email: str = Field(..., min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        return normalize_email(value) or ""


class SendCodeResponse(CamelModel):
    message: str = "verification code sent"
    code: str = ""


class LoginRequest(CamelModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return normalize_email(value)

    @model_validator(mode="after")
    def require_identifier(self) -> "LoginRequest":
        if not self.username and not self.email:
            raise ValueError("username or email is required")
        return self


class RegisterRequest(CamelModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    code: str | None = Field(default=None, min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return normalize_email(value)

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str | None) -> str | None:
        if value is not None and not value.isdigit():
            raise ValueError("verification code must be 6 digits")
        return value


class UserRead(CamelModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    is_active: bool = True
    created_at: datetime | None = None


class UserUpdate(CamelModel):
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    avatar: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return normalize_email(value)


class ChangePasswordRequest(CamelModel):
    old_password: str = Field(..., alias="oldPassword", min_length=1)
    new_password: str = Field(..., alias="newPassword", min_length=4, max_length=128)


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


AuthResponse = TokenResponse


# ---------- Material Library ----------

class UserMaterialItemBase(CamelModel):
    filename: str = Field(..., min_length=1, max_length=255)
    media_type: str = Field(default="audio", alias="mediaType", min_length=1, max_length=50)
    storage_path: str = Field(..., alias="storagePath", min_length=1, max_length=500)
    transcript: str | None = None
    duration_seconds: float | None = Field(default=None, alias="durationSeconds")
    file_size_bytes: int | None = Field(default=None, alias="fileSizeBytes")
    status: str = Field(default="ready", min_length=1, max_length=30)


class UserMaterialItemCreate(UserMaterialItemBase):
    pass


class UserMaterialItemUpdate(CamelModel):
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    media_type: str | None = Field(default=None, alias="mediaType", min_length=1, max_length=50)
    storage_path: str | None = Field(default=None, alias="storagePath", min_length=1, max_length=500)
    transcript: str | None = None
    duration_seconds: float | None = Field(default=None, alias="durationSeconds")
    file_size_bytes: int | None = Field(default=None, alias="fileSizeBytes")
    status: str | None = Field(default=None, min_length=1, max_length=30)


class UserMaterialItemRead(UserMaterialItemBase):
    id: int
    asset_id: int = Field(alias="assetId")
    created_at: datetime | None = Field(default=None, alias="createdAt")


class UserMaterialAssetBase(CamelModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    asset_type: str = Field(default="audio_dataset", alias="assetType", min_length=1, max_length=50)
    source_format: str = Field(default="audio", alias="sourceFormat", min_length=1, max_length=20)
    original_filename: str | None = Field(default=None, alias="originalFilename", max_length=255)
    storage_path: str | None = Field(default=None, alias="storagePath", max_length=500)
    status: str = Field(default="ready", min_length=1, max_length=30)
    metadata_json: str | None = Field(default=None, alias="metadataJson")


class UserMaterialAssetCreate(UserMaterialAssetBase):
    items: list[UserMaterialItemCreate] = Field(default_factory=list)


class UserMaterialAssetUpdate(CamelModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    asset_type: str | None = Field(default=None, alias="assetType", min_length=1, max_length=50)
    source_format: str | None = Field(default=None, alias="sourceFormat", min_length=1, max_length=20)
    original_filename: str | None = Field(default=None, alias="originalFilename", max_length=255)
    storage_path: str | None = Field(default=None, alias="storagePath", max_length=500)
    status: str | None = Field(default=None, min_length=1, max_length=30)
    metadata_json: str | None = Field(default=None, alias="metadataJson")
    items: list[UserMaterialItemCreate] | None = None


class UserMaterialAssetRead(UserMaterialAssetBase):
    id: int
    owner_id: int = Field(alias="ownerId")
    is_active: bool = Field(alias="isActive")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    items: list[UserMaterialItemRead] = Field(default_factory=list)


# ---------- Voice Training Jobs ----------

class VoiceTrainingJobBase(CamelModel):
    job_name: str = Field(..., alias="jobName", min_length=1, max_length=100)
    material_asset_id: int | None = Field(default=None, alias="materialAssetId")
    provider: str = Field(default="qwen3_tts", min_length=1, max_length=50)
    base_model: str = Field(default="qwen3-tts-1.7b", alias="baseModel", min_length=1, max_length=120)
    status: str = Field(default="queued", min_length=1, max_length=30)
    config_json: str | None = Field(default=None, alias="configJson")
    error_message: str | None = Field(default=None, alias="errorMessage")
    result_model_artifact_id: int | None = Field(default=None, alias="resultModelArtifactId")


class VoiceTrainingJobCreate(VoiceTrainingJobBase):
    pass


class VoiceTrainingJobUpdate(CamelModel):
    job_name: str | None = Field(default=None, alias="jobName", min_length=1, max_length=100)
    material_asset_id: int | None = Field(default=None, alias="materialAssetId")
    provider: str | None = Field(default=None, min_length=1, max_length=50)
    base_model: str | None = Field(default=None, alias="baseModel", min_length=1, max_length=120)
    status: str | None = Field(default=None, min_length=1, max_length=30)
    config_json: str | None = Field(default=None, alias="configJson")
    error_message: str | None = Field(default=None, alias="errorMessage")
    result_model_artifact_id: int | None = Field(default=None, alias="resultModelArtifactId")


class VoiceTrainingJobRead(VoiceTrainingJobBase):
    id: int
    owner_id: int = Field(alias="ownerId")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


# ---------- Voice Model Artifacts ----------

class VoiceModelArtifactBase(CamelModel):
    display_name: str = Field(..., alias="displayName", min_length=1, max_length=100)
    provider: str = Field(default="qwen3_tts", min_length=1, max_length=50)
    model_version: str | None = Field(default=None, alias="modelVersion", max_length=120)
    artifact_path: str = Field(..., alias="artifactPath", min_length=1, max_length=500)
    config_path: str | None = Field(default=None, alias="configPath", max_length=500)
    tokenizer_path: str | None = Field(default=None, alias="tokenizerPath", max_length=500)
    runtime_config_json: str | None = Field(default=None, alias="runtimeConfigJson")
    status: str = Field(default="ready", min_length=1, max_length=30)
    file_size_bytes: int | None = Field(default=None, alias="fileSizeBytes")
    training_job_id: int | None = Field(default=None, alias="trainingJobId")


class VoiceModelArtifactCreate(VoiceModelArtifactBase):
    pass


class VoiceModelArtifactUpdate(CamelModel):
    display_name: str | None = Field(default=None, alias="displayName", min_length=1, max_length=100)
    provider: str | None = Field(default=None, min_length=1, max_length=50)
    model_version: str | None = Field(default=None, alias="modelVersion", max_length=120)
    artifact_path: str | None = Field(default=None, alias="artifactPath", min_length=1, max_length=500)
    config_path: str | None = Field(default=None, alias="configPath", max_length=500)
    tokenizer_path: str | None = Field(default=None, alias="tokenizerPath", max_length=500)
    runtime_config_json: str | None = Field(default=None, alias="runtimeConfigJson")
    status: str | None = Field(default=None, min_length=1, max_length=30)
    file_size_bytes: int | None = Field(default=None, alias="fileSizeBytes")
    training_job_id: int | None = Field(default=None, alias="trainingJobId")


class VoiceModelArtifactRead(VoiceModelArtifactBase):
    id: int
    owner_id: int | None = Field(default=None, alias="ownerId")
    is_active: bool = Field(alias="isActive")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
