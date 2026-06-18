import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator


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


# ---------- Camel base ----------

class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------- Voice Provider ----------

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


class VoiceRead(VoiceBase):
    id: int
    is_active: bool = Field(alias="isActive")
    providers: list[VoiceProviderProfileRead] = Field(default_factory=list)


# ---------- Auth ----------

class SendCodeRequest(CamelModel):
    email: str = Field(..., min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("邮箱格式不正确")
        return value


class SendCodeResponse(CamelModel):
    message: str = "验证码已发送"
    # 开发阶段返回验证码（生产环境应删除此字段）
    code: str = ""


class RegisterRequest(CamelModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)
    code: str = Field(..., min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("验证码必须是6位数字")
        return value


class LoginRequest(CamelModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("邮箱格式不正确")
        return value


class UserRead(CamelModel):
    id: int
    email: str
    username: str
    isActive: bool = True
    createdAt: str = ""


class AuthResponse(CamelModel):
    success: bool
    message: str = ""
    user: UserRead | None = None
