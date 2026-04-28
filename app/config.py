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

    # Database
    database_url: str = "sqlite+aiosqlite:///data/gamesignhub.db"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Secret
    secret_key: str = ""

    # Logging
    log_level: str = "INFO"

    # Paths
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")
    plugins_dir: Path = Path("plugins")
    user_plugins_dir: Path = Path("user_plugins")

    # Max retries for sign-in
    max_sign_retries: int = 3

    @property
    def resolved_database_url(self) -> str:
        """Ensure the data directory exists and return absolute db URL."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            db_path = self.database_url.replace("sqlite+aiosqlite:///", "")
            abs_path = Path(db_path).resolve()
            return f"sqlite+aiosqlite:///{abs_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
