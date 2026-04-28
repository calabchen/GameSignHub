"""GameSignHub — FastAPI 入口.

本地多游戏社区签到可视化管理工具。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.plugin_loader import PluginLoader
from app.database import init_db
from app.routers.plugins import router as plugins_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化 DB + 加载插件."""
    settings = get_settings()

    # 初始化数据库表
    await init_db()

    # 加载插件
    loader = PluginLoader()
    plugin_registry = loader.load_all()

    # 注入到 app.state
    app.state.plugin_registry = plugin_registry
    app.state.is_unlocked = False

    print(f"GameSignHub 启动完成。已加载 {len(plugin_registry)} 个插件: {list(plugin_registry.keys())}")
    yield

    # 关闭时清理
    print("GameSignHub 正在关闭...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="GameSignHub",
        description="多游戏社区签到可视化管理工具",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — 仅本地访问，允许前端 dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(plugins_router)

    # 根路径
    @app.get("/")
    async def root():
        return {"name": "GameSignHub", "version": "0.1.0", "status": "running"}

    # 健康检查
    @app.get("/api/status")
    async def status(request: Request):
        return {
            "status": "running",
            "is_unlocked": request.app.state.is_unlocked,
            "plugins_loaded": len(request.app.state.plugin_registry),
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
