"""Core package."""

from app.core.plugin_base import BaseGamePlugin, GameInfo, PluginInfo, SignInResult
from app.core.plugin_loader import PluginLoader, get_plugin_loader

__all__ = [
    "BaseGamePlugin",
    "GameInfo",
    "PluginInfo",
    "SignInResult",
    "PluginLoader",
    "get_plugin_loader",
]
