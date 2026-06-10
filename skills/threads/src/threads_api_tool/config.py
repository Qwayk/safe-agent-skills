from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .oauth_tokens import read_access_token, token_path_for_env_file


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
    api_version: str
    token: str | None
    app_id: str | None
    app_secret: str | None
    redirect_uri: str | None
    default_user_id: str | None
    timeout_s: float


def load_config(
    env_file: str | None,
    *,
    api_version_override: str | None = None,
) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "THREADS_API_BASE_URL") or "https://graph.threads.net").rstrip("/")

    api_version = (api_version_override or _get(env, "THREADS_API_VERSION")) or "v1.0"
    api_version = api_version.strip()
    if not api_version:
        api_version = "v1.0"
    if not api_version.startswith("v"):
        api_version = f"v{api_version}"

    token = _get(env, "THREADS_API_TOKEN") or read_access_token(token_path_for_env_file(env_file or ".env"))
    app_id = _get(env, "THREADS_APP_ID") or None
    if app_id == "":
        app_id = None
    app_secret = _get(env, "THREADS_APP_SECRET") or None
    if app_secret == "":
        app_secret = None
    redirect_uri = _get(env, "THREADS_REDIRECT_URI") or None
    if redirect_uri == "":
        redirect_uri = None
    default_user_id = _get(env, "THREADS_DEFAULT_USER_ID") or None
    if default_user_id == "":
        default_user_id = None

    timeout_s_raw = _get(env, "THREADS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("THREADS_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("THREADS_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        api_version=api_version,
        token=token or None,
        app_id=app_id,
        app_secret=app_secret,
        redirect_uri=redirect_uri,
        default_user_id=default_user_id,
        timeout_s=timeout_s,
    )
