"""签到日志 — 表定义 + 查询函数。"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

CREATE_TABLE_SQL = """\
CREATE TABLE IF NOT EXISTS sign_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credential_id INTEGER,
    credential_name TEXT DEFAULT '',
    plugin_id TEXT NOT NULL,
    game_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reward TEXT DEFAULT '',
    message TEXT DEFAULT '',
    raw_response TEXT DEFAULT '',
    elapsed FLOAT DEFAULT 0.0,
    signed_at TIMESTAMP,
    created_at TIMESTAMP
)"""

MIGRATIONS = [
    "ALTER TABLE sign_logs ADD COLUMN elapsed FLOAT DEFAULT 0.0 NOT NULL",
]


async def get_logs(
    session_factory: async_sessionmaker,
    page: int = 1,
    page_size: int = 20,
    plugin_id: str | None = None,
    game_id: str | None = None,
    status: str | None = None,
    credential_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> tuple[list[dict], int]:
    wheres = []
    params: dict = {}

    if plugin_id:
        wheres.append("plugin_id = :plugin_id")
        params["plugin_id"] = plugin_id
    if game_id:
        wheres.append("game_id = :game_id")
        params["game_id"] = game_id
    if status:
        wheres.append("status = :status")
        params["status"] = status
    if credential_id:
        wheres.append("credential_id = :credential_id")
        params["credential_id"] = credential_id
    if date_from:
        wheres.append("signed_at >= :date_from")
        params["date_from"] = date_from
    if date_to:
        wheres.append("signed_at <= :date_to")
        params["date_to"] = date_to + " 23:59:59"

    where_clause = " AND ".join(wheres) if wheres else "1=1"

    async with session_factory() as session:
        r = await session.execute(
            text(f"SELECT COUNT(*) FROM sign_logs WHERE {where_clause}"),
            params,
        )
        total = r.scalar_one()

        r = await session.execute(
            text(f"SELECT * FROM sign_logs WHERE {where_clause} ORDER BY signed_at DESC LIMIT :limit OFFSET :offset"),
            {
                **params,
                "limit": page_size,
                "offset": (page - 1) * page_size,
            },
        )
        rows = [dict(row._mapping) for row in r]

    return rows, total


async def get_today_summary(
    session_factory: async_sessionmaker,
) -> dict:
    async with session_factory() as session:
        r = await session.execute(text("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'already' THEN 1 ELSE 0 END) as already,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM sign_logs
            WHERE date(signed_at) = date('now', 'localtime')
        """))
        row = dict(r.one()._mapping)
    return {
        "total": row["total"] or 0,
        "success": row["success"] or 0,
        "already": row["already"] or 0,
        "failed": row["failed"] or 0,
    }


async def clear_logs(
    session_factory: async_sessionmaker,
) -> None:
    async with session_factory() as session:
        await session.execute(text("DELETE FROM sign_logs"))
        await session.commit()
