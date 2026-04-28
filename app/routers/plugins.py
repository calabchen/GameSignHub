"""插件列表 API."""

from fastapi import APIRouter, Request

from app.core.plugin_base import BaseGamePlugin

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@router.get("")
async def list_plugins(request: Request) -> list[dict]:
    """返回所有已加载的插件列表."""
    registry: dict[str, BaseGamePlugin] = request.app.state.plugin_registry
    result = []
    for plugin_id, plugin in registry.items():
        info = plugin.plugin_info
        result.append({
            "id": info.id,
            "name": info.name,
            "version": info.version,
            "description": info.description,
            "homepage": info.homepage,
            "supported_games": [
                {"id": g.id, "name": g.name, "has_forum": g.has_forum}
                for g in info.supported_games
            ],
        })
    return result


@router.get("/{plugin_id}")
async def get_plugin(request: Request, plugin_id: str) -> dict:
    """返回单个插件详情."""
    registry: dict[str, BaseGamePlugin] = request.app.state.plugin_registry

    plugin = registry.get(plugin_id)
    if plugin is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")

    info = plugin.plugin_info
    return {
        "id": info.id,
        "name": info.name,
        "version": info.version,
        "description": info.description,
        "homepage": info.homepage,
        "supported_games": [
            {"id": g.id, "name": g.name, "has_forum": g.has_forum}
            for g in info.supported_games
        ],
    }
