from __future__ import annotations

import dataclasses
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
    credential_id: str
    credential_secret: str
    credential_version: str
    locale: str
    timeout_s: float
    token_url: str | None
    partner_tag: str


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "AMAZON_CREATORS_API_BASE_URL").rstrip("/")
    credential_id = _get(env, "AMAZON_CREATORS_CREDENTIAL_ID")
    credential_secret = _get(env, "AMAZON_CREATORS_CREDENTIAL_SECRET")
    credential_version = _get(env, "AMAZON_CREATORS_CREDENTIAL_VERSION")
    locale = _get(env, "AMAZON_CREATORS_LOCALE")
    token_url = _get(env, "AMAZON_CREATORS_TOKEN_URL") or None
    partner_tag = _get(env, "AMAZON_CREATORS_PARTNER_TAG")

    timeout_s_raw = _get(env, "AMAZON_CREATORS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AMAZON_CREATORS_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing AMAZON_CREATORS_API_BASE_URL")
    if not credential_id:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_ID")
    if not credential_secret:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_SECRET")
    if not credential_version:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_VERSION")
    if not locale:
        raise RuntimeError("Missing AMAZON_CREATORS_LOCALE")
    if not partner_tag:
        raise RuntimeError("Missing AMAZON_CREATORS_PARTNER_TAG")
    if timeout_s <= 0:
        raise RuntimeError("AMAZON_CREATORS_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        credential_id=credential_id,
        credential_secret=credential_secret,
        credential_version=credential_version,
        locale=locale,
        timeout_s=timeout_s,
        token_url=token_url,
        partner_tag=partner_tag,
    )
