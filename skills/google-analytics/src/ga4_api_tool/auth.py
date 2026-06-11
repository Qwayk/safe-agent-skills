from __future__ import annotations

from dataclasses import dataclass

try:
    import google.auth  # type: ignore[import-not-found]
    from google.auth.credentials import Credentials  # type: ignore[import-not-found]
    from google.auth.transport.requests import Request  # type: ignore[import-not-found]
    from google.oauth2 import credentials as oauth_credentials  # type: ignore[import-not-found]
    from google.oauth2 import service_account  # type: ignore[import-not-found]
except Exception:  # noqa: BLE001
    google = None  # type: ignore[assignment]
    Credentials = object  # type: ignore[misc,assignment]
    Request = object  # type: ignore[misc,assignment]
    oauth_credentials = None  # type: ignore[assignment]
    service_account = None  # type: ignore[assignment]

from .config import Config
from .errors import ValidationError


@dataclass(frozen=True)
class AuthSummary:
    auth_mode: str
    scopes_count: int
    service_account_json: str | None
    has_refresh_token: bool | None


def build_credentials(cfg: Config) -> Credentials:
    if google is None:
        raise ValidationError("Missing dependency: google-auth (install via: pip install -e '.[dev]')")
    scopes = list(cfg.scopes)
    mode = cfg.auth_mode

    if mode == "adc":
        creds, _ = google.auth.default(scopes=scopes)  # type: ignore[union-attr]
        return creds

    if mode == "service_account_json":
        if not cfg.service_account_json:
            raise ValidationError("Missing GA4_SERVICE_ACCOUNT_JSON for service_account_json auth mode")
        return service_account.Credentials.from_service_account_file(cfg.service_account_json, scopes=scopes)  # type: ignore[union-attr]

    if mode == "oauth_refresh_token":
        if not (cfg.oauth_client_id and cfg.oauth_client_secret and cfg.oauth_refresh_token):
            raise ValidationError("Missing OAuth refresh token config (client_id/client_secret/refresh_token)")
        return oauth_credentials.Credentials(  # type: ignore[union-attr]
            token=None,
            refresh_token=cfg.oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cfg.oauth_client_id,
            client_secret=cfg.oauth_client_secret,
            scopes=scopes,
        )

    raise ValidationError(f"Unknown auth_mode: {mode}")


def ensure_fresh_access_token(creds: Credentials) -> None:
    if creds.valid and getattr(creds, "token", None):
        return
    creds.refresh(Request())  # type: ignore[misc]


def authorization_header(cfg: Config, *, refresh: bool) -> dict[str, str]:
    creds = build_credentials(cfg)
    if refresh:
        ensure_fresh_access_token(creds)
    token = getattr(creds, "token", None)
    if not token:
        raise ValidationError("No access token available (try GA4_AUTH_MODE=adc or refresh-token/service-account auth)")
    return {"Authorization": f"Bearer {token}"}


def auth_summary(cfg: Config) -> dict:
    return {
        "auth_mode": cfg.auth_mode,
        "scopes_count": len(cfg.scopes),
        "service_account_json": cfg.service_account_json if cfg.auth_mode == "service_account_json" else None,
        "has_refresh_token": bool(cfg.oauth_refresh_token) if cfg.auth_mode == "oauth_refresh_token" else None,
    }
