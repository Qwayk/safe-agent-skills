from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError

GIANTPANDA_API_HOST = "https://account.giantpanda.com"
DEFAULT_TIMEOUT_S = 30
_SENTINEL_PLACEHOLDERS = {
    "your_token_here",
    "token_here",
    "paste_token_here",
    "insert_your_token_here",
    "changeme",
    "change_me",
    "change_me_here",
}


def is_placeholder_token(token: str) -> bool:
    value = token.strip()
    if not value:
        return True
    normalized = value.lower().replace(" ", "")
    if value == "CHANGE_ME":
        return True
    return normalized in _SENTINEL_PLACEHOLDERS or normalized.startswith("changeme")


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
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


def _env_val(file_env: dict[str, str], key: str) -> str:
    if key in os.environ:
        return os.environ[key].strip()
    return (file_env.get(key) or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    host: str
    token: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    raw_timeout = _env_val(env, "GIANTPANDA_TIMEOUT_S")
    if raw_timeout:
        try:
            timeout_s = float(raw_timeout)
        except ValueError as exc:
            raise ValidationError("GIANTPANDA_TIMEOUT_S must be a positive number of seconds") from exc
        if timeout_s <= 0:
            raise ValidationError("GIANTPANDA_TIMEOUT_S must be > 0")
    else:
        timeout_s = float(DEFAULT_TIMEOUT_S)

    token = _env_val(env, "GIANTPANDA_API_TOKEN")

    return Config(host=GIANTPANDA_API_HOST, token=token or None, timeout_s=timeout_s)
