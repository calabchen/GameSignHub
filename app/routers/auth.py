"""认证 API：密码解锁、锁定与改密。"""

import yaml
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.config import get_project_root
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas import LockResponse, StatusResponse, UnlockRequest, UnlockResponse

router = APIRouter(prefix="/api", tags=["auth"])

SETTINGS_PATH = get_project_root() / "app" / "config" / "settings.yaml"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=1, max_length=128)


def _read_settings() -> dict:
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _write_password_hash(hash_val: str) -> None:
    data = _read_settings()
    data["password_hash"] = hash_val
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def _is_password_set() -> bool:
    return bool(_read_settings().get("password_hash"))


@router.post("/unlock", response_model=UnlockResponse)
async def unlock(request: Request, body: UnlockRequest):
    settings = _read_settings()
    password_hash = settings.get("password_hash")

    if not password_hash:
        password_hash = hash_password(body.password)
        _write_password_hash(password_hash)
        is_first = True
    else:
        if not verify_password(body.password, password_hash):
            raise HTTPException(status_code=401, detail="密码错误")
        is_first = False

    token = create_access_token()
    request.app.state.is_unlocked = True

    return UnlockResponse(token=token, is_first_time=is_first)


@router.post("/lock", response_model=LockResponse)
async def lock(request: Request):
    request.app.state.is_unlocked = False
    return LockResponse(message="已锁定")


@router.put("/unlock/password")
async def change_password(request: Request, body: ChangePasswordRequest):
    settings = _read_settings()
    current_hash = settings.get("password_hash", "")

    if not verify_password(body.old_password, current_hash):
        raise HTTPException(status_code=401, detail="旧密码错误")

    _write_password_hash(hash_password(body.new_password))
    return {"message": "密码已修改"}


@router.get("/status", response_model=StatusResponse)
async def status(request: Request):
    return StatusResponse(
        is_unlocked=request.app.state.is_unlocked,
        is_password_set=_is_password_set(),
        plugins_loaded=len(request.app.state.plugin_registry),
    )
