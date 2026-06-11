from __future__ import annotations

import dataclasses
import os
from pathlib import Path


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
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k:
            out[k] = v
    return out


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "DYNADOT_API_BASE_URL").strip()
    api_key = _get(env, "DYNADOT_API_KEY") or None

    timeout_s_raw = _get(env, "DYNADOT_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("DYNADOT_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing DYNADOT_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("DYNADOT_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, api_key=api_key, timeout_s=timeout_s)


def load_config_file_only(env_file: str | None) -> Config:
    """
    Load config from an env file only (ignore OS environment variables).

    This is important for workflows that use multiple Dynadot accounts in one process,
    so a caller can load a second account config without being accidentally overridden
    by the current shell environment.
    """
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (env.get("DYNADOT_API_BASE_URL") or "").strip()
    api_key = (env.get("DYNADOT_API_KEY") or "").strip() or None

    timeout_s_raw = (env.get("DYNADOT_TIMEOUT_S") or "30").strip()
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("DYNADOT_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing DYNADOT_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("DYNADOT_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, api_key=api_key, timeout_s=timeout_s)
