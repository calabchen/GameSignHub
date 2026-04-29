"""日志查询 schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


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


class TodaySummary(BaseModel):
    total: int = 0
    success: int = 0
    already: int = 0
    failed: int = 0
