from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Final

from .oauth_tokens import token_path_for_env_file, read_token_json

AUTH_MODES: Final[tuple[str, ...]] = ("personal", "oauth", "plan")
FIGMA_DEFAULT_BASE_URL: Final[str] = "https://api.figma.com"
FIGMA_DEFAULT_TIMEOUT_S: Final[str] = "30"

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
    auth_mode: str
    token: str | None
    token_source: str
    timeout_s: float


def _resolve_oauth_token(env_file: str, env: dict[str, str]) -> str | None:
    value = _get(env, "FIGMA_ACCESS_TOKEN")
    if value:
        return value
    path = token_path_for_env_file(env_file)
    data = read_token_json(path)
    if not data:
        return None
    token = data.get("access_token")
    if isinstance(token, str):
        stripped = token.strip()
        return stripped or None
    return None


def load_config(env_file: str | None) -> Config:
    env_path = Path(env_file or ".env")
    env = _parse_env_file(env_path)

    base_url = (_get(env, "FIGMA_BASE_URL") or FIGMA_DEFAULT_BASE_URL).rstrip("/")
    auth_mode = (_get(env, "FIGMA_AUTH_MODE") or "personal").lower()
    if auth_mode not in AUTH_MODES:
        raise RuntimeError(
            "FIGMA_AUTH_MODE must be one of: personal | oauth | plan"
        )

    token = _get(env, "FIGMA_ACCESS_TOKEN") or None
    token_source = "env"
    if not token and auth_mode == "oauth":
        token = _resolve_oauth_token(str(env_path), env)
        token_source = "token_file" if token else "missing"
    elif not token:
        token_source = "missing"
    else:
        token_source = "env"

    timeout_s_raw = _get(env, "FIGMA_TIMEOUT_S") or FIGMA_DEFAULT_TIMEOUT_S
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("FIGMA_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise RuntimeError("FIGMA_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        auth_mode=auth_mode,
        token=token,
        token_source=token_source,
        timeout_s=timeout_s,
    )
