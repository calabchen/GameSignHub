"""定时调度 API — 查看/修改 cron + 手动触发."""

from fastapi import APIRouter, HTTPException, Request

from app.core.scheduler import SignScheduler

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


def _get_scheduler(request: Request) -> SignScheduler:
    sched: SignScheduler | None = request.app.state.scheduler
    if sched is None:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    return sched


@router.get("")
async def get_schedule(request: Request):
    """获取当前调度配置."""
    sched = _get_scheduler(request)
    return await sched.get_config()


@router.put("")
async def update_schedule(request: Request, body: dict):
    """更新调度配置.

    Body:
        cron: str   — cron 表达式 (e.g. "0 7 * * *")
        enabled: bool — 是否启用
    """
    sched = _get_scheduler(request)
    cron_expr = body.get("cron", "0 7 * * *")
    enabled = body.get("enabled", True)
    await sched.set_cron(cron_expr, enabled)
    return {"message": "已更新", "cron": cron_expr, "enabled": enabled}


@router.post("/trigger")
async def trigger_schedule(request: Request):
    """手动触发一次签到."""
    sched = _get_scheduler(request)
    try:
        await sched.trigger_now()
        return {"message": "签到完成"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
