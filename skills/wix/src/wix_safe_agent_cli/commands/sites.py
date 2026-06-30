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


def _normalize_sort(sort_value: Any, field: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    if sort_value is None:
        return None
    if isinstance(sort_value, list):
        for i, item in enumerate(sort_value):
            if not isinstance(item, dict):
                raise ValidationError(f"Each item in --{field} must be an object")
            if not item:
                raise ValidationError(f"Item {i} in --{field} cannot be empty")
        return sort_value
    if isinstance(sort_value, dict):
        if not sort_value:
            raise ValidationError(f"--{field} cannot be empty")
        return sort_value
    raise ValidationError(f"--{field} must be an object or list of objects")


def _ensure_query_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"query": {}}
    if not isinstance(payload, dict):
        raise ValidationError("--query-json must be an object")
    if isinstance(payload.get("query"), dict):
        return dict(payload)
    return {"query": payload}


def _extract_filter_from_query(query_obj: dict[str, Any]) -> dict[str, Any] | None:
    if "filter" in query_obj and isinstance(query_obj.get("filter"), dict):
        return query_obj["filter"]
    nested = query_obj.get("query")
    if isinstance(nested, dict) and isinstance(nested.get("filter"), dict):
        return nested["filter"]
    return None


def _coerce_paging(*, cursor: str | None, limit: int | None) -> dict[str, Any]:
    if cursor is None and limit is None:
        return {}
    if limit is not None and limit > 100:
        raise ValidationError("--limit for sites query must be 100 or less")
    if limit is not None and limit <= 0:
        raise ValidationError("--limit must be a positive integer")

    paging: dict[str, Any] = {}
    if cursor is not None:
        paging["cursor"] = cursor
    if limit is not None:
        paging["limit"] = int(limit)
    return paging


def _build_query_body(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_value: dict[str, Any] | list[dict[str, Any]] | None,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    payload = _ensure_query_payload(query_json)
    query_obj = payload.get("query")
    if not isinstance(query_obj, dict):
        raise ValidationError("Query payload must include a query object")

    if filter_json is not None and "filter" not in query_obj:
        query_obj["filter"] = filter_json
    if sort_value is not None and "sort" not in query_obj:
        query_obj["sort"] = sort_value

    paging = _coerce_paging(cursor=cursor, limit=limit)
    if paging:
        query_obj["cursorPaging"] = paging
    return payload


def _validate_count_filters(filter_json: dict[str, Any] | None) -> None:
    if not filter_json:
        return
    if "premium" in filter_json:
        raise ValidationError("Count Sites does not support filtering by premium. Remove premium and use count without that filter.")
    if "appIds" in filter_json:
        raise ValidationError("Count Sites does not support filtering by appIds. Remove appIds and use a supported filter.")


def _build_count_body(*, query_json: dict[str, Any] | None, filter_json: dict[str, Any] | None) -> dict[str, Any]:
    if filter_json is not None and not isinstance(filter_json, dict):
        raise ValidationError("--filter-json must be an object")

    if query_json is not None and not isinstance(query_json, dict):
        raise ValidationError("--query-json must be an object")

    body_filter: dict[str, Any] | None = None
    if query_json is not None:
        payload = _ensure_query_payload(query_json)
        top_query = payload.get("query")
        if not isinstance(top_query, dict):
            raise ValidationError("Query payload must be an object")
        body_filter = _extract_filter_from_query(top_query)
        if body_filter is None and "filter" in payload and isinstance(payload["filter"], dict):
            body_filter = payload["filter"]

    if filter_json is not None and body_filter is not None:
        raise ValidationError("Do not pass both --query-json filter and --filter-json. Use one filter source.")

    effective_filter = filter_json if filter_json is not None else body_filter
    if effective_filter is None:
        return {}

    _validate_count_filters(effective_filter)
    return {"filter": effective_filter}


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )

    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_sites_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")

        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), "sort-json")
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        body = _build_query_body(
            query_json=dict(query_json) if isinstance(query_json, dict) else None,
            filter_json=filter_json,
            sort_value=sort_value,
            cursor=cursor,
            limit=getattr(args, "limit", None),
        )

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="sites",
        )

        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-list/v2/sites/query",
            headers=auth["headers"],
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "sites.query",
            "auth_mode": auth["mode"],
            "request": {
                "method": "POST",
                "path": "/site-list/v2/sites/query",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("sites.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_sites_count(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")

        body = _build_count_body(
            query_json=dict(query_json) if isinstance(query_json, dict) else None,
            filter_json=filter_json,
        )

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="sites",
        )

        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-list/v2/sites/count",
            headers=auth["headers"],
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "sites.count",
            "auth_mode": auth["mode"],
            "request": {
                "method": "POST",
                "path": "/site-list/v2/sites/count",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("sites.count", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1
