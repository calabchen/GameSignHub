"""认证 API — 密码解锁 / 锁定 / 修改密码."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.auth import create_access_token
from app.core.vault import Vault, VaultLockedError
from app.schemas.auth import (
    LockResponse,
    StatusResponse,
    UnlockRequest,
    UnlockResponse,
)

router = APIRouter(prefix="/api", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=1, max_length=128)


@router.post("/unlock", response_model=UnlockResponse)
async def unlock(request: Request, body: UnlockRequest):
    """密码解锁保险库，返回 JWT."""
    vault: Vault = request.app.state.vault

    success, is_first_time = await vault.unlock(body.password)
    if not success:
        raise HTTPException(status_code=401, detail="密码错误")

    token = create_access_token(vault.session_id)
    request.app.state.is_unlocked = True

    return UnlockResponse(token=token, is_first_time=is_first_time)


@router.post("/lock", response_model=LockResponse)
async def lock(request: Request):
    """锁定保险库，销毁解密密钥."""
    vault: Vault = request.app.state.vault

    if not vault.is_unlocked:
        raise HTTPException(status_code=400, detail="保险库已处于锁定状态")

    vault.lock()
    request.app.state.is_unlocked = False

    return LockResponse(message="已锁定")


@router.put("/unlock/password")
async def change_password(request: Request, body: ChangePasswordRequest):
    """修改解锁密码."""
    vault: Vault = request.app.state.vault

    if not vault.is_unlocked:
        raise HTTPException(status_code=403, detail="请先解锁")

    success = await vault.change_password(body.old_password, body.new_password)
    if not success:
        raise HTTPException(status_code=401, detail="旧密码错误")

    return {"message": "密码已修改"}


@router.get("/status", response_model=StatusResponse)
async def status(request: Request):
    """获取当前系统状态."""
    vault: Vault = request.app.state.vault

    return StatusResponse(
        is_unlocked=vault.is_unlocked,
        is_password_set=await vault.is_password_set(),
        plugins_loaded=len(request.app.state.plugin_registry),
    )
