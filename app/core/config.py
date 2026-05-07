"""Pydantic Settings — 环境变量与全局配置管理."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_project_root() -> Path:
    return _PROJECT_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///app/config/gamesignhub.db"
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = ""
    log_level: str = "INFO"
    config_dir: Path = Path("app/config")
    plugins_dir: Path = Path("plugins")
    user_plugins_dir: Path = Path("user_plugins")
    max_sign_retries: int = 3

    def model_post_init(self, __context):
        root = get_project_root()
        for attr in ("config_dir", "plugins_dir", "user_plugins_dir"):
            p: Path = getattr(self, attr)
            if not p.is_absolute():
                setattr(self, attr, root / p)

    @property
    def resolved_database_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            db_path = self.database_url.replace("sqlite+aiosqlite:///", "")
            p = Path(db_path)
            if not p.is_absolute():
                p = get_project_root() / p
            p.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{p}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
