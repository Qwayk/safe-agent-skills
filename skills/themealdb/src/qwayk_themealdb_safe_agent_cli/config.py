from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from urllib.parse import quote

from .errors import ValidationError


DEFAULT_BASE_URL = "https://www.themealdb.com/api/json/v1"
DEFAULT_API_KEY = "1"
DEFAULT_TIMEOUT_S = 30.0


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
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            out[key] = value
    return out


def _load_project_config(path: str | None) -> dict[str, object]:
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise ValidationError(f"Config file not found: {path}")
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Config file is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValidationError("Config file must contain one JSON object")
    return data


def _pick_str(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str
    api_key_source: str
    timeout_s: float

    @property
    def api_root(self) -> str:
        return f"{self.base_url}/{quote(self.api_key, safe='')}"


def load_config(
    env_file: str | None,
    *,
    config_file: str | None = None,
    timeout_override: float | None = None,
) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))
    project = _load_project_config(config_file)

    base_url = _pick_str(
        os.environ.get("THEMEALDB_BASE_URL"),
        env.get("THEMEALDB_BASE_URL"),
        project.get("base_url"),
        DEFAULT_BASE_URL,
    ).rstrip("/")
    api_key = _pick_str(
        os.environ.get("THEMEALDB_API_KEY"),
        env.get("THEMEALDB_API_KEY"),
        DEFAULT_API_KEY,
    )
    timeout_raw = _pick_str(
        timeout_override,
        os.environ.get("THEMEALDB_TIMEOUT_S"),
        env.get("THEMEALDB_TIMEOUT_S"),
        project.get("timeout_s"),
        DEFAULT_TIMEOUT_S,
    )

    try:
        timeout_s = float(timeout_raw)
    except Exception as exc:
        raise ValidationError("THEMEALDB_TIMEOUT_S must be a number (seconds)") from exc

    if not base_url:
        raise ValidationError("THEMEALDB_BASE_URL cannot be empty")
    if not api_key:
        raise ValidationError("THEMEALDB_API_KEY cannot be empty")
    if timeout_s <= 0:
        raise ValidationError("THEMEALDB_TIMEOUT_S must be > 0")

    if os.environ.get("THEMEALDB_API_KEY", "").strip():
        api_key_source = "os_env"
    elif env.get("THEMEALDB_API_KEY", "").strip():
        api_key_source = "env_file"
    else:
        api_key_source = "default_public_key"

    return Config(
        base_url=base_url,
        api_key=api_key,
        api_key_source=api_key_source,
        timeout_s=timeout_s,
    )
