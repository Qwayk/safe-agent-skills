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
    raw = os.environ.get(key) if key in os.environ else env.get(key)
    return (raw or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str | None
    oauth2_client_id: str | None
    oauth2_redirect_uri: str | None
    oauth2_scopes: str | None
    oauth2_authorization_url: str | None
    oauth2_token_url: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "X_API_BASE_URL").rstrip("/")
    token = _get(env, "X_API_BEARER_TOKEN") or None
    oauth2_client_id = _get(env, "X_API_OAUTH2_CLIENT_ID") or None
    oauth2_redirect_uri = _get(env, "X_API_OAUTH2_REDIRECT_URI") or None
    oauth2_scopes = _get(env, "X_API_OAUTH2_SCOPES") or None
    oauth2_authorization_url = _get(env, "X_API_OAUTH2_AUTH_URL") or None
    oauth2_token_url = _get(env, "X_API_OAUTH2_TOKEN_URL") or None

    timeout_s_raw = _get(env, "X_API_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("X_API_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing X_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("X_API_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        token=token,
        oauth2_client_id=oauth2_client_id,
        oauth2_redirect_uri=oauth2_redirect_uri,
        oauth2_scopes=oauth2_scopes,
        oauth2_authorization_url=oauth2_authorization_url,
        oauth2_token_url=oauth2_token_url,
        timeout_s=timeout_s,
    )
