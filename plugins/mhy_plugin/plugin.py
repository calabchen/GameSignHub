"""米游社插件 — 米哈游旗下社区签到.

支持游戏:
  - 原神 (genshin)
  - 崩坏星穹铁道 (honkai_sr)
  - 绝区零 (zzz)
  - 崩坏3 (honkai3rd)
  - 崩坏2 (honkai2)
  - 未定事件簿 (tears_of_themis)
"""

from app.core.plugin_base import BaseGamePlugin, GameInfo, PluginInfo, SignInResult


class MhyPlugin(BaseGamePlugin):
    """米游社签到插件."""

    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            id="mhy",
            name="米游社",
            version="0.1.0",
            description="米哈游旗下游戏社区签到",
            homepage="https://github.com/Womsxd/MihoyoBBSTools",
            supported_games=[
                GameInfo(
                    id="genshin", name="原神", has_forum=True, icon="/icons/genshin.png"
                ),
                GameInfo(
                    id="honkai_sr",
                    name="崩坏星穹铁道",
                    has_forum=True,
                    icon="/icons/honkai_sr.png",
                ),
                GameInfo(
                    id="zzz", name="绝区零", has_forum=True, icon="/icons/zzz.png"
                ),
                GameInfo(
                    id="honkai3rd",
                    name="崩坏3",
                    has_forum=True,
                    icon="/icons/honkai3rd.png",
                ),
                GameInfo(
                    id="honkai2",
                    name="崩坏学园2",
                    has_forum=True,
                    icon="/icons/honkai2.png",
                ),
                GameInfo(
                    id="tears_of_themis",
                    name="未定事件簿",
                    has_forum=True,
                    icon="/icons/tears_of_themis.png",
                ),
            ],
        )

    # --------------- Phase 3 实现 ---------------

    async def validate_credentials(self, credentials: dict) -> bool:
        raise NotImplementedError

    async def sign_in(self, credentials: dict, game_id: str) -> list[SignInResult]:
        raise NotImplementedError

    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        raise NotImplementedError

    async def get_user_info(self, credentials: dict) -> dict:
        raise NotImplementedError
