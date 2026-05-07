"""游戏账户管理 API：增删改查与校验。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from app.core import crud_yaml
from app.routers.deps import require_unlocked
from app.schemas import GameAccountScheduleUpdate, GameAccountSummary, ValidateResult

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class GameAccountCreate(BaseModel):
    plugin_id: str = "kuro"
    user_id: str = ""
    token: str = ""
    devcode: str = ""
    distinct_id: str = ""
    is_enabled: bool = True
    wuwa_role_id: str = ""
    pgr_role_id: str = ""


class GameAccountUpdate(BaseModel):
    user_id: str | None = None
    token: str | None = None
    devcode: str | None = None
    distinct_id: str | None = None
    is_enabled: bool | None = None
    wuwa_role_id: str | None = None
    pgr_role_id: str | None = None


@router.get("", response_model=list[GameAccountSummary])
async def list_accounts(
    plugin: str | None = Query(default=None),
    _=Depends(require_unlocked),
):
    return crud_yaml.list_all(plugin_id=plugin)


@router.get("/{account_id}", response_model=GameAccountSummary)
async def get_account(
    account_id: int,
    plugin: str = Query(),
    _=Depends(require_unlocked),
):
    items = crud_yaml.list_all(plugin_id=plugin, account_id=account_id)
    if not items:
        raise HTTPException(status_code=404, detail="Account not found")
    return items[0]


@router.get("/{account_id}/detail")
async def get_account_detail(
    account_id: int,
    plugin: str = Query(),
    _=Depends(require_unlocked),
):
    data = crud_yaml.get(plugin, account_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return data


@router.post("", response_model=GameAccountSummary)
async def create_account(
    body: GameAccountCreate,
    _=Depends(require_unlocked),
):
    data = {
        "enable": body.is_enabled,
        "user_id": body.user_id,
        "token": body.token,
        "devcode": body.devcode,
        "distinct_id": body.distinct_id,
        "wuwa": {"role_id": body.wuwa_role_id, "enabled": True, "schedule_cron": "", "schedule_enabled": False},
        "pgr": {"role_id": body.pgr_role_id, "enabled": False, "schedule_cron": "", "schedule_enabled": False},
    }
    account_id = crud_yaml.save(body.plugin_id, data)
    return GameAccountSummary(
        id=account_id,
        plugin_id=body.plugin_id,
        user_id=body.user_id,
        is_enabled=body.is_enabled,
        wuwa_role_id=body.wuwa_role_id,
        pgr_role_id=body.pgr_role_id,
    )


@router.patch("/{account_id}", response_model=GameAccountSummary)
async def update_account(
    account_id: int,
    plugin: str = Query(),
    body: GameAccountUpdate = None,
    _=Depends(require_unlocked),
):
    existing = crud_yaml.get(plugin, account_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Account not found")

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

    crud_yaml.save(plugin, existing, account_id)
    return GameAccountSummary(
        id=account_id,
        plugin_id=plugin,
        user_id=existing.get("user_id", ""),
        is_enabled=existing.get("enable", True),
        wuwa_role_id=(existing.get("wuwa", {}) or {}).get("role_id", ""),
        pgr_role_id=(existing.get("pgr", {}) or {}).get("role_id", ""),
    )


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    plugin: str = Query(),
    request: Request = None,
    _=Depends(require_unlocked),
):
    items = crud_yaml.list_all(plugin_id=plugin, account_id=account_id)
    if not items:
        raise HTTPException(status_code=404, detail="Account not found")
    crud_yaml.delete(plugin, account_id)
    request.app.state.scheduler.remove_credential(account_id)
    return {"message": "已删除"}


@router.post("/{account_id}/validate", response_model=ValidateResult)
async def validate_account(
    account_id: int,
    plugin: str = Query(),
    request: Request = None,
    _=Depends(require_unlocked),
):
    data = crud_yaml.get(plugin, account_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    plugin_obj = request.app.state.plugin_registry.get(plugin)
    if plugin_obj is None:
        return ValidateResult(valid=False, message=f"未知插件: {plugin}")
    try:
        valid = await plugin_obj.validate_credentials(data)
        return ValidateResult(valid=valid, message="有效" if valid else "无效")
    except Exception as e:
        return ValidateResult(valid=False, message=str(e))


@router.get("/{account_id}/schedule/{game_id}", response_model=GameAccountScheduleUpdate)
async def get_schedule(
    account_id: int,
    game_id: str,
    plugin: str = Query(),
    _=Depends(require_unlocked),
):
    data = crud_yaml.get(plugin, account_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    g = (data or {}).get(game_id, {}) or {}
    return GameAccountScheduleUpdate(cron=g.get("schedule_cron", ""), enabled=g.get("schedule_enabled", False))


@router.put("/{account_id}/schedule/{game_id}", response_model=GameAccountScheduleUpdate)
async def update_schedule(
    account_id: int,
    game_id: str,
    plugin: str = Query(),
    body: GameAccountScheduleUpdate = None,
    request: Request = None,
    _=Depends(require_unlocked),
):
    data = crud_yaml.get(plugin, account_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    cron = body.cron if body.enabled else ""
    crud_yaml.update_schedule(plugin, account_id, game_id, body.cron, body.enabled)
    request.app.state.scheduler.register(account_id, plugin, game_id, cron)
    return body
