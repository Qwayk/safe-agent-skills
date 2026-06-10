from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .discovery import load_discovery_doc
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


def _split_csv(s: str) -> list[str]:
    out: list[str] = []
    for raw in (s or "").split(","):
        v = raw.strip()
        if v:
            out.append(v)
    return out


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    timeout_s: float
    min_delay_s: float
    read_retries: int
    auth_mode: str
    scopes: tuple[str, ...]

    # oauth_refresh_token
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_refresh_token: str | None

    # service_account_json
    service_account_json_path: str | None


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    discovery_doc = load_discovery_doc()
    default_base = str(discovery_doc.get("baseUrl") or "https://tagmanager.googleapis.com/").strip()
    base_url = (_get(env, "GTM_BASE_URL") or default_base).rstrip("/") + "/"

    timeout_s_raw = _get(env, "GTM_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("GTM_TIMEOUT_S must be a number (seconds)") from None

    min_delay_s_raw = _get(env, "GTM_MIN_DELAY_S") or "4"
    try:
        min_delay_s = float(min_delay_s_raw)
    except Exception:
        raise ValidationError("GTM_MIN_DELAY_S must be a number (seconds)") from None

    read_retries_raw = _get(env, "GTM_READ_RETRIES") or "5"
    try:
        read_retries = int(read_retries_raw)
    except Exception:
        raise ValidationError("GTM_READ_RETRIES must be an integer") from None

    auth_mode = (_get(env, "GTM_AUTH_MODE") or "adc").strip()
    if auth_mode not in {"adc", "oauth_refresh_token", "service_account_json"}:
        raise ValidationError("GTM_AUTH_MODE must be one of: adc, oauth_refresh_token, service_account_json")

    scopes_raw = _get(env, "GTM_SCOPES")
    if scopes_raw:
        scopes = _split_csv(scopes_raw)
    else:
        # Default to full scope coverage for this "100% API coverage" tool.
        # Source of truth is the pinned discovery snapshot (for auditability).
        scopes_obj = ((discovery_doc.get("auth") or {}).get("oauth2") or {}).get("scopes") or {}
        scopes = sorted([str(k).strip() for k in scopes_obj.keys() if str(k).strip()]) or [
            "https://www.googleapis.com/auth/tagmanager.readonly"
        ]
    if not scopes:
        raise ValidationError("GTM_SCOPES must include at least one scope")

    # Warn: we keep the values in memory but must never print them.
    oauth_client_id = _get(env, "GTM_OAUTH_CLIENT_ID") or None
    oauth_client_secret = _get(env, "GTM_OAUTH_CLIENT_SECRET") or None
    oauth_refresh_token = _get(env, "GTM_OAUTH_REFRESH_TOKEN") or None
    service_account_json_path = _get(env, "GTM_SERVICE_ACCOUNT_JSON_PATH") or None

    if not base_url:
        raise ValidationError("Missing GTM_BASE_URL")
    if timeout_s <= 0:
        raise ValidationError("GTM_TIMEOUT_S must be > 0")
    if min_delay_s < 0:
        raise ValidationError("GTM_MIN_DELAY_S must be >= 0")
    if read_retries < 0:
        raise ValidationError("GTM_READ_RETRIES must be >= 0")

    # Minimal validation per mode (no network).
    if auth_mode == "oauth_refresh_token":
        missing: list[str] = []
        if not oauth_client_id:
            missing.append("GTM_OAUTH_CLIENT_ID")
        if not oauth_client_secret:
            missing.append("GTM_OAUTH_CLIENT_SECRET")
        if not oauth_refresh_token:
            missing.append("GTM_OAUTH_REFRESH_TOKEN")
        if missing:
            raise ValidationError("Missing required env var(s) for oauth_refresh_token: " + ", ".join(missing))
    if auth_mode == "service_account_json":
        if not service_account_json_path:
            raise ValidationError("Missing GTM_SERVICE_ACCOUNT_JSON_PATH for service_account_json mode")

    return Config(
        base_url=base_url,
        timeout_s=timeout_s,
        min_delay_s=min_delay_s,
        read_retries=read_retries,
        auth_mode=auth_mode,
        scopes=tuple(scopes),
        oauth_client_id=oauth_client_id,
        oauth_client_secret=oauth_client_secret,
        oauth_refresh_token=oauth_refresh_token,
        service_account_json_path=service_account_json_path,
    )
