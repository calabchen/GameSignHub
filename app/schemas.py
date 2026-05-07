"""Pydantic request/response models."""

from pydantic import BaseModel, Field


# ── Auth ──────────────────────────────────────────────

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


# ── Game Account ───────────────────────────────────────

class GameAccountSummary(BaseModel):
    id: int
    plugin_id: str
    user_id: str = ""
    is_enabled: bool
    wuwa_role_id: str = ""
    pgr_role_id: str = ""


class GameAccountScheduleUpdate(BaseModel):
    cron: str = Field(default="", description="cron 表达式")
    enabled: bool = Field(default=False)


class ValidateResult(BaseModel):
    valid: bool
    message: str


# ── Log ────────────────────────────────────────────────

class SignLogEntry(BaseModel):
    id: int
    credential_id: int | None
    credential_name: str
    plugin_id: str
    game_id: str
    status: str
    reward: str
    message: str
    elapsed: float = 0.0
    signed_at: str
    created_at: str


class SignLogPage(BaseModel):
    items: list[SignLogEntry]
    total: int
    page: int
    page_size: int


# ── Sign ───────────────────────────────────────────────

class SignInResult(BaseModel):
    game_id: str
    status: str
    reward: str
    message: str


class SignInResponse(BaseModel):
    results: dict[str, list[SignInResult]] = Field(
        default_factory=dict,
        description="{game_id: [SignInResult, ...]}"
    )
