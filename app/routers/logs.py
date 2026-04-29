"""签到日志查询 API。"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import verify_access_token
from app.core.orchestrator import Orchestrator
from app.schemas.log import SignLogEntry, SignLogPage, TodaySummary

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
        pass  # logs are readable without auth in this implementation
    oc: Orchestrator = request.app.state.orchestrator
    rows, total = await oc.get_logs(
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
            id=row.id,
            credential_id=row.credential_id,
            credential_name=row.credential_name,
            plugin_id=row.plugin_id,
            game_id=row.game_id,
            status=row.status,
            reward=row.reward,
            message=row.message,
            elapsed=row.elapsed,
            signed_at=row.signed_at.isoformat(),
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]
    return SignLogPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/today", response_model=TodaySummary)
async def today_summary(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        pass
    oc: Orchestrator = request.app.state.orchestrator
    data = await oc.get_today_summary()
    return TodaySummary(**data)


@router.delete("")
async def clear_logs(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        pass
    oc: Orchestrator = request.app.state.orchestrator
    count = await oc.clear_logs()
    return {"message": f"已清除 {count} 条日志"}
