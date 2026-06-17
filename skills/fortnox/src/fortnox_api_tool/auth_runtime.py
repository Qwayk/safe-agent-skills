from __future__ import annotations

import base64
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

from .errors import ValidationError
from .http import HttpClient
from .oauth_tokens import (
    TokenStatus,
    access_token_from_dict,
    get_token_status,
    read_token_json,
    refresh_token_from_dict,
    redact_token_dict,
    token_is_expired,
    token_path_for_env_file,
    write_token_dict,
)


@dataclass(frozen=True)
class ResolvedAccessToken:
    token: str | None
    source: str
    expired: bool | None
    status: TokenStatus
    token_path: str


def oauth_state_path_for_env_file(env_file: str, token_override: str | None = None) -> Path:
    _ = token_override
    root = Path(env_file).resolve().parent
    return root / ".state" / "oauth_state.json"


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"State file must be a JSON object: {path}")
    return data


def _write_json_object(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _token_headers(cfg, *, tenant_id: str | None = None) -> dict[str, str]:
    if not cfg.client_id or not cfg.client_secret:
        raise ValidationError("FORTNOX_CLIENT_ID and FORTNOX_CLIENT_SECRET are required")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": _basic_auth_header(cfg.client_id, cfg.client_secret),
    }
    if tenant_id:
        headers["TenantId"] = tenant_id
    return headers


def _call_token_endpoint(*, url: str, headers: dict[str, str], form: dict[str, str], timeout_s: float) -> dict[str, Any]:
    resp = requests.post(url, headers=headers, data=form, timeout=timeout_s)
    text = resp.text or ""
    try:
        payload = json.loads(text) if text.strip() else {}
    except Exception:
        payload = {"raw_response": text[:4000]}
    if resp.status_code >= 400:
        if isinstance(payload, dict):
            error = str(payload.get("error") or "").strip()
            description = str(payload.get("error_description") or "").strip()
            if error or description:
                raise RuntimeError(f"Token endpoint rejected the request: {error or 'error'} {description}".strip())
        raise RuntimeError(f"Token endpoint returned HTTP {resp.status_code}")
    if not isinstance(payload, dict):
        raise RuntimeError("Token endpoint response must be a JSON object")
    return payload


def resolve_access_token(*, cfg, env_file: str) -> ResolvedAccessToken:
    token_path = token_path_for_env_file(env_file, cfg.token_file)
    status = get_token_status(token_path)
    if cfg.api_token:
        return ResolvedAccessToken(
            token=cfg.api_token,
            source="env",
            expired=None,
            status=status,
            token_path=str(token_path),
        )

    token_data = read_token_json(token_path) or {}
    access_token = access_token_from_dict(token_data)
    expired = token_is_expired(token_data) if access_token else None
    if access_token:
        return ResolvedAccessToken(
            token=access_token,
            source="token_file",
            expired=expired,
            status=status,
            token_path=str(token_path),
        )

    return ResolvedAccessToken(
        token=None,
        source="missing",
        expired=None,
        status=status,
        token_path=str(token_path),
    )


def build_authorize_url(*, cfg, env_file: str, scopes: tuple[str, ...], service_account: bool, state: str | None) -> dict[str, Any]:
    if not cfg.client_id:
        raise ValidationError("FORTNOX_CLIENT_ID is required for auth login")
    if not cfg.redirect_uri:
        raise ValidationError("FORTNOX_REDIRECT_URI is required for auth login")
    if not scopes:
        raise ValidationError("At least one scope is required for auth login")

    actual_state = (state or "").strip() or secrets.token_urlsafe(24)
    params = {
        "client_id": cfg.client_id,
        "response_type": "code",
        "state": actual_state,
        "scope": " ".join(scopes),
        "redirect_uri": cfg.redirect_uri,
        "access_type": "offline",
    }
    if service_account:
        params["account_type"] = "service"

    url = cfg.oauth_authorize_url + "?" + urlencode(params)
    state_path = oauth_state_path_for_env_file(env_file, cfg.token_file)
    _write_json_object(
        state_path,
        {
            "state": actual_state,
            "redirect_uri": cfg.redirect_uri,
            "scope": list(scopes),
            "service_account": service_account,
        },
    )
    return {
        "authorize_url": url,
        "state": actual_state,
        "state_file": str(state_path),
        "scope": list(scopes),
        "service_account": service_account,
        "redirect_uri": cfg.redirect_uri,
    }


def exchange_authorization_code(
    *,
    cfg,
    env_file: str,
    code: str,
    state: str | None,
    timeout_s: float,
) -> dict[str, Any]:
    code_value = str(code or "").strip()
    if not code_value:
        raise ValidationError("--code is required")
    if not cfg.redirect_uri:
        raise ValidationError("FORTNOX_REDIRECT_URI is required for auth exchange-code")

    state_path = oauth_state_path_for_env_file(env_file, cfg.token_file)
    saved_state = _read_json_object(state_path)
    if saved_state and str(saved_state.get("state") or "").strip():
        expected = str(saved_state.get("state") or "").strip()
        provided = str(state or "").strip()
        if not provided:
            raise ValidationError(f"--state is required because {state_path} exists")
        if provided != expected:
            raise ValidationError("The provided --state does not match the saved login state")

    payload = _call_token_endpoint(
        url=cfg.oauth_token_url,
        headers=_token_headers(cfg),
        form={
            "grant_type": "authorization_code",
            "code": code_value,
            "redirect_uri": cfg.redirect_uri,
        },
        timeout_s=timeout_s,
    )
    token_path = token_path_for_env_file(env_file, cfg.token_file)
    status = write_token_dict(
        data=payload,
        dest_file=token_path,
        existing=read_token_json(token_path),
        token_source="authorization_code",
        grant_type="authorization_code",
        preserve_refresh_token=False,
    )
    token_data = read_token_json(token_path) or {}
    if state_path.exists():
        state_path.unlink()
    return {
        "stored_to": str(token_path),
        "token_status": status.__dict__,
        "token": redact_token_dict(token_data),
    }


def refresh_access_token(*, cfg, env_file: str, timeout_s: float) -> dict[str, Any]:
    token_path = token_path_for_env_file(env_file, cfg.token_file)
    existing = read_token_json(token_path) or {}
    refresh_token = cfg.refresh_token or refresh_token_from_dict(existing)
    if not refresh_token:
        raise ValidationError(
            "Missing refresh token. Set FORTNOX_REFRESH_TOKEN or store a token file with `auth exchange-code` or `auth token set`."
        )

    payload = _call_token_endpoint(
        url=cfg.oauth_token_url,
        headers=_token_headers(cfg),
        form={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout_s=timeout_s,
    )
    status = write_token_dict(
        data=payload,
        dest_file=token_path,
        existing=existing,
        token_source="refresh_token",
        grant_type="refresh_token",
        preserve_refresh_token=True,
    )
    token_data = read_token_json(token_path) or {}
    return {
        "stored_to": str(token_path),
        "token_status": status.__dict__,
        "token": redact_token_dict(token_data),
    }


def request_service_account_access_token(
    *,
    cfg,
    env_file: str,
    scopes: tuple[str, ...],
    timeout_s: float,
) -> dict[str, Any]:
    tenant_id = str(cfg.service_tenant_id or "").strip()
    if not tenant_id:
        raise ValidationError("FORTNOX_SERVICE_TENANT_ID is required for service-account token requests")

    form = {"grant_type": "client_credentials"}
    if scopes:
        form["scope"] = " ".join(scopes)

    payload = _call_token_endpoint(
        url=cfg.oauth_token_url,
        headers=_token_headers(cfg, tenant_id=tenant_id),
        form=form,
        timeout_s=timeout_s,
    )
    token_path = token_path_for_env_file(env_file, cfg.token_file)
    status = write_token_dict(
        data=payload,
        dest_file=token_path,
        existing=None,
        token_source="service_account_client_credentials",
        grant_type="client_credentials",
        tenant_id=tenant_id,
        preserve_refresh_token=False,
    )
    token_data = read_token_json(token_path) or {}
    return {
        "stored_to": str(token_path),
        "tenant_id": tenant_id,
        "scope": list(scopes),
        "token_status": status.__dict__,
        "token": redact_token_dict(token_data),
    }


def get_me(*, cfg, access_token: str, timeout_s: float, verbose: bool, user_agent: str) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)
    resp = client.request(
        "GET",
        f"{cfg.base_url}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not resp.body:
        return {}
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Expected /me to return a JSON object")
    return data
