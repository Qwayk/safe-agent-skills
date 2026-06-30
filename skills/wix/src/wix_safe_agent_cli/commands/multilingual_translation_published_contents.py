from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")
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


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-translation-published-contents",
    )
    return auth["headers"], auth["mode"]


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


def _query_body(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_json: Any,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    body = dict(query_json) if isinstance(query_json, dict) and isinstance(query_json.get("query"), dict) else {"query": dict(query_json or {})}
    query = body["query"]
    if filter_json is not None:
        if not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")
        query.setdefault("filter", filter_json)
    if sort_json is not None:
        if not isinstance(sort_json, (dict, list)):
            raise ValidationError("--sort-json must be an object or array")
        query.setdefault("sort", sort_json)
    if cursor or limit is not None:
        if limit is not None and (limit <= 0 or limit > 100):
            raise ValidationError("--limit must be between 1 and 100")
        paging = dict(query.get("cursorPaging") or {})
        if cursor:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        query["cursorPaging"] = paging
    _validate_required_schema_key_filter(query.get("filter"))
    return body


def _has_filter_value(filter_obj: Any, dotted_field: str) -> bool:
    if not isinstance(filter_obj, dict):
        return False
    if dotted_field in filter_obj:
        return True
    parts = dotted_field.split(".")
    node: Any = filter_obj
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def _validate_required_schema_key_filter(filter_obj: Any) -> None:
    missing = [field for field in ("schemaKey.appId", "schemaKey.entityType", "schemaKey.scope") if not _has_filter_value(filter_obj, field)]
    if missing:
        raise ValidationError("Published content query requires filters for schemaKey.appId, schemaKey.entityType, and schemaKey.scope")


def _emit_read(*, method: str, request: dict[str, Any], response: dict[str, Any], auth_mode: str, ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_multilingual_translation_published_contents_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), "query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        body = _query_body(
            query_json=query_json,
            filter_json=_read_json_arg(getattr(args, "filter_json", None), "filter-json"),
            sort_json=_read_json_arg(getattr(args, "sort_json", None), "sort-json"),
            cursor=str(getattr(args, "cursor", "") or "").strip() or None,
            limit=getattr(args, "limit", None),
        )
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/translation-published-content/v3/published-contents/query"
        response = _request_json(method="POST", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, json_body=body, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-published-contents.query", request={"method": "POST", "path": path, "body": body}, response=response, auth_mode=auth_mode, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-published-contents.query"})
        return 1
