from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


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


def _coerce_stores_location_id(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --stores-location-id")
    if not isinstance(raw, str):
        raise ValidationError("--stores-location-id must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError("Missing --stores-location-id")
    return value


def _coerce_query_payload(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="query-json")
    if not isinstance(payload, dict):
        raise ValidationError("--query-json must be a JSON object")
    if "query" in payload:
        nested = payload.get("query")
        if not isinstance(nested, dict):
            raise ValidationError("--query-json query must be a JSON object")
        return payload
    return {"query": payload}


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


def _resolve_stores_locations_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="stores-locations-v3",
    )
    return auth["headers"], auth["mode"]


def cmd_stores_locations_v3_get(args, ctx) -> int:
    try:
        stores_location_id = _coerce_stores_location_id(getattr(args, "stores_location_id", None))
        headers, auth_mode = _resolve_stores_locations_v3_auth(ctx=ctx)
        request_path = f"/stores/v3/locations/{stores_location_id}"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="stores-locations-v3.get",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-locations-v3.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-locations-v3.get"}
        )
        return 1


def cmd_stores_locations_v3_query(args, ctx) -> int:
    try:
        body = _coerce_query_payload(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_stores_locations_v3_auth(ctx=ctx)
        request_path = "/stores/v3/locations/query"
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
            method="stores-locations-v3.query",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-locations-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-locations-v3.query"}
        )
        return 1
