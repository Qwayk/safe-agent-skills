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


OFFICIAL_BASE_URL = "https://spaceship.dev/api"


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    value = os.environ.get(key) if key in os.environ else env.get(key)
    return (value or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str
    api_secret: str
    timeout_s: float


def load_config(env_file: str | None, *, require_credentials: bool = True) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = OFFICIAL_BASE_URL

    api_key = _get(env, "SPACESHIP_API_KEY")
    api_secret = _get(env, "SPACESHIP_API_SECRET")

    timeout_s_raw = _get(env, "SPACESHIP_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("SPACESHIP_TIMEOUT_S must be a number (seconds)") from None
    if require_credentials:
        if not api_key:
            raise RuntimeError("Missing SPACESHIP_API_KEY")
        if not api_secret:
            raise RuntimeError("Missing SPACESHIP_API_SECRET")
    else:
        api_key = api_key or ""
        api_secret = api_secret or ""

    if timeout_s <= 0:
        raise RuntimeError("SPACESHIP_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, api_key=api_key, api_secret=api_secret, timeout_s=timeout_s)
