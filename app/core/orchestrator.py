"""签到编排器：遍历插件/用户/游戏执行签到，写入日志。"""

import logging
import time
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core import crud_yaml
from app.core.plugin_base import BaseGamePlugin

logger = logging.getLogger("app.orchestrator")


class Orchestrator:
    def __init__(
        self,
        plugin_registry: dict[str, BaseGamePlugin],
        session_factory: async_sessionmaker,
    ) -> None:
        self._registry = plugin_registry
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

    def _get_credential(self, plugin_id: str, account_id: int) -> dict:
        cred = crud_yaml.get(plugin_id, account_id)
        if cred is None:
            raise ValueError(f"Account {account_id} not found for plugin {plugin_id}")
        return cred

    def _get_enabled_games(self, plugin: BaseGamePlugin, cred: dict) -> list[str]:
        return [g.id for g in plugin.plugin_info.supported_games]

    async def sign_once(self, plugin_id: str, account_id: int, game_id: str) -> list[dict]:
        plugin = self._get_plugin(plugin_id)
        cred = self._get_credential(plugin_id, account_id)
        enabled_games = self._get_enabled_games(plugin, cred)
        if game_id not in enabled_games:
            raise ValueError(
                f"Game {game_id} is not enabled for account {account_id} in plugin {plugin_id}"
            )

        t_start = time.monotonic()
        sign_results = await plugin.sign_in(cred, game_id)
        elapsed = round(time.monotonic() - t_start, 3)
        now = datetime.now()
        now_iso = now.isoformat()

        logs = []
        for r in sign_results:
            logs.append({
                "credential_id": account_id,
                "credential_name": cred.get("display_name", ""),
                "plugin_id": plugin_id,
                "game_id": game_id,
                "status": r.status,
                "reward": r.reward,
                "message": r.message,
                "elapsed": elapsed,
                "signed_at": now_iso,
                "created_at": now_iso,
            })

        if logs:
            sql = text("""
                INSERT INTO sign_logs
                (credential_id, credential_name, plugin_id, game_id, status, reward, message, elapsed, signed_at, created_at)
                VALUES (:credential_id, :credential_name, :plugin_id, :game_id, :status, :reward, :message, :elapsed, :signed_at, :created_at)
            """)
            async with self._session_factory() as session:
                for log in logs:
                    await session.execute(sql, log)
                await session.commit()

        for r in sign_results:
            logger.info(
                "sign_in | plugin=%s game=%s account=%s elapsed=%.3fs status=%s",
                plugin_id, game_id, cred.get("display_name", account_id),
                elapsed, r.status,
            )

        return logs

    async def sign_credential(self, plugin_id: str, account_id: int) -> list[dict]:
        plugin = self._get_plugin(plugin_id)
        cred = self._get_credential(plugin_id, account_id)
        enabled_games = self._get_enabled_games(plugin, cred)

        self._running = True
        all_logs = []
        try:
            for game_id in enabled_games:
                logs = await self.sign_once(plugin_id, account_id, game_id)
                all_logs.extend(logs)
        finally:
            self._running = False
        return all_logs

    async def sign_plugin(self, plugin_id: str) -> list[dict]:
        self._get_plugin(plugin_id)
        creds = crud_yaml.list_all(plugin_id=plugin_id)
        enabled = [c for c in creds if c.get("is_enabled", True)]

        self._running = True
        all_logs = []
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

    async def sign_all(self) -> list[dict]:
        self._running = True
        all_logs = []
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
