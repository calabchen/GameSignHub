"""定时调度 API：查看、修改计划并支持手动触发。"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_access_token
from app.core.scheduler import SignScheduler

router = APIRouter(prefix="/api/schedules", tags=["schedule"])
security = HTTPBearer()


def _auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="未授权")


@router.get("")
async def get_schedules(request: Request, _=Depends(_auth)):
    sched: SignScheduler = request.app.state.scheduler
    return await sched.get_config()


@router.put("")
async def update_schedules(request: Request, body: dict, _=Depends(_auth)):
    sched: SignScheduler = request.app.state.scheduler
    cron_expr = body.get("cron", "0 7 * * *")
    enabled = body.get("enabled", True)
    await sched.set_cron(cron_expr, enabled)
    return {"message": "已更新", "cron": cron_expr, "enabled": enabled}


@router.post("/triggers")
async def trigger_schedules(request: Request, _=Depends(_auth)):
    sched: SignScheduler = request.app.state.scheduler
    try:
        await sched.trigger_now()
        return {"message": "签到完成"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
