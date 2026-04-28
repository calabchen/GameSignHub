"""插件加载器 — 扫描并加载所有 GamePlugin 实现."""

import sys
from pathlib import Path

from app.config import get_settings
from app.core.plugin_base import BaseGamePlugin


class PluginLoader:
    """插件发现、加载与注册.

    两种加载来源:
    1. plugins/ 目录 — 官方内置插件
    2. user_plugins/ 目录 — 用户手动安装的第三方插件
    """

    def __init__(self) -> None:
        self._plugins: dict[str, BaseGamePlugin] = {}

    def load_all(self) -> dict[str, BaseGamePlugin]:
        """加载所有来源的插件，去重 (内置优先)."""
        self._plugins = {}

        # 1. 官方内置插件 (plugins/ 目录)
        self._load_from_directory(
            get_settings().plugins_dir,
            priority="builtin",
        )

        # 2. 用户第三方插件 (user_plugins/ 目录)
        self._load_from_directory(
            get_settings().user_plugins_dir,
            priority="user",
        )

        return self._plugins

    def _load_from_directory(self, directory: Path, priority: str) -> None:
        """扫描目录下含 plugin.py 的子包，加载 BaseGamePlugin 子类."""
        if not directory.exists():
            return

        sys.path.insert(0, str(directory.parent))

        for pkg_path in directory.iterdir():
            if not pkg_path.is_dir():
                continue
            if pkg_path.name.startswith("_"):
                continue

            plugin_module = pkg_path / "plugin.py"
            if not plugin_module.exists():
                continue

            try:
                pkg = __import__(
                    f"{directory.name}.{pkg_path.name}.plugin",
                    fromlist=["*"],
                )
                plugin_instance = self._find_plugin_class(pkg)
                if plugin_instance is None:
                    continue

                plugin_id = plugin_instance.plugin_info.id

                # 内置插件优先，不覆盖
                if priority == "user" and plugin_id in self._plugins:
                    continue

                self._plugins[plugin_id] = plugin_instance
            except Exception as e:
                # 插件加载失败不应阻止其他插件
                import logging
                logging.getLogger("app").warning(
                    "Failed to load plugin %s: %s", pkg_path.name, e
                )

        sys.path.pop(0)

    @staticmethod
    def _find_plugin_class(module) -> BaseGamePlugin | None:
        """在模块中寻找第一个 BaseGamePlugin 的具体子类."""
        from app.core.plugin_base import BaseGamePlugin as BGP

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BGP)
                and attr is not BGP
            ):
                return attr()
        return None

    def get(self, plugin_id: str) -> BaseGamePlugin | None:
        return self._plugins.get(plugin_id)

    def list_all(self) -> list[BaseGamePlugin]:
        return list(self._plugins.values())

    def get_registry(self) -> dict[str, BaseGamePlugin]:
        return self._plugins.copy()


# 单例工厂
_plugin_loader: PluginLoader | None = None


def get_plugin_loader() -> PluginLoader:
    global _plugin_loader
    if _plugin_loader is None:
        _plugin_loader = PluginLoader()
    return _plugin_loader
