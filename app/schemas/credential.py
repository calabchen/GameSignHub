"""凭据管理 Pydantic schemas."""

from pydantic import BaseModel, Field


class CredentialSummary(BaseModel):
    id: int
    plugin_id: str
    user_id: str = ""
    is_enabled: bool
    wuwa_role_id: str = ""
    pgr_role_id: str = ""


class CredentialScheduleUpdate(BaseModel):
    cron: str = Field(default="", description="cron 表达式")
    enabled: bool = Field(default=False)


class ValidateResult(BaseModel):
    valid: bool
    message: str
