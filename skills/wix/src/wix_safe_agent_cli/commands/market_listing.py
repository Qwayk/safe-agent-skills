from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient

_MAX_PAGE_SIZE = 50


def _coerce_search_term(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --search-term")
    if not isinstance(raw, str):
        raise ValidationError("--search-term must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("Missing --search-term")
    return value


def _coerce_language_code(raw: Any) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError("--language-code must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("--language-code cannot be empty")
    return value


def _coerce_limit(raw: Any) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise ValidationError("--limit must be an integer between 1 and 50")
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError("--limit must be an integer between 1 and 50") from exc
    if value < 1 or value > _MAX_PAGE_SIZE:
        raise ValidationError("--limit must be an integer between 1 and 50")
    return value


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_market_listing_search(args, ctx) -> int:
    try:
        search_term = _coerce_search_term(getattr(args, "search_term", None))
        language_code = _coerce_language_code(getattr(args, "language_code", None))
        limit = _coerce_limit(getattr(args, "limit", None))

        body: dict[str, Any] = {"searchTerm": search_term}
        if language_code is not None:
            body["languageCode"] = language_code
        if limit is not None:
            body["paging"] = {"limit": limit}

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="market-listing",
        )
        request_path = "/devcenter/app-market-listing/v1/market-listings/search"
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "market-listing.search",
            "auth_mode": auth["mode"],
            "request": {
                "method": "POST",
                "path": request_path,
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("market-listing.search", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
