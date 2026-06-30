from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .http import HttpClient

_REDACTED_TOKEN = "***REDACTED***"


@dataclass(frozen=True)
class TokenStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]
    has_refresh_token: bool | None
    has_access_token: bool | None
    expires_at_utc: str | None


def token_path_for_env_file(env_file: str) -> Path:
    """
    Store OAuth tokens next to the env file (per-environment), under `.state/token.json`.
    """
    root = Path(env_file).resolve().parent
    return root / ".state" / "token.json"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def read_token_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")
    return data


def write_token_from_dict(*, token_payload: dict[str, Any], dest_file: Path) -> TokenStatus:
    if not isinstance(token_payload, dict):
        raise RuntimeError("Token payload must be a JSON object")
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(json.dumps(token_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return get_token_status(dest_file)


def write_token_from_file(*, src_file: Path, dest_file: Path) -> TokenStatus:
    if not src_file.exists():
        raise RuntimeError(f"Token file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")

    return write_token_from_dict(token_payload=data, dest_file=dest_file)


def get_token_status(path: Path) -> TokenStatus:
    if not path.exists():
        return TokenStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
            has_refresh_token=None,
            has_access_token=None,
            expires_at_utc=None,
        )

    data = read_token_json(path) or {}
    fields = sorted([k for k in data.keys() if isinstance(k, str)])
    has_refresh_token = None
    if "refresh_token" in data:
        has_refresh_token = bool(data.get("refresh_token"))
    has_access_token = None
    if "access_token" in data:
        has_access_token = bool(data.get("access_token"))

    # Best-effort: many OAuth tokens store either `expires_at` (unix) or `expiry` (iso).
    expires_at_utc = None
    if isinstance(data.get("expires_at"), (int, float)):
        expires_at_utc = _utc(float(data["expires_at"]))
    elif isinstance(data.get("expiry"), str) and data["expiry"].strip():
        expires_at_utc = data["expiry"].strip()
    elif isinstance(data.get("expires_in"), (int, float)) and isinstance(data.get("_wix_issued_at"), (int, float)):
        expires_at_utc = _utc(float(data["_wix_issued_at"]) + float(data["expires_in"]))

    st = path.stat()
    return TokenStatus(
        exists=True,
        path=str(path),
        updated_at_utc=_utc(st.st_mtime),
        fields=fields,
        has_refresh_token=has_refresh_token,
        has_access_token=has_access_token,
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
            out[k] = _REDACTED_TOKEN
        else:
            out[k] = v
    return out


def _request_json(*, base_url: str, path: str, payload: dict[str, Any], timeout_s: float, verbose: bool) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request("POST", base_url.rstrip("/") + "/" + path.lstrip("/"), json_body=payload)
    body = response.json()
    if not isinstance(body, dict):
        raise RuntimeError(f"Wix endpoint returned non-object response: {path}")
    return body


def create_access_token(
    *, base_url: str, app_id: str, app_secret: str, instance_id: str, timeout_s: float, verbose: bool = False
) -> dict[str, Any]:
    if not app_id:
        raise RuntimeError("Missing WIX_APP_ID")
    if not app_secret:
        raise RuntimeError("Missing WIX_APP_SECRET")
    if not instance_id:
        raise RuntimeError("Missing WIX_INSTANCE_ID")
    return _request_json(
        base_url=base_url,
        path="/oauth2/token",
        payload={
            "grant_type": "client_credentials",
            "client_id": app_id,
            "client_secret": app_secret,
            "instance_id": instance_id,
        },
        timeout_s=timeout_s,
        verbose=verbose,
    )


def request_access_token(
    *,
    base_url: str,
    app_id: str,
    app_secret: str,
    code: str,
    timeout_s: float,
    verbose: bool = False,
) -> dict[str, Any]:
    if not app_id:
        raise RuntimeError("Missing WIX_APP_ID")
    if not app_secret:
        raise RuntimeError("Missing WIX_APP_SECRET")
    if not code:
        raise RuntimeError("Missing authorization code")
    return _request_json(
        base_url=base_url,
        path="/oauth/access",
        payload={
            "grant_type": "authorization_code",
            "client_id": app_id,
            "client_secret": app_secret,
            "code": code,
        },
        timeout_s=timeout_s,
        verbose=verbose,
    )


def inspect_access_token(*, base_url: str, token: str, timeout_s: float, verbose: bool = False) -> dict[str, Any]:
    if not token:
        raise RuntimeError("Missing token")
    return _request_json(
        base_url=base_url,
        path="/oauth2/token-info",
        payload={"token": token},
        timeout_s=timeout_s,
        verbose=verbose,
    )


def read_access_token_from_file(path: Path) -> str | None:
    data = read_token_json(path)
    if not isinstance(data, dict):
        return None
    token = data.get("access_token")
    return token.strip() if isinstance(token, str) and token.strip() else None


def read_refresh_token_from_file(path: Path) -> str | None:
    data = read_token_json(path)
    if not isinstance(data, dict):
        return None
    token = data.get("refresh_token")
    return token.strip() if isinstance(token, str) and token.strip() else None


def refresh_access_token(
    *, base_url: str, app_id: str, app_secret: str, refresh_token: str, timeout_s: float, verbose: bool = False
) -> dict[str, Any]:
    if not app_id:
        raise RuntimeError("Missing WIX_APP_ID")
    if not app_secret:
        raise RuntimeError("Missing WIX_APP_SECRET")
    if not refresh_token:
        raise RuntimeError("Missing refresh token")
    return _request_json(
        base_url=base_url,
        path="/oauth/access/",
        payload={
            "grant_type": "refresh_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "refresh_token": refresh_token,
        },
        timeout_s=timeout_s,
        verbose=verbose,
    )


def metadata_view(data: dict[str, Any]) -> dict[str, Any]:
    out = redact_token_dict(data)
    out["received_at_utc"] = _utc(time.time())
    return out
