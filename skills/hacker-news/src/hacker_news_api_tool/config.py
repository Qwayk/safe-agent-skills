from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .errors import ValidationError


DEFAULT_HACKER_NEWS_API_ROOT = "https://hacker-news.firebaseio.com/v0"


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


def normalize_hacker_news_api_root(raw: str) -> str:
    """
    Normalize/validate the Hacker News API base URL.

    We expect a root like `https://hacker-news.firebaseio.com/v0`.
    """
    raw = str(raw or "").strip()
    if not raw:
        return DEFAULT_HACKER_NEWS_API_ROOT
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("HACKER_NEWS_API_ROOT must start with http:// or https://")
    if not parsed.netloc:
        raise ValidationError("HACKER_NEWS_API_ROOT must include a hostname")
    if parsed.query or parsed.fragment:
        raise ValidationError("HACKER_NEWS_API_ROOT must not include query or fragment")
    path = parsed.path or "/"
    normalized = urlunsplit((parsed.scheme, parsed.netloc, path.rstrip("/"), "", ""))
    return normalized.rstrip("/")


@dataclasses.dataclass(frozen=True)
class Config:
    api_root: str
    timeout_s: float


def load_config(env_file: str | None, *, config_defaults: dict[str, str] | None = None) -> Config:
    env: dict[str, str] = dict(config_defaults or {})
    env.update(_parse_env_file(Path(env_file or ".env")))

    api_root = normalize_hacker_news_api_root(
        _get(env, "HACKER_NEWS_API_ROOT") or _get(env, "HACKER_NEWS_BASE_URL")
    )

    timeout_s_raw = _get(env, "HACKER_NEWS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("HACKER_NEWS_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise ValidationError("HACKER_NEWS_TIMEOUT_S must be > 0")

    return Config(api_root=api_root, timeout_s=timeout_s)
