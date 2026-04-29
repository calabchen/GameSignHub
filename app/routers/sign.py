"""签到触发 API."""

from fastapi import APIRouter, HTTPException, Request

from app.core.orchestrator import Orchestrator
from app.schemas.sign import SignInResponse, SignInStatus

router = APIRouter(prefix="/api/sign", tags=["sign"])


def _get_orchestrator(request: Request) -> Orchestrator:
    oc: Orchestrator = request.app.state.orchestrator
    if oc is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return oc


@router.post("/credential/{cred_id}", response_model=SignInResponse)
async def sign_credential(request: Request, cred_id: int):
    """单个凭据签到."""
    oc = _get_orchestrator(request)
    vault = request.app.state.vault

    for plugin_id, creds in vault.get_all_credentials().items():
        for c in creds:
            if c["id"] == cred_id:
                logs = await oc.sign_credential(plugin_id, cred_id)
                return _logs_to_response(logs)

    raise HTTPException(status_code=404, detail="Credential not found")


@router.post("/plugin/{plugin_id}", response_model=SignInResponse)
async def sign_plugin(request: Request, plugin_id: str):
    """某个插件的全部用户签到."""
    oc = _get_orchestrator(request)
    try:
        logs = await oc.sign_plugin(plugin_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _logs_to_response(logs)


@router.post("/all", response_model=SignInResponse)
async def sign_all(request: Request):
    """所有插件的所有用户签到."""
    oc = _get_orchestrator(request)
    logs = await oc.sign_all()
    return _logs_to_response(logs)


@router.get("/status", response_model=SignInStatus)
async def sign_status(request: Request):
    """当前签到进度."""
    oc = _get_orchestrator(request)
    return SignInStatus(is_running=oc.is_running)


def _logs_to_response(logs) -> SignInResponse:
    results: dict[str, list] = {}
    for log in logs:
        key = log.game_id
        results.setdefault(key, []).append({
            "game_id": log.game_id,
            "status": log.status,
            "reward": log.reward,
            "message": log.message,
        })
    return SignInResponse(results=results)
