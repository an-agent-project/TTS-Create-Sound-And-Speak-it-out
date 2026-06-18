from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# ── Auth schemas ──────────────────────────────────────────────


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=4)
    email: str | None = Field(default=None, max_length=120)


class UserRead(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    avatar: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# ── Voice schemas ──────────────────────────────────────────────


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class VoiceProviderProfileBase(CamelModel):
    provider: str = Field(..., min_length=1, max_length=50)
    provider_voice_id: str = Field(..., alias="providerVoiceId", min_length=1, max_length=120)
    locale: str | None = Field(default=None, max_length=20)
    supports_wav: bool = Field(default=False, alias="supportsWav")
    supports_mp3: bool = Field(default=True, alias="supportsMp3")
    is_default: bool = Field(default=False, alias="isDefault")


class VoiceProviderProfileCreate(VoiceProviderProfileBase):
    pass


class VoiceProviderProfileRead(VoiceProviderProfileBase):
    id: int
    is_active: bool = Field(alias="isActive")


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
