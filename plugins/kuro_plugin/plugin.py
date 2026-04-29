"""库街区插件 — 库洛游戏旗下社区签到.
支持游戏:
  - 鸣潮 (wuwa)
  - 战双帕弥什 (pgr)
"""

import asyncio
import random

from app.core.plugin_base import BaseGamePlugin, GameInfo, PluginInfo, SignInResult
from plugins.kuro_plugin.client import KuroHttpClient
from plugins.kuro_plugin.games.base import PGRGame, WuwaGame
from plugins.kuro_plugin.models import KuroCredentials


class KuroPlugin(BaseGamePlugin):
    """库街区签到插件."""

    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            id="kuro",
            name="库街区",
            version="0.1.0",
            description="库洛游戏旗下游戏社区签到",
            homepage="https://github.com/mxyooR/Kuro-autosignin",
            supported_games=[
                GameInfo(
                    id="wuwa", name="鸣潮", has_forum=True, icon="/icons/wuwa.png"
                ),
                GameInfo(
                    id="pgr", name="战双帕弥什", has_forum=True, icon="/icons/pgr.png"
                ),
            ],
        )

    async def validate_credentials(self, credentials: dict) -> bool:
        """验证 Token 是否有效."""
        cred = KuroCredentials.from_dict(credentials.get("credentials", credentials))
        if not cred.token:
            return False
        try:
            client = KuroHttpClient(cred)
            await client.get_user_id()
            return True
        except Exception:
            return False

    async def sign_in(self, credentials: dict, game_id: str) -> list[SignInResult]:
        """单个游戏签到."""
        cred = KuroCredentials.from_dict(credentials.get("credentials", credentials))
        client = KuroHttpClient(cred)

        # 获取 userId（优先用已提供的，否则从 API 获取）
        if cred.user_id:
            user_id = cred.user_id
        else:
            try:
                user_id = await client.get_user_id()
            except Exception as e:
                return [SignInResult(game_id, "failed", "", f"获取userId失败: {e}")]

        if game_id == "wuwa":
            game = WuwaGame(client)
            game_type_id = "3"
        elif game_id == "pgr":
            game = PGRGame(client)
            game_type_id = "2"
        else:
            return [SignInResult(game_id, "failed", "", f"未知游戏: {game_id}")]

        # 鸣潮优先用已提供的 roleId
        role_id = cred.get_role_id(game_id)
        if role_id:
            r = await game.sign_in(role_id=role_id, user_id=user_id)
            return [SignInResult(
                game_id=game_id,
                status=r["status"],
                reward=r["reward"],
                message=r["message"],
            )]

        # 从 API 获取角色列表
        try:
            roles = await client.get_game_role(game_type_id)
        except Exception:
            roles = []

        if not roles:
            return [SignInResult(game_id, "failed", "", "未找到游戏角色")]

        results = []
        for role in roles:
            r = await game.sign_in(
                role_id=role["roleId"],
                user_id=user_id,
            )
            results.append(
                SignInResult(
                    game_id=game_id,
                    status=r["status"],
                    reward=r["reward"],
                    message=f"{role.get('roleName', '')}: {r['message']}",
                )
            )
            if len(roles) > 1:
                await asyncio.sleep(random.uniform(0.5, 1.5))

        return results

    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        """所有游戏签到."""
        all_results: dict[str, list[SignInResult]] = {}

        for game_id in ("wuwa", "pgr"):
            if self._is_game_enabled(credentials, game_id):
                all_results[game_id] = await self.sign_in(credentials, game_id)

        return all_results

    async def get_user_info(self, credentials: dict) -> dict:
        """获取用户信息."""
        cred = KuroCredentials.from_dict(credentials.get("credentials", credentials))
        client = KuroHttpClient(cred)
        try:
            user_id = await client.get_user_id()
            return {"user_id": user_id, "nickname": f"User-{user_id[:6]}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _is_game_enabled(credentials: dict, game_id: str) -> bool:
        enabled = credentials.get("enabled_games", [])
        return game_id in enabled if enabled else True
