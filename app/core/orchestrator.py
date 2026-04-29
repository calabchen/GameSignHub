"""签到编排器：遍历插件/用户/游戏执行签到，写入日志。"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.plugin_base import BaseGamePlugin
from app.core.vault import Vault, VaultLockedError
from app.models.sign_log import SignLog

logger = logging.getLogger("app.orchestrator")


class Orchestrator:
    """签到编排器。"""

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

    def _get_plugin(self, plugin_id: str) -> BaseGamePlugin:
        plugin = self._registry.get(plugin_id)
        if plugin is None:
            raise ValueError(f"Unknown plugin: {plugin_id}")
        return plugin

    def _get_credential(self, plugin_id: str, cred_id: int) -> dict:
        creds_list = self._vault.get_credentials(plugin_id)
        cred = next((c for c in creds_list if c["id"] == cred_id), None)
        if cred is None:
            raise ValueError(f"Credential {cred_id} not found in vault")
        return cred

    def _get_enabled_games(self, plugin: BaseGamePlugin, cred: dict) -> list[str]:
        enabled_games = list(cred.get("enabled_games", []) or [])
        if enabled_games:
            return enabled_games
        return [g.id for g in plugin.plugin_info.supported_games]

    async def sign_once(self, plugin_id: str, cred_id: int, game_id: str) -> list[SignLog]:
        """原子签到：单插件 + 单凭据 + 单游戏。"""
        self._ensure_unlocked()

        plugin = self._get_plugin(plugin_id)
        cred = self._get_credential(plugin_id, cred_id)
        enabled_games = self._get_enabled_games(plugin, cred)
        if game_id not in enabled_games:
            raise ValueError(
                f"Game {game_id} is not enabled for credential {cred_id} in plugin {plugin_id}"
            )

        sign_results = await plugin.sign_in(cred, game_id)
        now = datetime.now()
        logs: list[SignLog] = []
        for r in sign_results:
            logs.append(
                SignLog(
                    credential_id=cred_id,
                    credential_name=cred.get("display_name", ""),
                    plugin_id=plugin_id,
                    game_id=game_id,
                    status=r.status,
                    reward=r.reward,
                    message=r.message,
                    signed_at=now,
                )
            )

        if logs:
            async with self._session_factory() as session:
                session.add_all(logs)
                await session.commit()
        return logs

    async def sign_credential_game(self, plugin_id: str, cred_id: int, game_id: str) -> list[SignLog]:
        """某个凭据在指定游戏签到。"""
        self._ensure_unlocked()
        self._get_plugin(plugin_id)
        self._get_credential(plugin_id, cred_id)

        self._running = True
        try:
            return await self.sign_once(plugin_id, cred_id, game_id)
        finally:
            self._running = False

    async def sign_credential(self, plugin_id: str, cred_id: int) -> list[SignLog]:
        """单个凭据签到（该插件下所有启用游戏）。"""
        self._ensure_unlocked()
        plugin = self._get_plugin(plugin_id)
        cred = self._get_credential(plugin_id, cred_id)
        enabled_games = self._get_enabled_games(plugin, cred)

        self._running = True
        all_logs: list[SignLog] = []

        try:
            for game_id in enabled_games:
                logs = await self.sign_once(plugin_id, cred_id, game_id)
                all_logs.extend(logs)
        finally:
            self._running = False

        return all_logs

    async def sign_plugin_game(self, plugin_id: str, game_id: str) -> list[SignLog]:
        """某个插件的所有启用凭据在指定游戏签到。"""
        self._ensure_unlocked()
        self._get_plugin(plugin_id)
        creds_list = self._vault.get_credentials(plugin_id)
        enabled = [c for c in creds_list if c.get("is_enabled", True)]

        self._running = True
        all_logs: list[SignLog] = []
        try:
            for cred in enabled:
                try:
                    logs = await self.sign_once(plugin_id, cred["id"], game_id)
                    all_logs.extend(logs)
                except Exception as e:
                    logger.error("sign_once failed for %s/%d/%s: %s", plugin_id, cred["id"], game_id, e)
        finally:
            self._running = False
        return all_logs

    async def sign_plugin(self, plugin_id: str) -> list[SignLog]:
        """某个插件的所有启用凭据签到。"""
        self._ensure_unlocked()
        self._get_plugin(plugin_id)

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
        """所有插件的所有启用凭据签到。"""
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
        """查询签到日志。"""
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

            count_stmt = select(SignLog).where(stmt.whereclause) if stmt.whereclause is not None else select(SignLog)
            r = await session.execute(count_stmt.with_only_columns(SignLog.id))
            total = len(r.scalars().all())

            stmt = stmt.order_by(SignLog.signed_at.desc())
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            r = await session.execute(stmt)
            rows = list(r.scalars().all())

            return rows, total

    async def get_today_summary(self) -> dict:
        """今日签到汇总。"""
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
        """清除所有签到日志，返回删除数量。"""
        from sqlalchemy import delete

        async with self._session_factory() as session:
            result = await session.execute(delete(SignLog))
            await session.commit()
            return result.rowcount

    def _ensure_unlocked(self) -> None:
        if not self._vault.is_unlocked:
            raise VaultLockedError()
