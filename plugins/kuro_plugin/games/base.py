"""库洛游戏签到基类."""

from abc import abstractmethod
from datetime import datetime

from plugins.kuro_plugin.client import KuroApiError, KuroHttpClient
from plugins.kuro_plugin.models import KuroGameType


class KuroBaseGame:
    """单个库洛游戏的签到逻辑.

    子类: WuwaGame, PGRGame
    """

    game_type: KuroGameType
    display_name: str

    def __init__(self, client: KuroHttpClient) -> None:
        self.client = client

    async def sign_in(
        self, role_id: str, user_id: str, auto_replenish: bool = True,
    ) -> dict:
        """执行签到.

        Returns:
            {"status": "success"|"already"|"failed", "reward": "...", "message": "..."}
        """
        month = datetime.now().strftime("%m")

        data = {
            "gameId": self.game_type.value,
            "serverId": self.game_type.server_id,
            "roleId": role_id,
            "userId": user_id,
            "reqMonth": month,
        }

        try:
            resp = await self.client.game_post("/encourage/signIn/v2", data)
        except KuroApiError as e:
            return {"status": "failed", "reward": "", "message": str(e)}

        code = resp.get("code")

        if code == 200:
            reward = await self._get_sign_reward(user_id, role_id)
            return {"status": "success", "reward": reward, "message": resp.get("msg", "签到成功")}

        if code == 1511:
            return {"status": "already", "reward": "", "message": "今日已签到"}

        if code == 1513:
            return {"status": "failed", "reward": "", "message": "用户信息错误"}

        if code == 220:
            return {"status": "failed", "reward": "", "message": "Token 已过期"}

        return {"status": "failed", "reward": "", "message": resp.get("msg", f"code={code}")}

    async def _get_sign_reward(self, user_id: str, role_id: str) -> str:
        """获取签到奖励名称."""
        month = datetime.now().strftime("%m")
        try:
            resp = await self.client.game_post("/encourage/signIn/queryRecordV2", {
                "gameId": self.game_type.value,
                "serverId": self.game_type.server_id,
                "roleId": role_id,
                "userId": user_id,
                "reqMonth": month,
            })
            goods_list = resp.get("data", {}).get("signInRecordList", [])
            if goods_list:
                return goods_list[-1].get("goodsName", "")
        except Exception:
            pass
        return ""


class WuwaGame(KuroBaseGame):
    game_type = KuroGameType.WUWA
    display_name = "鸣潮"


class PGRGame(KuroBaseGame):
    game_type = KuroGameType.PGR
    display_name = "战双帕弥什"
