from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..http import HttpClient
from ..oauth_tokens import create_access_token, read_access_token_from_file, token_path_for_env_file


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


def _read_str_list(raw: Any, field: str) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
    return value


def _normalize_sort(sort_value: Any, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
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


def _coerce_cursor_paging(*, cursor: str | None, limit: int | None) -> dict[str, Any]:
    cursor_paging: dict[str, Any] = {}
    if cursor:
        cursor_paging["cursor"] = cursor
    if limit is not None:
        cursor_paging["limit"] = int(limit)
    return cursor_paging


def _build_query_payload(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_value: Any,
    fields: list[str] | None,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    payload = _ensure_query_payload(query_json)
    query_obj = payload.get("query")
    if not isinstance(query_obj, dict):
        raise ValidationError("Query payload must include a query object")

    if query_json is None:
        if filter_json is not None:
            query_obj["filter"] = filter_json
        if sort_value is not None:
            query_obj["sort"] = sort_value
    else:
        # Explicit query payload is treated as authoritative.
        pass

    cursor_paging = _coerce_cursor_paging(cursor=cursor, limit=limit)
    if cursor_paging:
        query_obj["cursorPaging"] = cursor_paging

    if fields is not None:
        payload["fields"] = fields
    return payload


def _build_search_payload(
    *,
    search_json: dict[str, Any] | None,
    expression: str | None,
    fields: list[str] | None,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    if search_json is not None:
        if not isinstance(search_json, dict):
            raise ValidationError("--search-json must be an object")
        payload = dict(search_json)
        search_obj = payload.get("search")
        if not isinstance(search_obj, dict):
            raise ValidationError("--search-json must include an object at `search`")
    else:
        if not expression:
            raise ValidationError("Missing --search text")
        payload = {"search": {"search": {"expression": expression}}}
        search_obj = payload["search"]

    cursor_paging = _coerce_cursor_paging(cursor=cursor, limit=limit)
    if cursor_paging:
        search_obj["cursorPaging"] = cursor_paging

    if fields is not None:
        payload["fields"] = fields
    return payload


def _resolve_access_token(*, cfg, env_file: str, verbose: bool) -> str:
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


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    headers = {"Authorization": token}
    if method.upper() != "GET":
        headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_app_installations_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), "sort-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        if sort_value is not None and not isinstance(sort_value, (dict, list)):
            raise ValidationError("--sort-json must be an object or list of objects")

        body = _build_query_payload(
            query_json=query_json,
            filter_json=filter_json,
            sort_value=sort_value,
            fields=fields,
            cursor=cursor,
            limit=getattr(args, "limit", None),
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/app/installations/v1/app-installation/query",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "app-installations.query",
            "request": {
                "method": "POST",
                "path": "/app/installations/v1/app-installation/query",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("app-installations.query", out)
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


def cmd_app_installations_search(args, ctx) -> int:
    try:
        search_json = _read_json_arg(getattr(args, "search_json", None), field="search-json")
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        expression = str(getattr(args, "search", "") or "").strip() or None
        body = _build_search_payload(
            search_json=search_json,
            expression=expression,
            fields=fields,
            cursor=cursor,
            limit=getattr(args, "limit", None),
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/app/installations/v1/app-installation/search",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "app-installations.search",
            "request": {
                "method": "POST",
                "path": "/app/installations/v1/app-installation/search",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("app-installations.search", out)
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
