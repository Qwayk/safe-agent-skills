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
    api_key: str
    site_id: str
    timeout_s: float
    cf_access_client_id: str | None
    cf_access_client_secret: str | None


def load_config(env_file: str | None) -> Config:
    env_path = Path(env_file or ".env")
    env = _parse_env_file(env_path)
    env_file_exists = env_path.exists()

    base_url = _get(env, "PLAUSIBLE_BASE_URL").rstrip("/")
    api_key = _get(env, "PLAUSIBLE_API_KEY")
    site_id = _get(env, "PLAUSIBLE_SITE_ID")

    # Optional: Cloudflare Access Service Token (for Plausible instances protected by Cloudflare Access).
    # https://developers.cloudflare.com/cloudflare-one/identity/service-tokens/
    # These are secrets and must never be printed.
    cf_access_client_id = _get(env, "CF_ACCESS_CLIENT_ID") or _get(env, "CLOUDFLARE_ACCESS_CLIENT_ID") or ""
    cf_access_client_secret = _get(env, "CF_ACCESS_CLIENT_SECRET") or _get(env, "CLOUDFLARE_ACCESS_CLIENT_SECRET") or ""
    if not cf_access_client_id:
        cf_access_client_id = None
    if not cf_access_client_secret:
        cf_access_client_secret = None

    timeout_s_raw = _get(env, "PLAUSIBLE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("PLAUSIBLE_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        hint = (
            f" (env file not found at {env_path}; copy .env.example -> .env and fill values)"
            if not env_file_exists
            else ""
        )
        raise RuntimeError(f"Missing PLAUSIBLE_BASE_URL{hint}")
    if not api_key:
        hint = (
            f" (env file not found at {env_path}; copy .env.example -> .env and fill values)"
            if not env_file_exists
            else ""
        )
        raise RuntimeError(f"Missing PLAUSIBLE_API_KEY{hint}")
    if not site_id:
        hint = (
            f" (env file not found at {env_path}; copy .env.example -> .env and fill values)"
            if not env_file_exists
            else ""
        )
        raise RuntimeError(f"Missing PLAUSIBLE_SITE_ID{hint}")
    if timeout_s <= 0:
        raise RuntimeError("PLAUSIBLE_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        api_key=api_key,
        site_id=site_id,
        timeout_s=timeout_s,
        cf_access_client_id=cf_access_client_id,
        cf_access_client_secret=cf_access_client_secret,
    )
