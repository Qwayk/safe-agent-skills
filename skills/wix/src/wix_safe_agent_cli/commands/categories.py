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

_DEFAULT_TREE_REFERENCE = {"appNamespace": "@wix/stores", "treeKey": None}


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


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return payload


def _require_revision(raw: Any, *, field: str) -> None:
    if raw is None:
        raise ValidationError(f"--{field} revision is required")
    if isinstance(raw, str) and not raw.strip():
        raise ValidationError(f"--{field} revision cannot be empty")


def _normalize_category_body(raw: Any, *, field: str, category_id: str | None = None, require_revision: bool = False) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field=field)
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    body = dict(payload) if "category" in payload else {"category": payload}
    category = body.get("category")
    if not isinstance(category, dict) or not category:
        raise ValidationError(f"--{field} must include a non-empty category object")
    if category_id is not None:
        payload_id = category.get("id")
        if payload_id is not None and str(payload_id).strip() != category_id:
            raise SafetyError("Refused: category id in body does not match --category-id")
        category.setdefault("id", category_id)
    if require_revision:
        _require_revision(category.get("revision"), field=field)
    return _with_tree_reference(body)


def _normalize_categories_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = _with_tree_reference(dict(payload))
        categories = body.get("categories")
    elif isinstance(payload, list):
        categories = payload
        body = {"treeReference": dict(_DEFAULT_TREE_REFERENCE), "categories": categories}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(categories, list) or not categories:
        raise ValidationError(f"--{field} must include a non-empty categories array")
    if require_revision:
        for index, category in enumerate(categories):
            if not isinstance(category, dict):
                raise ValidationError(f"--{field} categories[{index}] must be an object")
            try:
                _require_revision(category.get("revision"), field=field)
            except ValidationError as exc:
                raise ValidationError(f"--{field} categories[{index}].revision is required for bulk update") from exc
    return body


def _tree_reference_params(raw: Any) -> dict[str, str]:
    tree_reference = dict(_DEFAULT_TREE_REFERENCE)
    if raw is not None:
        payload = _coerce_json_object(raw, field="tree-reference-json")
        tree_reference = dict(payload)
    app_namespace = tree_reference.get("appNamespace")
    if not isinstance(app_namespace, str) or not app_namespace.strip():
        raise ValidationError("--tree-reference-json appNamespace must be a non-empty string")
    return {
        "treeReference.appNamespace": app_namespace.strip(),
        "treeReference.treeKey": "null" if tree_reference.get("treeKey") is None else str(tree_reference.get("treeKey")),
    }


def _with_tree_reference(payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    tree_reference = body.get("treeReference")
    if tree_reference is None:
        body["treeReference"] = dict(_DEFAULT_TREE_REFERENCE)
        return body
    if not isinstance(tree_reference, dict):
        raise ValidationError("treeReference must be a JSON object")
    app_namespace = tree_reference.get("appNamespace")
    if not isinstance(app_namespace, str) or not app_namespace.strip():
        raise ValidationError("treeReference.appNamespace must be a non-empty string")
    body["treeReference"] = dict(tree_reference)
    return body


def _normalize_query_body(raw: Any, *, field: str, wrapper_key: str) -> dict[str, Any]:
    if raw is None:
        return {"treeReference": dict(_DEFAULT_TREE_REFERENCE)}
    payload = _coerce_json_object(raw, field=field)
    payload = _with_tree_reference(payload)
    if wrapper_key in payload:
        nested = payload.get(wrapper_key)
        if not isinstance(nested, dict):
            raise ValidationError(f"--{field} {wrapper_key} must be a JSON object")
        return payload
    tree_reference = payload.pop("treeReference")
    return {"treeReference": tree_reference, wrapper_key: payload}


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {"treeReference": dict(_DEFAULT_TREE_REFERENCE)}
    payload = _coerce_json_object(raw, field="filter-json")
    payload = _with_tree_reference(payload)
    if "filter" in payload:
        return payload
    tree_reference = payload.pop("treeReference")
    return {"treeReference": tree_reference, "filter": payload}


def _normalize_request_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {"treeReference": dict(_DEFAULT_TREE_REFERENCE)}
    payload = _coerce_json_object(raw, field="request-json")
    return _with_tree_reference(payload)


def _normalize_non_empty_request_body(raw: Any) -> dict[str, Any]:
    payload = _normalize_request_body(raw)
    meaningful_keys = set(payload) - {"treeReference"}
    if not meaningful_keys:
        raise ValidationError("--request-json cannot be empty")
    return payload


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
    if json_body is not None:
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


def _resolve_categories_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="categories",
    )
    return auth["headers"], auth["mode"]


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in --apply --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-stores-category-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": {},
        },
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot exists for this Categories write in the current boundary.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary; run follow-up get, query, list, or arrangement commands for live verification.",
        },
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Recovery is manual and may require new reviewed plans.",
        },
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="categories")


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
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": False,
            "notes": "Receipt is linked to a reviewed plan, but no useful before-state snapshot was available.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only and may require new reviewed plans.",
        },
    }


def _emit_safety_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": method,
        }
    )
    return 0


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
) -> int:
    headers, auth_mode = _resolve_categories_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not plan_in:
        _should_apply(ctx, requires_ack=requires_ack)
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=proposed_changes,
            requires_ack=requires_ack,
        )
    if not _should_apply(ctx, requires_ack=requires_ack):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    verification = {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider accepted the Categories request. Follow-up get, query, list, or arrangement commands are recommended for live verification.",
    }
    receipt = _build_receipt(
        method=method_name,
        selector=selector,
        request=request,
        response=response,
        verification=verification,
        plan=loaded_plan,
        ctx=ctx,
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def _run_get(
    *,
    method: str,
    path: str,
    tree_reference_json: Any,
    ctx: dict[str, Any],
) -> int:
    headers, auth_mode = _resolve_categories_auth(ctx=ctx)
    params = _tree_reference_params(tree_reference_json)
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    _emit_success(
        method=method,
        auth_mode=auth_mode,
        request={"method": "GET", "path": path, "params": params},
        response=payload,
        ctx=ctx,
    )
    return 0


def _run_post(
    *,
    method: str,
    path: str,
    body: dict[str, Any],
    ctx: dict[str, Any],
) -> int:
    headers, auth_mode = _resolve_categories_auth(ctx=ctx)
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    _emit_success(
        method=method,
        auth_mode=auth_mode,
        request={"method": "POST", "path": path, "body": body},
        response=payload,
        ctx=ctx,
    )
    return 0


def cmd_categories_get(args, ctx) -> int:
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        return _run_get(
            method="categories.get",
            path=f"/categories/v1/categories/{category_id}",
            tree_reference_json=getattr(args, "tree_reference_json", None),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.get"})
        return 1


def cmd_categories_get_by_slug(args, ctx) -> int:
    try:
        slug = _coerce_non_empty_text(getattr(args, "slug", None), field="slug")
        return _run_get(
            method="categories.get-by-slug",
            path=f"/categories/v1/categories/slug/{slug}",
            tree_reference_json=getattr(args, "tree_reference_json", None),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.get-by-slug"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.get-by-slug"}
        )
        return 1


def cmd_categories_query(args, ctx) -> int:
    try:
        return _run_post(
            method="categories.query",
            path="/categories/v1/categories/query",
            body=_normalize_query_body(getattr(args, "query_json", None), field="query-json", wrapper_key="query"),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.query"})
        return 1


def cmd_categories_create(args, ctx) -> int:
    method = "categories.create"
    try:
        body = _normalize_category_body(getattr(args, "category_json", None), field="category-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/categories/v1/categories",
            body=body,
            selector={"operation": "create"},
            proposed_changes=[{"op": "create-category", "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_update(args, ctx) -> int:
    method = "categories.update"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        body = _normalize_category_body(
            getattr(args, "category_json", None),
            field="category-json",
            category_id=category_id,
            require_revision=True,
        )
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/categories/v1/categories/{category_id}",
            body=body,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "update-category", "category_id": category_id, "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_delete(args, ctx) -> int:
    method = "categories.delete"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/categories/v1/categories/{category_id}",
            body=None,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "delete-category", "category_id": category_id}],
            ctx=ctx,
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_update(args, ctx) -> int:
    method = "categories.bulk-update"
    try:
        body = _normalize_categories_body(getattr(args, "categories_json", None), field="categories-json", require_revision=True)
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/categories/v1/bulk/categories/update",
            body=body,
            selector={"operation": "bulk-update"},
            proposed_changes=[{"op": "bulk-update-categories", "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_update_visibility(args, ctx) -> int:
    method = "categories.update-visibility"
    try:
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path="/categories/v1/categories/visibility",
            body=body,
            selector={"operation": "update-visibility"},
            proposed_changes=[{"op": "update-category-visibility", "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_show(args, ctx) -> int:
    method = "categories.bulk-show"
    try:
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/categories/v1/bulk/categories/show",
            body=body,
            selector={"operation": "bulk-show"},
            proposed_changes=[{"op": "bulk-show-categories", "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_add_items_to_category(args, ctx) -> int:
    method = "categories.bulk-add-items-to-category"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/categories/v1/bulk/categories/{category_id}/add-items",
            body=body,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "bulk-add-items-to-category", "category_id": category_id, "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_add_item_to_categories(args, ctx) -> int:
    method = "categories.bulk-add-item-to-categories"
    try:
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/categories/v1/bulk/categories/add-item",
            body=body,
            selector={"operation": "bulk-add-item-to-categories"},
            proposed_changes=[{"op": "bulk-add-item-to-categories", "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_remove_items_from_category(args, ctx) -> int:
    method = "categories.bulk-remove-items-from-category"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/categories/v1/bulk/categories/{category_id}/remove-items",
            body=body,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "bulk-remove-items-from-category", "category_id": category_id, "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_bulk_remove_item_from_categories(args, ctx) -> int:
    method = "categories.bulk-remove-item-from-categories"
    try:
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/categories/v1/bulk/categories/remove-item",
            body=body,
            selector={"operation": "bulk-remove-item-from-categories"},
            proposed_changes=[{"op": "bulk-remove-item-from-categories", "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_move(args, ctx) -> int:
    method = "categories.move"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/categories/v1/categories/{category_id}/move",
            body=body,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "move-category", "category_id": category_id, "body": body}],
            ctx=ctx,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1


def cmd_categories_set_arranged_items(args, ctx) -> int:
    method = "categories.set-arranged-items"
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        body = _normalize_non_empty_request_body(getattr(args, "request_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/categories/v1/categories/{category_id}/set-arranged-items",
            body=body,
            selector={"category_id": category_id},
            proposed_changes=[{"op": "set-arranged-items", "category_id": category_id, "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.query"})
        return 1


def cmd_categories_search(args, ctx) -> int:
    try:
        return _run_post(
            method="categories.search",
            path="/categories/v1/categories/search",
            body=_normalize_query_body(getattr(args, "search_json", None), field="search-json", wrapper_key="search"),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.search"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.search"})
        return 1


def cmd_categories_count(args, ctx) -> int:
    try:
        return _run_post(
            method="categories.count",
            path="/categories/v1/categories/count",
            body=_normalize_count_body(getattr(args, "filter_json", None)),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.count"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.count"})
        return 1


def cmd_categories_list_trees(args, ctx) -> int:
    try:
        return _run_get(
            method="categories.list-trees",
            path="/categories/v1/categories/list-trees",
            tree_reference_json=getattr(args, "tree_reference_json", None),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.list-trees"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.list-trees"}
        )
        return 1


def cmd_categories_get_arranged_items(args, ctx) -> int:
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        return _run_get(
            method="categories.get-arranged-items",
            path=f"/categories/v1/categories/{category_id}/arranged-items",
            tree_reference_json=getattr(args, "tree_reference_json", None),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "categories.get-arranged-items"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "categories.get-arranged-items"}
        )
        return 1


def cmd_categories_list_categories_for_item(args, ctx) -> int:
    try:
        return _run_post(
            method="categories.list-categories-for-item",
            path="/categories/v1/categories/list-categories-for-item",
            body=_normalize_request_body(getattr(args, "request_json", None)),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "categories.list-categories-for-item",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "categories.list-categories-for-item",
            }
        )
        return 1


def cmd_categories_list_categories_for_items(args, ctx) -> int:
    try:
        return _run_post(
            method="categories.list-categories-for-items",
            path="/categories/v1/categories/list-categories-for-items",
            body=_normalize_request_body(getattr(args, "request_json", None)),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "categories.list-categories-for-items",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "categories.list-categories-for-items",
            }
        )
        return 1


def cmd_categories_list_items_in_category(args, ctx) -> int:
    try:
        category_id = _coerce_non_empty_text(getattr(args, "category_id", None), field="category-id")
        return _run_post(
            method="categories.list-items-in-category",
            path=f"/categories/v1/categories/{category_id}/list-items",
            body=_normalize_request_body(getattr(args, "request_json", None)),
            ctx=ctx,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "categories.list-items-in-category",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "categories.list-items-in-category",
            }
        )
        return 1
