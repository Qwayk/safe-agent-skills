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
    client_id: str
    client_secret: str
    auth_base_url: str
    api_base_url: str | None
    oauth_project_id: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    client_id = _get(env, "CONTENTSQUARE_CLIENT_ID")
    client_secret = _get(env, "CONTENTSQUARE_CLIENT_SECRET")
    auth_base_url = (_get(env, "CONTENTSQUARE_AUTH_BASE_URL") or "https://api.contentsquare.com").rstrip("/")
    api_base_url = _get(env, "CONTENTSQUARE_API_BASE_URL").rstrip("/") or None
    oauth_project_id = _get(env, "CONTENTSQUARE_PROJECT_ID") or _get(env, "CONTENTSQUARE_OAUTH_PROJECT_ID") or None

    timeout_s_raw = _get(env, "CONTENTSQUARE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("CONTENTSQUARE_TIMEOUT_S must be a number (seconds)") from None

    if not client_id:
        raise RuntimeError("Missing CONTENTSQUARE_CLIENT_ID")
    if not client_secret:
        raise RuntimeError("Missing CONTENTSQUARE_CLIENT_SECRET")
    if timeout_s <= 0:
        raise RuntimeError("CONTENTSQUARE_TIMEOUT_S must be > 0")

    return Config(
        client_id=client_id,
        client_secret=client_secret,
        auth_base_url=auth_base_url,
        api_base_url=api_base_url,
        oauth_project_id=oauth_project_id,
        timeout_s=timeout_s,
    )
