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
    access_token: str | None
    app_id: str | None
    app_secret: str | None
    refresh_token: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "PINTEREST_API_BASE_URL") or "https://api.pinterest.com/v5").rstrip("/")
    access_token = _get(env, "PINTEREST_ACCESS_TOKEN") or None
    app_id = _get(env, "PINTEREST_APP_ID") or None
    app_secret = _get(env, "PINTEREST_APP_SECRET") or None
    refresh_token = _get(env, "PINTEREST_REFRESH_TOKEN") or None

    timeout_s_raw = _get(env, "PINTEREST_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("PINTEREST_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("PINTEREST_API_BASE_URL must not be empty")
    if access_token is not None and not access_token.strip():
        raise RuntimeError("PINTEREST_ACCESS_TOKEN must not be empty if set")
    if app_id is not None and not app_id.strip():
        raise RuntimeError("PINTEREST_APP_ID must not be empty if set")
    if app_secret is not None and not app_secret.strip():
        raise RuntimeError("PINTEREST_APP_SECRET must not be empty if set")
    if refresh_token is not None and not refresh_token.strip():
        raise RuntimeError("PINTEREST_REFRESH_TOKEN must not be empty if set")
    if timeout_s <= 0:
        raise RuntimeError("PINTEREST_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        access_token=access_token,
        app_id=app_id,
        app_secret=app_secret,
        refresh_token=refresh_token,
        timeout_s=timeout_s,
    )
