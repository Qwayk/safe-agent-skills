from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse, urlunparse

from .config import Config
from .errors import ValidationError


@dataclass(frozen=True)
class AuthResult:
    headers: dict[str, str]
    basic: tuple[str, str] | None
    warnings: tuple[str, ...]
    public_summary: dict[str, Any]


def route_server(server: str, cfg: Config) -> str:
    if not (cfg.region and cfg.edge):
        return server.rstrip("/")
    parsed = urlparse(server)
    hostname = parsed.hostname or ""
    if not hostname.endswith(".twilio.com"):
        raise ValidationError("Pinned Twilio server is outside the allowed twilio.com boundary")
    prefix = hostname[: -len(".twilio.com")]
    routed_host = f"{prefix}.{cfg.edge}.{cfg.region}.twilio.com"
    if parsed.port:
        routed_host += f":{parsed.port}"
    return urlunparse((parsed.scheme, routed_host, parsed.path.rstrip("/"), "", "", ""))


def build_auth(
    operation: dict[str, Any],
    cfg: Config,
    declared_headers: dict[str, Any],
) -> AuthResult:
    headers = {str(key): str(value) for key, value in declared_headers.items()}
    declared_authorization = headers.get("Authorization")
    if declared_authorization:
        return AuthResult(
            headers=headers,
            basic=None,
            warnings=("Using the operation's declared Authorization header; live behavior is unverified.",),
            public_summary={"method": "declared_authorization_header", "fallback": False},
        )

    requirements = operation.get("security", {}).get("requirements", [])
    if not requirements:
        return AuthResult(headers=headers, basic=None, warnings=(), public_summary={"method": "none"})
    scheme_names = {name for alternative in requirements for name in alternative}
    if "oAuth2ClientCredentials" in scheme_names:
        if not cfg.oauth_access_token:
            raise ValidationError("This operation requires TWILIO_OAUTH_ACCESS_TOKEN")
        headers["Authorization"] = f"Bearer {cfg.oauth_access_token}"
        return AuthResult(
            headers=headers,
            basic=None,
            warnings=(),
            public_summary={"method": "oauth_client_credentials", "fallback": False},
        )
    if scheme_names & {"accountSid_authToken", "basic_apikey_or_accountsid"}:
        if cfg.api_key_sid and cfg.api_key_secret:
            return AuthResult(
                headers=headers,
                basic=(cfg.api_key_sid, cfg.api_key_secret),
                warnings=(),
                public_summary={"method": "api_key_basic", "fallback": False},
            )
        if cfg.auth_token:
            return AuthResult(
                headers=headers,
                basic=(cfg.account_sid, cfg.auth_token),
                warnings=("Using the Account Auth Token fallback; prefer a Restricted API key.",),
                public_summary={"method": "account_auth_token_basic", "fallback": True},
            )
        raise ValidationError("This operation requires Twilio Basic authentication")
    raise ValidationError("The pinned operation uses an unsupported authentication scheme")
