from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import credentials as google_oauth_credentials
from google.oauth2 import service_account

from .config import Config
from .errors import ToolError, ValidationError
from .oauth_tokens import token_path_for_env_file


DEFAULT_OAUTH_SCOPES: tuple[str, ...] = ("https://www.googleapis.com/auth/content",)
DEFAULT_TOKEN_URI = "https://oauth2.googleapis.com/token"


@dataclass(frozen=True)
class CredentialsStatus:
    kind: str
    source: str | None
    valid: bool
    expiry_utc: str | None
    scopes: tuple[str, ...]
    path: str | None = None


def _utc(ts: float) -> str:
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _scope_list(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_OAUTH_SCOPES
    scopes = [x.strip() for x in raw.split(",") if x.strip()]
    return tuple(sorted(dict.fromkeys(scopes)).keys()) if scopes else DEFAULT_OAUTH_SCOPES


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ValidationError(f"OAuth token file not found: {path}") from e
    try:
        data = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"OAuth token file not valid JSON: {path}: {type(e).__name__}: {e}") from e
    if not isinstance(data, dict):
        raise ValidationError(f"OAuth token file must be an object: {path}")
    return data


def _looks_like_placeholder(raw: str | None) -> bool:
    text = (raw or "").strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered in {
        "replace_me",
        "replace-me",
        "your_value_here",
        "your_token_here",
        "your_client_id",
        "your_client_secret",
    }:
        return True
    if lowered.startswith("<") and lowered.endswith(">"):
        return True
    return False


def _load_oauth_token_source(
    cfg: Config,
    env_file: str,
) -> tuple[dict[str, Any], str]:
    raw = (cfg.oauth_refresh_token or "").strip()
    if raw:
        candidate = Path(os.path.expanduser(raw))
        if candidate.exists():
            return _read_json_file(candidate), str(candidate)

        if raw.startswith("{") and raw.endswith("}"):
            try:
                parsed = json.loads(raw)
            except Exception as e:  # noqa: BLE001
                raise ValidationError(f"Invalid inline OAuth JSON token: {type(e).__name__}: {e}") from e
            if not isinstance(parsed, dict):
                raise ValidationError("Inline OAuth token JSON must be an object")
            return parsed, "inline"

        if not _looks_like_placeholder(raw):
            return {"refresh_token": raw}, "inline"

    fallback = token_path_for_env_file(env_file)
    if not fallback.exists():
        raise ValidationError(
            "OAuth refresh token source not found. Set GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN "
            "or use auth token set --file <json>."
        )
    return _read_json_file(fallback), str(fallback)


def _ensure_credentials_refresh(creds: Any) -> Any:
    if not creds:
        return creds
    valid = bool(getattr(creds, "valid", False))
    expired = bool(getattr(creds, "expired", False))
    if valid and not expired:
        return creds
    request = GoogleAuthRequest()
    try:
        creds.refresh(request)
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Failed to refresh credentials: {type(e).__name__}: {e}") from e
    return creds


def _credential_status(creds: Any, *, kind: str, source: str | None) -> CredentialsStatus:
    expiry = getattr(creds, "expiry", None)
    if expiry is not None:
        try:
            expiry_ts = expiry.timestamp()
            expiry_utc = _utc(float(expiry_ts))
        except Exception:
            expiry_utc = None
    else:
        expiry_utc = None
    scopes = tuple(sorted({str(s) for s in (getattr(creds, "scopes", []) or [])}))
    return CredentialsStatus(
        kind=kind,
        source=source,
        valid=bool(getattr(creds, "valid", False)),
        expiry_utc=expiry_utc,
        scopes=scopes,
        path=source,
    )


def _redact_oauth_dict(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in data.items():
        lk = str(k).lower()
        if lk in {
            "access_token",
            "refresh_token",
            "id_token",
            "token",
            "client_secret",
            "token_uri",
        }:
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


def describe_oauth_file(path: Path) -> CredentialsStatus:
    data = _read_json_file(path)
    fake = google_oauth_credentials.Credentials(
        token=str(data.get("access_token") or ""),
        refresh_token=str(data.get("refresh_token") or ""),
        token_uri=str(data.get("token_uri") or DEFAULT_TOKEN_URI),
        client_id=str(data.get("client_id") or ""),
        client_secret=str(data.get("client_secret") or ""),
        scopes=[str(x) for x in data.get("scopes") if isinstance(x, str)] or list(DEFAULT_OAUTH_SCOPES),
    )
    return _credential_status(fake, kind="oauth_refresh_file", source=str(path))


def load_credentials_from_config(*, cfg: Config, env_file: str) -> tuple[Any, CredentialsStatus]:
    mode = (cfg.auth_mode or "").strip().lower()
    if not mode:
        raise ValidationError("Missing GOOGLE_MERCHANT_API_AUTH_MODE")

    if mode not in {"service_account_json", "oauth_refresh_token", "adc"}:
        raise ValidationError(
            f"Unsupported auth mode: {mode}. Expected service_account_json, oauth_refresh_token, or adc"
        )

    if mode == "service_account_json":
        path_raw = (cfg.service_account_json or "").strip()
        if _looks_like_placeholder(path_raw):
            raise ValidationError("GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON is required for service_account_json mode")
        sa_path = Path(os.path.expanduser(path_raw))
        if not sa_path.exists():
            raise ValidationError(f"Service account JSON not found: {sa_path}")
        try:
            creds = service_account.Credentials.from_service_account_file(
                str(sa_path), scopes=list(cfg.oauth_scopes or DEFAULT_OAUTH_SCOPES)
            )
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Invalid service account JSON: {sa_path}: {type(e).__name__}: {e}") from e
        _ensure_credentials_refresh(creds)
        return creds, _credential_status(creds, kind="service_account_json", source=str(sa_path))

    if mode == "oauth_refresh_token":
        data, source = _load_oauth_token_source(cfg, env_file)

        client_id = str(data.get("client_id") or cfg.oauth_client_id or "").strip()
        client_secret = str(data.get("client_secret") or cfg.oauth_client_secret or "").strip()
        if _looks_like_placeholder(client_id) or _looks_like_placeholder(client_secret):
            raise ValidationError("OAuth client_id/client_secret are required for oauth_refresh_token mode")

        token_uri = str(data.get("token_uri") or cfg.oauth_token_uri or DEFAULT_TOKEN_URI).strip() or DEFAULT_TOKEN_URI
        refresh_token = data.get("refresh_token")
        if not isinstance(refresh_token, str) or not refresh_token.strip():
            raise ValidationError("OAuth token file missing refresh_token")
        if _looks_like_placeholder(str(refresh_token).strip()):
            raise ValidationError("OAuth refresh_token value looks like a placeholder")

        try:
            creds = google_oauth_credentials.Credentials(
                token=data.get("access_token") if isinstance(data.get("access_token"), str) else None,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=list(cfg.oauth_scopes or DEFAULT_OAUTH_SCOPES),
            )
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Invalid OAuth refresh credentials: {type(e).__name__}: {e}") from e

        _ensure_credentials_refresh(creds)
        info = _credential_status(creds, kind="oauth_refresh_token", source=source)
        return creds, info

    # adc
    try:
        creds, _ = google.auth.default(scopes=list(cfg.oauth_scopes or DEFAULT_OAUTH_SCOPES))
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Failed to load ADC credentials: {type(e).__name__}: {e}") from e
    _ensure_credentials_refresh(creds)
    return creds, _credential_status(creds, kind="adc", source=str(getattr(creds, "quota_project_id", None)))


def redacted_credentials_info(data: dict[str, Any]) -> dict[str, Any]:
    return _redact_oauth_dict(data)
