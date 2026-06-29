from __future__ import annotations

import dataclasses
import hashlib
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
    api_key: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "N8N_BASE_URL").rstrip("/")
    api_key = _get(env, "N8N_API_KEY") or None

    timeout_s_raw = _get(env, "N8N_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("N8N_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing N8N_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("N8N_TIMEOUT_S must be > 0")
    if base_url and not base_url.endswith("/api/v1"):
        raise RuntimeError("N8N_BASE_URL must point to the n8n API root and end with /api/v1")

    return Config(base_url=base_url, api_key=api_key, timeout_s=timeout_s)


def credential_fingerprint(api_key: str | None) -> str | None:
    if not api_key:
        return None
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]
