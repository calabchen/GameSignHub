"""定时任务调度器 — APScheduler 封装.

负责定时签到的 cron 调度，配置持久化在 configs 表中。
支持运行时修改 cron 表达式、启用/禁用、手动触发。
"""

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.config import Config

logger = logging.getLogger("app.scheduler")

DEFAULT_CRON = "0 7 * * *"  # 每天 07:00


class SignScheduler:
    """签到任务调度器."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._aps = AsyncIOScheduler()
        self._sign_all_fn = None
        self._running = False

    def set_sign_fn(self, fn):
        """设置签到回调函数 (orchestrator.sign_all)."""
        self._sign_all_fn = fn

    async def start(self) -> None:
        """启动调度器，从数据库加载配置."""
        cron_expr, enabled = await self._load_config()

        if enabled and cron_expr:
            self._add_job(cron_expr)
            logger.info("调度器已启动，cron=%s", cron_expr)
        else:
            logger.info("调度器未启用或未配置 cron")

        self._aps.start()

    async def shutdown(self) -> None:
        """关闭调度器."""
        self._aps.shutdown(wait=False)
        logger.info("调度器已关闭")

    async def get_config(self) -> dict:
        """获取当前调度配置."""
        cron_expr, enabled = await self._load_config()
        return {
            "cron": cron_expr or DEFAULT_CRON,
            "enabled": enabled,
            "running": self._running,
        }

    async def set_cron(self, cron_expr: str, enabled: bool = True) -> None:
        """修改 cron 表达式并持久化."""
        async with self._session_factory() as session:
            # 保存 cron
            await self._upsert_config(session, "schedule_cron", cron_expr)
            # 保存启用状态
            await self._upsert_config(session, "schedule_enabled", "1" if enabled else "0")
            await session.commit()

        self._remove_existing_job()
        if enabled:
            self._add_job(cron_expr)
            logger.info("cron 已更新: %s", cron_expr)
        else:
            logger.info("定时签到已禁用")

    async def trigger_now(self) -> None:
        """立即触发一次签到."""
        if self._sign_all_fn is None:
            raise RuntimeError("sign_all function not set")

        self._running = True
        try:
            logger.info("手动触发签到...")
            await self._sign_all_fn()
        finally:
            self._running = False

    # ----------------------------------------------------------------
    # Internal
    # ----------------------------------------------------------------

    async def _load_config(self) -> tuple[str, bool]:
        async with self._session_factory() as session:
            cron_row = await session.get(Config, "schedule_cron")
            enabled_row = await session.get(Config, "schedule_enabled")

        cron_expr = cron_row.value if cron_row and cron_row.value else ""
        enabled = enabled_row.value != "0" if enabled_row else False
        return cron_expr, enabled

    def _add_job(self, cron_expr: str) -> None:
        if self._sign_all_fn is None:
            return

        try:
            trigger = CronTrigger.from_crontab(cron_expr)
        except Exception as e:
            logger.warning("无效的 cron 表达式 '%s': %s", cron_expr, e)
            trigger = CronTrigger.from_crontab(DEFAULT_CRON)

        self._aps.add_job(
            self._wrapped_sign,
            trigger=trigger,
            id="sign_all_job",
            name="签到定时任务",
            replace_existing=True,
        )

    def _remove_existing_job(self) -> None:
        try:
            self._aps.remove_job("sign_all_job")
        except Exception:
            pass

    async def _wrapped_sign(self) -> None:
        if self._running:
            logger.info("上次签到仍在执行，跳过")
            return
        self._running = True
        try:
            logger.info("定时签到开始")
            await self._sign_all_fn()
            logger.info("定时签到完成")
        except Exception as e:
            logger.error("定时签到失败: %s", e)
        finally:
            self._running = False

    @staticmethod
    async def _upsert_config(session: AsyncSession, key: str, value: str) -> None:
        row = await session.get(Config, key)
        if row:
            row.value = value
        else:
            session.add(Config(key=key, value=value))
