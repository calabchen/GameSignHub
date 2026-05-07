"""依赖注入 — 认证与鉴权."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_access_token

_security = HTTPBearer()


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(_security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="未授权")


def require_unlocked(request: Request, _=Depends(require_auth)):
    if not request.app.state.is_unlocked:
        raise HTTPException(status_code=403, detail="请先解锁")
