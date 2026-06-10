from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from typing import Any


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'").strip('"')
    return out


def _parse_config_file(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"Config file not found: {p}")
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in config file {p}: {type(e).__name__}: {e}") from None
    if not isinstance(payload, dict):
        raise RuntimeError(f"Config file {p} must be a JSON object")
    return payload


def _get(env: dict[str, str], key: str) -> str:
    return os.environ.get(key, env.get(key, "")).strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    timeout_s: float
    user_agent_app: str
    contact: str | None


def load_config(env_file: str | None, config_file: str | None = None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))
    cfg = _parse_config_file(Path(config_file) if config_file else None)

    base_url = (
        str(cfg.get("base_url")).rstrip("/")
        if cfg.get("base_url") is not None
        else _get(env, "OPEN_LIBRARY_BASE_URL").rstrip("/") or "https://openlibrary.org"
    )

    timeout_s_raw = cfg.get("timeout_s") if cfg.get("timeout_s") is not None else _get(env, "OPEN_LIBRARY_TIMEOUT_S")
    if timeout_s_raw == "":
        timeout_s_raw = "30"
    timeout_s: float
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("OPEN_LIBRARY_TIMEOUT_S (or config timeout_s) must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("OPEN_LIBRARY_TIMEOUT_S (or config timeout_s) must be > 0")

    user_agent_app = (
        str(cfg.get("user_agent_app")).strip()
        if cfg.get("user_agent_app") is not None
        else _get(env, "OPEN_LIBRARY_USER_AGENT_APP") or "qwayk-open-library-safe-agent-cli"
    )
    if not user_agent_app:
        raise RuntimeError("OPEN_LIBRARY_USER_AGENT_APP (or config user_agent_app) is required")

    contact = str(cfg.get("contact")).strip() if cfg.get("contact") is not None else _get(env, "OPEN_LIBRARY_CONTACT") or None

    return Config(
        base_url=base_url,
        timeout_s=timeout_s,
        user_agent_app=user_agent_app,
        contact=contact or None,
    )
