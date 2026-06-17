from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Final

FORTNOX_DEFAULT_BASE_URL: Final[str] = "https://api.fortnox.se/3"
FORTNOX_DEFAULT_WS_URL: Final[str] = "wss://ws.fortnox.se/topics-v1"
FORTNOX_DEFAULT_AUTHORIZE_URL: Final[str] = "https://apps.fortnox.se/oauth-v1/auth"
FORTNOX_DEFAULT_TOKEN_URL: Final[str] = "https://apps.fortnox.se/oauth-v1/token"
FORTNOX_DEFAULT_REVOKE_URL: Final[str] = "https://apps.fortnox.se/oauth-v1/revoke"
FORTNOX_DEFAULT_TIMEOUT_S: Final[str] = "30"
FORTNOX_DEFAULT_SCOPES: Final[tuple[str, ...]] = ("companyinformation",)


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
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _parse_scopes(raw: str) -> tuple[str, ...]:
    parts = [part.strip() for part in raw.replace(",", " ").split()]
    scopes = tuple(part for part in parts if part)
    return scopes or FORTNOX_DEFAULT_SCOPES


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    ws_url: str
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None
    api_token: str | None
    refresh_token: str | None
    service_tenant_id: str | None
    oauth_scopes: tuple[str, ...]
    oauth_authorize_url: str
    oauth_token_url: str
    oauth_revoke_url: str
    token_file: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env_path = Path(env_file or ".env")
    env = _parse_env_file(env_path)

    base_url = (_get(env, "FORTNOX_API_BASE_URL") or FORTNOX_DEFAULT_BASE_URL).rstrip("/")
    ws_url = (_get(env, "FORTNOX_WS_URL") or FORTNOX_DEFAULT_WS_URL).rstrip("/")
    client_id = _get(env, "FORTNOX_CLIENT_ID") or None
    client_secret = _get(env, "FORTNOX_CLIENT_SECRET") or None
    redirect_uri = _get(env, "FORTNOX_REDIRECT_URI") or None
    api_token = _get(env, "FORTNOX_API_TOKEN") or None
    refresh_token = _get(env, "FORTNOX_REFRESH_TOKEN") or None
    service_tenant_id = _get(env, "FORTNOX_SERVICE_TENANT_ID") or None
    oauth_scopes = _parse_scopes(_get(env, "FORTNOX_OAUTH_SCOPES"))
    oauth_authorize_url = (_get(env, "FORTNOX_OAUTH_AUTHORIZE_URL") or FORTNOX_DEFAULT_AUTHORIZE_URL).rstrip("/")
    oauth_token_url = (_get(env, "FORTNOX_OAUTH_TOKEN_URL") or FORTNOX_DEFAULT_TOKEN_URL).rstrip("/")
    oauth_revoke_url = (_get(env, "FORTNOX_OAUTH_REVOKE_URL") or FORTNOX_DEFAULT_REVOKE_URL).rstrip("/")
    token_file = _get(env, "FORTNOX_TOKEN_FILE") or None

    timeout_s_raw = _get(env, "FORTNOX_TIMEOUT_S") or FORTNOX_DEFAULT_TIMEOUT_S
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("FORTNOX_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing FORTNOX_API_BASE_URL")
    if not ws_url:
        raise RuntimeError("Missing FORTNOX_WS_URL")
    if timeout_s <= 0:
        raise RuntimeError("FORTNOX_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        ws_url=ws_url,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        api_token=api_token,
        refresh_token=refresh_token,
        service_tenant_id=service_tenant_id,
        oauth_scopes=oauth_scopes,
        oauth_authorize_url=oauth_authorize_url,
        oauth_token_url=oauth_token_url,
        oauth_revoke_url=oauth_revoke_url,
        token_file=token_file,
        timeout_s=timeout_s,
    )
