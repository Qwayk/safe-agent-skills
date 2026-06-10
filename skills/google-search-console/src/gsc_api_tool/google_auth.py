from __future__ import annotations

import json
import os
import stat
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import credentials as google_credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

from .errors import ToolError, ValidationError


DEFAULT_SCOPES = [
    # Full-access scope (includes read-only capabilities).
    "https://www.googleapis.com/auth/webmasters",
]


def credentials_path_for_env_file(env_file: str) -> Path:
    """
    Store OAuth credentials next to the env file (per-environment), under `.state/`.
    """
    root = Path(env_file).resolve().parent
    return root / ".state" / "gsc_oauth_credentials.json"


@dataclass(frozen=True)
class CredentialsInfo:
    kind: str  # installed_app | service_account
    scopes: list[str]
    expiry_utc: str | None
    valid: bool
    exists: bool
    path: str | None


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _parse_scopes(raw: str | None) -> list[str]:
    raw = str(raw or "").strip()
    if not raw:
        return list(DEFAULT_SCOPES)
    scopes = [s.strip() for s in raw.split(",") if s.strip()]
    return scopes or list(DEFAULT_SCOPES)


def get_scopes_from_env(env: dict[str, str]) -> list[str]:
    # OS env overrides env-file behavior is handled by config.py; this helper is for config parsing.
    raw = env.get("GSC_OAUTH_SCOPES") or ""
    return _parse_scopes(raw)


def read_installed_app_credentials(path: Path) -> google_credentials.Credentials | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid credentials JSON: {path}: {type(e).__name__}: {e}") from None
    if not isinstance(data, dict):
        raise ValidationError(f"Invalid credentials JSON: {path}: must be an object")
    try:
        return google_credentials.Credentials.from_authorized_user_info(data)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid credentials JSON: {path}: {type(e).__name__}: {e}") from None


def write_installed_app_credentials(path: Path, creds: google_credentials.Credentials) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(creds.to_json() + "\n", encoding="utf-8")
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass
    return str(path)


def login_installed_app(
    *,
    client_secrets_file: str,
    scopes: list[str],
    dest_path: Path,
) -> CredentialsInfo:
    p = Path(client_secrets_file)
    if not p.exists():
        raise ValidationError(f"Client secrets file not found: {p}")
    flow = InstalledAppFlow.from_client_secrets_file(str(p), scopes=scopes)
    creds = flow.run_local_server(access_type="offline", prompt="consent")
    write_installed_app_credentials(dest_path, creds)
    info = describe_credentials(creds, kind="installed_app", exists=True, path=str(dest_path))
    return info


def load_service_account_credentials(
    *,
    service_account_file: str,
    scopes: list[str],
) -> service_account.Credentials:
    p = Path(service_account_file)
    if not p.exists():
        raise ValidationError(f"Service account file not found: {p}")
    try:
        return service_account.Credentials.from_service_account_file(str(p), scopes=scopes)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid service account file: {p}: {type(e).__name__}: {e}") from None


def ensure_fresh(creds: Any) -> None:
    try:
        if getattr(creds, "valid", False) and not getattr(creds, "expired", False):
            return
        req = GoogleAuthRequest()
        creds.refresh(req)
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Failed to refresh credentials: {type(e).__name__}: {e}") from None


def describe_credentials(
    creds: Any,
    *,
    kind: str,
    exists: bool,
    path: str | None,
) -> CredentialsInfo:
    scopes = list(getattr(creds, "scopes", None) or []) if creds is not None else []
    expiry = getattr(creds, "expiry", None)
    expiry_utc = None
    try:
        if expiry is not None:
            expiry_utc = str(expiry).replace(" ", "T")
    except Exception:
        expiry_utc = None
    valid = bool(getattr(creds, "valid", False)) if creds is not None else False
    return CredentialsInfo(
        kind=kind,
        scopes=[str(s) for s in scopes],
        expiry_utc=expiry_utc,
        valid=valid,
        exists=exists,
        path=path,
    )


def load_credentials_from_config(
    *,
    env_file: str,
    oauth_client_secrets_file: str | None,
    service_account_file: str | None,
    scopes: list[str],
) -> tuple[Any | None, CredentialsInfo]:
    if service_account_file:
        creds = load_service_account_credentials(service_account_file=service_account_file, scopes=scopes)
        ensure_fresh(creds)
        return creds, describe_credentials(creds, kind="service_account", exists=True, path=str(service_account_file))

    dest_path = credentials_path_for_env_file(env_file)
    creds = read_installed_app_credentials(dest_path)
    if creds is None:
        return None, CredentialsInfo(
            kind="installed_app",
            scopes=scopes,
            expiry_utc=None,
            valid=False,
            exists=False,
            path=str(dest_path),
        )

    if oauth_client_secrets_file:
        try:
            # Ensure the stored creds match the intended scopes if the user changed them.
            creds = google_credentials.Credentials(
                token=creds.token,
                refresh_token=creds.refresh_token,
                token_uri=creds.token_uri,
                client_id=creds.client_id,
                client_secret=creds.client_secret,
                scopes=scopes,
            )
        except Exception:
            pass

    ensure_fresh(creds)
    return creds, describe_credentials(creds, kind="installed_app", exists=True, path=str(dest_path))

