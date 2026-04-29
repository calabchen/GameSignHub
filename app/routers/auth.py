"""认证 API：密码解锁、锁定与改密。"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.auth import create_access_token
from app.core.vault import Vault
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
    """解锁屏保，使用有效密码并返回访问令牌。"""
    vault: Vault = request.app.state.vault

    success, is_first_time = await vault.unlock(body.password)
    if not success:
        raise HTTPException(status_code=401, detail="密码错误")

    token = create_access_token(vault.session_id)
    request.app.state.is_unlocked = True

    return UnlockResponse(token=token, is_first_time=is_first_time)


@router.post("/lock", response_model=LockResponse)
async def lock(request: Request):
    """锁定屏保，在当前处于解锁状态时清除会话密钥。"""
    vault: Vault = request.app.state.vault

    if not vault.is_unlocked:
        raise HTTPException(status_code=400, detail="屏保已处于锁定状态")

    vault.lock()
    request.app.state.is_unlocked = False

    return LockResponse(message="已锁定")


@router.put("/unlock/password")
async def change_password(request: Request, body: ChangePasswordRequest):
    """修改屏保密码，在当前已解锁且旧密码正确时生效。"""
    vault: Vault = request.app.state.vault

    if not vault.is_unlocked:
        raise HTTPException(status_code=403, detail="请先解锁")

    success = await vault.change_password(body.old_password, body.new_password)
    if not success:
        raise HTTPException(status_code=401, detail="旧密码错误")

    return {"message": "密码已修改"}


@router.get("/status", response_model=StatusResponse)
async def status(request: Request):
    """获取屏保状态，在任意登录态下返回解锁与加载信息。"""
    vault: Vault = request.app.state.vault

    return StatusResponse(
        is_unlocked=vault.is_unlocked,
        is_password_set=await vault.is_password_set(),
        plugins_loaded=len(request.app.state.plugin_registry),
    )

