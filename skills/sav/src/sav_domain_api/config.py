from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ValidationError
from .safety import parse_timeout_s


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
        out[k.strip()] = v.strip().strip("'").strip('"')
    return out


def _get_env(env: dict[str, str], key: str, *, default: str = "") -> str:
    # Environment variable takes precedence over env file.
    raw = os.environ.get(key) if key in os.environ else env.get(key, default)
    return (raw or "").strip()


@dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str | None
    timeout_s: float = 30.0


BASE_URL = "https://api.sav.com/domains_api_v1"


def load_config(*, env_file: str, require_api_key: bool) -> Config:
    try:
        env = _parse_env_file(Path(env_file))
    except OSError as exc:
        raise ValidationError("Unable to load env file") from exc
    api_key = _get_env(env, "SAV_API_KEY") or None

    timeout_raw = _get_env(env, "SAV_TIMEOUT_S", default="30")
    timeout_s = parse_timeout_s(timeout_raw, field_name="SAV_TIMEOUT_S")

    if require_api_key and not api_key:
        raise ValidationError("Missing SAV_API_KEY in environment or env file")

    return Config(base_url=BASE_URL, api_key=api_key, timeout_s=timeout_s)
