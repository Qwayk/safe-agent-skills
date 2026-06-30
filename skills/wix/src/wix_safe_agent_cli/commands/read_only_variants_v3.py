from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        return {}
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


def _coerce_wrapped_payload(raw: Any, *, field: str, wrapper_key: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        return {}
    if wrapper_key in payload:
        nested = payload.get(wrapper_key)
        if not isinstance(nested, dict):
            raise ValidationError(f"--{field} {wrapper_key} must be a JSON object")
        return payload
    return {wrapper_key: payload}


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if json_body is not None:
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


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _resolve_read_only_variants_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="read-only-variants-v3",
    )
    return auth["headers"], auth["mode"]


def cmd_read_only_variants_v3_query(args, ctx) -> int:
    try:
        body = _coerce_wrapped_payload(getattr(args, "query_json", None), field="query-json", wrapper_key="query")
        headers, auth_mode = _resolve_read_only_variants_v3_auth(ctx=ctx)
        request_path = "/stores/v3/products/query-variants"
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="read-only-variants-v3.query",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "read-only-variants-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "read-only-variants-v3.query"}
        )
        return 1


def cmd_read_only_variants_v3_search(args, ctx) -> int:
    try:
        body = _coerce_wrapped_payload(
            getattr(args, "search_json", None),
            field="search-json",
            wrapper_key="search",
        )
        headers, auth_mode = _resolve_read_only_variants_v3_auth(ctx=ctx)
        request_path = "/stores/v3/products/search-variants"
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="read-only-variants-v3.search",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "read-only-variants-v3.search"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "read-only-variants-v3.search"}
        )
        return 1
