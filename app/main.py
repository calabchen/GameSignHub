"""GameSignHub — FastAPI 入口.

本地多游戏社区签到可视化管理工具。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.plugin_loader import PluginLoader
from app.core.vault import Vault
from app.database import get_session_factory, init_db
from app.routers import auth as auth_router
from app.routers import plugins as plugins_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化 DB + 加载插件 + 创建 Vault."""
    settings = get_settings()

    # 初始化数据库表
    await init_db()

    # 创建凭据保险库
    session_factory = get_session_factory()
    vault = Vault(session_factory)

    # 加载插件
    loader = PluginLoader()
    plugin_registry = loader.load_all()

    # 注入到 app.state
    app.state.vault = vault
    app.state.plugin_registry = plugin_registry
    app.state.is_unlocked = False

    print(f"GameSignHub 启动完成。已加载 {len(plugin_registry)} 个插件: {list(plugin_registry.keys())}")
    yield

    # 关闭时清理
    vault.lock()
    print("GameSignHub 正在关闭...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="GameSignHub",
        description="多游戏社区签到可视化管理工具",
        version="0.2.0",
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
    app.include_router(auth_router.router)
    app.include_router(plugins_router.router)

    # 根路径
    @app.get("/")
    async def root():
        return {"name": "GameSignHub", "version": "0.2.0", "status": "running"}

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
