from __future__ import annotations

import dataclasses
import time
from typing import Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import credentials as oauth_credentials
from google.oauth2 import service_account

from .config import Config
from .errors import ValidationError


@dataclasses.dataclass(frozen=True)
class AccessToken:
    token: str
    expiry_utc: str | None


def _utc_ts(dt: Any) -> str | None:
    try:
        if not dt:
            return None
        # google-auth returns datetime with tzinfo in many cases; fall back to best-effort.
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def auth_summary(cfg: Config) -> dict[str, Any]:
    """
    Safe-to-print summary (never includes token values, client secrets, or refresh tokens).
    """
    return {
        "mode": cfg.auth_mode,
        "scopes": list(cfg.scopes),
        "scopes_count": len(cfg.scopes),
        "service_account_json_path": cfg.service_account_json_path if cfg.auth_mode == "service_account_json" else None,
        "oauth": {
            "client_id_present": bool(cfg.oauth_client_id) if cfg.auth_mode == "oauth_refresh_token" else None,
            "client_secret_present": bool(cfg.oauth_client_secret) if cfg.auth_mode == "oauth_refresh_token" else None,
            "refresh_token_present": bool(cfg.oauth_refresh_token) if cfg.auth_mode == "oauth_refresh_token" else None,
        },
    }


def get_access_token(cfg: Config) -> AccessToken:
    """
    Fetch/refresh an access token according to cfg.auth_mode.

    Never print token values.
    """
    req = Request()

    if cfg.auth_mode == "oauth_refresh_token":
        if not (cfg.oauth_client_id and cfg.oauth_client_secret and cfg.oauth_refresh_token):
            raise ValidationError("oauth_refresh_token mode is missing required credentials")
        creds = oauth_credentials.Credentials(
            token=None,
            refresh_token=cfg.oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cfg.oauth_client_id,
            client_secret=cfg.oauth_client_secret,
            scopes=list(cfg.scopes),
        )
        creds.refresh(req)
        if not creds.token:
            raise ValidationError("Failed to obtain an access token (oauth_refresh_token)")
        return AccessToken(token=creds.token, expiry_utc=_utc_ts(getattr(creds, "expiry", None)))

    if cfg.auth_mode == "service_account_json":
        if not cfg.service_account_json_path:
            raise ValidationError("service_account_json mode is missing GTM_SERVICE_ACCOUNT_JSON_PATH")
        creds = service_account.Credentials.from_service_account_file(
            cfg.service_account_json_path,
            scopes=list(cfg.scopes),
        )
        creds.refresh(req)
        if not creds.token:
            raise ValidationError("Failed to obtain an access token (service_account_json)")
        return AccessToken(token=creds.token, expiry_utc=_utc_ts(getattr(creds, "expiry", None)))

    if cfg.auth_mode == "adc":
        creds, _project = google.auth.default(scopes=list(cfg.scopes))
        creds.refresh(req)
        tok = getattr(creds, "token", None)
        if not tok:
            raise ValidationError("Failed to obtain an access token (adc)")
        return AccessToken(token=str(tok), expiry_utc=_utc_ts(getattr(creds, "expiry", None)))

    raise ValidationError(f"Unsupported auth_mode: {cfg.auth_mode}")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

