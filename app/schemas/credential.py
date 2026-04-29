"""凭据管理 Pydantic schemas."""

from pydantic import BaseModel, Field


class CredentialCreate(BaseModel):
    plugin_id: str = Field(..., description="插件标识，如 kuro")
    display_name: str = Field(default="", description="用户备注名")
    credentials: dict = Field(default_factory=dict, description="凭据内容 (token, cookie 等)")
    enabled_games: list[str] = Field(default_factory=list, description="启用的游戏列表")
    is_enabled: bool = Field(default=True, description="总开关")


class CredentialUpdate(BaseModel):
    display_name: str | None = None
    credentials: dict | None = None
    enabled_games: list[str] | None = None
    is_enabled: bool | None = None


class CredentialSummary(BaseModel):
    id: int
    plugin_id: str
    display_name: str
    enabled_games: list[str]
    is_enabled: bool


class ValidateResult(BaseModel):
    valid: bool
    message: str
