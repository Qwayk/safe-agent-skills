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


def _coerce_site_folders_filter(raw: Any, field: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")

    allowed = {"name", "id", "parentId"}
    for key in value:
        if key not in allowed:
            raise ValidationError(f"--{field} can only contain name, id, and parentId")
    return value


def _coerce_sort(raw: Any, field: str) -> list[dict[str, Any]] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
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
        if order.upper() not in {"ASC", "DESC"}:
            raise ValidationError(f"--{field}[{i}].order must be ASC or DESC")

    return value


def _coerce_str(raw: Any, field: str, *, optional: bool = False) -> str | None:
    if raw is None:
        if optional:
            return None
        raise ValidationError(f"Missing --{field}")

    value = str(raw).strip()
    if not value:
        if optional:
            return None
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _ensure_query_payload(query_json: dict[str, Any] | None) -> dict[str, Any]:
    if query_json is None:
        return {"query": {}}
    if not isinstance(query_json, dict):
        raise ValidationError("--query-json must be an object")
    if isinstance(query_json.get("query"), dict):
        return dict(query_json)
    return {"query": query_json}


def _coerce_paging(*, limit: int | None, offset: int | None) -> dict[str, Any]:
    if limit is None:
        limit = 1000
    if not isinstance(limit, int) or limit <= 0:
        raise ValidationError("--limit must be a positive integer")
    if limit > 1000:
        raise ValidationError("--limit must be at most 1000")
    if offset is not None:
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("--offset must be zero or greater")
    payload: dict[str, Any] = {"limit": int(limit)}
    if offset is not None:
        payload["offset"] = int(offset)
    return payload


def _build_query_body(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_value: list[dict[str, Any]] | None,
    limit: int | None,
    offset: int | None,
) -> dict[str, Any]:
    payload = _ensure_query_payload(query_json)
    query = payload.get("query")
    if not isinstance(query, dict):
        raise ValidationError("Query payload must include a query object")

    if filter_json is not None and "filter" not in query:
        query["filter"] = filter_json
    if sort_value is not None and "sort" not in query:
        query["sort"] = sort_value
    query["paging"] = _coerce_paging(limit=limit, offset=offset)
    return {"query": query}


def _resolve_site_folders_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="site-folders",
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


def _read_folder_from_payload(*, payload: dict[str, Any], context: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"{context} returned a non-object payload")
    folder = payload.get("folder")
    if not isinstance(folder, dict):
        raise ValidationError(f"{context} returned no folder object")
    return folder


def _extract_folder_by_id(payload: dict[str, Any], *, folder_id: str) -> dict[str, Any] | None:
    folders = payload.get("folders")
    if not isinstance(folders, list):
        return None
    for item in folders:
        if not isinstance(item, dict):
            continue
        candidate_id = str(item.get("id") or "").strip()
        if candidate_id == folder_id:
            return item
    return None


def _read_site_folder_by_id(
    *,
    folder_id: str,
    base_url: str,
    auth_headers: dict[str, str],
    ctx: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _request_json(
        method="POST",
        base_url=base_url,
        path="/site-folders/v2/folders/query",
        headers=auth_headers,
        params=None,
        json_body={"query": {"filter": {"id": folder_id}, "paging": {"limit": 1000}}},
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_folder_by_id(payload=payload, folder_id=folder_id)


def _query_site_folder_by_site(
    *,
    site_id: str,
    base_url: str,
    auth_headers: dict[str, str],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=base_url,
        path=f"/site-folders/v2/folders/sites/{site_id}",
        headers=auth_headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _read_folder_from_payload(payload=payload, context="get-folder-by-site")


def _extract_folder_id(folder: dict[str, Any] | None) -> str:
    if not isinstance(folder, dict):
        return ""
    value = folder.get("id")
    if not isinstance(value, str):
        return ""
    folder_id = value.strip()
    return folder_id


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    baseline_before: dict[str, Any] | None = None,
    proposed_changes: list[dict[str, Any]] | None = None,
    verification_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
    }
    if baseline_before is not None:
        baseline["before_state"] = baseline_before

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["site-folders-write"],
        "preconditions": ["env_fingerprint must match", "selector must match"],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [],
        "verification_plan": verification_plan or {
            "type": "read-after-write",
            "notes": "Verify by reading resource(s) after write",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan missing baseline")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="site-folders")


def _assert_no_folder_drift(
    *,
    plan: dict[str, Any],
    current_state: dict[str, Any],
    folder_id: str,
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if baseline_state.get("id") != folder_id:
        raise SafetyError("Refused: plan selector does not match current folder")
    if current_state != baseline_state:
        raise SafetyError("Refused: folder changed since plan was created")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _assert_no_site_drift(
    *,
    plan: dict[str, Any],
    current_assignments: dict[str, str],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if baseline_state != current_assignments:
        raise SafetyError("Refused: folder assignment changed since plan was created")


def _assert_no_folder_collection_drift(
    *,
    plan: dict[str, Any],
    current_state: dict[str, dict[str, Any]],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if baseline_state != current_state:
        raise SafetyError("Refused: folder state changed since plan was created")


def _coerce_site_ids(raw: Any, field: str) -> list[str]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 500:
        raise ValidationError(f"--{field} supports at most 500 IDs")

    seen: set[str] = set()
    site_ids: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        site_id = item.strip()
        if not site_id:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if site_id in seen:
            raise ValidationError(f"--{field} contains duplicate site id: {site_id}")
        seen.add(site_id)
        site_ids.append(site_id)
    return site_ids


def _coerce_folder_ids(raw: Any, field: str) -> list[str]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 1000:
        raise ValidationError(f"--{field} supports at most 1000 IDs")

    seen: set[str] = set()
    folder_ids: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        folder_id = item.strip()
        if not folder_id:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if folder_id in seen:
            raise ValidationError(f"--{field} contains duplicate folder id: {folder_id}")
        seen.add(folder_id)
        folder_ids.append(folder_id)
    return folder_ids


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cmd_site_folders_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        filter_json = _coerce_site_folders_filter(getattr(args, "filter_json", None), field="filter-json")
        sort_value = _coerce_sort(getattr(args, "sort_json", None), field="sort-json")

        body = _build_query_body(
            query_json=dict(query_json) if isinstance(query_json, dict) else None,
            filter_json=filter_json,
            sort_value=sort_value,
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
        )
        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-folders/v2/folders/query",
            headers=auth_headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "site-folders.query",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/site-folders/v2/folders/query", "body": body},
            "response": payload,
        }
        ctx["audit"].write("site-folders.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.query"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.query"}
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_get_folder_by_site(args, ctx) -> int:
    try:
        site_id = _coerce_str(getattr(args, "site_id", ""), "site-id")
        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        folder = _query_site_folder_by_site(
            site_id=site_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            ctx=ctx,
        )
        payload = {"folder": folder}
        out = {
            "ok": True,
            "method": "site-folders.get-folder-by-site",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": f"/site-folders/v2/folders/sites/{site_id}"},
            "response": payload,
        }
        ctx["audit"].write("site-folders.get-folder-by-site", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.get-folder-by-site"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-folders.get-folder-by-site",
        }
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_create(args, ctx) -> int:
    try:
        name = _coerce_str(getattr(args, "name", ""), "name")
        parent_id = _coerce_str(getattr(args, "parent_id", None), "parent-id", optional=True)

        folder_payload: dict[str, Any] = {"name": name}
        if parent_id:
            folder_payload["parentId"] = parent_id

        request: dict[str, Any] = {
            "method": "POST",
            "path": "/site-folders/v2/folders",
            "body": {"folder": folder_payload},
        }
        selector = {"kind": "site-folder", "operation": "create", "name": name}
        if parent_id:
            selector["parent_id"] = parent_id
        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)

        plan = _build_plan(
            method="site-folders.create",
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=[{"operation": "create", "name": name}],
            verification_plan={"type": "read-after-write", "notes": "Verify returned folder name"},
        )
        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-folders.create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-folders/v2/folders",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        folder = response.get("folder")
        if not isinstance(folder, dict):
            raise ValidationError("Create response does not include a folder object")
        verification = {
            "ok": str(folder.get("name") or "") == name,
            "type": "read-after-write",
            "path": "/site-folders/v2/folders",
            "method": "POST",
            "response": response,
        }

        receipt = _build_receipt(
            method="site-folders.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-folders.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("site-folders.create.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-folders.create",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.create"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.create"}
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_update(args, ctx) -> int:
    try:
        folder_id = _coerce_str(getattr(args, "folder_id", ""), "folder-id")
        new_name = _coerce_str(getattr(args, "name", ""), "name")

        request: dict[str, Any] = {
            "method": "PATCH",
            "path": f"/site-folders/v2/folders/{folder_id}",
            "body": {"folder": {"id": folder_id, "name": new_name}, "fieldMask": "name"},
        }

        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        current_state = _read_site_folder_by_id(
            folder_id=folder_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            ctx=ctx,
        )
        if current_state is None:
            raise SafetyError(f"Refused: folder does not exist: {folder_id}")

        selector = {"kind": "site-folder", "operation": "update", "folder_id": folder_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(str(plan_in), expected_method="site-folders.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="site-folders.update",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=current_state,
                proposed_changes=[{"operation": "update", "folder_id": folder_id, "name": new_name}],
                verification_plan={"type": "read-after-write", "notes": "Verify folder name after rename"},
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-folders.update",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(str(plan_in), expected_method="site-folders.update", expected_selector=selector, ctx=ctx) if plan_in else plan
        _assert_no_folder_drift(plan=loaded_plan, current_state=current_state, folder_id=folder_id)

        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/site-folders/v2/folders/{folder_id}",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _read_site_folder_by_id(
            folder_id=folder_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            ctx=ctx,
        )
        if after_state is None:
            verification = {"ok": False, "type": "read-after-write", "notes": "Folder missing after update"}
        else:
            verification = {
                "ok": _extract_folder_id(after_state) == folder_id and str(after_state.get("name") or "") == new_name,
                "type": "read-after-write",
                "path": f"/site-folders/v2/folders/{folder_id}",
                "method": "GET",
                "response": after_state,
            }

        receipt = _build_receipt(
            method="site-folders.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-folders.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-folders.update",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.update"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.update"}
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_delete(args, ctx) -> int:
    try:
        folder_id = _coerce_str(getattr(args, "folder_id", ""), "folder-id")
        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        current_state = _read_site_folder_by_id(
            folder_id=folder_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            ctx=ctx,
        )
        if current_state is None:
            raise SafetyError(f"Refused: folder does not exist: {folder_id}")

        request = {"method": "DELETE", "path": f"/site-folders/v2/folders/{folder_id}"}
        selector = {"kind": "site-folder", "operation": "delete", "folder_id": folder_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(str(plan_in), expected_method="site-folders.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="site-folders.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=current_state,
                proposed_changes=[{"operation": "delete", "folder_id": folder_id}],
                verification_plan={"type": "read-after-delete", "notes": "Read folder by id and require no match"},
            )

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: delete requires --ack-irreversible")

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-folders.delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(str(plan_in), expected_method="site-folders.delete", expected_selector=selector, ctx=ctx) if plan_in else plan
        _assert_no_folder_drift(plan=loaded_plan, current_state=current_state, folder_id=folder_id)

        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/site-folders/v2/folders/{folder_id}",
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _read_site_folder_by_id(
            folder_id=folder_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            ctx=ctx,
        )
        verification = {
            "ok": after_state is None,
            "type": "read-after-delete",
            "path": "/site-folders/v2/folders/query",
            "method": "POST",
            "notes": "Folder should not be found after delete",
            "before": current_state,
            "after": after_state,
        }
        receipt = _build_receipt(
            method="site-folders.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-folders.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("site-folders.delete.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-folders.delete",
        }
        ctx["audit"].write("site-folders.delete.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.delete"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.delete"}
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_move_sites(args, ctx) -> int:
    try:
        site_ids = _coerce_site_ids(getattr(args, "site_ids_json", None), field="site-ids-json")
        target_folder_id = _coerce_str(getattr(args, "target_folder_id", None), "target-folder-id", optional=True)
        to_root = bool(getattr(args, "to_root", False))

        if bool(target_folder_id) and to_root:
            raise ValidationError("Use either --target-folder-id or --to-root, not both")
        if not target_folder_id and not to_root:
            raise ValidationError("Choose one target form: --target-folder-id or --to-root")
        requested_target_id = "" if to_root else str(target_folder_id)

        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        before_state: dict[str, str] = {}
        for site_id in site_ids:
            before_state[site_id] = _extract_folder_id(_query_site_folder_by_site(
                site_id=site_id,
                base_url=ctx["cfg"].base_url,
                auth_headers=auth_headers,
                ctx=ctx,
            ))

        request = {
            "method": "POST",
            "path": "/site-folders/v2/folders/bulk/sites/move",
            "body": {"sites": {"id": {"$in": site_ids}}, "targetFolderId": requested_target_id},
        }
        selector = {
            "kind": "site-folder",
            "operation": "move-sites",
            "target_folder_id": requested_target_id,
            "site_ids": site_ids,
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(str(plan_in), expected_method="site-folders.move-sites", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="site-folders.move-sites",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "move-sites", "site_ids": site_ids, "target_folder_id": requested_target_id}],
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-folders.move-sites",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(str(plan_in), expected_method="site-folders.move-sites", expected_selector=selector, ctx=ctx) if plan_in else plan
        _assert_no_site_drift(plan=loaded_plan, current_assignments=before_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-folders/v2/folders/bulk/sites/move",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        current_state: dict[str, str] = {}
        checks: list[dict[str, Any]] = []
        for site_id in site_ids:
            current_folder = _query_site_folder_by_site(
                site_id=site_id,
                base_url=ctx["cfg"].base_url,
                auth_headers=auth_headers,
                ctx=ctx,
            )
            current_folder_id = _extract_folder_id(current_folder)
            current_state[site_id] = current_folder_id
            checks.append(
                {
                    "site_id": site_id,
                    "expected_folder_id": requested_target_id,
                    "actual_folder_id": current_folder_id,
                }
            )

        verification = {
            "ok": all(check["actual_folder_id"] == check["expected_folder_id"] for check in checks),
            "type": "read-after-write",
            "path": "/site-folders/v2/folders/sites/{siteId}",
            "method": "GET",
            "checks": checks,
        }

        receipt = _build_receipt(
            method="site-folders.move-sites",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-folders.move-sites",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-folders.move-sites",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.move-sites"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.move-sites"}
        ctx["out"].emit(out)
        return 1


def cmd_site_folders_move_folders(args, ctx) -> int:
    try:
        folder_ids = _coerce_folder_ids(getattr(args, "folder_ids_json", None), field="folder-ids-json")
        target_folder_id = _coerce_str(getattr(args, "target_folder_id", None), "target-folder-id", optional=True)
        to_root = bool(getattr(args, "to_root", False))

        if bool(target_folder_id) and to_root:
            raise ValidationError("Use either --target-folder-id or --to-root, not both")
        if not target_folder_id and not to_root:
            raise ValidationError("Choose one target form: --target-folder-id or --to-root")
        requested_target_id = "" if to_root else str(target_folder_id)

        auth_headers, auth_mode = _resolve_site_folders_auth(ctx=ctx)
        before_state: dict[str, Any] = {}
        for folder_id in folder_ids:
            folder_state = _read_site_folder_by_id(
                folder_id=folder_id,
                base_url=ctx["cfg"].base_url,
                auth_headers=auth_headers,
                ctx=ctx,
            )
            if folder_state is None:
                raise SafetyError(f"Refused: folder does not exist: {folder_id}")
            before_state[folder_id] = folder_state

        request = {
            "method": "PATCH",
            "path": "/site-folders/v2/folders/bulk/move",
            "body": {"folderIds": folder_ids, "targetFolderId": requested_target_id},
        }
        selector = {
            "kind": "site-folder",
            "operation": "move-folders",
            "target_folder_id": requested_target_id,
            "folder_ids": folder_ids,
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(str(plan_in), expected_method="site-folders.move-folders", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="site-folders.move-folders",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "move-folders", "folder_ids": folder_ids, "target_folder_id": requested_target_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify each folder has the expected parentId after move",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-folders.move-folders",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(str(plan_in), expected_method="site-folders.move-folders", expected_selector=selector, ctx=ctx) if plan_in else plan
        _assert_no_folder_collection_drift(plan=loaded_plan, current_state=before_state)

        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path="/site-folders/v2/folders/bulk/move",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        checks: list[dict[str, Any]] = []
        for folder_id in folder_ids:
            current_folder = _read_site_folder_by_id(
                folder_id=folder_id,
                base_url=ctx["cfg"].base_url,
                auth_headers=auth_headers,
                ctx=ctx,
            )
            actual_parent_id = "" if not current_folder else str(current_folder.get("parentId") or "")
            checks.append(
                {
                    "folder_id": folder_id,
                    "expected_parent_id": requested_target_id,
                    "actual_parent_id": actual_parent_id,
                }
            )

        verification = {
            "ok": all(check["actual_parent_id"] == check["expected_parent_id"] for check in checks),
            "type": "read-after-write",
            "path": "/site-folders/v2/folders/query",
            "method": "POST",
            "checks": checks,
        }

        receipt = _build_receipt(
            method="site-folders.move-folders",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-folders.move-folders",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-folders.move-folders",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-folders.move-folders"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-folders.move-folders"}
        ctx["out"].emit(out)
        return 1
