from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests

from .config import Config
from .errors import ValidationError


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
    settings_file = Path(env_file).resolve()
    if settings_file.name == ".env":
        return settings_file.parent / ".state" / "token.json"
    suffix = hashlib.sha256(settings_file.name.encode()).hexdigest()[:24]
    return settings_file.parent / ".state" / f"token-{suffix}.json"


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
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except ValueError:
        raise ValidationError("The saved token file is invalid. Fetch a new token.") from None
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")
    return data


def _write_private_token(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_token_from_file(*, src_file: Path, dest_file: Path) -> TokenStatus:
    if not src_file.exists():
        raise RuntimeError(f"Token file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")

    _ensure_expiry_fields(data)
    _write_private_token(dest_file, data)
    return get_token_status(dest_file)


def get_token_status(path: Path) -> TokenStatus:
    data = read_token_json(path)
    if data is None:
        return TokenStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
            has_refresh_token=None,
            expires_at_utc=None,
        )

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
        fetched_at = data.get("fetched_at")
        if not isinstance(fetched_at, (int, float)):
            return None
        try:
            delta = float(expires_in)
        except (TypeError, ValueError):
            return None
        return float(fetched_at) + delta
    return None


def _ensure_token_not_expired(data: dict[str, Any]) -> None:
    expiry = _expiry_timestamp(data)
    if expiry is None or not math.isfinite(expiry):
        raise ValidationError("The saved token has no valid expiry time. Fetch a new token.")
    if expiry <= time.time() + TOKEN_EXPIRY_SKEW_S:
        raise ValidationError(
            "Cached OAuth token has expired or is about to expire. Run "
            "`amazon-creators-api-tool auth token fetch` to preview the refresh."
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


def _validated_token(cfg: Config, token_data: dict[str, Any] | None) -> str:
    if not token_data:
        raise ValidationError(
            "No cached OAuth token found. Run "
            "`amazon-creators-api-tool auth token fetch` to preview getting a token."
        )
    if token_data.get("account_fingerprint") != cfg.account_fingerprint:
        raise ValidationError("The saved token is not tied to these credentials. Fetch a new token for this account.")
    _ensure_token_not_expired(token_data)
    access_token = _first_token_value(token_data)
    if not access_token:
        raise ValidationError("Token file is missing an access token value.")
    return access_token


def authorization_header(cfg: Config, env_file: str) -> str:
    access_token = _validated_token(cfg, load_cached_token(token_path_for_env_file(env_file)))
    header = f"Bearer {access_token}"
    version = _normalize_credential_version(cfg.credential_version)
    if version.startswith("2"):
        header = f"{header}, Version {version}"
    return header


def fetch_and_cache_token(cfg: Config, env_file: str, *, force: bool = False) -> TokenStatus:
    path = token_path_for_env_file(env_file)
    if not force:
        try:
            _validated_token(cfg, load_cached_token(path))
        except ValidationError:
            pass
        else:
            return get_token_status(path)

    token_url = cfg.token_endpoint
    endpoint = urlsplit(token_url)
    if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username is not None:
        raise ValidationError("The Amazon token endpoint must be an HTTPS URL without login details.")
    version = _normalize_credential_version(cfg.credential_version)
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
        resp = requests.post(token_url, timeout=cfg.timeout_s, allow_redirects=False, **request_kwargs)
    except requests.RequestException as exc:
        raise RuntimeError(f"Token request failed: {type(exc).__name__}") from None

    if not 200 <= resp.status_code < 300:
        raise RuntimeError(f"Token request failed with status {resp.status_code}")

    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError("Token response was not valid JSON") from None

    if not isinstance(data, dict):
        raise RuntimeError("Token response must be a JSON object")

    data["account_fingerprint"] = cfg.account_fingerprint
    _ensure_expiry_fields(data, now=time.time())
    _validated_token(cfg, data)
    _write_private_token(path, data)
    return get_token_status(path)
