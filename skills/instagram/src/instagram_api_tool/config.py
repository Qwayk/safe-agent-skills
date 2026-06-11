from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


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
    auth_api_base_url: str
    auth_web_base_url: str
    graph_version: str
    app_id: str | None
    app_secret: str | None
    redirect_uri: str | None
    ig_user_id: str | None
    token: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "INSTAGRAM_GRAPH_BASE_URL") or "https://graph.instagram.com").rstrip("/")
    auth_api_base_url = (_get(env, "INSTAGRAM_AUTH_API_BASE_URL") or "https://api.instagram.com").rstrip("/")
    auth_web_base_url = (_get(env, "INSTAGRAM_AUTH_WEB_BASE_URL") or "https://www.instagram.com").rstrip("/")
    graph_version = (_get(env, "INSTAGRAM_GRAPH_VERSION") or "v25.0").strip()
    app_id = _get(env, "INSTAGRAM_APP_ID") or None
    app_secret = _get(env, "INSTAGRAM_APP_SECRET") or None
    redirect_uri = _get(env, "INSTAGRAM_REDIRECT_URI") or None
    ig_user_id = _get(env, "INSTAGRAM_IG_USER_ID") or None
    token = _get(env, "INSTAGRAM_ACCESS_TOKEN") or None

    timeout_s_raw = _get(env, "INSTAGRAM_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("INSTAGRAM_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise ValidationError("Missing INSTAGRAM_GRAPH_BASE_URL")
    if timeout_s <= 0:
        raise ValidationError("INSTAGRAM_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        auth_api_base_url=auth_api_base_url,
        auth_web_base_url=auth_web_base_url,
        graph_version=graph_version,
        app_id=app_id,
        app_secret=app_secret,
        redirect_uri=redirect_uri,
        ig_user_id=ig_user_id,
        token=token,
        timeout_s=timeout_s,
    )
