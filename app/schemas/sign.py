"""签到请求/响应 schemas."""

from pydantic import BaseModel, Field


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


class SignInStatus(BaseModel):
    is_running: bool = False
    total: int = 0
    completed: int = 0
