"""签到触发 API。"""

from fastapi import APIRouter, HTTPException, Request

from app.core.orchestrator import Orchestrator
from app.schemas.sign import SignInResponse

router = APIRouter(prefix="/api/signs", tags=["sign"])


def _get_orchestrator(request: Request) -> Orchestrator:
    oc: Orchestrator = request.app.state.orchestrator
    if oc is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return oc


@router.post("/plugins/{plugin_id}/credentials/{cred_id}/games/{game_id}", response_model=SignInResponse)
async def sign_onces(request: Request, plugin_id: str, cred_id: int, game_id: str):
    """触发游戏社区签到，在单游戏社区与单游戏账户下执行一次。"""
    oc = _get_orchestrator(request)
    try:
        logs = await oc.sign_once(plugin_id, cred_id, game_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _logs_to_response(logs)


def _logs_to_response(logs) -> SignInResponse:
    results: dict[str, list] = {}
    for log in logs:
        key = log.game_id
        results.setdefault(key, []).append(
            {
                "game_id": log.game_id,
                "status": log.status,
                "reward": log.reward,
                "message": log.message,
            }
        )
    return SignInResponse(results=results)
