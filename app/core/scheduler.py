"""定时任务调度器 — APScheduler 封装。

每个账户的每个游戏可独立 cron，持久化在 config/{plugin_id}/{id}.yaml 中。
job_id = "sign_{account_id}_{game_id}"
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core import crud_yaml

logger = logging.getLogger("app.scheduler")

DEFAULT_CRON = "0 7 * * *"


class SignScheduler:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory
        self._aps = AsyncIOScheduler()
        self._sign_once_fn = None
        self._sign_all_fn = None
        self._running = False

    def set_sign_once_fn(self, fn):
        self._sign_once_fn = fn

    def set_sign_all_fn(self, fn):
        self._sign_all_fn = fn

    async def start(self) -> None:
        count = 0
        for item in crud_yaml.get_all_with_schedules():
            self._add_job(item["id"], item["plugin_id"], item["game_id"], item["schedule_cron"])
            count += 1

        self._aps.start()
        logger.info("调度器已启动，已注册 %d 个游戏定时任务", count)

    async def shutdown(self) -> None:
        self._aps.shutdown(wait=False)
        logger.info("调度器已关闭")

    def register(self, account_id: int, plugin_id: str, game_id: str, cron: str) -> None:
        self._remove_job(account_id, game_id)
        if cron:
            self._add_job(account_id, plugin_id, game_id, cron)
            logger.info("已注册定时 sign_%d_%s cron=%s", account_id, game_id, cron)

    def remove_credential(self, account_id: int) -> None:
        for game_id in ("wuwa", "pgr"):
            self._remove_job(account_id, game_id)

    async def trigger_now(self) -> None:
        if self._sign_all_fn is None:
            raise RuntimeError("sign_all function not set")
        self._running = True
        try:
            await self._sign_all_fn()
        finally:
            self._running = False

    async def get_config(self) -> dict:
        return {"cron": "", "enabled": False, "running": self._running}

    async def set_cron(self, cron_expr: str, enabled: bool = True) -> None:
        pass

    def _add_job(self, account_id: int, plugin_id: str, game_id: str, cron_expr: str) -> None:
        job_id = f"sign_{account_id}_{game_id}"
        try:
            trigger = CronTrigger.from_crontab(cron_expr)
        except Exception as e:
            logger.warning("无效 cron '%s': %s，使用默认", cron_expr, e)
            trigger = CronTrigger.from_crontab(DEFAULT_CRON)

        self._aps.add_job(
            lambda pid=plugin_id, cid=account_id, gid=game_id: self._wrapped_sign(pid, cid, gid),
            trigger=trigger,
            id=job_id,
            name=f"账户#{account_id}-{game_id}定时签到",
            replace_existing=True,
        )

    def _remove_job(self, account_id: int, game_id: str) -> None:
        try:
            self._aps.remove_job(f"sign_{account_id}_{game_id}")
        except Exception:
            pass

    async def _wrapped_sign(self, plugin_id: str, account_id: int, game_id: str) -> None:
        if self._sign_once_fn is None:
            return
        try:
            logger.info("定时签到 account=%d game=%s", account_id, game_id)
            await self._sign_once_fn(plugin_id, account_id, game_id)
        except Exception as e:
            logger.error("定时签到 account=%d game=%s 失败: %s", account_id, game_id, e)
