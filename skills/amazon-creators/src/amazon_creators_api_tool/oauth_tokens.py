from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .config import Config
from .errors import ValidationError
from .token_urls import default_token_url


TOKEN_EXPIRY_SKEW_S = 60.0


@dataclass(frozen=True)
class TokenStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]
    has_refresh_token: bool | None
    expires_at_utc: str | None


def token_path_for_env_file(env_file: str) -> Path:
    """
    Store OAuth tokens next to the env file (per-environment), under `.state/token.json`.
    """
    root = Path(env_file).resolve().parent
    return root / ".state" / "token.json"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _parse_iso_timestamp(value: str) -> float | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


def _ensure_expiry_fields(data: dict[str, Any], *, now: float | None = None) -> None:
    timestamp = float(now if now is not None else time.time())
    if "fetched_at" not in data or not isinstance(data["fetched_at"], (int, float)):
        data["fetched_at"] = timestamp
    if "expires_at" in data:
        return
    expires_in = data.get("expires_in")
    if expires_in is None:
        return
    try:
        expires_delta = float(expires_in)
    except (TypeError, ValueError):
        return
    data["expires_at"] = timestamp + expires_delta


def read_token_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")
    return data


def write_token_from_file(*, src_file: Path, dest_file: Path) -> TokenStatus:
    if not src_file.exists():
        raise RuntimeError(f"Token file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")

    _ensure_expiry_fields(data)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return get_token_status(dest_file)


def get_token_status(path: Path) -> TokenStatus:
    if not path.exists():
        return TokenStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
            has_refresh_token=None,
            expires_at_utc=None,
        )

    data = read_token_json(path) or {}
    fields = sorted([k for k in data.keys() if isinstance(k, str)])
    has_refresh_token = None
    if "refresh_token" in data:
        has_refresh_token = bool(data.get("refresh_token"))

    expires_at_utc = None
    if isinstance(data.get("expires_at"), (int, float)):
        expires_at_utc = _utc(float(data["expires_at"]))
    elif isinstance(data.get("expires_at"), str) and data["expires_at"].strip():
        expires_at_utc = data["expires_at"].strip()
    elif isinstance(data.get("expiry"), str) and data["expiry"].strip():
        expires_at_utc = data["expiry"].strip()

    st = path.stat()
    return TokenStatus(
        exists=True,
        path=str(path),
        updated_at_utc=_utc(st.st_mtime),
        fields=fields,
        has_refresh_token=has_refresh_token,
        expires_at_utc=expires_at_utc,
    )


def redact_token_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a safe view of a token dict (no secrets).
    """
    out: dict[str, Any] = {}
    for k, v in data.items():
        lk = str(k).lower()
        if lk in {"access_token", "refresh_token", "id_token", "client_secret", "token"} or lk.endswith("_token"):
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


def load_cached_token(path: Path) -> dict[str, Any] | None:
    return read_token_json(path)


def _expiry_timestamp(data: dict[str, Any]) -> float | None:
    expires_at = data.get("expires_at")
    if isinstance(expires_at, (int, float)):
        return float(expires_at)
    if isinstance(expires_at, str):
        numeric = expires_at.strip()
        if numeric.isdigit():
            try:
                return float(numeric)
            except ValueError:
                pass
        parsed = _parse_iso_timestamp(numeric)
        if parsed is not None:
            return parsed
    expiry = data.get("expiry")
    if isinstance(expiry, str):
        parsed = _parse_iso_timestamp(expiry.strip())
        if parsed is not None:
            return parsed
    expires_in = data.get("expires_in")
    if expires_in is not None:
        base_ts = None
        fetched_at = data.get("fetched_at")
        if isinstance(fetched_at, (int, float)):
            base_ts = float(fetched_at)
        else:
            base_ts = time.time()
        try:
            delta = float(expires_in)
        except (TypeError, ValueError):
            return None
        return base_ts + delta
    return None


def _ensure_token_not_expired(data: dict[str, Any]) -> None:
    expiry = _expiry_timestamp(data)
    if expiry is None:
        return
    if expiry <= time.time() + TOKEN_EXPIRY_SKEW_S:
        raise ValidationError(
            "Cached OAuth token has expired or is about to expire. Run "
            "`amazon-creators-api-tool auth token fetch` to review the blocked refresh plan."
        )


def _first_token_value(data: dict[str, Any]) -> str | None:
    for key in ("access_token", "token", "accessToken"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_credential_version(value: str | None) -> str:
    if not value:
        return ""
    normalized = str(value).strip()
    if normalized.lower().startswith("v"):
        normalized = normalized[1:].strip()
    return normalized


def authorization_header(cfg: object, env_file: str) -> str:
    token_data = load_cached_token(token_path_for_env_file(env_file))
    if not token_data:
        raise ValidationError(
            "No cached OAuth token found. Run "
            "`amazon-creators-api-tool auth token fetch` to review the blocked token-cache plan."
        )
    _ensure_token_not_expired(token_data)
    access_token = _first_token_value(token_data)
    if not access_token:
        raise ValidationError("Token file is missing an access token value.")
    header = f"Bearer {access_token}"
    version = _normalize_credential_version(getattr(cfg, "credential_version", ""))
    if version.startswith("2"):
        header = f"{header}, Version {version}"
    return header


def fetch_and_cache_token(cfg: Config, env_file: str, *, force: bool = False) -> TokenStatus:
    path = token_path_for_env_file(env_file)
    if not force:
        cached = load_cached_token(path)
        if cached:
            try:
                _ensure_token_not_expired(cached)
                return get_token_status(path)
            except ValidationError:
                pass

    token_url = cfg.token_url or default_token_url(cfg.credential_version, cfg.locale)
    version = _normalize_credential_version(getattr(cfg, "credential_version", ""))
    if version.startswith("3"):
        # v3.x credentials (LwA) use JSON and a different scope token.
        payload: dict[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": cfg.credential_id,
            "client_secret": cfg.credential_secret,
            "scope": "creatorsapi::default",
        }
        request_kwargs: dict[str, Any] = {
            "json": payload,
            "headers": {"Content-Type": "application/json"},
        }
    else:
        # v2.x credentials (Cognito) use form-encoded payload.
        payload = {
            "grant_type": "client_credentials",
            "client_id": cfg.credential_id,
            "client_secret": cfg.credential_secret,
            "scope": "creatorsapi/default",
        }
        request_kwargs = {
            "data": payload,
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        }
    try:
        resp = requests.post(token_url, timeout=cfg.timeout_s, **request_kwargs)
    except requests.RequestException as exc:
        raise RuntimeError(f"Token request failed: {type(exc).__name__}") from exc

    if resp.status_code >= 400:
        raise RuntimeError(f"Token request failed with status {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError("Token response was not valid JSON") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Token response must be a JSON object")

    _ensure_expiry_fields(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return get_token_status(path)
