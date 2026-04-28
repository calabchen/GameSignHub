"""认证相关 Pydantic schemas."""

from pydantic import BaseModel, Field


class UnlockRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)


class UnlockResponse(BaseModel):
    token: str
    is_first_time: bool


class LockResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    is_unlocked: bool
    is_password_set: bool
    plugins_loaded: int
