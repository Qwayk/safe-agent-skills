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
    oauth_client_secrets_file: str | None
    oauth_scopes: list[str]
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = API_BASE_URL
    oauth_client_secrets_file = _get(env, "GBP_OAUTH_CLIENT_SECRETS_FILE") or None
    oauth_scopes_raw = _get(env, "GBP_OAUTH_SCOPES")
    oauth_scopes = _parse_scopes(oauth_scopes_raw)

    timeout_s_raw = _get(env, "GBP_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("GBP_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("GBP_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        oauth_client_secrets_file=oauth_client_secrets_file,
        oauth_scopes=oauth_scopes,
        timeout_s=timeout_s,
    )
DEFAULT_OAUTH_SCOPE = "https://www.googleapis.com/auth/business.manage"
API_BASE_URL = "https://mybusinessbusinessinformation.googleapis.com"


def _parse_scopes(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return [DEFAULT_OAUTH_SCOPE]
    scopes: list[str] = []
    for item in raw.replace(",", " ").split():
        scope = item.strip()
        if scope:
            scopes.append(scope)
    return scopes or [DEFAULT_OAUTH_SCOPE]
