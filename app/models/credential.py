"""加密凭据存储模型."""

import json
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(Text, default="")
    encrypted_data: Mapped[bytes] = mapped_column(nullable=False)

    _enabled_games: Mapped[str] = mapped_column("enabled_games", Text, default="[]")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )

    @property
    def enabled_games(self) -> list[str]:
        return json.loads(self._enabled_games) if self._enabled_games else []

    @enabled_games.setter
    def enabled_games(self, value: list[str]) -> None:
        self._enabled_games = json.dumps(value)

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "plugin_id": self.plugin_id,
            "display_name": self.display_name,
            "enabled_games": self.enabled_games,
            "is_enabled": self.is_enabled,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
