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


def _resolve_orders_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="orders",
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


def _extract_order(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    order = payload.get("order")
    if not isinstance(order, dict):
        raise ValidationError(f"{operation} response did not include an order object")
    return order


def _extract_order_id(order: dict[str, Any], *, operation: str) -> str:
    raw_id = order.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable order id")
    return raw_id.strip()


def _get_order(*, order_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/ecom/v1/orders/{order_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_order(payload, operation="orders.get")


def _get_order_optional(*, order_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_order(order_id=order_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _normalize_search_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="search-json")
    if not isinstance(payload, dict):
        raise ValidationError("--search-json must be a JSON object")
    if "search" in payload:
        search = payload.get("search")
        if not isinstance(search, dict):
            raise ValidationError("--search-json search must be a JSON object")
        return payload
    return {"search": payload}


def _normalize_create_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="order-json")
    body = dict(payload) if "order" in payload else {"order": payload}
    order = body.get("order")
    if not isinstance(order, dict) or not order:
        raise ValidationError("--order-json must include a non-empty order object")
    line_items = order.get("lineItems")
    if not isinstance(line_items, list) or not line_items:
        raise ValidationError("--order-json order.lineItems must be a non-empty array")
    for index, item in enumerate(line_items):
        if not isinstance(item, dict):
            raise ValidationError(f"--order-json order.lineItems[{index}] must be a JSON object")
        item_type = item.get("itemType")
        preset = item_type.get("preset") if isinstance(item_type, dict) else None
        if preset == "DIGITAL" and not isinstance(item.get("digitalFile"), dict):
            raise ValidationError(
                f"--order-json order.lineItems[{index}].digitalFile is required when itemType.preset is DIGITAL"
            )
        if "id" in item and item.get("id") is not None and not isinstance(item.get("id"), str):
            raise ValidationError(f"--order-json order.lineItems[{index}].id must be a string when provided")
    return body


def _normalize_update_body(raw: Any, *, order_id: str) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="order-json")
    body = dict(payload) if "order" in payload else {"order": payload}
    order = body.get("order")
    if not isinstance(order, dict) or not order:
        raise ValidationError("--order-json must include a non-empty order object")
    payload_id = order.get("id")
    if payload_id is not None and str(payload_id).strip() != order_id:
        raise SafetyError("Refused: order id in body does not match --order-id")
    order.setdefault("id", order_id)
    return body


def _normalize_cancel_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="cancel-json")
    if not isinstance(payload, dict):
        raise ValidationError("--cancel-json must be a JSON object")
    return payload


def _normalize_bulk_update_body(raw: Any) -> tuple[dict[str, Any], list[str]]:
    payload = _read_json_arg(raw, field="orders-json")
    body = {"orders": payload} if isinstance(payload, list) else payload
    if not isinstance(body, dict):
        raise ValidationError("--orders-json must be a JSON array or object")
    orders = body.get("orders")
    if not isinstance(orders, list) or not orders:
        raise ValidationError("--orders-json must include a non-empty orders array")
    if len(orders) > 100:
        raise ValidationError("--orders-json orders array cannot include more than 100 orders")

    normalized: list[dict[str, Any]] = []
    order_ids: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(orders):
        if not isinstance(item, dict):
            raise ValidationError(f"--orders-json orders[{index}] must be a JSON object")
        order = item.get("order") if isinstance(item.get("order"), dict) else item
        if not isinstance(order, dict) or not order:
            raise ValidationError(f"--orders-json orders[{index}] must include a non-empty order object")
        order_id = _coerce_non_empty_text(order.get("id"), field=f"orders-json orders[{index}].order.id")
        if order_id in seen_ids:
            raise ValidationError(f"--orders-json contains duplicate order id: {order_id}")
        seen_ids.add(order_id)
        normalized.append({"order": order})
        order_ids.append(order_id)

    body = dict(body)
    body["orders"] = normalized
    body.setdefault("returnEntity", True)
    return body, order_ids


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
        "apply requires --plan-in, --apply, and --yes",
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
        "risk_reasons": ["wix-order-write"] + (["irreversible"] if requires_ack else []),
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
                    "Captured current provider state before planning."
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
                    "No automatic rollback. Use the saved before-state only as a manual reference."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="orders")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: order state changed since plan was created")


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


def cmd_orders_get(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "orders.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/ecom/v1/orders/{order_id}"},
                "response": {"order": order},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.get"})
        return 1


def cmd_orders_search(args, ctx) -> int:
    try:
        body = _normalize_search_body(getattr(args, "search_json", None))
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/ecom/v1/orders/search",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "orders.search",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/ecom/v1/orders/search", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.search"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.search"})
        return 1


def cmd_orders_create(args, ctx) -> int:
    try:
        order_json = _normalize_create_body(getattr(args, "order_json", None))
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        request = {"method": "POST", "path": "/ecom/v1/orders", "body": order_json}
        selector = {"kind": "wix-order", "operation": "create"}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="orders.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="orders.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": order_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify create response id and reread the created order."},
                state_capture_notes="No useful before-state snapshot exists before an order is created.",
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "orders.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="orders.create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/ecom/v1/orders",
            headers=headers,
            params=None,
            json_body=order_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_order = _extract_order(response, operation="orders.create")
        created_id = _extract_order_id(created_order, operation="orders.create")
        after_order = _get_order(order_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_order.get("id") or "") == created_id,
            "type": "read-after-write",
            "path": f"/ecom/v1/orders/{created_id}",
            "method": "GET",
            "after": after_order,
            "checks": [{"field": "id", "expected": created_id, "actual": after_order.get("id")}],
            "notes": "Create verification uses response id plus read-back get order.",
        }
        receipt = _build_receipt(
            method="orders.create",
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
                "method": "orders.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="orders.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.create"})
        return 1


def cmd_orders_update(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        order_json = _normalize_update_body(getattr(args, "order_json", None), order_id=order_id)
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        request = {"method": "PATCH", "path": f"/ecom/v1/orders/{order_id}", "body": order_json}
        selector = {"kind": "wix-order", "operation": "update", "order_id": order_id}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="orders.update", expected_selector=selector, ctx=ctx)
            current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        else:
            current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="orders.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"order": current_order},
                proposed_changes=[{"operation": "update", "order_id": order_id, "body": order_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify the updated order by rereading the same order id."},
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "orders.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="orders.update", expected_selector=selector, ctx=ctx)
        current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"order": current_order})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/ecom/v1/orders/{order_id}",
            headers=headers,
            params=None,
            json_body=order_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_order.get("id") or "") == order_id,
            "type": "read-after-write",
            "path": f"/ecom/v1/orders/{order_id}",
            "method": "GET",
            "before": current_order,
            "after": after_order,
            "checks": [{"field": "id", "expected": order_id, "actual": after_order.get("id")}],
            "notes": "Update verification uses read-back get order.",
        }
        receipt = _build_receipt(
            method="orders.update",
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
                "method": "orders.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="orders.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.update"})
        return 1


def cmd_orders_cancel(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        cancel_json = _normalize_cancel_body(getattr(args, "cancel_json", None))
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        request = {"method": "POST", "path": f"/ecom/v1/orders/{order_id}/cancel", "body": cancel_json}
        selector = {"kind": "wix-order", "operation": "cancel", "order_id": order_id}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx, requires_ack=True)
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="orders.cancel", expected_selector=selector, ctx=ctx)
            current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        else:
            current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="orders.cancel",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"order": current_order},
                proposed_changes=[{"operation": "cancel", "order_id": order_id, "body": cancel_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify cancel by rereading the same order and checking status CANCELED."},
                requires_ack=True,
                rollback_notes="No automatic rollback. Order cancel can trigger buyer email and restock side effects.",
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "orders.cancel",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="orders.cancel", expected_selector=selector, ctx=ctx)
        current_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"order": current_order})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/ecom/v1/orders/{order_id}/cancel",
            headers=headers,
            params=None,
            json_body=cancel_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_order = _get_order(order_id=order_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_order.get("status") or "") == "CANCELED",
            "type": "read-after-write",
            "path": f"/ecom/v1/orders/{order_id}",
            "method": "GET",
            "before": current_order,
            "after": after_order,
            "checks": [{"field": "status", "expected": "CANCELED", "actual": after_order.get("status")}],
            "notes": "Cancel verification uses read-back get order and expects status CANCELED.",
        }
        receipt = _build_receipt(
            method="orders.cancel",
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
                "method": "orders.cancel",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="orders.cancel", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.cancel"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.cancel"})
        return 1


def cmd_orders_bulk_update(args, ctx) -> int:
    try:
        orders_json, order_ids = _normalize_bulk_update_body(getattr(args, "orders_json", None))
        headers, auth_mode = _resolve_orders_auth(ctx=ctx)
        request = {"method": "POST", "path": "/ecom/v1/bulk/orders/update", "body": orders_json}
        selector = {"kind": "wix-order-bulk", "operation": "bulk-update", "order_ids": order_ids}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="orders.bulk-update", expected_selector=selector, ctx=ctx)
            current_orders = {order_id: _get_order(order_id=order_id, ctx=ctx, headers=headers) for order_id in order_ids}
        else:
            current_orders = {order_id: _get_order(order_id=order_id, ctx=ctx, headers=headers) for order_id in order_ids}
            plan = _build_plan(
                method="orders.bulk-update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"orders": current_orders},
                proposed_changes=[{"operation": "bulk-update", "order_ids": order_ids, "body": orders_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify bulk update by rereading each target order id."},
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "orders.bulk-update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="orders.bulk-update", expected_selector=selector, ctx=ctx)
        current_orders = {order_id: _get_order(order_id=order_id, ctx=ctx, headers=headers) for order_id in order_ids}
        _assert_no_state_drift(plan=loaded_plan, current_state={"orders": current_orders})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/ecom/v1/bulk/orders/update",
            headers=headers,
            params=None,
            json_body=orders_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_orders = {order_id: _get_order(order_id=order_id, ctx=ctx, headers=headers) for order_id in order_ids}
        verification = {
            "ok": set(after_orders) == set(order_ids),
            "type": "read-after-write",
            "path": "/ecom/v1/bulk/orders/update",
            "method": "POST",
            "before": current_orders,
            "after": after_orders,
            "checks": [{"field": "order_ids", "expected": order_ids, "actual": list(after_orders.keys())}],
            "notes": "Bulk update verification rereads each target order id. Returned entities are advisory only.",
        }
        receipt = _build_receipt(
            method="orders.bulk-update",
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
                "method": "orders.bulk-update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="orders.bulk-update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "orders.bulk-update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "orders.bulk-update"})
        return 1
