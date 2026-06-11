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
    app_id: str | None
    app_secret: str | None
    token: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "TIKTOK_MARKETING_API_BASE_URL").rstrip("/") or "https://business-api.tiktok.com")
    app_id = _get(env, "TIKTOK_MARKETING_APP_ID") or None
    app_secret = _get(env, "TIKTOK_MARKETING_APP_SECRET") or None
    token = _get(env, "TIKTOK_MARKETING_ACCESS_TOKEN") or None

    timeout_s_raw = _get(env, "TIKTOK_MARKETING_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("TIKTOK_MARKETING_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("TIKTOK_MARKETING_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        app_id=app_id,
        app_secret=app_secret,
        token=token,
        timeout_s=timeout_s,
    )
