from __future__ import annotations

import dataclasses
import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse


ALLOWED_BASE_HOSTS = {
    "eu1.make.com",
    "eu2.make.com",
    "us1.make.com",
    "us2.make.com",
    "eu1.make.celonis.com",
    "us1.make.celonis.com",
}


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
    timeout_s: float


def credential_fingerprint(token: str | None) -> str | None:
    if not token:
        return None
    digest = hashlib.sha256(("make-api-token-v1:" + token).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "MAKE_BASE_URL") or _get(env, "MAKE_ZONE_URL")).rstrip("/")
    token = _get(env, "MAKE_API_TOKEN") or None

    timeout_s_raw = _get(env, "MAKE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("MAKE_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing MAKE_BASE_URL")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or parsed.netloc not in ALLOWED_BASE_HOSTS:
        raise RuntimeError(
            "MAKE_BASE_URL must be one of the official Make zones, for example https://eu1.make.com"
        )
    if not base_url.endswith("/api/v2"):
        base_url = base_url.rstrip("/") + "/api/v2"
    if timeout_s <= 0:
        raise RuntimeError("MAKE_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, token=token, timeout_s=timeout_s)
