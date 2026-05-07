"""SQLAlchemy async engine and session management — 仅用于签到日志."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.crud_log import CREATE_TABLE_SQL, MIGRATIONS

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.resolved_database_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))
        for sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass
