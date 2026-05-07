import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi import FastAPI
import httpx

from app.core.config import Settings, get_settings
from app.core import crud_yaml
from app.core.crud_log import CREATE_TABLE_SQL
from app.core.orchestrator import Orchestrator
from app.core.plugin_base import BaseGamePlugin, PluginInfo, GameInfo, SignInResult

import app.core.db as _db
import app.core.config as _cfg


@pytest_asyncio.fixture(autouse=True)
async def _reset_module_state():
    _db._engine = None
    _db._session_factory = None
    _cfg.get_settings.cache_clear()
    crud_yaml.reset_store()
    yield
    _db._engine = None
    _db._session_factory = None
    _cfg.get_settings.cache_clear()
    crud_yaml.reset_store()


@pytest_asyncio.fixture
async def test_session_factory(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    test_settings = Settings(database_url=db_url, secret_key="test-jwt-secret-key", config_dir=tmp_path / "config")
    monkeypatch.setattr(_cfg, "get_settings", lambda: test_settings)

    engine = create_async_engine(db_url, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))

    factory = async_sessionmaker(engine, expire_on_commit=False)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    crud_yaml.init_store(str(tmp_path / "config"))
    yield factory

    await engine.dispose()


@pytest_asyncio.fixture
async def yaml_store():
    return crud_yaml


@pytest_asyncio.fixture(autouse=True)
def _reset_yaml_store():
    crud_yaml.reset_store()


class _MockPlugin(BaseGamePlugin):
    def __init__(self, plugin_id="mock", name="MockPlugin", games=None):
        self._info = PluginInfo(
            id=plugin_id,
            name=name,
            version="0.1.0",
            description="Mock plugin for testing",
            homepage=None,
            supported_games=games or [
                GameInfo(id="game1", name="Test Game", has_forum=False),
            ],
        )

    @property
    def plugin_info(self):
        return self._info

    async def validate_credentials(self, credentials):
        return True

    async def sign_in(self, credentials, game_id):
        return [SignInResult(game_id, "success", "100 coins", "OK")]

    async def sign_in_all(self, credentials):
        return {"game1": [SignInResult("game1", "success", "100 coins", "OK")]}

    async def get_user_info(self, credentials):
        return {"nickname": "test_user"}


@pytest_asyncio.fixture
def mock_plugin_registry():
    return {"mock": _MockPlugin()}


@pytest_asyncio.fixture
async def test_app(test_session_factory, mock_plugin_registry, tmp_path):
    from app.core.security import create_access_token

    orchestrator = Orchestrator(mock_plugin_registry, test_session_factory)

    token = create_access_token()

    app = FastAPI()
    app.state.plugin_registry = mock_plugin_registry
    app.state.orchestrator = orchestrator
    app.state.scheduler = type("obj", (), {"remove_credential": lambda s, x: None, "register": lambda s, *a: None})()
    app.state.is_unlocked = True

    from app.routers import accounts as accounts_router
    from app.routers import sign as sign_router
    app.include_router(accounts_router.router)
    app.include_router(sign_router.router)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
