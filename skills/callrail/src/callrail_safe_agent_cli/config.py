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
    token: str | None
    default_account_id: str | None
    timeout_s: float
    request_from: str | None


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "CALLRAIL_API_BASE_URL").rstrip("/")
    token = _get(env, "CALLRAIL_API_TOKEN") or None
    default_account_id = _get(env, "CALLRAIL_DEFAULT_ACCOUNT_ID") or None
    request_from = _get(env, "CALLRAIL_REQUEST_FROM") or None

    timeout_s_raw = _get(env, "CALLRAIL_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("CALLRAIL_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing CALLRAIL_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("CALLRAIL_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        token=token,
        default_account_id=default_account_id,
        timeout_s=timeout_s,
        request_from=request_from,
    )
