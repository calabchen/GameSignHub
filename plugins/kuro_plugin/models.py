"""库洛插件内部数据类."""

from dataclasses import dataclass, field
from enum import Enum

API_BASE = "https://api.kurobbs.com"


class KuroGameType(Enum):
    PGR = "2"      # 战双帕弥什
    WUWA = "3"     # 鸣潮

    @property
    def server_id(self) -> str:
        if self == KuroGameType.PGR:
            return "1000"
        return "76402e5b20be2c39f095a152090afddc"

    @property
    def name(self) -> str:
        if self == KuroGameType.PGR:
            return "战双帕弥什"
        return "鸣潮"


@dataclass
class GameRole:
    role_id: str
    role_name: str = ""
    server_name: str = ""


@dataclass
class KuroCredentials:
    token: str
    devcode: str = ""
    distinct_id: str = ""

    def to_dict(self) -> dict:
        return {
            "token": self.token,
            "devcode": self.devcode,
            "distinct_id": self.distinct_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KuroCredentials":
        return cls(
            token=data.get("token", ""),
            devcode=data.get("devcode", ""),
            distinct_id=data.get("distinct_id", ""),
        )
