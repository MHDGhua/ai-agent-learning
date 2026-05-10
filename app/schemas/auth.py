import re

from pydantic import BaseModel, Field, field_validator


def _validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("密码至少需要 8 位。")
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("密码必须同时包含字母和数字。")
    return value


class RegisterRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=80)
    role: str = Field(default="案件申请人", min_length=1, max_length=40)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=80)
    role: str = Field(default="案件申请人", min_length=1, max_length=40)


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: str
    updated_at: str


class AuthResponse(BaseModel):
    user: UserResponse


class SessionResponse(BaseModel):
    user: UserResponse | None = None
