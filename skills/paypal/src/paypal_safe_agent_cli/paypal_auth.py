from __future__ import annotations

import dataclasses
from typing import Any

from .config import Config
from .http import HttpClient


@dataclasses.dataclass(frozen=True)
class AccessTokenResult:
    access_token: str
    token_type: str
    expires_in: int | None
    scope: str | None
    app_id: str | None
    source: str
    nonce: str | None = None


def resolve_access_token(*, cfg: Config, verbose: bool, timeout_s: float | None = None) -> AccessTokenResult:
    if cfg.access_token:
        return AccessTokenResult(
            access_token=cfg.access_token,
            token_type="Bearer",
            expires_in=None,
            scope=None,
            app_id=None,
            source="env-access-token",
            nonce=None,
        )

    if not cfg.client_id or not cfg.client_secret:
        raise RuntimeError("PayPal client credentials are missing")

    client = HttpClient(
        timeout_s=timeout_s if timeout_s is not None else cfg.timeout_s,
        verbose=verbose,
        user_agent="qwayk-paypal-safe-agent-cli/safe-apis",
    )
    response = client.request(
        "POST",
        f"{cfg.base_url}/v1/oauth2/token",
        auth=(cfg.client_id, cfg.client_secret),
        headers={
            "Accept": "application/json",
            "Accept-Language": cfg.accept_language or "en_US",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )
    payload = response.json()
    access_token = str(payload.get("access_token") or "").strip()
    if not access_token:
        raise RuntimeError("PayPal token response did not include access_token")

    expires_in_raw = payload.get("expires_in")
    expires_in: int | None
    if isinstance(expires_in_raw, int):
        expires_in = expires_in_raw
    elif isinstance(expires_in_raw, str) and expires_in_raw.isdigit():
        expires_in = int(expires_in_raw)
    else:
        expires_in = None

    return AccessTokenResult(
        access_token=access_token,
        token_type=str(payload.get("token_type") or "Bearer"),
        expires_in=expires_in,
        scope=str(payload.get("scope") or "").strip() or None,
        app_id=str(payload.get("app_id") or "").strip() or None,
        source="oauth2-client-credentials",
        nonce=str(payload.get("nonce") or "").strip() or None,
    )
