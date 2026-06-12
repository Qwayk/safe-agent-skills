from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .oauth_tokens import read_stored_access_token


def _coalesce_base_url(value: str) -> str:
    if value:
        return value.rstrip("/")
    return "https://api.getjobber.com"


def _coalesce_graphql_version(value: str) -> str:
    v = (value or "").strip()
    return v or "2025-04-16"


def _coerce_timeout(value: str) -> float:
    try:
        timeout_s = float(value)
    except Exception:
        raise RuntimeError("JOBBER_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise RuntimeError("JOBBER_TIMEOUT_S must be > 0")
    return timeout_s


def _normalize_graphql_endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/api/graphql"):
        return base
    if base.endswith("/api"):
        return base + "/graphql"
    return base + "/api/graphql"


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
    graphql_url: str
    token: str | None
    timeout_s: float
    graphql_version: str
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _coalesce_base_url(_get(env, "JOBBER_API_BASE_URL"))
    graphql_url = _normalize_graphql_endpoint(base_url)
    timeout_s = _coerce_timeout(_get(env, "JOBBER_TIMEOUT_S") or "30")

    client_id = _get(env, "JOBBER_CLIENT_ID") or None
    client_secret = _get(env, "JOBBER_CLIENT_SECRET") or None
    redirect_uri = _get(env, "JOBBER_REDIRECT_URI") or None
    graphql_version = _coalesce_graphql_version(_get(env, "JOBBER_GRAPHQL_VERSION"))

    token = read_stored_access_token(
        env_file=env_file or ".env",
        fallback_token=_get(env, "JOBBER_API_TOKEN") or None,
    )

    return Config(
        base_url=base_url,
        graphql_url=graphql_url,
        token=token,
        timeout_s=timeout_s,
        graphql_version=graphql_version,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
