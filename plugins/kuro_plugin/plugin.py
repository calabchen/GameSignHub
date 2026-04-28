"""库街区插件 — 库洛游戏旗下游戏签到.

支持游戏:
  - 鸣潮 (wuwa)
  - 战双帕弥什 (pgr)
"""

from app.core.plugin_base import BaseGamePlugin, GameInfo, PluginInfo, SignInResult


class KuroPlugin(BaseGamePlugin):
    """库街区签到插件."""

    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            id="kuro",
            name="库街区",
            version="0.1.0",
            description="库洛游戏社区签到：鸣潮、战双帕弥什",
            homepage="https://github.com/mxyooR/Kuro-autosignin",
            supported_games=[
                GameInfo(id="wuwa", name="鸣潮", has_forum=True),
                GameInfo(id="pgr", name="战双帕弥什", has_forum=True),
            ],
        )

    # --------------- Phase 4 实现 ---------------

    async def validate_credentials(self, credentials: dict) -> bool:
        raise NotImplementedError

    async def sign_in(self, credentials: dict, game_id: str) -> list[SignInResult]:
        raise NotImplementedError

    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        raise NotImplementedError

    async def get_user_info(self, credentials: dict) -> dict:
        raise NotImplementedError
