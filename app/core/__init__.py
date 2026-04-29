"""Core package."""

from app.core.auth import (
    create_access_token,
    derive_encryption_key,
    hash_password,
    verify_access_token,
    verify_password,
)
from app.core.orchestrator import Orchestrator
from app.core.plugin_base import BaseGamePlugin, GameInfo, PluginInfo, SignInResult
from app.core.plugin_loader import PluginLoader, get_plugin_loader
from app.core.vault import Vault, VaultLockedError

__all__ = [
    "BaseGamePlugin",
    "GameInfo",
    "PluginInfo",
    "SignInResult",
    "Orchestrator",
    "PluginLoader",
    "get_plugin_loader",
    "Vault",
    "VaultLockedError",
    "create_access_token",
    "verify_access_token",
    "derive_encryption_key",
    "hash_password",
    "verify_password",
]
