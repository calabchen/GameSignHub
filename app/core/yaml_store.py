"""YAML 文件凭据存储 — config/{plugin_id}/{id}.yaml."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("app.yaml_store")

DEFAULT_CONFIG_DIR = "config"


class YamlStore:
    def __init__(self, config_dir: str = DEFAULT_CONFIG_DIR) -> None:
        self._root = Path(config_dir)

    def _dir(self, plugin_id: str) -> Path:
        return self._root / plugin_id

    def _path(self, plugin_id: str, cred_id: int) -> Path:
        return self._dir(plugin_id) / f"{cred_id}.yaml"

    def list_all(self) -> list[dict]:
        result = []
        if not self._root.exists():
            return result
        for plugin_dir in sorted(self._root.iterdir()):
            if not plugin_dir.is_dir():
                continue
            plugin_id = plugin_dir.name
            for yaml_file in sorted(plugin_dir.glob("*.yaml")):
                try:
                    cred_id = int(yaml_file.stem)
                except ValueError:
                    continue
                data = self._read_file(yaml_file)
                result.append({
                    "id": cred_id,
                    "plugin_id": plugin_id,
                    "user_id": data.get("user_id", ""),
                    "is_enabled": data.get("enable", True),
                    "wuwa_role_id": (data.get("wuwa", {}) or {}).get("role_id", ""),
                    "pgr_role_id": (data.get("pgr", {}) or {}).get("role_id", ""),
                })
        return result

    def list_by_plugin(self, plugin_id: str) -> list[dict]:
        return [a for a in self.list_all() if a["plugin_id"] == plugin_id]

    def get(self, plugin_id: str, cred_id: int) -> dict | None:
        p = self._path(plugin_id, cred_id)
        if not p.exists():
            return None
        data = self._read_file(p)
        data["id"] = cred_id
        data["plugin_id"] = plugin_id
        return data

    def get_all_with_schedules(self) -> list[dict]:
        result = []
        for a in self.list_all():
            data = self.get(a["plugin_id"], a["id"])
            if data is None:
                continue
            for game_id in ("wuwa", "pgr"):
                g = data.get(game_id, {}) or {}
                if g.get("schedule_cron") and g.get("schedule_enabled"):
                    result.append({
                        "id": a["id"],
                        "plugin_id": a["plugin_id"],
                        "game_id": game_id,
                        "schedule_cron": g["schedule_cron"],
                    })
        return result

    def next_id(self, plugin_id: str) -> int:
        d = self._dir(plugin_id)
        if not d.exists():
            return 1
        ids = [int(f.stem) for f in d.glob("*.yaml") if f.stem.isdigit()]
        return max(ids, default=0) + 1

    def save(self, plugin_id: str, data: dict, cred_id: int | None = None) -> int:
        if cred_id is None:
            cred_id = self.next_id(plugin_id)

        out = {
            "enable": data.get("enable", data.get("is_enabled", True)),
            "user_id": data.get("user_id", ""),
            "token": data.get("token", ""),
            "devcode": data.get("devcode", ""),
            "distinct_id": data.get("distinct_id", ""),
            "wuwa": data.get("wuwa", {"role_id": "", "enabled": True, "schedule_cron": "", "schedule_enabled": False}),
            "pgr": data.get("pgr", {"role_id": "", "enabled": False, "schedule_cron": "", "schedule_enabled": False}),
        }

        d = self._dir(plugin_id)
        d.mkdir(parents=True, exist_ok=True)
        p = self._path(plugin_id, cred_id)
        with open(p, "w", encoding="utf-8") as f:
            yaml.dump(out, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        logger.info("Saved config/%s/%d.yaml", plugin_id, cred_id)
        return cred_id

    def delete(self, plugin_id: str, cred_id: int) -> None:
        p = self._path(plugin_id, cred_id)
        if p.exists():
            p.unlink()
            logger.info("Deleted config/%s/%d.yaml", plugin_id, cred_id)

    def update_schedule(self, plugin_id: str, cred_id: int, game_id: str, cron: str, enabled: bool) -> bool:
        data = self.get(plugin_id, cred_id)
        if data is None:
            return False
        g = data.setdefault(game_id, {})
        g["schedule_cron"] = cron
        g["schedule_enabled"] = enabled
        self.save(plugin_id, data, cred_id)
        return True

    @staticmethod
    def _read_file(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
