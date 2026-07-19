from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

from .errors import ValidationError
from .http import HttpResponse
from .state import read_json_object, write_private_json

AUTHORIZE_URL = "https://login.xero.com/identity/connect/authorize"
TOKEN_URL = "https://identity.xero.com/connect/token"


class TokenStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()

    def write(self, token: dict[str, Any]) -> None:
        if not isinstance(token.get("access_token"), str) or not token["access_token"]:
            raise ValidationError("Xero token response is missing access_token")
        stored = dict(token)
        stored["credential_fingerprint"] = hashlib.sha256(
            str(stored["access_token"]).encode("utf-8")
        ).hexdigest()
        now = int(time.time())
        stored["stored_at"] = now
        if isinstance(stored.get("expires_in"), (int, float)):
            stored["expires_at"] = now + int(stored["expires_in"])
        write_private_json(self.path, stored)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            raise ValidationError("No local Xero token. Run auth start and auth exchange first.")
        try:
            token = read_json_object(self.path)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(f"Local Xero token file is invalid: {type(exc).__name__}") from None
        if not isinstance(token.get("access_token"), str) or not token["access_token"]:
            raise ValidationError("Local Xero token has no access_token")
        actual_fingerprint = hashlib.sha256(
            str(token["access_token"]).encode("utf-8")
        ).hexdigest()
        if token.get("credential_fingerprint") != actual_fingerprint:
            raise ValidationError("Local Xero token credential fingerprint is invalid")
        return token

    def status(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "exists": False,
                "path": str(self.path),
                "has_refresh_token": None,
                "expires_at": None,
                "scopes": [],
            }
        token = self.read()
        raw_scopes = token.get("scope") or []
        scopes = raw_scopes.split() if isinstance(raw_scopes, str) else list(raw_scopes)
        return {
            "exists": True,
            "path": str(self.path),
            "has_refresh_token": bool(token.get("refresh_token")),
            "expires_at": token.get("expires_at"),
            "scopes": sorted(str(value) for value in scopes),
        }


def begin_pkce(
    *,
    client_id: str,
    redirect_uri: str,
    scopes: list[str],
    state_dir: str | Path,
    verifier: str | None = None,
    state: str | None = None,
) -> dict[str, Any]:
    if not client_id.strip():
        raise ValidationError("Missing XERO_CLIENT_ID")
    try:
        parsed_redirect = urlsplit(redirect_uri)
        hostname = parsed_redirect.hostname
    except ValueError:
        hostname = None
        parsed_redirect = None
    # Xero permits insecure loopback redirects only for the literal localhost host.
    local_hosts = {"localhost"}
    valid_https = bool(
        parsed_redirect
        and parsed_redirect.scheme.lower() == "https"
        and hostname
        and parsed_redirect.username is None
        and parsed_redirect.password is None
    )
    valid_loopback_http = bool(
        parsed_redirect
        and parsed_redirect.scheme.lower() == "http"
        and hostname in local_hosts
        and parsed_redirect.username is None
        and parsed_redirect.password is None
    )
    if not valid_https and not valid_loopback_http:
        raise ValidationError(
            "Xero redirect URI must be HTTPS or use the exact localhost host over HTTP"
        )
    requested = sorted(set(str(value).strip() for value in scopes if str(value).strip()))
    if not requested:
        raise ValidationError("Choose at least one command scope before starting Xero authorization")
    code_verifier = verifier or secrets.token_urlsafe(64)
    if not 43 <= len(code_verifier) <= 128:
        raise ValidationError("PKCE verifier must be 43 to 128 characters")
    csrf_state = state or secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    state_path = Path(state_dir).expanduser().resolve() / "pkce.json"
    write_private_json(
        state_path,
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": requested,
            "state": csrf_state,
            "code_verifier": code_verifier,
            "created_at": int(time.time()),
        },
    )
    authorization_url = AUTHORIZE_URL + "?" + urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(requested),
            "state": csrf_state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    return {
        "ok": True,
        "authorization_url": authorization_url,
        "redirect_uri": redirect_uri,
        "scopes": requested,
        "state_path": str(state_path),
        "next": "Open the authorization URL, then pass the returned code and state to auth exchange.",
    }


def load_pkce_state(path: str | Path, *, returned_state: str) -> dict[str, Any]:
    try:
        stored = read_json_object(path)
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"PKCE state file is invalid: {type(exc).__name__}") from None
    if not secrets.compare_digest(str(stored.get("state") or ""), returned_state):
        raise ValidationError("Returned OAuth state does not match the saved PKCE request")
    if int(time.time()) - int(stored.get("created_at") or 0) > 900:
        raise ValidationError("Saved PKCE request is older than 15 minutes; start authorization again")
    return stored


def _token_payload(response: HttpResponse) -> dict[str, Any]:
    if response.status >= 400:
        raise ValidationError(f"Xero token endpoint returned HTTP {response.status}")
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValidationError("Xero token endpoint returned an invalid response") from None
    if not isinstance(payload, dict) or not payload.get("access_token"):
        raise ValidationError("Xero token endpoint response has no access_token")
    return payload


def exchange_pkce(
    *,
    transport: Any,
    state_path: str | Path,
    code_file: str | Path,
    returned_state: str,
    token_store: TokenStore,
) -> dict[str, Any]:
    stored = load_pkce_state(state_path, returned_state=returned_state)
    source = Path(code_file).expanduser().resolve()
    if not source.is_file():
        raise ValidationError(f"OAuth code file not found: {source}")
    code = source.read_text(encoding="utf-8").strip()
    if not code or any(character.isspace() for character in code):
        raise ValidationError("OAuth code file must contain exactly one authorization code")
    response = transport.request(
        "POST",
        TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "grant_type": "authorization_code",
            "client_id": stored["client_id"],
            "code": code,
            "redirect_uri": stored["redirect_uri"],
            "code_verifier": stored["code_verifier"],
        },
        retries=0,
    )
    payload = _token_payload(response)
    if not payload.get("scope"):
        payload["scope"] = " ".join(str(value) for value in stored.get("scopes") or [])
    token_store.write(payload)
    return {"ok": True, "token": token_store.status(), "next": "Discover and select a Xero tenant."}


def refresh_pkce(*, transport: Any, client_id: str, token_store: TokenStore) -> dict[str, Any]:
    token = token_store.read()
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise ValidationError("Local Xero token has no refresh_token; authorize again with offline_access")
    response = transport.request(
        "POST",
        TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        },
        retries=0,
    )
    payload = _token_payload(response)
    if not payload.get("scope"):
        payload["scope"] = token.get("scope") or []
    if not payload.get("refresh_token") and token.get("refresh_token"):
        payload["refresh_token"] = token["refresh_token"]
    token_store.write(payload)
    return {"ok": True, "token": token_store.status()}


def client_credentials_token(
    *,
    transport: Any,
    client_id: str,
    client_secret: str,
    scopes: list[str],
    token_store: TokenStore,
) -> dict[str, Any]:
    if not client_id or not client_secret:
        raise ValidationError("Client credentials require a client ID and client secret in the local env file")
    if not scopes:
        raise ValidationError("Client credentials require at least one explicit scope")
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode("ascii")
    response = transport.request(
        "POST",
        TOKEN_URL,
        headers={"Accept": "application/json", "Authorization": "Basic " + basic},
        data={"grant_type": "client_credentials", "scope": " ".join(sorted(set(scopes)))},
        retries=0,
    )
    payload = _token_payload(response)
    if not payload.get("scope"):
        payload["scope"] = " ".join(sorted(set(scopes)))
    token_store.write(payload)
    return {"ok": True, "token": token_store.status()}
