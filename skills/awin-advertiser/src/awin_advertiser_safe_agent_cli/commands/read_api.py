from __future__ import annotations

import datetime
from typing import Any

from ..config import Config
from ..errors import ValidationError
from ..http import HttpClient, HttpResponse, redact_sensitive_text


def redact_error(value: str, token: str | None) -> str:
    secrets = {token} if token else None
    return redact_sensitive_text(value, secrets=secrets)


def parse_iso8601(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} is required")
    raw = value.strip()
    try:
        datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} must be ISO8601") from exc
    return raw


def emit_setup_needed_result(
    out,
    *,
    error: str,
    next_step: str = "Run onboarding first: awin-advertiser-safe-cli onboarding",
) -> None:
    payload = {
        "ok": False,
        "blocked": True,
        "setup_needed": True,
        "error": error,
        "error_type": "SetupNeeded",
        "next_step": next_step,
    }
    out.emit(payload)


def require_read_context(out, cfg: Config | None) -> Config | None:
    if cfg is None or not cfg.base_url:
        emit_setup_needed_result(
            out,
            error="Missing configuration",
            next_step="Run onboarding first: awin-advertiser-safe-cli onboarding",
        )
        return None

    if not cfg.token:
        emit_setup_needed_result(
            out,
            error="Missing AWIN_API_TOKEN",
            next_step="Set AWIN_API_TOKEN in .env and run again",
        )
        return None

    return cfg


def read_request(
    http: HttpClient,
    *,
    base_url: str,
    token: str | None,
    endpoint: str,
    params: dict[str, Any] | None = None,
    method: str = "GET",
    include_access_token: bool = True,
) -> HttpResponse:
    if not token:
        raise ValidationError("Missing AWIN_API_TOKEN")

    query: dict[str, Any] = {}
    if include_access_token:
        query["accessToken"] = token
    if params:
        query.update(params)

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    return http.request(method, url, headers=headers, params=query)


def extract_list(payload: Any, *, keys: tuple[str, ...]) -> list[Any]:
    if isinstance(payload, list):
        return [x for x in payload]

    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value]
    return []
