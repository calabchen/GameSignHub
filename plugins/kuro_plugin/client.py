"""库街区 API HTTP 客户端.

三套 Header 配置，模拟不同客户端:
  1. BBS Headers — iOS KuroGameBox app, 用于论坛操作
  2. Game Headers — iOS Safari WebKit, 用于游戏签到
  3. User Info Headers — Android OkHttp, 用于用户信息查询

Header 投放规则 (严格仿原 Kuro-autosignin):
  | 字段        | BBS          | GAME              | USER_INFO   |
  |-------------|--------------|-------------------|-------------|
  | Cookie      | user_token=  | —                 | —           |
  | Ip          | 真实 IP      | —                 | 模板自带假IP |
  | distinct_id | ✅           | —                 | ✅          |
  | devCode(大写)| UUID         | "{ip}, UA string" | —           |
  | devcode(小写)| —             | —                 | UUID        |
  | token       | ✅           | ✅                | ✅          |
"""

import json
import socket
import uuid
from typing import Any

import httpx

from plugins.kuro_plugin.models import API_BASE, KuroCredentials

# ---------------------------------------------------------------------------
# Header templates (仅静态部分)
# ---------------------------------------------------------------------------

_COMMON = {
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

BBS_TEMPLATE = {
    "Host": "api.kurobbs.com",
    "source": "ios",
    "lang": "zh-Hans",
    "User-Agent": "KuroGameBox/2.2.0 (iPhone; iOS 17.3; Scale/3.00)",
    "channelId": "1",
    "channel": "appstore",
    "version": "2.2.0",
    "model": "iPhone15,2",
    "osVersion": "17.3",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    **_COMMON,
}

GAME_TEMPLATE = {
    "Host": "api.kurobbs.com",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "source": "ios",
    "Origin": "https://web-static.kurobbs.com",
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://web-static.kurobbs.com/",
    **_COMMON,
}

USER_INFO_TEMPLATE = {
    "osversion": "Android",
    "countrycode": "CN",
    "ip": "10.0.2.233",
    "model": "2211133C",
    "source": "android",
    "lang": "zh-Hans",
    "version": "1.0.9",
    "versioncode": "1090",
    "content-type": "application/x-www-form-urlencoded",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/3.10.0",
}


class KuroHttpClient:
    """库洛论坛/游戏 API 异步 HTTP 客户端."""

    def __init__(self, credentials: KuroCredentials) -> None:
        self._token = credentials.token
        self._devcode = credentials.devcode or str(uuid.uuid4())
        self._distinct_id = credentials.distinct_id or str(uuid.uuid4())
        self._ip = _get_ip()

    def update_credentials(self, credentials: KuroCredentials) -> None:
        self._token = credentials.token
        self._devcode = credentials.devcode or self._devcode
        self._distinct_id = credentials.distinct_id or self._distinct_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def bbs_post(self, path: str, data: dict | None = None) -> dict[str, Any]:
        return await self._request("POST", path, data, self._bbs_headers())

    async def game_post(self, path: str, data: dict | None = None) -> dict[str, Any]:
        return await self._request("POST", path, data, self._game_headers())

    async def user_info_post(self, path: str, data: dict | None = None) -> dict[str, Any]:
        return await self._request("POST", path, data, self._user_info_headers())

    async def get_user_id(self) -> str:
        """获取库洛社区 userId."""
        resp = await self.user_info_post("/user/mineV2")
        code = resp.get("code")
        if code != 200:
            raise KuroApiError(code, resp.get("msg", ""))
        return resp["data"]["mine"]["userId"]

    async def get_game_roles(self, game_id: str) -> list[dict]:
        """获取指定游戏的绑定角色列表."""
        resp = await self.user_info_post(
            "/user/role/findRoleList",
            data={"gameId": game_id},
        )
        code = resp.get("code")
        if code != 200:
            raise KuroApiError(code, resp.get("msg", ""))
        data = resp.get("data", [])
        return data if isinstance(data, list) else []

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _bbs_headers(self) -> dict:
        h = dict(BBS_TEMPLATE)
        h["Cookie"] = f"user_token={self._token}"
        h["Ip"] = self._ip
        h["distinct_id"] = self._distinct_id
        h["devCode"] = self._devcode
        h["token"] = self._token
        return h

    def _game_headers(self) -> dict:
        ua = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) KuroGameBox/2.2.0"
        )
        h = dict(GAME_TEMPLATE)
        h["devCode"] = f"{self._ip}, {ua}"
        h["token"] = self._token
        return h

    def _user_info_headers(self) -> dict:
        h = dict(USER_INFO_TEMPLATE)
        h["devcode"] = self._devcode
        h["distinct_id"] = self._distinct_id
        h["token"] = self._token
        return h

    async def _request(
        self, method: str, path: str, data: dict | None, headers: dict,
    ) -> dict[str, Any]:
        url = f"{API_BASE}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "POST":
                resp = await client.post(url, data=data, headers=headers)
            else:
                resp = await client.get(url, params=data, headers=headers)
        if resp.status_code != 200:
            raise KuroApiError(-1, f"HTTP {resp.status_code}")
        try:
            return resp.json()
        except json.JSONDecodeError:
            raise KuroApiError(-1, f"invalid JSON: {resp.text[:200]}")


class KuroApiError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


def _get_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
