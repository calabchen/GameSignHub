"""GameSignHub — FastAPI 入口.

本地多游戏社区签到可视化管理工具。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.orchestrator import Orchestrator
from app.core.plugin_loader import PluginLoader
from app.core.scheduler import SignScheduler
from app.core.vault import Vault, VaultLockedError
from app.database import get_session_factory, init_db
from app.routers import auth as auth_router
from app.routers import credentials as credentials_router
from app.routers import logs as logs_router
from app.routers import plugins as plugins_router
from app.routers import schedule as schedule_router
from app.routers import sign as sign_router


# FastAPI exception handler for VaultLockedError
from fastapi import Request
from fastapi.responses import JSONResponse


async def vault_locked_handler(request: Request, exc: VaultLockedError) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "保险库已锁定，请先解锁"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化 DB + 加载插件 + 创建 Vault + Orchestrator."""
    settings = get_settings()

    # 初始化数据库表
    await init_db()

    # 创建凭据保险库
    session_factory = get_session_factory()
    vault = Vault(session_factory)

    # 首次启动自动设置默认密码 12345678
    if await vault.ensure_default_password():
        print("首次启动，已设置默认密码: 12345678")

    # 加载插件
    loader = PluginLoader()
    plugin_registry = loader.load_all()

    # 创建签到编排器
    orchestrator = Orchestrator(plugin_registry, vault, session_factory)

    # 创建并启动定时调度器
    scheduler = SignScheduler(session_factory)
    scheduler.set_sign_fn(orchestrator.sign_all)
    await scheduler.start()

    # 注入到 app.state
    app.state.vault = vault
    app.state.plugin_registry = plugin_registry
    app.state.orchestrator = orchestrator
    app.state.scheduler = scheduler
    app.state.is_unlocked = False

    print(f"GameSignHub 启动完成。已加载 {len(plugin_registry)} 个插件: {list(plugin_registry.keys())}")
    yield

    # 关闭时清理
    await scheduler.shutdown()
    vault.lock()
    print("GameSignHub 正在关闭...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="GameSignHub",
        description="多游戏社区签到可视化管理工具",
        version="0.3.0",
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

    # 异常处理
    app.add_exception_handler(VaultLockedError, vault_locked_handler)

    # 注册路由
    app.include_router(auth_router.router)
    app.include_router(plugins_router.router)
    app.include_router(credentials_router.router)
    app.include_router(sign_router.router)
    app.include_router(logs_router.router)
    app.include_router(schedule_router.router)

    # 根路径
    @app.get("/")
    async def root():
        return {"name": "GameSignHub", "version": "0.3.0", "status": "running"}

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
