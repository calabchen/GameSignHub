"""YAML 游戏账户存储 — config/{plugin_id}/{account_id}.yaml."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("app.crud_yaml")

_ROOT: Path | None = None


def init_store(config_dir: str) -> None:
    global _ROOT
    _ROOT = Path(config_dir)


def reset_store() -> None:
    global _ROOT
    _ROOT = None


def _dir(plugin_id: str) -> Path:
    assert _ROOT is not None, "crud_yaml not initialized"
    return _ROOT / plugin_id


def _path(plugin_id: str, account_id: int) -> Path:
    return _dir(plugin_id) / f"{account_id}.yaml"


def list_all(*, plugin_id: str | None = None, account_id: int | None = None) -> list[dict]:
    if _ROOT is None or not _ROOT.exists():
        return []
    result = []
    for plugin_dir in sorted(_ROOT.iterdir()):
        if not plugin_dir.is_dir():
            continue
        pid = plugin_dir.name
        if plugin_id is not None and pid != plugin_id:
            continue
        for yaml_file in sorted(plugin_dir.glob("*.yaml")):
            try:
                    aid = int(yaml_file.stem)
            except ValueError:
                continue
            if account_id is not None and aid != account_id:
                continue
            data = _read_file(yaml_file)
            result.append({
                "id": aid,
                "plugin_id": pid,
                "user_id": data.get("user_id", ""),
                "is_enabled": data.get("enable", True),
                "wuwa_role_id": (data.get("wuwa", {}) or {}).get("role_id", ""),
                "pgr_role_id": (data.get("pgr", {}) or {}).get("role_id", ""),
            })
    return result


def get(plugin_id: str, account_id: int) -> dict | None:
    p = _path(plugin_id, account_id)
    if not p.exists():
        return None
    data = _read_file(p)
    data["id"] = account_id
    data["plugin_id"] = plugin_id
    return data


def get_all_with_schedules() -> list[dict]:
    result = []
    for a in list_all():
        data = get(a["plugin_id"], a["id"])
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


def next_id(plugin_id: str) -> int:
    d = _dir(plugin_id)
    if not d.exists():
        return 1
    ids = [int(f.stem) for f in d.glob("*.yaml") if f.stem.isdigit()]
    return max(ids, default=0) + 1


def save(plugin_id: str, data: dict, account_id: int | None = None) -> int:
    if account_id is None:
        account_id = next_id(plugin_id)

    out = {
        "enable": data.get("enable", data.get("is_enabled", True)),
        "user_id": data.get("user_id", ""),
        "token": data.get("token", ""),
        "devcode": data.get("devcode", ""),
        "distinct_id": data.get("distinct_id", ""),
        "wuwa": data.get("wuwa", {"role_id": "", "enabled": True, "schedule_cron": "", "schedule_enabled": False}),
        "pgr": data.get("pgr", {"role_id": "", "enabled": False, "schedule_cron": "", "schedule_enabled": False}),
    }

    d = _dir(plugin_id)
    d.mkdir(parents=True, exist_ok=True)
    p = _path(plugin_id, account_id)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(out, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    logger.info("Saved config/%s/%d.yaml", plugin_id, account_id)
    return account_id


def delete(plugin_id: str, account_id: int) -> None:
    p = _path(plugin_id, account_id)
    if p.exists():
        p.unlink()
        logger.info("Deleted config/%s/%d.yaml", plugin_id, account_id)


def update_schedule(plugin_id: str, account_id: int, game_id: str, cron: str, enabled: bool) -> bool:
    data = get(plugin_id, account_id)
    if data is None:
        return False
    g = data.setdefault(game_id, {})
    g["schedule_cron"] = cron
    g["schedule_enabled"] = enabled
    save(plugin_id, data, account_id)
    return True


def _read_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
