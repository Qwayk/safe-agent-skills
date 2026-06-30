from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient

_ALLOWED_DOCUMENT_TYPES = {
    "BLOG_POSTS",
    "BOOKING_SERVICES",
    "EVENTS",
    "FORUM_CONTENT",
    "ONLINE_PROGRAMS",
    "PROGALLERY_ITEM",
    "STORES_PRODUCTS",
}


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string or @file path")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_document_type(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --document-type")
    if not isinstance(raw, str):
        raise ValidationError("--document-type must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError("Missing --document-type")
    if value not in _ALLOWED_DOCUMENT_TYPES:
        raise ValidationError(
            "--document-type must be one of: " + ", ".join(sorted(_ALLOWED_DOCUMENT_TYPES))
        )
    return value


def _coerce_optional_language(raw: Any) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError("--language must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("--language cannot be empty")
    return value


def _coerce_search_payload(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="search-json")
    if not isinstance(payload, dict):
        raise ValidationError("--search-json must be a JSON object")
    return payload


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


def cmd_site_search_search(args, ctx) -> int:
    try:
        document_type = _coerce_document_type(getattr(args, "document_type", None))
        search_payload = _coerce_search_payload(getattr(args, "search_json", None))
        language = _coerce_optional_language(getattr(args, "language", None))

        body: dict[str, Any] = {
            "documentType": document_type,
            "search": search_payload,
        }
        if language is not None:
            body["language"] = language

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="site-search",
        )
        request_path = "/_api/site-search/v1/search"
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
            "method": "site-search.search",
            "auth_mode": auth["mode"],
            "request": {
                "method": "POST",
                "path": request_path,
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("site-search.search", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
