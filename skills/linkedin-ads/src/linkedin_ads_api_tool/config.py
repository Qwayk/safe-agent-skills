from __future__ import annotations

import hashlib
import json
import dataclasses
from pathlib import Path
import os

from .oauth_tokens import read_token_json, token_path_for_env_file


DEFAULT_BASE_URL = "https://api.linkedin.com/rest"
DEFAULT_LINKEDIN_VERSION = "202605"
DEFAULT_RESTLI_PROTOCOL_VERSION = "2.0.0"


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


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str | None
    linkedin_version: str
    restli_protocol_version: str
    timeout_s: float
    env_fingerprint: str


def _first_present(env: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in os.environ:
            return (os.environ.get(key) or "").strip()
        if key in env:
            return env[key].strip()
    return ""


def _read_token_from_state_file(env_file: str) -> str | None:
    path = token_path_for_env_file(env_file)
    data = read_token_json(path)
    if not isinstance(data, dict):
        return None
    for key in ("access_token", "accessToken", "token"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _token_fingerprint(token: str | None) -> str:
    if not token or not str(token).strip():
        return "none"
    return hashlib.sha256(str(token).encode("utf-8")).hexdigest()


def _build_env_fingerprint(
    *,
    base_url: str,
    linkedin_version: str,
    restli_protocol_version: str,
    token: str | None,
) -> str:
    payload = {
        "base_url": base_url,
        "linkedin_version": linkedin_version,
        "restli_protocol_version": restli_protocol_version,
        "token_fingerprint": _token_fingerprint(token),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _first_present(env, "LINKEDIN_ADS_BASE_URL", "LINKEDIN_ADS_API_BASE_URL")
    if not base_url:
        base_url = DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")

    linkedin_version = _first_present(
        env,
        "LINKEDIN_ADS_LINKEDIN_VERSION",
        "LINKEDIN_ADS_VERSION",
        "LINKEDIN_ADS_LINKEDIN_API_VERSION",
    ).strip()
    if not linkedin_version:
        linkedin_version = DEFAULT_LINKEDIN_VERSION

    restli_protocol_version = _first_present(
        env,
        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION",
        "LINKEDIN_ADS_RESTLI_VERSION",
    ).strip()
    if not restli_protocol_version:
        restli_protocol_version = DEFAULT_RESTLI_PROTOCOL_VERSION

    token = _first_present(env, "LINKEDIN_ADS_TOKEN", "LINKEDIN_ADS_ACCESS_TOKEN", "LINKEDIN_ADS_API_TOKEN")
    if not token:
        token = _read_token_from_state_file(env_file or ".env")

    env_fingerprint = _build_env_fingerprint(
        base_url=base_url,
        linkedin_version=linkedin_version,
        restli_protocol_version=restli_protocol_version,
        token=token,
    )

    timeout_s_raw = _first_present(env, "LINKEDIN_ADS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("LINKEDIN_ADS_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing LINKEDIN_ADS_BASE_URL (or LINKEDIN_ADS_API_BASE_URL)")
    if timeout_s <= 0:
        raise RuntimeError("LINKEDIN_ADS_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        token=token,
        linkedin_version=linkedin_version,
        restli_protocol_version=restli_protocol_version,
        timeout_s=timeout_s,
        env_fingerprint=env_fingerprint,
    )
