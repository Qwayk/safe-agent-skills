from __future__ import annotations

from pathlib import Path
from typing import Any

from .json_files import read_json_file, write_json_file


def _state_dir_for_env_file(env_file: str) -> Path:
    return Path(env_file).expanduser().resolve().parent / ".state"

def cache_dir_for_env_file(env_file: str) -> Path:
    return _state_dir_for_env_file(env_file) / "cache"


def defaults_path_for_env_file(env_file: str) -> Path:
    return _state_dir_for_env_file(env_file) / "defaults.json"


def load_defaults(env_file: str) -> dict[str, Any]:
    p = defaults_path_for_env_file(env_file)
    if not p.exists():
        return {"by_env_file": {}, "by_fingerprint": {}}
    obj = read_json_file(p)
    if not isinstance(obj, dict):
        return {"by_env_file": {}, "by_fingerprint": {}}
    if "by_env_file" not in obj or not isinstance(obj.get("by_env_file"), dict):
        obj["by_env_file"] = {}
    if "by_fingerprint" not in obj or not isinstance(obj.get("by_fingerprint"), dict):
        obj["by_fingerprint"] = {}
    return obj  # type: ignore[return-value]


def _env_key(env_file: str) -> str:
    return str(Path(env_file).expanduser().resolve())


def get_default_account_id(env_file: str, *, fingerprint: str | None = None) -> str | None:
    obj = load_defaults(env_file)
    if fingerprint:
        by_fp = obj.get("by_fingerprint") or {}
        if isinstance(by_fp, dict):
            entry = by_fp.get(str(fingerprint)) or {}
            if isinstance(entry, dict):
                v = entry.get("default_account_id")
                if v:
                    return str(v)
    by_env = obj.get("by_env_file") or {}
    if not isinstance(by_env, dict):
        return None
    entry = by_env.get(_env_key(env_file)) or {}
    if isinstance(entry, dict):
        v = entry.get("default_account_id")
        return str(v) if v else None
    return None


def set_default_account_id(env_file: str, account_id: str, *, fingerprint: str | None = None) -> str:
    obj = load_defaults(env_file)
    by_env = obj.get("by_env_file")
    if not isinstance(by_env, dict):
        by_env = {}
        obj["by_env_file"] = by_env
    by_env[_env_key(env_file)] = {"default_account_id": str(account_id).strip()}
    if fingerprint:
        by_fp = obj.get("by_fingerprint")
        if not isinstance(by_fp, dict):
            by_fp = {}
            obj["by_fingerprint"] = by_fp
        by_fp[str(fingerprint)] = {"default_account_id": str(account_id).strip()}
    return write_json_file(defaults_path_for_env_file(env_file), obj)
