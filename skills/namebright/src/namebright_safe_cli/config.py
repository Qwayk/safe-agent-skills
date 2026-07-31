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
    env_value = os.environ.get(key)
    if env_value is None:
        env_value = env.get(key)
    return (env_value or "").strip()


OFFICIAL_NAMEBRIGHT_REST_BASE_URL = "https://api.namebright.com/rest"
OFFICIAL_NAMEBRIGHT_TOKEN_URL = "https://api.namebright.com/auth/token"
DEFAULT_TIMEOUT_S = 30.0


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    timeout_s: float
    client_id: str
    client_secret: str
    token_url: str


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    client_id = _get(env, "NAMEBRIGHT_CLIENT_ID")
    client_secret = _get(env, "NAMEBRIGHT_CLIENT_SECRET")

    timeout_s_raw = _get(env, "NAMEBRIGHT_TIMEOUT_S") or str(DEFAULT_TIMEOUT_S)
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("NAMEBRIGHT_TIMEOUT_S must be a number (seconds)") from None

    if not client_id:
        raise RuntimeError("Missing NAMEBRIGHT_CLIENT_ID")
    if not client_secret:
        raise RuntimeError("Missing NAMEBRIGHT_CLIENT_SECRET")

    if timeout_s <= 0:
        raise RuntimeError("NAMEBRIGHT_TIMEOUT_S must be > 0")

    return Config(
        base_url=OFFICIAL_NAMEBRIGHT_REST_BASE_URL.rstrip("/"),
        token_url=OFFICIAL_NAMEBRIGHT_TOKEN_URL.rstrip("/"),
        timeout_s=timeout_s,
        client_id=client_id,
        client_secret=client_secret,
    )
