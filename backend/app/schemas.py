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


class VoiceRead(VoiceBase):
    id: int
    is_active: bool = Field(alias="isActive")
    providers: list[VoiceProviderProfileRead] = Field(default_factory=list)
