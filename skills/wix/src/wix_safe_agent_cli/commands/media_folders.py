from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


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


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        return None
    return value


def _coerce_bool_arg(value: Any, field: str) -> bool:
    if not isinstance(value, str):
        raise ValidationError(f"--{field} must be true or false")
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValidationError(f"--{field} must be true or false")


def _coerce_str_list(raw: Any, *, field: str, max_count: int | None = None) -> list[str]:
    value = _read_json_arg(raw, field=field)
    if value is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if max_count is not None and len(value) > max_count:
        raise ValidationError(f"--{field} supports at most {max_count} values")

    seen: set[str] = set()
    normalized: list[str] = []
    for i, raw_id in enumerate(value):
        if not isinstance(raw_id, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        value_str = raw_id.strip()
        if not value_str:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if value_str in seen:
            raise ValidationError(f"--{field} contains duplicate value: {value_str}")
        seen.add(value_str)
        normalized.append(value_str)
    return normalized


def _coerce_sort(raw: Any, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if isinstance(value, dict):
        if not value:
            raise ValidationError(f"--{field} cannot be empty")
        return value
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be an object or list of objects")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field}[{i}] must be an object")
        if not item:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        field_name = item.get("fieldName")
        if not isinstance(field_name, str) or not field_name.strip():
            raise ValidationError(f"--{field}[{i}].fieldName must be a string")
        order = item.get("order")
        if not isinstance(order, str) or not order.strip():
            raise ValidationError(f"--{field}[{i}].order must be a string")
    return value


def _coerce_root_folder(raw: Any, *, field: str) -> str:
    value = _coerce_optional_text(raw=raw, field=field) or "MEDIA_ROOT"
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_query_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if value is None:
        return {"query": {}}
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if isinstance(value.get("query"), dict):
        return value
    return {"query": value}


def _coerce_int_if_set(value: Any, *, field: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValidationError(f"--{field} must be an integer")
    if value < 0:
        raise ValidationError(f"--{field} must be 0 or greater")
    return value


def _require_positive_limit(limit: int | None, *, max_value: int, field: str = "limit") -> int | None:
    if limit is None:
        return None
    if limit <= 0:
        raise ValidationError(f"--{field} must be greater than 0")
    if limit > max_value:
        raise ValidationError(f"--{field} must be at most {max_value}")
    return limit


def _resolve_media_folders_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="media-folders",
    )
    return auth["headers"], auth["mode"]


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


def _extract_folder(payload: dict[str, Any], *, context: str) -> dict[str, Any]:
    if "folder" in payload:
        folder = payload.get("folder")
        if isinstance(folder, dict):
            return folder
        raise ValidationError(f"{context} returned no folder object")

    if "id" in payload and isinstance(payload.get("id"), str):
        return payload

    raise ValidationError(f"{context} returned no folder object")


def _add_sort_query_params(sort_value: Any, params: dict[str, Any]) -> None:
    if sort_value is None:
        return
    if isinstance(sort_value, list):
        if not sort_value:
            return
        sort_obj = sort_value[0]
    else:
        sort_obj = sort_value

    if not isinstance(sort_obj, dict):
        raise ValidationError("sort json must include an object or list of objects")

    if "fieldName" in sort_obj:
        params["sort.fieldName"] = str(sort_obj["fieldName"])
    if "order" in sort_obj:
        params["sort.order"] = str(sort_obj["order"])


def _build_list_params(
    *,
    parent_folder_id: str | None,
    cursor: str | None,
    limit: int | None,
    sort_json: Any,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if parent_folder_id:
        params["parentFolderId"] = parent_folder_id
    if cursor is not None:
        params["paging.cursor"] = cursor
    if limit is not None:
        params["paging.limit"] = int(limit)
    _add_sort_query_params(sort_value=sort_json, params=params)
    return params


def _build_search_body(
    *,
    search: str | None,
    root_folder: str,
    sort_json: Any,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "rootFolder": root_folder,
    }
    if search is not None:
        body["search"] = search
    if sort_json is not None:
        if isinstance(sort_json, list):
            if not sort_json:
                raise ValidationError("--sort-json cannot be empty")
            body["sort"] = sort_json[0]
        else:
            body["sort"] = sort_json
    if cursor is not None or limit is not None:
        paging: dict[str, Any] = {}
        if cursor is not None:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        body["paging"] = paging
    return body


def _build_query_body(*, query_json: dict[str, Any] | None, sort_json: Any, limit: int | None, offset: int | None) -> dict[str, Any]:
    payload = dict(query_json or {"query": {}})
    query = payload.get("query")
    if not isinstance(query, dict):
        raise ValidationError("query-json must include a query object")
    query = dict(query)
    payload["query"] = query

    if sort_json is not None and "sort" not in query:
        query["sort"] = sort_json
    if limit is not None or offset is not None:
        paging: dict[str, Any] = {}
        if limit is not None:
            paging["limit"] = int(limit)
        if offset is not None:
            paging["offset"] = int(offset)
        query["paging"] = paging
    return payload


def _fetch_folder(*, folder_id: str, auth_headers: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/site-media/v1/folders/{folder_id}",
        headers=auth_headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_folder(payload, context="folder preflight")


def _fetch_folders(*, folder_ids: list[str], auth_headers: dict[str, str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    if not folder_ids:
        return []
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/site-media/v1/folders/query",
        headers=auth_headers,
        params=None,
        json_body={
            "query": {
                "filter": {"id": {"$in": folder_ids}},
                "paging": {"limit": len(folder_ids)},
            },
        },
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    folders_raw = payload.get("folders")
    if not isinstance(folders_raw, list):
        raise ValidationError("folder query returned invalid response")
    folders: list[dict[str, Any]] = []
    for folder in folders_raw:
        if not isinstance(folder, dict):
            continue
        folder_id = str(folder.get("id") or "").strip()
        if folder_id:
            folders.append(folder)
    index = {str(folder.get("id") or ""): folder for folder in folders}
    missing: list[str] = [folder_id for folder_id in folder_ids if folder_id not in index]
    if missing:
        raise SafetyError("Refused: requested folder id(s) not found: " + ", ".join(missing))
    return [index[folder_id] for folder_id in folder_ids]


def _build_selector(
    *,
    operation: str,
    folder_id: str | None = None,
    folder_ids: list[str] | None = None,
    permanent: bool | None = None,
    display_name: str | None = None,
    parent_folder_id: str | None = None,
) -> dict[str, Any]:
    selector = {
        "kind": "wix-media-folder",
        "operation": operation,
    }
    if folder_id:
        selector["folder_id"] = folder_id
    if folder_ids is not None:
        selector["folder_ids"] = folder_ids
    if permanent is not None:
        selector["permanent"] = permanent
    if display_name is not None:
        selector["display_name"] = display_name
    if parent_folder_id is not None:
        selector["parent_folder_id"] = parent_folder_id
    return selector


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
    verification_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --apply and --yes",
        "apply requires --plan-in and reviewed plan",
    ]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")

    risk_reasons = ["wix-media-folder-write"]
    if requires_ack:
        risk_reasons.append("irreversible")

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                "Captured folder state before planning." if has_before_state else "No useful before-state snapshot is available for this write."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan
        or {"type": "provider-response", "notes": "Verification is limited to the API response in this slice."},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Keep the saved plan and receipts for manual recovery planning."
            if has_before_state
            else "No automatic rollback and no useful before-state snapshot is available.",
        },
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _assert_no_state_drift(*, method: str, selector: dict[str, Any], current_state: dict[str, Any] | None, plan: dict[str, Any]) -> None:
    baseline = plan.get("baseline", {})
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if not before_state:
        return
    if method in {"media-folders.update", "media-folders.bulk-delete", "media-folders.bulk-restore"} and before_state != current_state:
        raise SafetyError("Refused: target state changed since plan was created")


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _build_receipt(*, method: str, selector: dict[str, Any], request: dict[str, Any], response: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any], verification: dict[str, Any] | None = None) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(response),
        "verification": verification
        or {"type": "provider-response", "notes": "Provider response was returned and should be inspected manually."},
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No useful before-state snapshot was available for this receipt."
            ),
        },
        "diff_applied": plan.get("proposed_changes", []),
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use plan and before-state as a reference." if has_before_state else "Recovery is manual and no reliable before-state snapshot exists."
            ),
        },
    }


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="media-folders")


def _emit_refused(ctx: dict[str, Any], *, method: str, exc: Exception) -> None:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": exc.__class__.__name__,
            "method": method,
        }
    )


def _emit_validation_error(ctx: dict[str, Any], exc: ValidationError) -> None:
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})


def _emit_runtime_error(ctx: dict[str, Any], exc: RuntimeError) -> None:
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})


def cmd_media_folders_list(args, ctx) -> int:
    try:
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")
        cursor = getattr(args, "cursor", None)
        limit = _coerce_int_if_set(getattr(args, "limit", None), field="limit")
        limit = _require_positive_limit(limit, max_value=100)
        sort_json = _coerce_sort(getattr(args, "sort_json", None), field="sort-json")

        params = _build_list_params(
            parent_folder_id=parent_folder_id,
            cursor=cursor,
            limit=limit,
            sort_json=sort_json,
        )

        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = "/site-media/v1/folders"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        request = {"method": "GET", "path": request_path}
        if params:
            request["params"] = params

        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.list",
                "auth_mode": auth_mode,
                "request": request,
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_get(args, ctx) -> int:
    try:
        folder_id = _coerce_required_text(getattr(args, "folder_id", None), field="folder-id")
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = f"/site-media/v1/folders/{folder_id}"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": request_path},
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_search(args, ctx) -> int:
    try:
        search = _coerce_optional_text(getattr(args, "search", None), field="search")
        root_folder = _coerce_root_folder(getattr(args, "root_folder", None), field="root-folder")
        cursor = getattr(args, "cursor", None)
        limit = _coerce_int_if_set(getattr(args, "limit", None), field="limit")
        limit = _require_positive_limit(limit, max_value=200)
        sort_json = _coerce_sort(getattr(args, "sort_json", None), field="sort-json")

        body = _build_search_body(
            search=search,
            root_folder=root_folder,
            sort_json=sort_json,
            cursor=cursor,
            limit=limit,
        )
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = "/site-media/v1/folders/search"
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.search",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": request_path, "body": body},
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_query(args, ctx) -> int:
    try:
        limit = _coerce_int_if_set(getattr(args, "limit", None), field="limit")
        offset = _coerce_int_if_set(getattr(args, "offset", None), field="offset")
        limit = _require_positive_limit(limit, max_value=200)
        sort_json = _coerce_sort(getattr(args, "sort_json", None), field="sort-json")
        query_json = _coerce_query_payload(getattr(args, "query_json", None), field="query-json")

        body = _build_query_body(
            query_json=query_json,
            sort_json=sort_json,
            limit=limit,
            offset=offset,
        )
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = "/site-media/v1/folders/query"
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": request_path, "body": body},
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_list_deleted(args, ctx) -> int:
    try:
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")
        cursor = getattr(args, "cursor", None)
        limit = _coerce_int_if_set(getattr(args, "limit", None), field="limit")
        limit = _require_positive_limit(limit, max_value=100)
        sort_json = _coerce_sort(getattr(args, "sort_json", None), field="sort-json")

        params = _build_list_params(
            parent_folder_id=parent_folder_id,
            cursor=cursor,
            limit=limit,
            sort_json=sort_json,
        )
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = "/site-media/v1/trash-bin/folders"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        request = {"method": "GET", "path": request_path}
        if params:
            request["params"] = params

        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.list-deleted",
                "auth_mode": auth_mode,
                "request": request,
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_create(args, ctx) -> int:
    try:
        display_name = _coerce_required_text(getattr(args, "display_name", None), field="display-name")
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")

        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        body: dict[str, Any] = {"displayName": display_name}
        if parent_folder_id:
            body["parentFolderId"] = parent_folder_id

        request = {
            "method": "POST",
            "path": "/site-media/v1/folders",
            "body": body,
        }
        selector = _build_selector(
            operation="create",
            display_name=display_name,
            parent_folder_id=parent_folder_id,
        )

        if _should_apply(ctx):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="media-folders.create", expected_selector=selector, ctx=ctx)
            _assert_no_state_drift(method="media-folders.create", selector=selector, current_state=None, plan=plan)
            response = _request_json(
                method="POST",
                base_url=ctx["cfg"].base_url,
                path=request["path"],
                headers=auth_headers,
                params=None,
                json_body=body,
                timeout_s=float(ctx["cfg"].timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            receipt = _build_receipt(
                method="media-folders.create",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("media-folders.create.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "media-folders.create",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        plan = _build_plan(
            method="media-folders.create",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state={},
            proposed_changes=[{"operation": "create", "display_name": display_name}],
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "media-folders.create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except SafetyError as exc:
        _emit_refused(ctx, method="media-folders.create", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_update(args, ctx) -> int:
    try:
        folder_id = _coerce_required_text(getattr(args, "folder_id", None), field="folder-id")
        display_name = _coerce_optional_text(getattr(args, "display_name", None), field="display-name")
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")

        if display_name is None and parent_folder_id is None:
            raise ValidationError("--display-name or --parent-folder-id is required for media-folders update")

        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        folder_payload: dict[str, Any] = {}
        if display_name is not None:
            folder_payload["displayName"] = display_name
        if parent_folder_id is not None:
            folder_payload["parentFolderId"] = parent_folder_id
        folder_payload["id"] = folder_id

        request = {
            "method": "PATCH",
            "path": f"/site-media/v1/folders/{folder_id}",
            "body": {"folder": folder_payload},
        }

        selector = _build_selector(
            operation="update",
            folder_id=folder_id,
            display_name=display_name,
            parent_folder_id=parent_folder_id,
        )

        if _should_apply(ctx):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="media-folders.update", expected_selector=selector, ctx=ctx)
            current_state = _fetch_folder(folder_id=folder_id, auth_headers=auth_headers, ctx=ctx)
            _assert_no_state_drift(method="media-folders.update", selector=selector, current_state=current_state, plan=plan)
            response = _request_json(
                method="PATCH",
                base_url=ctx["cfg"].base_url,
                path=request["path"],
                headers=auth_headers,
                params=None,
                json_body=request["body"],
                timeout_s=float(ctx["cfg"].timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            receipt = _build_receipt(
                method="media-folders.update",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("media-folders.update.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "media-folders.update",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        before_state = _fetch_folder(folder_id=folder_id, auth_headers=auth_headers, ctx=ctx)
        proposed_changes = [
            {
                "operation": "update",
                "folder_id": folder_id,
            }
        ]
        plan = _build_plan(
            method="media-folders.update",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=before_state,
            proposed_changes=proposed_changes,
            verification_plan={
                "type": "read-after-write",
                "notes": "Verify by querying the target folder id for updated fields.",
            },
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "media-folders.update",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except SafetyError as exc:
        _emit_refused(ctx, method="media-folders.update", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_bulk_delete(args, ctx) -> int:
    try:
        folder_ids = _coerce_str_list(getattr(args, "folder_ids_json", None), field="folder-ids-json", max_count=100)
        permanent = _coerce_bool_arg(getattr(args, "permanent", None), field="permanent")
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)

        request = {
            "method": "POST",
            "path": "/site-media/v1/bulk/folders/delete",
            "body": {
                "folderIds": folder_ids,
                "permanent": permanent,
            },
        }
        selector = _build_selector(operation="bulk-delete", folder_ids=folder_ids, permanent=permanent)

        if _should_apply(ctx, requires_ack=True):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="media-folders.bulk-delete", expected_selector=selector, ctx=ctx)
            baseline = plan.get("baseline", {})
            if isinstance(baseline, dict):
                before_state = baseline.get("before_state")
            else:
                before_state = None
            if isinstance(before_state, dict):
                current_state = _fetch_folders(folder_ids=folder_ids, auth_headers=auth_headers, ctx=ctx)
                ordered_current = {folder.get("id"): folder for folder in current_state if isinstance(folder.get("id"), str)}
                if before_state and ordered_current:
                    reconstructed = {folder_id: ordered_current.get(folder_id) for folder_id in folder_ids if folder_id in ordered_current}
                    if bool(reconstructed) and reconstructed != before_state:
                        raise SafetyError("Refused: requested folders changed since plan was created")

            response = _request_json(
                method="POST",
                base_url=ctx["cfg"].base_url,
                path=request["path"],
                headers=auth_headers,
                params=None,
                json_body=request["body"],
                timeout_s=float(ctx["cfg"].timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            receipt = _build_receipt(
                method="media-folders.bulk-delete",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={
                    "type": "provider-response",
                    "notes": "Expected trash-bin state to change for listed folder ids.",
                },
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("media-folders.bulk-delete.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "media-folders.bulk-delete",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        before_state_list = _fetch_folders(folder_ids=folder_ids, auth_headers=auth_headers, ctx=ctx)
        before_state = {str(folder.get("id")): folder for folder in before_state_list if folder.get("id") is not None}
        plan = _build_plan(
            method="media-folders.bulk-delete",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=before_state,
            proposed_changes=[{"operation": "bulk-delete", "folder_ids": folder_ids}],
            requires_ack=True,
            verification_plan={"type": "provider-response", "notes": "Verify by querying each folder id after operation."},
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "media-folders.bulk-delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except SafetyError as exc:
        _emit_refused(ctx, method="media-folders.bulk-delete", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_bulk_restore(args, ctx) -> int:
    try:
        folder_ids = _coerce_str_list(getattr(args, "folder_ids_json", None), field="folder-ids-json", max_count=100)
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request = {
            "method": "POST",
            "path": "/site-media/v1/bulk/trash-bin/folders/restore",
            "body": {"folderIds": folder_ids},
        }
        selector = _build_selector(operation="bulk-restore", folder_ids=folder_ids)

        if _should_apply(ctx):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="media-folders.bulk-restore", expected_selector=selector, ctx=ctx)
            baseline = plan.get("baseline", {})
            if isinstance(baseline, dict):
                before_state = baseline.get("before_state")
            else:
                before_state = None
            if isinstance(before_state, dict) and before_state:
                current_state = _fetch_folders(folder_ids=folder_ids, auth_headers=auth_headers, ctx=ctx)
                ordered_current = {folder.get("id"): folder for folder in current_state if isinstance(folder.get("id"), str)}
                if before_state and ordered_current:
                    reconstructed = {folder_id: ordered_current.get(folder_id) for folder_id in folder_ids if folder_id in ordered_current}
                    if bool(reconstructed) and reconstructed != before_state:
                        raise SafetyError("Refused: requested folders changed since plan was created")

            response = _request_json(
                method="POST",
                base_url=ctx["cfg"].base_url,
                path=request["path"],
                headers=auth_headers,
                params=None,
                json_body=request["body"],
                timeout_s=float(ctx["cfg"].timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            receipt = _build_receipt(
                method="media-folders.bulk-restore",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={
                    "type": "provider-response",
                    "notes": "Expected folder ids to reappear in active folders list.",
                },
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("media-folders.bulk-restore.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "media-folders.bulk-restore",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        plan = _build_plan(
            method="media-folders.bulk-restore",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state={},
            proposed_changes=[{"operation": "bulk-restore", "folder_ids": folder_ids}],
            verification_plan={
                "type": "provider-response",
                "notes": "Verify by querying the returned folder ids in /site-media/v1/folders/query after restore.",
            },
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "media-folders.bulk-restore",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except SafetyError as exc:
        _emit_refused(ctx, method="media-folders.bulk-restore", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_media_folders_generate_download_url(args, ctx) -> int:
    try:
        folder_id = _coerce_required_text(getattr(args, "folder_id", None), field="folder-id")
        auth_headers, auth_mode = _resolve_media_folders_auth(ctx=ctx)
        request_path = f"/site-media/v1/folders/{folder_id}/generate-download-url"
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=None,
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "media-folders.generate-download-url",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": request_path, "body": {}},
                "response": response,
            }
        )
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1
