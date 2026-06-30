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


def _coerce_bool_arg(value: Any, field: str) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise ValidationError(f"--{field} must be true or false")

    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValidationError(f"--{field} must be true or false")


def _coerce_positive_int(value: Any, *, field: str, max_value: int | None = None) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValidationError(f"--{field} must be an integer")
    if value <= 0:
        raise ValidationError(f"--{field} must be greater than 0")
    if max_value is not None and value > max_value:
        raise ValidationError(f"--{field} must be at most {max_value}")
    return value


def _read_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_str_list(raw: Any, field: str, *, max_count: int | None = None) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if max_count is not None and len(value) > max_count:
        raise ValidationError(f"--{field} supports at most {max_count} values")
    normalized: list[str] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        value_str = item.strip()
        if not value_str:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if value_str in seen:
            raise ValidationError(f"--{field} contains duplicate value: {value_str}")
        seen.add(value_str)
        normalized.append(value_str)
    return normalized


def _normalize_sort(sort_value: Any, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    if sort_value is None:
        return None
    if isinstance(sort_value, list):
        if not sort_value:
            raise ValidationError(f"--{field} cannot be empty")
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


def _resolve_files_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="files",
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


def _build_files_list_params(
    *,
    parent_folder_id: str | None,
    media_types: list[str] | None,
    private_value: bool | None,
    sort_value: dict[str, Any] | list[dict[str, Any]] | None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if parent_folder_id:
        params["parentFolderId"] = parent_folder_id
    if media_types is not None:
        params["mediaTypes"] = media_types
    if private_value is not None:
        params["private"] = bool(private_value)
    if cursor is not None:
        params["paging.cursor"] = cursor
    if limit is not None:
        params["paging.limit"] = int(limit)
    _add_sort_query_params(sort_value=sort_value, params=params)
    return params


def _ensure_query_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"query": {}}
    if isinstance(payload.get("query"), dict):
        return dict(payload)
    return {"query": payload}


def _build_query_payload(payload_json: Any) -> dict[str, Any]:
    if payload_json is None:
        return {"query": {}}
    if not isinstance(payload_json, dict):
        raise ValidationError("--query-json must be an object")
    payload = _ensure_query_payload(payload_json)
    query_obj = payload.get("query")
    if not isinstance(query_obj, dict):
        raise ValidationError("Query payload must include a query object")
    return payload


def _build_search_body(
    *,
    search: str | None,
    media_types: list[str] | None,
    private_value: bool | None,
    root_folder: str | None,
    sort_value: dict[str, Any] | list[dict[str, Any]] | None,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if search is not None:
        body["search"] = search
    if media_types is not None:
        body["mediaTypes"] = media_types
    if private_value is not None:
        body["private"] = bool(private_value)
    if root_folder is not None:
        body["rootFolder"] = root_folder
    if sort_value is not None:
        if isinstance(sort_value, list):
            if sort_value:
                body["sort"] = sort_value[0]
        else:
            body["sort"] = sort_value
    if cursor is not None or limit is not None:
        paging: dict[str, Any] = {}
        if cursor is not None:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        body["paging"] = paging
    return body


def _extract_file(payload: dict[str, Any], *, context: str) -> dict[str, Any]:
    if isinstance(payload.get("file"), dict):
        return dict(payload["file"])
    if isinstance(payload.get("files"), list):
        files = payload["files"]
        if len(files) == 1 and isinstance(files[0], dict):
            return dict(files[0])
    if isinstance(payload.get("id"), str):
        return dict(payload)
    raise ValidationError(f"{context} returned no file object")


def _fetch_file(*, file_id: str, auth_headers: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/site-media/v1/files/get-file-by-id",
        headers=auth_headers,
        params={"fileId": file_id},
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_file(payload, context="files.get")


def _fetch_files_batch(*, file_ids: list[str], auth_headers: dict[str, str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/site-media/v1/files/get-files",
        headers=auth_headers,
        params=None,
        json_body={"fileIds": file_ids},
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValidationError("files.batch-get returned no files array")
    normalized: list[dict[str, Any]] = []
    for item in files:
        if isinstance(item, dict):
            normalized.append(dict(item))
    return normalized


def _build_selector(
    *,
    operation: str,
    file_id: str | None = None,
    file_ids: list[str] | None = None,
    permanent: bool | None = None,
) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "kind": "wix-media-file",
        "operation": operation,
    }
    if file_id:
        selector["file_id"] = file_id
    if file_ids is not None:
        selector["file_ids"] = file_ids
    if permanent is not None:
        selector["permanent"] = permanent
    return selector


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any] | list[dict[str, Any]],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
    verification_plan: dict[str, Any] | None = None,
    risk_reasons: list[str] | None = None,
    state_capture_notes: str | None = None,
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

    computed_risk_reasons = list(risk_reasons or ["wix-media-file-write"])
    if requires_ack and "irreversible" not in computed_risk_reasons:
        computed_risk_reasons.append("irreversible")

    if state_capture_notes is None:
        state_capture_notes = (
            "Captured file state before planning."
            if has_before_state
            else "No useful before-state snapshot is available for this write."
        )

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": computed_risk_reasons,
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
            "notes": state_capture_notes,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan
        or {"type": "provider-response", "notes": "Verification is limited to the API response for this command."},
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Keep the saved plan and receipts for manual recovery planning."
                if has_before_state
                else "No automatic rollback and no useful before-state snapshot is available."
            ),
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


def _assert_no_state_drift(*, current_state: dict[str, Any] | list[dict[str, Any]] | None, plan: dict[str, Any]) -> None:
    baseline = plan.get("baseline", {})
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if not before_state:
        return
    if before_state != current_state:
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


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
    verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    state_capture = plan.get("state_capture") if isinstance(plan, dict) else None
    before_state_available = bool(before_state)
    state_capture_notes = (
        state_capture.get("notes")
        if isinstance(state_capture, dict) and isinstance(state_capture.get("notes"), str)
        else (
            "Receipt is linked to a saved before-state snapshot from the reviewed plan."
            if before_state_available
            else "No useful before-state snapshot was available for this receipt."
        )
    )
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
            "before_state_available": before_state_available,
            "notes": state_capture_notes,
        },
        "diff_applied": plan.get("proposed_changes", []),
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use plan and before-state as a reference."
                if before_state_available
                else "Recovery is manual and no reliable before-state snapshot exists."
            ),
        },
    }


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="files")


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


def cmd_files_list(args, ctx) -> int:
    try:
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")
        media_types = _read_str_list(getattr(args, "media_types_json", None), field="media-types-json")
        private_value = _coerce_bool_arg(getattr(args, "private", None), field="private")
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")

        params = _build_files_list_params(
            parent_folder_id=parent_folder_id,
            media_types=media_types,
            private_value=private_value,
            sort_value=sort_value,
        )

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files",
            headers=auth_headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.list",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/site-media/v1/files", "params": params},
            "response": payload,
        }
        ctx["audit"].write("files.list", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_get(args, ctx) -> int:
    try:
        file_id = _coerce_required_text(getattr(args, "file_id", None), field="file-id")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/get-file-by-id",
            headers=auth_headers,
            params={"fileId": file_id},
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.get",
            "auth_mode": auth_mode,
            "request": {
                "method": "GET",
                "path": "/site-media/v1/files/get-file-by-id",
                "params": {"fileId": file_id},
            },
            "response": payload,
        }
        ctx["audit"].write("files.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_batch_get(args, ctx) -> int:
    try:
        file_ids = _read_str_list(getattr(args, "file_ids_json", None), field="file-ids-json", max_count=100)
        if not file_ids:
            raise ValidationError("--file-ids-json cannot be empty")

        payload_body = {"fileIds": file_ids}
        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/get-files",
            headers=auth_headers,
            params=None,
            json_body=payload_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.batch-get",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/site-media/v1/files/get-files", "body": payload_body},
            "response": payload,
        }
        ctx["audit"].write("files.batch-get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_search(args, ctx) -> int:
    try:
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        search = _coerce_optional_text(getattr(args, "search", None), field="search")
        media_types = _read_str_list(getattr(args, "media_types_json", None), field="media-types-json")
        private_value = _coerce_bool_arg(getattr(args, "private", None), field="private")
        root_folder = _coerce_optional_text(getattr(args, "root_folder", None), field="root-folder")
        cursor = _coerce_optional_text(getattr(args, "cursor", None), field="cursor")
        limit = _coerce_positive_int(getattr(args, "limit", None), field="limit", max_value=100)

        body = _build_search_body(
            search=search,
            media_types=media_types,
            private_value=private_value,
            root_folder=root_folder,
            sort_value=sort_value,
            cursor=cursor,
            limit=limit,
        )

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/search",
            headers=auth_headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.search",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/site-media/v1/files/search", "body": body},
            "response": payload,
        }
        ctx["audit"].write("files.search", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_query(args, ctx) -> int:
    try:
        query_payload = _build_query_payload(_read_json_arg(getattr(args, "query_json", None), field="query-json"))

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/query",
            headers=auth_headers,
            params=None,
            json_body=query_payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.query",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/site-media/v1/files/query", "body": query_payload},
            "response": payload,
        }
        ctx["audit"].write("files.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_list_deleted(args, ctx) -> int:
    try:
        parent_folder_id = _coerce_optional_text(getattr(args, "parent_folder_id", None), field="parent-folder-id")
        media_types = _read_str_list(getattr(args, "media_types_json", None), field="media-types-json")
        private_value = _coerce_bool_arg(getattr(args, "private", None), field="private")
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        cursor = _coerce_optional_text(getattr(args, "cursor", None), field="cursor")

        params = _build_files_list_params(
            parent_folder_id=parent_folder_id,
            media_types=media_types,
            private_value=private_value,
            sort_value=sort_value,
            cursor=cursor,
        )

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/trash-bin/files",
            headers=auth_headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.list-deleted",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/site-media/v1/trash-bin/files", "params": params},
            "response": payload,
        }
        ctx["audit"].write("files.list-deleted", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_update(args, ctx) -> int:
    try:
        file_id = _coerce_required_text(getattr(args, "file_id", None), field="file-id")
        file_json = _read_json_object(getattr(args, "file_json", None), field="file-json")
        if "id" in file_json and str(file_json["id"]).strip() != file_id:
            raise ValidationError("--file-json.id must match --file-id when provided")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        file_payload = dict(file_json)
        file_payload["id"] = file_id
        if len(file_payload) == 1:
            raise ValidationError("--file-json must include at least one updatable field besides id")

        request = {
            "method": "PATCH",
            "path": "/site-media/v1/files/update-file-descriptor",
            "body": {"file": file_payload},
        }
        selector = _build_selector(operation="update", file_id=file_id)

        if _should_apply(ctx):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="files.update", expected_selector=selector, ctx=ctx)
            current_state = _fetch_file(file_id=file_id, auth_headers=auth_headers, ctx=ctx)
            _assert_no_state_drift(current_state=current_state, plan=plan)
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
                method="files.update",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={"type": "read-after-write", "notes": "Verify by rereading the target file descriptor."},
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("files.update.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "files.update",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        before_state = _fetch_file(file_id=file_id, auth_headers=auth_headers, ctx=ctx)
        plan = _build_plan(
            method="files.update",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=before_state,
            proposed_changes=[{"operation": "update", "file_id": file_id}],
            verification_plan={"type": "read-after-write", "notes": "Verify by rereading the target file descriptor."},
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "files.update",
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
        _emit_refused(ctx, method="files.update", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_bulk_delete(args, ctx) -> int:
    try:
        file_ids = _read_str_list(getattr(args, "file_ids_json", None), field="file-ids-json", max_count=1000)
        if not file_ids:
            raise ValidationError("--file-ids-json cannot be empty")
        permanent = _coerce_bool_arg(getattr(args, "permanent", None), field="permanent")
        if permanent is None:
            raise ValidationError("Missing --permanent")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        request = {
            "method": "POST",
            "path": "/site-media/v1/bulk/files/delete",
            "body": {
                "fileIds": file_ids,
                "permanent": permanent,
            },
        }
        selector = _build_selector(operation="bulk-delete", file_ids=file_ids, permanent=permanent)

        if _should_apply(ctx, requires_ack=True):
            plan = _load_plan(
                plan_in=ctx.get("plan_in"),
                expected_method="files.bulk-delete",
                expected_selector=selector,
                ctx=ctx,
            )
            baseline = plan.get("baseline", {})
            before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
            current_state = None
            if isinstance(before_state, list) and before_state:
                current_state = _fetch_files_batch(file_ids=file_ids, auth_headers=auth_headers, ctx=ctx)
            _assert_no_state_drift(current_state=current_state, plan=plan)
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
                method="files.bulk-delete",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={"type": "provider-response", "notes": "Verify targeted file ids moved to trash or were permanently removed."},
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("files.bulk-delete.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "files.bulk-delete",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        before_state: list[dict[str, Any]] = []
        state_capture_notes = (
            "Captured file descriptors before planning."
            if len(file_ids) <= 100
            else "No useful before-state snapshot is available for more than 100 files because the shipped readback helper is capped at Wix's 100-file batch-get boundary."
        )
        if len(file_ids) <= 100:
            before_state = _fetch_files_batch(file_ids=file_ids, auth_headers=auth_headers, ctx=ctx)
        plan = _build_plan(
            method="files.bulk-delete",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=before_state,
            proposed_changes=[{"operation": "bulk-delete", "file_ids": file_ids, "permanent": permanent}],
            requires_ack=True,
            verification_plan={"type": "provider-response", "notes": "Verify targeted file ids moved to trash or were permanently removed."},
            state_capture_notes=state_capture_notes,
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "files.bulk-delete",
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
        _emit_refused(ctx, method="files.bulk-delete", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_bulk_restore(args, ctx) -> int:
    try:
        file_ids = _read_str_list(getattr(args, "file_ids_json", None), field="file-ids-json", max_count=1000)
        if not file_ids:
            raise ValidationError("--file-ids-json cannot be empty")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        request = {
            "method": "POST",
            "path": "/site-media/v1/bulk/trash-bin/files/restore",
            "body": {"fileIds": file_ids},
        }
        selector = _build_selector(operation="bulk-restore", file_ids=file_ids)

        if _should_apply(ctx):
            plan = _load_plan(
                plan_in=ctx.get("plan_in"),
                expected_method="files.bulk-restore",
                expected_selector=selector,
                ctx=ctx,
            )
            _assert_no_state_drift(current_state=None, plan=plan)
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
                method="files.bulk-restore",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={"type": "provider-response", "notes": "Verify restored file ids reappear in active Media Manager file reads."},
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("files.bulk-restore.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "files.bulk-restore",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        plan = _build_plan(
            method="files.bulk-restore",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=[],
            proposed_changes=[{"operation": "bulk-restore", "file_ids": file_ids}],
            verification_plan={"type": "provider-response", "notes": "Verify restored file ids reappear in active Media Manager file reads."},
            state_capture_notes="No useful before-state snapshot is available for trash-bin restore because this tool does not ship a direct deleted-file get-by-id read path.",
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "files.bulk-restore",
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
        _emit_refused(ctx, method="files.bulk-restore", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_generate_upload_url(args, ctx) -> int:
    try:
        upload_json = _read_json_object(getattr(args, "upload_json", None), field="upload-json")
        mime_type = upload_json.get("mimeType")
        if not isinstance(mime_type, str) or not mime_type.strip():
            raise ValidationError("--upload-json must include non-empty mimeType")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/generate-upload-url",
            headers=auth_headers,
            params=None,
            json_body=upload_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.generate-upload-url",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/site-media/v1/files/generate-upload-url", "body": upload_json},
            "response": payload,
        }
        ctx["audit"].write("files.generate-upload-url", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_generate_resumable_upload_url(args, ctx) -> int:
    try:
        upload_json = _read_json_object(getattr(args, "upload_json", None), field="upload-json")
        mime_type = upload_json.get("mimeType")
        if not isinstance(mime_type, str) or not mime_type.strip():
            raise ValidationError("--upload-json must include non-empty mimeType")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/generate-resumable-upload-url",
            headers=auth_headers,
            params=None,
            json_body=upload_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.generate-resumable-upload-url",
            "auth_mode": auth_mode,
            "request": {
                "method": "POST",
                "path": "/site-media/v1/files/generate-resumable-upload-url",
                "body": upload_json,
            },
            "response": payload,
        }
        ctx["audit"].write("files.generate-resumable-upload-url", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_import(args, ctx) -> int:
    try:
        import_json = _read_json_object(getattr(args, "import_json", None), field="import-json")
        url = import_json.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ValidationError("--import-json must include non-empty url")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        request = {
            "method": "POST",
            "path": "/site-media/v1/files/import",
            "body": import_json,
        }
        selector = _build_selector(operation="import")

        if _should_apply(ctx):
            plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method="files.import", expected_selector=selector, ctx=ctx)
            _assert_no_state_drift(current_state=None, plan=plan)
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
                method="files.import",
                selector=selector,
                request=request,
                response=response,
                plan=plan,
                ctx=ctx,
                verification={"type": "provider-response", "notes": "Verify imported file metadata from the response or a later read/search."},
            )
            _receipt_out_if_needed(ctx=ctx, receipt=receipt)
            ctx["audit"].write("files.import.apply", {"receipt": receipt})
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "method": "files.import",
                    "auth_mode": auth_mode,
                    "request": request,
                    "response": response,
                    "receipt": receipt,
                }
            )
            return 0

        plan = _build_plan(
            method="files.import",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=[],
            proposed_changes=[{"operation": "import", "url": url}],
            verification_plan={"type": "provider-response", "notes": "Verify imported file metadata from the response or a later read/search."},
            state_capture_notes="No useful before-state snapshot is available for file import because the external source file does not yet exist in the target Media Manager state.",
        )
        plan_out = _plan_out_if_needed(ctx=ctx, plan=plan)
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": "files.import",
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
        _emit_refused(ctx, method="files.import", exc=exc)
        return 0
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1


def cmd_files_generate_download_url(args, ctx) -> int:
    try:
        download_json = _read_json_object(getattr(args, "download_json", None), field="download-json")
        file_id = download_json.get("fileId")
        if not isinstance(file_id, str) or not file_id.strip():
            raise ValidationError("--download-json must include non-empty fileId")

        auth_headers, auth_mode = _resolve_files_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-media/v1/files/generate-file-download-url",
            headers=auth_headers,
            params=None,
            json_body=download_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "files.generate-download-url",
            "auth_mode": auth_mode,
            "request": {
                "method": "POST",
                "path": "/site-media/v1/files/generate-file-download-url",
                "body": download_json,
            },
            "response": payload,
        }
        ctx["audit"].write("files.generate-download-url", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        _emit_validation_error(ctx, exc)
        return 1
    except RuntimeError as exc:
        _emit_runtime_error(ctx, exc)
        return 1
