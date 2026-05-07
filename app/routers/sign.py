"""签到触发 API。"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_access_token
from app.core.orchestrator import Orchestrator
from app.schemas import SignInResponse

router = APIRouter(prefix="/api/signs", tags=["sign"])
security = HTTPBearer()


def _auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="未授权")


@router.post("/plugins/{plugin_id}/credentials/{cred_id}/games/{game_id}", response_model=SignInResponse)
async def sign_once(request: Request, plugin_id: str, cred_id: int, game_id: str, _=Depends(_auth)):
    oc: Orchestrator = request.app.state.orchestrator
    try:
        logs = await oc.sign_once(plugin_id, cred_id, game_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _logs_to_response(logs)


@router.post("/plugins/{plugin_id}", response_model=SignInResponse)
async def sign_plugin_all(request: Request, plugin_id: str, _=Depends(_auth)):
    oc: Orchestrator = request.app.state.orchestrator
    try:
        all_logs = await oc.sign_plugin(plugin_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    combined: dict[str, list] = {}
    for log in all_logs:
        key = log["game_id"]
        combined.setdefault(key, []).append({
            "game_id": log["game_id"],
            "status": log["status"],
            "reward": log["reward"],
            "message": log["message"],
        })
    return SignInResponse(results=combined)


def _logs_to_response(logs) -> SignInResponse:
    results: dict[str, list] = {}
    for log in logs:
        key = log["game_id"]
        results.setdefault(key, []).append({
            "game_id": log["game_id"],
            "status": log["status"],
            "reward": log["reward"],
            "message": log["message"],
        })
    return SignInResponse(results=results)
