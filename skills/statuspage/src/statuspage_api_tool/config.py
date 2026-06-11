from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .errors import ValidationError


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


def normalize_statuspage_base_url(raw: str) -> str:
    """
    Normalize/validate the status site base URL.

    We expect a site root like `https://status.somevendor.com` (no path/query/fragment).
    """
    raw = str(raw or "").strip()
    if not raw:
        raise ValidationError("Missing STATUSPAGE_BASE_URL")
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("STATUSPAGE_BASE_URL must start with http:// or https://")
    if not parsed.netloc:
        raise ValidationError("STATUSPAGE_BASE_URL must include a hostname")
    if parsed.query or parsed.fragment:
        raise ValidationError("STATUSPAGE_BASE_URL must not include query or fragment")
    path = parsed.path or ""
    if path not in {"", "/"}:
        raise ValidationError("STATUSPAGE_BASE_URL must not include a path")
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    timeout_s: float


def load_config(env_file: str | None, *, config_defaults: dict[str, str] | None = None) -> Config:
    env: dict[str, str] = dict(config_defaults or {})
    env.update(_parse_env_file(Path(env_file or ".env")))

    base_url = normalize_statuspage_base_url(_get(env, "STATUSPAGE_BASE_URL"))

    timeout_s_raw = _get(env, "STATUSPAGE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("STATUSPAGE_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise ValidationError("STATUSPAGE_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, timeout_s=timeout_s)
