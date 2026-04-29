"""游戏账户管理 API：增删改查与校验。"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import verify_access_token
from app.core.yaml_store import YamlStore
from app.schemas.credential import CredentialScheduleUpdate, CredentialSummary, ValidateResult
from app.schemas.credential import BaseModel

router = APIRouter(prefix="/api/credentials", tags=["credentials"])
security = HTTPBearer()


class CredentialCreateRequest(BaseModel):
    plugin_id: str = "kuro"
    user_id: str = ""
    token: str = ""
    devcode: str = ""
    distinct_id: str = ""
    is_enabled: bool = True
    wuwa_role_id: str = ""
    pgr_role_id: str = ""


class CredentialUpdateRequest(BaseModel):
    user_id: str | None = None
    token: str | None = None
    devcode: str | None = None
    distinct_id: str | None = None
    is_enabled: bool | None = None
    wuwa_role_id: str | None = None
    pgr_role_id: str | None = None


def _get_store(request: Request) -> YamlStore:
    return request.app.state.yaml_store


def _require_auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="未授权")
    if not request.app.state.is_unlocked:
        raise HTTPException(status_code=403, detail="请先解锁")


@router.get("", response_model=list[CredentialSummary])
async def list_credentials(request: Request, _=Depends(_require_auth)):
    return _get_store(request).list_all()


@router.post("", response_model=CredentialSummary)
async def create_credential(request: Request, body: CredentialCreateRequest, _=Depends(_require_auth)):
    store = _get_store(request)
    data = {
        "enable": body.is_enabled,
        "user_id": body.user_id,
        "token": body.token,
        "devcode": body.devcode,
        "distinct_id": body.distinct_id,
        "wuwa": {"role_id": body.wuwa_role_id, "enabled": True, "schedule_cron": "", "schedule_enabled": False},
        "pgr": {"role_id": body.pgr_role_id, "enabled": False, "schedule_cron": "", "schedule_enabled": False},
    }
    cred_id = store.save(body.plugin_id, data)
    return CredentialSummary(id=cred_id, plugin_id=body.plugin_id, user_id=body.user_id, is_enabled=body.is_enabled)


@router.put("/{credential_id}", response_model=CredentialSummary)
async def update_credential(request: Request, credential_id: int, body: CredentialUpdateRequest, _=Depends(_require_auth)):
    store = _get_store(request)
    for a in store.list_all():
        if a["id"] == credential_id:
            existing = store.get(a["plugin_id"], credential_id)
            if existing is None:
                raise HTTPException(status_code=404, detail="Credential not found")
            if body.user_id is not None:
                existing["user_id"] = body.user_id
            if body.token is not None:
                existing["token"] = body.token
            if body.devcode is not None:
                existing["devcode"] = body.devcode
            if body.distinct_id is not None:
                existing["distinct_id"] = body.distinct_id
            if body.is_enabled is not None:
                existing["enable"] = body.is_enabled
            if body.wuwa_role_id is not None:
                existing.setdefault("wuwa", {})["role_id"] = body.wuwa_role_id
            if body.pgr_role_id is not None:
                existing.setdefault("pgr", {})["role_id"] = body.pgr_role_id
            store.save(a["plugin_id"], existing, credential_id)
            return CredentialSummary(
                id=credential_id, plugin_id=a["plugin_id"],
                user_id=existing.get("user_id", ""),
                is_enabled=existing.get("enable", True),
            )
    raise HTTPException(status_code=404, detail="Credential not found")


@router.get("/{credential_id}/detail")
async def get_credential_detail(request: Request, credential_id: int, _=Depends(_require_auth)):
    store = _get_store(request)
    for a in store.list_all():
        if a["id"] == credential_id:
            return store.get(a["plugin_id"], credential_id)
    raise HTTPException(status_code=404, detail="Credential not found")


@router.delete("/{credential_id}")
async def delete_credential(request: Request, credential_id: int, _=Depends(_require_auth)):
    store = _get_store(request)
    scheduler = request.app.state.scheduler
    for a in store.list_all():
        if a["id"] == credential_id:
            store.delete(a["plugin_id"], credential_id)
            scheduler.remove_credential(credential_id)
            return {"message": "deleted"}
    raise HTTPException(status_code=404, detail="Credential not found")


@router.post("/{credential_id}/validate", response_model=ValidateResult)
async def validate_credential(request: Request, credential_id: int, _=Depends(_require_auth)):
    store = _get_store(request)
    for a in store.list_all():
        if a["id"] == credential_id:
            data = store.get(a["plugin_id"], credential_id)
            plugin = request.app.state.plugin_registry.get(a["plugin_id"])
            if plugin is None:
                return ValidateResult(valid=False, message=f"未知插件: {a['plugin_id']}")
            try:
                valid = await plugin.validate_credentials(data)
                return ValidateResult(valid=valid, message="有效" if valid else "无效")
            except Exception as e:
                return ValidateResult(valid=False, message=str(e))
    raise HTTPException(status_code=404, detail="Credential not found")


@router.get("/{credential_id}/schedule/{game_id}", response_model=CredentialScheduleUpdate)
async def get_credential_schedule(request: Request, credential_id: int, game_id: str, _=Depends(_require_auth)):
    store = _get_store(request)
    for a in store.list_all():
        if a["id"] == credential_id:
            data = store.get(a["plugin_id"], credential_id)
            g = (data or {}).get(game_id, {}) or {}
            return CredentialScheduleUpdate(cron=g.get("schedule_cron", ""), enabled=g.get("schedule_enabled", False))
    raise HTTPException(status_code=404, detail="Credential not found")


@router.put("/{credential_id}/schedule/{game_id}", response_model=CredentialScheduleUpdate)
async def update_credential_schedule(request: Request, credential_id: int, game_id: str, body: CredentialScheduleUpdate, _=Depends(_require_auth)):
    store = _get_store(request)
    scheduler = request.app.state.scheduler
    for a in store.list_all():
        if a["id"] == credential_id:
            cron = body.cron if body.enabled else ""
            store.update_schedule(a["plugin_id"], credential_id, game_id, body.cron, body.enabled)
            scheduler.register(credential_id, a["plugin_id"], game_id, cron)
            return body
    raise HTTPException(status_code=404, detail="Credential not found")
