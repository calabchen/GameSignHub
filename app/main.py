"""GameSignHub — FastAPI 入口."""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.orchestrator import Orchestrator
from app.core.plugin_loader import PluginLoader
from app.core.scheduler import SignScheduler
from app.core.yaml_store import YamlStore
from app.database import get_session_factory, init_db
from app.routers import auth as auth_router
from app.routers import credentials as credentials_router
from app.routers import logs as logs_router
from app.routers import plugins as plugins_router
from app.routers import schedule as schedule_router
from app.routers import sign as sign_router
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    await init_db()

    session_factory = get_session_factory()
    yaml_store = YamlStore(str(settings.config_dir))

    _auto_import_login_json(yaml_store)

    loader = PluginLoader()
    plugin_registry = loader.load_all()

    orchestrator = Orchestrator(plugin_registry, yaml_store, session_factory)

    scheduler = SignScheduler(session_factory)
    scheduler.set_sign_once_fn(lambda pid, cid, gid: orchestrator.sign_once(pid, cid, gid))
    scheduler.set_sign_all_fn(orchestrator.sign_all)
    scheduler.set_yaml_store(yaml_store)
    await scheduler.start()

    app.state.yaml_store = yaml_store
    app.state.plugin_registry = plugin_registry
    app.state.orchestrator = orchestrator
    app.state.scheduler = scheduler
    app.state.is_unlocked = False

    print(f"GameSignHub 启动完成。已加载 {len(plugin_registry)} 个游戏社区: {list(plugin_registry.keys())}")
    yield

    await scheduler.shutdown()
    print("GameSignHub 正在关闭...")


def _auto_import_login_json(store: YamlStore) -> None:
    login_path = Path("login_data.json")
    if not login_path.exists():
        return

    try:
        raw = json.loads(login_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    existing = store.list_by_plugin("kuro")
    if existing:
        return

    credential_data = {
        "enable": True,
        "enabled_games": ["wuwa"],
        "user_id": str(raw.get("userId", "")),
        "token": raw.get("token", ""),
        "devcode": raw.get("deviceCode", ""),
        "distinct_id": raw.get("distinctId", ""),
        "wuwa": {
            "role_id": str(raw.get("roleId", "")),
            "enabled": True,
            "schedule_cron": "",
            "schedule_enabled": False,
        },
        "pgr": {
            "role_id": "",
            "enabled": False,
            "schedule_cron": "",
            "schedule_enabled": False,
        },
    }

    cid = store.save("kuro", credential_data)
    print(f"已导入 login_data.json → config/kuro/{cid}.yaml")
    try:
        login_path.unlink()
    except OSError:
        pass


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="GameSignHub",
        description="多游戏社区签到可视化管理工具",
        version="0.4.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8001",
            "http://127.0.0.1:8001",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router)
    app.include_router(plugins_router.router)
    app.include_router(credentials_router.router)
    app.include_router(sign_router.router)
    app.include_router(logs_router.router)
    app.include_router(schedule_router.router)

    dist_path = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if dist_path.exists():
        app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")

    @app.get("/version", include_in_schema=False)
    async def version():
        return {"name": "GameSignHub", "version": "0.4.0", "status": "running"}

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
