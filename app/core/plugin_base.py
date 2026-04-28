"""Game Plugin 抽象基类 — 所有游戏插件必须实现此接口."""

from abc import ABC, abstractmethod
from typing import NamedTuple


class GameInfo(NamedTuple):
    id: str             # 游戏标识，如 "genshin"
    name: str           # 显示名称，如 "原神"
    has_forum: bool     # 是否有论坛任务


class PluginInfo(NamedTuple):
    id: str                         # 插件标识，如 "mhy"
    name: str                       # 插件名称，如 "米游社"
    version: str                    # 版本号
    description: str                # 描述
    homepage: str | None = None     # 项目主页
    supported_games: list[GameInfo] = []


class SignInResult(NamedTuple):
    game_id: str
    status: str                     # success / already / failed / captcha / skipped
    reward: str
    message: str
    raw: dict | None = None


class BaseGamePlugin(ABC):
    """所有游戏签到插件的基类.

    每个插件代表一个游戏平台（如米游社、库洛），
    内部通过 games/ 目录下的子类区分不同的游戏。
    """

    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """插件元信息."""

    @abstractmethod
    async def validate_credentials(self, credentials: dict) -> bool:
        """验证凭据是否有效.

        Args:
            credentials: 解密后的凭据字典，插件自行定义格式。
        """

    @abstractmethod
    async def sign_in(self, credentials: dict, game_id: str) -> list[SignInResult]:
        """单个游戏的签到.

        Args:
            credentials: 解密后的凭据字典。
            game_id: 插件内游戏标识，如 "genshin"。

        Returns:
            该游戏所有角色/账号的签到结果列表。
        """

    @abstractmethod
    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        """该用户在本插件下所有游戏的签到.

        Returns:
            {game_id: [SignInResult, ...]}
        """

    @abstractmethod
    async def get_user_info(self, credentials: dict) -> dict:
        """获取用户展示信息.

        Returns:
            {"nickname": "...", "avatar": "...", "level": 1}
        """

    async def forum_tasks(self, credentials: dict) -> list[SignInResult]:
        """论坛每日任务（可选实现）."""
        return []

    async def validate_all(self, credentials: dict) -> dict:
        """验证凭据有效性，返回该用户在所有游戏中的绑定信息（可选实现）."""
        return {}
