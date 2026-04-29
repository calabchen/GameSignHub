"""游戏账户管理 API：增删改查与校验。"""

from fastapi import APIRouter, HTTPException, Request

from app.core.vault import Vault, VaultLockedError
from app.schemas.credential import (
    CredentialCreate,
    CredentialSummary,
    CredentialUpdate,
    ValidateResult,
)

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


def _get_vault(request: Request) -> Vault:
    vault: Vault = request.app.state.vault
    if not vault.is_unlocked:
        raise VaultLockedError()
    return vault


@router.get("", response_model=list[CredentialSummary])
async def list_credentials(request: Request):
    """获取游戏账户列表，在屏保已解锁时返回账户摘要。"""
    vault = _get_vault(request)
    return vault.list_summaries()


@router.post("", response_model=CredentialSummary)
async def create_credential(request: Request, body: CredentialCreate):
    """创建游戏账户，在提供社区 ID 与账户信息时保存记录。"""
    vault = _get_vault(request)

    data = {
        "display_name": body.display_name,
        "credentials": body.credentials,
        "enabled_games": body.enabled_games,
        "is_enabled": body.is_enabled,
    }
    cred_id = await vault.save_credential(body.plugin_id, data)

    creds = vault.get_credentials(body.plugin_id)
    for c in creds:
        if c["id"] == cred_id:
            return CredentialSummary(
                id=c["id"],
                plugin_id=body.plugin_id,
                display_name=c["display_name"],
                enabled_games=c.get("enabled_games", []),
                is_enabled=c.get("is_enabled", True),
            )
    raise HTTPException(status_code=500, detail="Failed to create")


@router.put("/{credential_id}", response_model=CredentialSummary)
async def update_credential(request: Request, credential_id: int, body: CredentialUpdate):
    """更新游戏账户，在账户 ID 存在时覆盖可变字段。"""
    vault = _get_vault(request)

    for plugin_id, creds in vault.get_all_credentials().items():
        for c in creds:
            if c["id"] == credential_id:
                if body.display_name is not None:
                    c["display_name"] = body.display_name
                if body.credentials is not None:
                    c["credentials"] = body.credentials
                if body.enabled_games is not None:
                    c["enabled_games"] = body.enabled_games
                if body.is_enabled is not None:
                    c["is_enabled"] = body.is_enabled
                await vault.save_credential(plugin_id, c)
                return CredentialSummary(
                    id=c["id"],
                    plugin_id=plugin_id,
                    display_name=c["display_name"],
                    enabled_games=c.get("enabled_games", []),
                    is_enabled=c.get("is_enabled", True),
                )

    raise HTTPException(status_code=404, detail="Credential not found")


@router.delete("/{credential_id}")
async def delete_credential(request: Request, credential_id: int):
    """删除游戏账户，在账户 ID 存在时移除该记录。"""
    vault = _get_vault(request)
    await vault.delete_credential(credential_id)
    return {"message": "deleted"}


@router.post("/{credential_id}/validate", response_model=ValidateResult)
async def validate_credential(request: Request, credential_id: int):
    """校验游戏账户，在对应游戏社区可访问时返回有效性。"""
    vault = _get_vault(request)

    for creds in vault.get_all_credentials().values():
        for c in creds:
            if c["id"] == credential_id:
                plugin_id = c.get("plugin_id", "")
                plugin = request.app.state.plugin_registry.get(plugin_id)
                if plugin is None:
                    return ValidateResult(valid=False, message=f"未知插件: {plugin_id}")
                try:
                    valid = await plugin.validate_credentials(c)
                    return ValidateResult(valid=valid, message="有效" if valid else "无效")
                except Exception as e:
                    return ValidateResult(valid=False, message=str(e))

    raise HTTPException(status_code=404, detail="Credential not found")
