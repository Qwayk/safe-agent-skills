from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import ValidationError
from .oauth_tokens import create_access_token, read_access_token_from_file, token_path_for_env_file


@dataclass(frozen=True)
class ResolvedAuth:
    headers: dict[str, str]
    mode: str


def _resolve_api_token(*, cfg, env_file: str, verbose: bool) -> str:
    token = getattr(cfg, "access_token", None)
    if token:
        return str(token).strip()

    token_file = token_path_for_env_file(env_file)
    token = read_access_token_from_file(token_file)
    if token:
        return token

    if not bool(getattr(cfg, "has_official_app_auth", False)):
        raise ValidationError(
            "Missing official Wix credentials and no access token source. Add WIX_ACCESS_TOKEN or app credentials."
        )

    token_response = create_access_token(
        base_url=cfg.base_url,
        app_id=cfg.app_id,
        app_secret=cfg.app_secret,
        instance_id=cfg.instance_id,
        timeout_s=cfg.timeout_s,
        verbose=verbose,
    )
    access_token = token_response.get("access_token") if isinstance(token_response, dict) else None
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValidationError("OAuth token response did not include access_token")
    return access_token.strip()


def _resolve_account_api_headers(*, cfg) -> dict[str, str]:
    api_key = getattr(cfg, "api_key", None)
    account_id = getattr(cfg, "account_id", None)
    if not api_key:
        raise ValidationError(
            "Missing required account API key. Set WIX_API_KEY and WIX_ACCOUNT_ID for account-level commands."
        )
    if not account_id:
        raise ValidationError(
            "Missing required account ID. Set WIX_API_KEY and WIX_ACCOUNT_ID for account-level commands."
        )

    return {
        "Authorization": str(api_key).strip(),
        "wix-account-id": str(account_id).strip(),
    }


def _resolve_ai_credits_api_headers(*, cfg) -> dict[str, str]:
    api_key = getattr(cfg, "api_key", None)
    if not api_key:
        raise ValidationError("Missing required AI Credits API key. Set WIX_API_KEY for ai-credits commands.")

    return {
        "Authorization": str(api_key).strip(),
    }


def resolve_authorization_headers(*, cfg, env_file: str, verbose: bool, command_family: str) -> ResolvedAuth:
    if command_family == "ai-credits":
        headers = _resolve_ai_credits_api_headers(cfg=cfg)
        return ResolvedAuth(headers=headers, mode="ai_credits_api_key_only")

    if command_family in {
        "accounts",
        "sites",
        "site-folders",
        "site-actions",
        "projects",
        "domains",
        "domain-dns",
        "dns-propagation",
        "connected-domains",
        "app-permissions-write",
        "resellers",
        "b2b-site-transfer",
        "partner-profiles",
    }:
        headers = _resolve_account_api_headers(cfg=cfg)
        return ResolvedAuth(headers=headers, mode="account_api_key")

    token = _resolve_api_token(cfg=cfg, env_file=env_file, verbose=verbose)
    return ResolvedAuth(headers={"Authorization": token}, mode="app_token")


def resolve_auth_mode(*, cfg, env_file: str, verbose: bool, command_family: str) -> dict[str, Any]:
    resolved = resolve_authorization_headers(cfg=cfg, env_file=env_file, verbose=verbose, command_family=command_family)
    return {
        "headers": resolved.headers,
        "mode": resolved.mode,
    }
