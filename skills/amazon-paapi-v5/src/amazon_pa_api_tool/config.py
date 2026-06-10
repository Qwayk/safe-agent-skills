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
    access_key_id: str
    secret_access_key: str
    partner_tag: str
    partner_type: str
    host: str
    region: str
    marketplace: str
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    access_key_id = _get(env, "AMAZON_PA_ACCESS_KEY_ID")
    secret_access_key = _get(env, "AMAZON_PA_SECRET_ACCESS_KEY")
    partner_tag = _get(env, "AMAZON_PA_PARTNER_TAG")
    partner_type = _get(env, "AMAZON_PA_PARTNER_TYPE") or "Associates"
    host = _get(env, "AMAZON_PA_HOST") or "webservices.amazon.com"
    region = _get(env, "AMAZON_PA_REGION") or "us-east-1"
    marketplace = _get(env, "AMAZON_PA_MARKETPLACE") or "www.amazon.com"

    timeout_s_raw = _get(env, "AMAZON_PA_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AMAZON_PA_TIMEOUT_S must be a number (seconds)") from None

    if not access_key_id:
        raise RuntimeError("Missing AMAZON_PA_ACCESS_KEY_ID")
    if not secret_access_key:
        raise RuntimeError("Missing AMAZON_PA_SECRET_ACCESS_KEY")
    if not partner_tag:
        raise RuntimeError("Missing AMAZON_PA_PARTNER_TAG")
    if " " in partner_tag:
        raise RuntimeError("AMAZON_PA_PARTNER_TAG must not contain spaces")
    if not host:
        raise RuntimeError("Missing AMAZON_PA_HOST")
    if not region:
        raise RuntimeError("Missing AMAZON_PA_REGION")
    if not marketplace:
        raise RuntimeError("Missing AMAZON_PA_MARKETPLACE")
    if timeout_s <= 0:
        raise RuntimeError("AMAZON_PA_TIMEOUT_S must be > 0")

    return Config(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        partner_tag=partner_tag,
        partner_type=partner_type,
        host=host,
        region=region,
        marketplace=marketplace,
        timeout_s=timeout_s,
    )
