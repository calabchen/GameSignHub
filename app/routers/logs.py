"""签到日志查询 API（只读）。"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_access_token
from app.core.crud_log import clear_logs, get_logs, get_today_summary
from app.schemas import SignLogEntry, SignLogPage

router = APIRouter(prefix="/api/logs", tags=["logs"])
security = HTTPBearer()


@router.get("", response_model=SignLogPage)
async def list_logs(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    plugin_id: str | None = Query(default=None),
    game_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    credential_id: int | None = Query(default=None),
    date_from: str | None = Query(default=None, description="开始日期 YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="结束日期 YYYY-MM-DD"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        pass

    rows, total = await get_logs(
        request.app.state.session_factory,
        page=page,
        page_size=page_size,
        plugin_id=plugin_id,
        game_id=game_id,
        status=status,
        credential_id=credential_id,
        date_from=date_from,
        date_to=date_to,
    )
    items = [
        SignLogEntry(
            id=row["id"],
            credential_id=row["credential_id"],
            credential_name=row["credential_name"],
            plugin_id=row["plugin_id"],
            game_id=row["game_id"],
            status=row["status"],
            reward=row["reward"],
            message=row["message"],
            elapsed=row["elapsed"],
            signed_at=row["signed_at"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
    return SignLogPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/today")
async def today_summary(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        pass
    return await get_today_summary(request.app.state.session_factory)


@router.delete("")
async def delete_logs(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="未授权")
    await clear_logs(request.app.state.session_factory)
    return {"message": "日志已清空"}
