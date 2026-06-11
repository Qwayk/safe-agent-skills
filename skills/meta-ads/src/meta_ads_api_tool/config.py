from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


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
    api_version: str
    access_token: str | None
    ad_account_id: str | None
    timeout_s: float
    max_retries: int


def normalize_ad_account_id(raw: str | None) -> str | None:
    v = str(raw or "").strip()
    if not v:
        return None
    if v.startswith("act_"):
        return v
    if v.isdigit():
        return "act_" + v
    return v


def load_config(
    env_file: str | None,
    *,
    ad_account_id_override: str | None = None,
    api_version_override: str | None = None,
) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "META_ADS_BASE_URL") or "https://graph.facebook.com").rstrip("/")
    access_token = _get(env, "META_ADS_ACCESS_TOKEN") or None

    api_version = _get(env, "META_ADS_API_VERSION") or "v24.0"
    if api_version_override:
        api_version = str(api_version_override).strip()

    ad_account_id = normalize_ad_account_id(_get(env, "META_ADS_AD_ACCOUNT_ID") or None)
    if ad_account_id_override:
        ad_account_id = normalize_ad_account_id(ad_account_id_override)

    timeout_s_raw = _get(env, "META_ADS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("META_ADS_TIMEOUT_S must be a number (seconds)") from None

    max_retries_raw = _get(env, "META_ADS_MAX_RETRIES") or "5"
    try:
        max_retries = int(max_retries_raw)
    except Exception:
        raise ValidationError("META_ADS_MAX_RETRIES must be an integer") from None

    if not base_url:
        raise ValidationError("META_ADS_BASE_URL is required (or leave blank to use the default)")
    if timeout_s <= 0:
        raise ValidationError("META_ADS_TIMEOUT_S must be > 0")
    if max_retries < 0:
        raise ValidationError("META_ADS_MAX_RETRIES must be >= 0")

    if not api_version.startswith("v"):
        raise ValidationError("META_ADS_API_VERSION must look like v24.0")

    return Config(
        base_url=base_url,
        api_version=api_version,
        access_token=access_token,
        ad_account_id=ad_account_id,
        timeout_s=timeout_s,
        max_retries=max_retries,
    )
