from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .oauth_tokens import read_token_json, token_path_for_env_file


DEFAULT_API_VERSION = "67.0"


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
    instance_url: str
    token: str | None
    token_source: str | None
    api_version: str
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env_path = Path(env_file or ".env")
    env = _parse_env_file(env_path)
    token_json = read_token_json(token_path_for_env_file(str(env_path))) or {}

    instance_url = (_get(env, "SALESFORCE_INSTANCE_URL") or str(token_json.get("instance_url") or "")).rstrip("/")
    token = _get(env, "SALESFORCE_ACCESS_TOKEN") or str(token_json.get("access_token") or "") or None
    token_source = None
    if _get(env, "SALESFORCE_ACCESS_TOKEN"):
        token_source = "env"
    elif token_json.get("access_token"):
        token_source = "token_json"

    api_version = (_get(env, "SALESFORCE_API_VERSION") or DEFAULT_API_VERSION).strip()
    if api_version.startswith("v"):
        api_version = api_version[1:]

    timeout_s_raw = _get(env, "SALESFORCE_TIMEOUT_S") or "60"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("SALESFORCE_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("SALESFORCE_TIMEOUT_S must be > 0")
    if instance_url and not instance_url.startswith(("https://", "http://")):
        raise RuntimeError("SALESFORCE_INSTANCE_URL must start with https:// or http://")
    if api_version.count(".") != 1:
        raise RuntimeError("SALESFORCE_API_VERSION must look like 67.0")

    return Config(
        instance_url=instance_url,
        token=token,
        token_source=token_source,
        api_version=api_version,
        timeout_s=timeout_s,
    )
