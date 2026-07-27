from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError

OFFICIAL_BASE_URL = "https://app.asana.com/api/1.0"


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip().strip("'").strip('"')
    return values


def _get(values: dict[str, str], key: str) -> str:
    return str(os.environ.get(key, values.get(key, ""))).strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str
    timeout_s: float


def load_config(env_file: str | None, *, require_token: bool = True) -> Config:
    values = _parse_env_file(Path(env_file or ".env"))
    token = _get(values, "ASANA_ACCESS_TOKEN")
    timeout_raw = _get(values, "ASANA_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_raw)
    except ValueError:
        raise ValidationError("ASANA_TIMEOUT_S must be a number of seconds") from None
    if timeout_s <= 0:
        raise ValidationError("ASANA_TIMEOUT_S must be greater than zero")
    if require_token and not token:
        raise ValidationError(
            "Missing ASANA_ACCESS_TOKEN. Put the bearer token in the environment or .env file."
        )
    return Config(base_url=OFFICIAL_BASE_URL, token=token, timeout_s=timeout_s)
