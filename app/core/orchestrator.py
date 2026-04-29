"""签到编排器 — 遍历插件/用户/游戏执行签到，写入日志.

依赖:
  - PluginLoader: 获取插件实例
  - Vault: 获取解密凭据
  - SQLAlchemy session: 写入 sign_logs
"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.plugin_base import BaseGamePlugin, SignInResult
from app.core.vault import Vault, VaultLockedError
from app.models.sign_log import SignLog

logger = logging.getLogger("app.orchestrator")


class Orchestrator:
    """签到编排器."""

    def __init__(
        self,
        plugin_registry: dict[str, BaseGamePlugin],
        vault: Vault,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._registry = plugin_registry
        self._vault = vault
        self._session_factory = session_factory
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    async def sign_credential(self, plugin_id: str, cred_id: int) -> list[SignLog]:
        """单个凭据签到（该插件的所有启用游戏 + 论坛）."""
        self._ensure_unlocked()

        plugin = self._registry.get(plugin_id)
        if plugin is None:
            raise ValueError(f"Unknown plugin: {plugin_id}")

        creds_list = self._vault.get_credentials(plugin_id)
        cred = next((c for c in creds_list if c["id"] == cred_id), None)
        if cred is None:
            raise ValueError(f"Credential {cred_id} not found in vault")

        plugin_info = plugin.plugin_info
        self._running = True
        all_logs: list[SignLog] = []

        try:
            # 签到该插件的所有游戏
            results = await plugin.sign_in_all(cred)

            # 写入日志
            now = datetime.now()
            for game_id, sign_results in results.items():
                for r in sign_results:
                    log = SignLog(
                        credential_id=cred_id,
                        credential_name=cred.get("display_name", ""),
                        plugin_id=plugin_id,
                        game_id=game_id,
                        status=r.status,
                        reward=r.reward,
                        message=r.message,
                        signed_at=now,
                    )
                    all_logs.append(log)

            if all_logs:
                async with self._session_factory() as session:
                    session.add_all(all_logs)
                    await session.commit()

        finally:
            self._running = False

        return all_logs

    async def sign_plugin(self, plugin_id: str) -> list[SignLog]:
        """某个插件的所有用户签到."""
        self._ensure_unlocked()

        plugin = self._registry.get(plugin_id)
        if plugin is None:
            raise ValueError(f"Unknown plugin: {plugin_id}")

        creds_list = self._vault.get_credentials(plugin_id)
        enabled = [c for c in creds_list if c.get("is_enabled", True)]

        self._running = True
        all_logs: list[SignLog] = []

        try:
            for cred in enabled:
                try:
                    logs = await self.sign_credential(plugin_id, cred["id"])
                    all_logs.extend(logs)
                except Exception as e:
                    logger.error("sign_credential failed for %s/%d: %s", plugin_id, cred["id"], e)
        finally:
            self._running = False

        return all_logs

    async def sign_all(self) -> list[SignLog]:
        """所有插件的所有用户签到."""
        self._ensure_unlocked()

        self._running = True
        all_logs: list[SignLog] = []

        try:
            for plugin_id in self._registry:
                try:
                    logs = await self.sign_plugin(plugin_id)
                    all_logs.extend(logs)
                except Exception as e:
                    logger.error("sign_plugin failed for %s: %s", plugin_id, e)
        finally:
            self._running = False

        return all_logs

    async def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        plugin_id: str | None = None,
        game_id: str | None = None,
        status: str | None = None,
        credential_id: int | None = None,
    ) -> tuple[list[SignLog], int]:
        """查询签到日志."""
        async with self._session_factory() as session:
            stmt = select(SignLog)

            if plugin_id:
                stmt = stmt.where(SignLog.plugin_id == plugin_id)
            if game_id:
                stmt = stmt.where(SignLog.game_id == game_id)
            if status:
                stmt = stmt.where(SignLog.status == status)
            if credential_id:
                stmt = stmt.where(SignLog.credential_id == credential_id)

            # 总数
            count_stmt = select(SignLog).where(stmt.whereclause) if stmt.whereclause is not None else select(SignLog)
            r = await session.execute(count_stmt.with_only_columns(SignLog.id))
            total = len(r.scalars().all())

            # 分页
            stmt = stmt.order_by(SignLog.signed_at.desc())
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            r = await session.execute(stmt)
            rows = list(r.scalars().all())

            return rows, total

    async def get_today_summary(self) -> dict:
        """今日签到汇总."""
        today = datetime.now().strftime("%Y-%m-%d")
        async with self._session_factory() as session:
            stmt = select(SignLog).where(SignLog.signed_at >= today)
            r = await session.execute(stmt)
            rows = r.scalars().all()

        summary = {"total": 0, "success": 0, "already": 0, "failed": 0}
        for row in rows:
            summary["total"] += 1
            if row.status in ("success", "already"):
                summary.setdefault(row.status, 0)
                summary[row.status] += 1
            else:
                summary["failed"] += 1
        return summary

    async def clear_logs(self) -> int:
        """清除所有签到日志，返回删除数量."""
        from sqlalchemy import delete
        async with self._session_factory() as session:
            result = await session.execute(delete(SignLog))
            await session.commit()
            return result.rowcount

    def _ensure_unlocked(self) -> None:
        if not self._vault.is_unlocked:
            raise VaultLockedError()
