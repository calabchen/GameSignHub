"""库洛插件内部数据类."""

from dataclasses import dataclass, field
from enum import Enum

API_BASE = "https://api.kurobbs.com"


class KuroGameType(Enum):
    PGR = "2"
    WUWA = "3"

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
    user_id: str = ""
    roles: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "token": self.token,
            "devcode": self.devcode,
            "distinct_id": self.distinct_id,
            "user_id": self.user_id,
            "roles": self.roles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KuroCredentials":
        roles = cls._parse_roles(data)
        return cls(
            token=data.get("token", ""),
            devcode=data.get("devcode") or data.get("deviceCode", ""),
            distinct_id=data.get("distinct_id") or data.get("distinctId", ""),
            user_id=str(data.get("user_id") or data.get("userId", "")),
            roles=roles,
        )

    @staticmethod
    def _parse_roles(data: dict) -> list[dict]:
        roles = []
        for game_id in ("wuwa", "pgr"):
            g = data.get(game_id, {})
            if isinstance(g, dict) and g.get("role_id"):
                roles.append({"id": str(g["role_id"]), "tag": game_id})
        if not roles:
            old_role = data.get("role_id") or data.get("wuwa_role_id") or data.get("roleId") or data.get("wwroleId") or ""
            if old_role:
                roles.append({"id": str(old_role), "tag": ""})
            old_pgr = data.get("pgr_role_id") or data.get("eeeroleId") or ""
            if old_pgr and old_pgr != old_role:
                roles.append({"id": str(old_pgr), "tag": ""})
        return roles

    def get_role_ids(self, game_id: str) -> list[str]:
        matching = [r["id"] for r in self.roles if r.get("tag") == game_id]
        if matching:
            return matching
        untagged = [r["id"] for r in self.roles if not r.get("tag")]
        if untagged:
            return untagged
        return []
