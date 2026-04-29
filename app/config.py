"""Pydantic Settings — 环境变量与全局配置管理."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///config/gamesignhub.db"
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = ""
    log_level: str = "INFO"
    config_dir: Path = Path("config")
    plugins_dir: Path = Path("plugins")
    user_plugins_dir: Path = Path("user_plugins")
    max_sign_retries: int = 3

    @property
    def resolved_database_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            db_path = self.database_url.replace("sqlite+aiosqlite:///", "")
            abs_path = Path(db_path).resolve()
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{abs_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
