"""签到编排器：遍历插件/用户/游戏执行签到，写入日志。"""

import logging
import time
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.plugin_base import BaseGamePlugin
from app.core.yaml_store import YamlStore
from app.models.sign_log import SignLog

logger = logging.getLogger("app.orchestrator")


class Orchestrator:
    def __init__(
        self,
        plugin_registry: dict[str, BaseGamePlugin],
        yaml_store: YamlStore,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._registry = plugin_registry
        self._store = yaml_store
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
        cred = self._store.get(plugin_id, cred_id)
        if cred is None:
            raise ValueError(f"Credential {cred_id} not found for plugin {plugin_id}")
        return cred

    def _get_enabled_games(self, plugin: BaseGamePlugin, cred: dict) -> list[str]:
        return [g.id for g in plugin.plugin_info.supported_games]

    async def sign_once(self, plugin_id: str, cred_id: int, game_id: str) -> list[SignLog]:
        plugin = self._get_plugin(plugin_id)
        cred = self._get_credential(plugin_id, cred_id)
        enabled_games = self._get_enabled_games(plugin, cred)
        if game_id not in enabled_games:
            raise ValueError(
                f"Game {game_id} is not enabled for credential {cred_id} in plugin {plugin_id}"
            )

        t_start = time.monotonic()
        sign_results = await plugin.sign_in(cred, game_id)
        elapsed = round(time.monotonic() - t_start, 3)
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
                    elapsed=elapsed,
                    signed_at=now,
                )
            )

        if logs:
            async with self._session_factory() as session:
                session.add_all(logs)
                await session.commit()

        for r in sign_results:
            logger.info(
                "sign_in | plugin=%s game=%s account=%s elapsed=%.3fs status=%s",
                plugin_id, game_id, cred.get("display_name", cred_id),
                elapsed, r.status,
            )

        return logs

    async def sign_credential(self, plugin_id: str, cred_id: int) -> list[SignLog]:
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

    async def sign_plugin(self, plugin_id: str) -> list[SignLog]:
        self._get_plugin(plugin_id)
        creds = self._store.list_by_plugin(plugin_id)
        enabled = [c for c in creds if c.get("is_enabled", True)]

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
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[SignLog], int]:
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
            if date_from:
                stmt = stmt.where(SignLog.signed_at >= date_from)
            if date_to:
                stmt = stmt.where(SignLog.signed_at <= date_to + " 23:59:59")

            count_stmt = select(SignLog).where(stmt.whereclause) if stmt.whereclause is not None else select(SignLog)
            r = await session.execute(count_stmt.with_only_columns(SignLog.id))
            total = len(r.scalars().all())

            stmt = stmt.order_by(SignLog.signed_at.desc())
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            r = await session.execute(stmt)
            rows = list(r.scalars().all())

            return rows, total

    async def get_today_summary(self) -> dict:
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
        from sqlalchemy import delete

        async with self._session_factory() as session:
            result = await session.execute(delete(SignLog))
            await session.commit()
            return result.rowcount
