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
        raise ValidationError(f"Missing --{field}")
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
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _http_status_from_error(exc: RuntimeError) -> int | None:
    text = str(exc)
    if not text.startswith("HTTP "):
        return None
    parts = text.split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _require_revision(raw: Any) -> None:
    if raw is None:
        raise ValidationError("--inventory-item-json inventoryItem.revision is required for update")
    if isinstance(raw, str) and not raw.strip():
        raise ValidationError("--inventory-item-json inventoryItem.revision cannot be empty")


def _normalize_query_body(raw: Any, *, field: str, wrapper_key: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if wrapper_key in payload:
        nested = payload.get(wrapper_key)
        if not isinstance(nested, dict):
            raise ValidationError(f"--{field} {wrapper_key} must be a JSON object")
        return payload
    return {wrapper_key: payload}


def _normalize_create_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="inventory-item-json")
    body = dict(payload) if "inventoryItem" in payload else {"inventoryItem": payload}
    inventory_item = body.get("inventoryItem")
    if not isinstance(inventory_item, dict) or not inventory_item:
        raise ValidationError("--inventory-item-json must include a non-empty inventoryItem object")
    return body


def _normalize_update_body(raw: Any, *, inventory_item_id: str) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="inventory-item-json")
    body = dict(payload) if "inventoryItem" in payload else {"inventoryItem": payload}
    inventory_item = body.get("inventoryItem")
    if not isinstance(inventory_item, dict) or not inventory_item:
        raise ValidationError("--inventory-item-json must include a non-empty inventoryItem object")
    payload_id = inventory_item.get("id")
    if payload_id is not None and str(payload_id).strip() != inventory_item_id:
        raise SafetyError("Refused: inventory item id in body does not match --inventory-item-id")
    inventory_item.setdefault("id", inventory_item_id)
    _require_revision(inventory_item.get("revision"))
    return body


def _resolve_stores_inventory_items_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="stores-inventory-items-v3",
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


def _extract_inventory_item(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    inventory_item = payload.get("inventoryItem")
    if not isinstance(inventory_item, dict):
        raise ValidationError(f"{operation} response did not include an inventoryItem object")
    return inventory_item


def _extract_inventory_item_id(inventory_item: dict[str, Any], *, operation: str) -> str:
    raw_id = inventory_item.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable inventory item id")
    return raw_id.strip()


def _get_inventory_item(*, inventory_item_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/stores/v3/inventory-items/{inventory_item_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_inventory_item(payload, operation="stores-inventory-items-v3.get")


def _get_inventory_item_optional(
    *,
    inventory_item_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    requires_ack: bool = False,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
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
        "risk_reasons": ["wix-stores-inventory-write"],
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
                state_capture_notes
                or (
                    "Captured current inventory item state before planning."
                    if has_before_state
                    else "No useful before-state snapshot exists for this create-style write."
                )
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                rollback_notes
                or (
                    "No automatic rollback. Use the reviewed plan snapshot as a manual reference."
                    if has_before_state
                    else "No automatic rollback and no useful before-state snapshot."
                )
            ),
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
    return reviewed_plan_apply_requested(
        ctx,
        requires_ack=requires_ack,
        command_label="stores-inventory-items-v3",
    )


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: inventory item state changed since plan was created")


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
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
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
            "before_state_available": has_before_state,
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No useful before-state snapshot was available for this create-style write."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the reviewed plan snapshot as a reference."
                if has_before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
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


def _emit_read_result(*, ctx: dict[str, Any], method: str, path: str, body: dict[str, Any], payload: dict[str, Any], auth_mode: str) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "method": method,
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": path, "body": body},
            "response": payload,
        }
    )
    return 0


def cmd_stores_inventory_items_v3_get(args, ctx) -> int:
    try:
        inventory_item_id = _coerce_non_empty_text(getattr(args, "inventory_item_id", None), field="inventory-item-id")
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "stores-inventory-items-v3.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/stores/v3/inventory-items/{inventory_item_id}"},
                "response": {"inventoryItem": inventory_item},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.get"}
        )
        return 1


def cmd_stores_inventory_items_v3_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json", wrapper_key="query")
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/inventory-items/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-inventory-items-v3.query",
            path="/stores/v3/inventory-items/query",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.query"}
        )
        return 1


def cmd_stores_inventory_items_v3_search(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "search_json", None), field="search-json", wrapper_key="search")
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/inventory-items/search",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-inventory-items-v3.search",
            path="/stores/v3/inventory-items/search",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.search"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.search"}
        )
        return 1


def cmd_stores_inventory_items_v3_create(args, ctx) -> int:
    try:
        inventory_item_json = _normalize_create_body(getattr(args, "inventory_item_json", None))
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        request = {"method": "POST", "path": "/stores/v3/inventory-items", "body": inventory_item_json}
        selector = {"kind": "wix-stores-inventory-item-v3", "operation": "create"}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-inventory-items-v3.create",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else _build_plan(
                method="stores-inventory-items-v3.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": inventory_item_json}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and reread the created inventory item.",
                },
                state_capture_notes="No useful before-state snapshot exists before an inventory item is created.",
            )
        )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-inventory-items-v3.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-inventory-items-v3.create",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/inventory-items",
            headers=headers,
            params=None,
            json_body=inventory_item_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_inventory_item = _extract_inventory_item(response, operation="stores-inventory-items-v3.create")
        created_id = _extract_inventory_item_id(created_inventory_item, operation="stores-inventory-items-v3.create")
        after_inventory_item = _get_inventory_item(inventory_item_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_inventory_item.get("id") or "") == created_id,
            "type": "read-after-write",
            "path": f"/stores/v3/inventory-items/{created_id}",
            "method": "GET",
            "after": after_inventory_item,
            "checks": [{"field": "id", "expected": created_id, "actual": after_inventory_item.get("id")}],
            "notes": "Create verification uses response id plus read-back get inventory item.",
        }
        receipt = _build_receipt(
            method="stores-inventory-items-v3.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-inventory-items-v3.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-inventory-items-v3.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.create"}
        )
        return 1


def cmd_stores_inventory_items_v3_update(args, ctx) -> int:
    try:
        inventory_item_id = _coerce_non_empty_text(getattr(args, "inventory_item_id", None), field="inventory-item-id")
        inventory_item_json = _normalize_update_body(
            getattr(args, "inventory_item_json", None),
            inventory_item_id=inventory_item_id,
        )
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        request = {
            "method": "PATCH",
            "path": f"/stores/v3/inventory-items/{inventory_item_id}",
            "body": inventory_item_json,
        }
        selector = {
            "kind": "wix-stores-inventory-item-v3",
            "operation": "update",
            "inventory_item_id": inventory_item_id,
        }
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-inventory-items-v3.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            current_inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="stores-inventory-items-v3.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"inventoryItem": current_inventory_item},
                proposed_changes=[
                    {"operation": "update", "inventory_item_id": inventory_item_id, "body": inventory_item_json}
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the updated inventory item by rereading the same inventory item id.",
                },
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-inventory-items-v3.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-inventory-items-v3.update",
            expected_selector=selector,
            ctx=ctx,
        )
        current_inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"inventoryItem": current_inventory_item})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/inventory-items/{inventory_item_id}",
            headers=headers,
            params=None,
            json_body=inventory_item_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_inventory_item.get("id") or "") == inventory_item_id,
            "type": "read-after-write",
            "path": f"/stores/v3/inventory-items/{inventory_item_id}",
            "method": "GET",
            "before": current_inventory_item,
            "after": after_inventory_item,
            "checks": [{"field": "id", "expected": inventory_item_id, "actual": after_inventory_item.get("id")}],
            "notes": "Update verification uses read-back get inventory item.",
        }
        receipt = _build_receipt(
            method="stores-inventory-items-v3.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-inventory-items-v3.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-inventory-items-v3.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.update"}
        )
        return 1


def cmd_stores_inventory_items_v3_delete(args, ctx) -> int:
    try:
        inventory_item_id = _coerce_non_empty_text(getattr(args, "inventory_item_id", None), field="inventory-item-id")
        headers, auth_mode = _resolve_stores_inventory_items_v3_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not plan_in:
            _should_apply(ctx, requires_ack=True)
        request = {"method": "DELETE", "path": f"/stores/v3/inventory-items/{inventory_item_id}"}
        selector = {
            "kind": "wix-stores-inventory-item-v3",
            "operation": "delete",
            "inventory_item_id": inventory_item_id,
        }
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-inventory-items-v3.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            current_inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="stores-inventory-items-v3.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"inventoryItem": current_inventory_item},
                proposed_changes=[{"operation": "delete", "inventory_item_id": inventory_item_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify delete by expecting get inventory item to return 404.",
                },
                requires_ack=True,
            )
        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-inventory-items-v3.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-inventory-items-v3.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        current_inventory_item = _get_inventory_item(inventory_item_id=inventory_item_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"inventoryItem": current_inventory_item},
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/inventory-items/{inventory_item_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_inventory_item, after_status = _get_inventory_item_optional(
            inventory_item_id=inventory_item_id,
            ctx=ctx,
            headers=headers,
        )
        verification = {
            "ok": after_status == 404 and after_inventory_item is None,
            "type": "read-after-write",
            "path": f"/stores/v3/inventory-items/{inventory_item_id}",
            "method": "GET",
            "before": current_inventory_item,
            "after": after_inventory_item,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get inventory item to return 404.",
        }
        receipt = _build_receipt(
            method="stores-inventory-items-v3.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-inventory-items-v3.delete",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-inventory-items-v3.delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-inventory-items-v3.delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-inventory-items-v3.delete"}
        )
        return 1
