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


def _coerce_money_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field=field)
    _coerce_non_empty_text(payload.get("amount"), field=f"{field}.amount")
    return payload


def _resolve_order_billing_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
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
    json_body: dict[str, Any],
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


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _normalize_refund_items(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="refund-items-json")
    line_items = payload.get("lineItems")
    if line_items is not None:
        if not isinstance(line_items, list) or not line_items:
            raise ValidationError("--refund-items-json lineItems must be a non-empty array when provided")
        for index, item in enumerate(line_items):
            if not isinstance(item, dict):
                raise ValidationError(f"--refund-items-json lineItems[{index}] must be an object")
            _coerce_non_empty_text(item.get("lineItemId"), field=f"refund-items-json lineItems[{index}].lineItemId")
            if "quantity" not in item:
                raise ValidationError(f"--refund-items-json lineItems[{index}].quantity is required")
    shipping = payload.get("shipping")
    if shipping is not None and not isinstance(shipping, dict):
        raise ValidationError("--refund-items-json shipping must be an object when provided")
    additional_fees = payload.get("additionalFees")
    if additional_fees is not None:
        if not isinstance(additional_fees, list) or not additional_fees:
            raise ValidationError("--refund-items-json additionalFees must be a non-empty array when provided")
        for index, item in enumerate(additional_fees):
            if not isinstance(item, dict):
                raise ValidationError(f"--refund-items-json additionalFees[{index}] must be an object")
            _coerce_non_empty_text(
                item.get("additionalFeeId"),
                field=f"refund-items-json additionalFees[{index}].additionalFeeId",
            )
            if "amount" not in item:
                raise ValidationError(f"--refund-items-json additionalFees[{index}].amount is required")
    return payload


def _normalize_payment_refunds(raw: Any) -> list[dict[str, Any]]:
    payload = _read_json_arg(raw, field="payment-refunds-json")
    if not isinstance(payload, list) or not payload:
        raise ValidationError("--payment-refunds-json must be a non-empty JSON array")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValidationError(f"--payment-refunds-json[{index}] must be an object")
        _coerce_non_empty_text(item.get("paymentId"), field=f"payment-refunds-json[{index}].paymentId")
        if "amount" not in item or item.get("amount") is None:
            raise ValidationError(f"--payment-refunds-json[{index}].amount is required")
        external_refund = item.get("externalRefund")
        if external_refund is not None and not isinstance(external_refund, bool):
            raise ValidationError(f"--payment-refunds-json[{index}].externalRefund must be boolean when provided")
        normalized.append(item)
    return normalized


def _normalize_side_effects(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    return _coerce_json_object(raw, field="side-effects-json")


def _normalize_delayed_capture_settings(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    payload = _coerce_json_object(raw, field="delayed-capture-settings-json")
    _coerce_non_empty_text(
        payload.get("scheduledAction"),
        field="delayed-capture-settings-json.scheduledAction",
    )
    delay_duration = payload.get("delayDuration")
    if not isinstance(delay_duration, dict) or not delay_duration:
        raise ValidationError("--delayed-capture-settings-json delayDuration must be a JSON object")
    if "count" not in delay_duration:
        raise ValidationError("--delayed-capture-settings-json delayDuration.count is required")
    _coerce_non_empty_text(
        delay_duration.get("unit"),
        field="delayed-capture-settings-json.delayDuration.unit",
    )
    return payload


def _normalize_capture_payments(raw: Any) -> list[dict[str, Any]]:
    payload = _read_json_arg(raw, field="payments-json")
    if not isinstance(payload, list) or not payload:
        raise ValidationError("--payments-json must be a non-empty JSON array")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValidationError(f"--payments-json[{index}] must be an object")
        _coerce_non_empty_text(item.get("paymentId"), field=f"payments-json[{index}].paymentId")
        amount = item.get("amount")
        if not isinstance(amount, dict) or not amount:
            raise ValidationError(f"--payments-json[{index}].amount must be an object")
        _coerce_non_empty_text(amount.get("amount"), field=f"payments-json[{index}].amount.amount")
        normalized.append(item)
    return normalized


def _normalize_payment_ids(raw: Any, *, field: str) -> list[str]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, list) or not payload:
        raise ValidationError(f"--{field} must be a non-empty JSON array")
    normalized: list[str] = []
    for index, item in enumerate(payload):
        normalized.append(_coerce_non_empty_text(item, field=f"{field}[{index}]"))
    return normalized


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
    risk_reasons: list[str] | None = None,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
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
        "risk_reasons": risk_reasons or (["wix-order-billing-write"] + (["irreversible", "money-moving"] if requires_ack else [])),
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": bool(before_state),
            "notes": state_capture_notes or "Captured current order refundability before planning.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": rollback_notes
            or "No automatic rollback. Refunds can be money-moving and may trigger restock or customer notifications.",
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="order-billing")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: order refundability changed since plan was created")


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
            "before_state_available": bool(before_state),
            "notes": "Receipt is linked to the saved before-state refundability snapshot from the reviewed plan.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Refund recovery is manual only. External/manual refund flags, restock choices, and customer notification side effects are recorded in this receipt."
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


def _get_order_refundability(*, order_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    return _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/ecom/v1/order-billing/get-order-refundability",
        headers=headers,
        json_body={"orderId": order_id},
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _run_reviewed_write(
    *,
    ctx: dict[str, Any],
    headers: dict[str, str],
    auth_mode: str,
    method_name: str,
    path: str,
    body: dict[str, Any],
    order_id: str,
    requires_ack: bool,
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    verification_mode: str,
    risk_reasons: list[str] | None = None,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> int:
    request = {"method": "POST", "path": path, "body": body}
    selector = {"kind": "wix-order-billing", "orderId": order_id}
    plan_in = ctx.get("plan_in")
    apply_allowed = False
    if bool(ctx.get("apply")) and bool(ctx.get("yes")):
        apply_allowed = _should_apply(ctx, requires_ack=requires_ack)

    if plan_in:
        plan = _load_plan(
            plan_in=str(plan_in),
            expected_method=method_name,
            expected_selector=selector,
            ctx=ctx,
        )
    else:
        before_state = _get_order_refundability(order_id=order_id, ctx=ctx, headers=headers)
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            before_state=before_state,
            proposed_changes=proposed_changes,
            verification_plan=verification_plan,
            requires_ack=requires_ack,
            risk_reasons=risk_reasons,
            state_capture_notes=state_capture_notes,
            rollback_notes=rollback_notes,
        )

    if not apply_allowed:
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

    loaded_plan = _load_plan(
        plan_in=str(plan_in),
        expected_method=method_name,
        expected_selector=selector,
        ctx=ctx,
    )
    current_state = _get_order_refundability(order_id=order_id, ctx=ctx, headers=headers)
    _assert_no_state_drift(plan=loaded_plan, current_state=current_state)

    response = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )

    after_state: dict[str, Any] | None = None
    verification_checks = [
        {"field": "response", "expected": "non-empty object", "actual": "non-empty object" if response else "empty"}
    ]
    if verification_mode == "provider-response-plus-readback":
        after_state = _get_order_refundability(order_id=order_id, ctx=ctx, headers=headers)
        verification_checks.append(
            {
                "field": "follow_up_refundability",
                "expected": f"readback for {order_id}",
                "actual": f"readback for {order_id}" if after_state else "missing",
            }
        )

    verification: dict[str, Any] = {
        "ok": bool(response) and (bool(after_state) if verification_mode == "provider-response-plus-readback" else True),
        "type": verification_mode,
        "path": path,
        "method": "POST",
        "before": current_state,
        "checks": verification_checks,
    }
    if after_state is not None:
        verification["after"] = after_state

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
            "method": method_name,
            "auth_mode": auth_mode,
            "response": response,
            "verification": verification,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def cmd_order_billing_get_order_refundability(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id}
        payload = _get_order_refundability(order_id=order_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "order-billing.get-order-refundability",
                "auth_mode": auth_mode,
                "request": {
                    "method": "POST",
                    "path": "/ecom/v1/order-billing/get-order-refundability",
                    "body": body,
                },
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.get-order-refundability",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.get-order-refundability",
            }
        )
        return 1


def cmd_order_billing_calculate_refund(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        refund_items = _normalize_refund_items(getattr(args, "refund_items_json", None))
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id, "refundItems": refund_items}
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/ecom/v1/order-billing/calculate-refund",
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "order-billing.calculate-refund",
                "auth_mode": auth_mode,
                "request": {
                    "method": "POST",
                    "path": "/ecom/v1/order-billing/calculate-refund",
                    "body": body,
                },
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.calculate-refund",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.calculate-refund",
            }
        )
        return 1


def cmd_order_billing_refund_payments(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        payment_refunds = _normalize_payment_refunds(getattr(args, "payment_refunds_json", None))
        refund_items_raw = getattr(args, "refund_items_json", None)
        refund_items = _normalize_refund_items(refund_items_raw) if refund_items_raw is not None else None
        side_effects = _normalize_side_effects(getattr(args, "side_effects_json", None))
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body: dict[str, Any] = {"orderId": order_id, "paymentRefunds": payment_refunds}
        if refund_items is not None:
            body["refundItems"] = refund_items
        if side_effects is not None:
            body["sideEffects"] = side_effects
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.refund-payments",
            path="/ecom/v1/order-billing/refund-payments",
            body=body,
            order_id=order_id,
            requires_ack=True,
            proposed_changes=[
                {
                    "operation": "refund-payments",
                    "paymentRefunds": payment_refunds,
                    "refundItems": refund_items,
                    "sideEffects": side_effects,
                }
            ],
            verification_plan={
                "type": "provider-response-plus-readback",
                "notes": "Verify refund response fields and reread current refundability for the same order.",
            },
            verification_mode="provider-response-plus-readback",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="order-billing.refund-payments", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.refund-payments",
            }
        )
        return 1


def cmd_order_billing_authorize_charge_with_saved_payment_method(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        amount = _coerce_money_object(getattr(args, "amount_json", None), field="amount-json")
        currency = _coerce_non_empty_text(getattr(args, "currency", None), field="currency")
        delayed_capture_settings = _normalize_delayed_capture_settings(
            getattr(args, "delayed_capture_settings_json", None)
        )
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body: dict[str, Any] = {"orderId": order_id, "amount": amount, "currency": currency}
        if delayed_capture_settings is not None:
            body["delayedCaptureSettings"] = delayed_capture_settings
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.authorize-charge-with-saved-payment-method",
            path="/ecom/v1/order-billing/authorize-charge-with-saved-payment-method",
            body=body,
            order_id=order_id,
            requires_ack=False,
            proposed_changes=[
                {
                    "operation": "authorize-charge-with-saved-payment-method",
                    "amount": amount,
                    "currency": currency,
                    "delayedCaptureSettings": delayed_capture_settings,
                }
            ],
            verification_plan={
                "type": "provider-response-plus-readback",
                "notes": "Verify authorization response fields and reread current refundability for the same order.",
            },
            verification_mode="provider-response-plus-readback",
            risk_reasons=["wix-order-billing-write", "payment-authorization"],
            rollback_notes="No automatic rollback. The authorization can later be captured or voided through separate official Order Billing methods.",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(
            ctx,
            method="order-billing.authorize-charge-with-saved-payment-method",
            exc=exc,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.authorize-charge-with-saved-payment-method",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.authorize-charge-with-saved-payment-method",
            }
        )
        return 1


def cmd_order_billing_capture_authorized_payments(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        payments = _normalize_capture_payments(getattr(args, "payments_json", None))
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id, "payments": payments}
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.capture-authorized-payments",
            path="/ecom/v1/order-billing/capture-authorized-payments",
            body=body,
            order_id=order_id,
            requires_ack=True,
            proposed_changes=[{"operation": "capture-authorized-payments", "payments": payments}],
            verification_plan={
                "type": "provider-response-plus-readback",
                "notes": "Verify capture response fields and reread current refundability for the same order.",
            },
            verification_mode="provider-response-plus-readback",
            risk_reasons=["wix-order-billing-write", "irreversible", "money-moving", "payment-capture"],
            rollback_notes="No automatic rollback. Captured payments may only be reversed through separate refund flows.",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="order-billing.capture-authorized-payments", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.capture-authorized-payments",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.capture-authorized-payments",
            }
        )
        return 1


def cmd_order_billing_void_authorized_payments(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        payment_ids = _normalize_payment_ids(getattr(args, "payment_ids_json", None), field="payment-ids-json")
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id, "paymentIds": payment_ids}
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.void-authorized-payments",
            path="/ecom/v1/order-billing/void-authorized-payments",
            body=body,
            order_id=order_id,
            requires_ack=True,
            proposed_changes=[{"operation": "void-authorized-payments", "paymentIds": payment_ids}],
            verification_plan={
                "type": "provider-response-plus-readback",
                "notes": "Verify void response fields and reread current refundability for the same order.",
            },
            verification_mode="provider-response-plus-readback",
            risk_reasons=["wix-order-billing-write", "irreversible", "payment-void"],
            rollback_notes="No automatic rollback. Voided authorizations cannot be restored through this CLI.",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="order-billing.void-authorized-payments", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.void-authorized-payments",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.void-authorized-payments",
            }
        )
        return 1


def cmd_order_billing_generate_receipts(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        payment_ids = _normalize_payment_ids(getattr(args, "payment_ids_json", None), field="payment-ids-json")
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id, "paymentIds": payment_ids}
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.generate-receipts",
            path="/ecom/v1/order-billing/generate-receipts",
            body=body,
            order_id=order_id,
            requires_ack=False,
            proposed_changes=[{"operation": "generate-receipts", "paymentIds": payment_ids}],
            verification_plan={
                "type": "provider-response-only",
                "notes": "Verify receipt-generation response fields. Receipt delivery and rendered receipt output happen outside this CLI.",
            },
            verification_mode="provider-response-only",
            risk_reasons=["wix-order-billing-write", "customer-notification"],
            rollback_notes="No automatic rollback. Receipt sending and downstream delivery happen outside this CLI.",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="order-billing.generate-receipts", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.generate-receipts",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.generate-receipts",
            }
        )
        return 1


def cmd_order_billing_redeem_gift_card(args, ctx) -> int:
    try:
        order_id = _coerce_non_empty_text(getattr(args, "order_id", None), field="order-id")
        gift_card_code = _coerce_non_empty_text(getattr(args, "gift_card_code", None), field="gift-card-code")
        amount = _coerce_money_object(getattr(args, "amount_json", None), field="amount-json")
        currency = _coerce_non_empty_text(getattr(args, "currency", None), field="currency")
        headers, auth_mode = _resolve_order_billing_auth(ctx=ctx)
        body = {"orderId": order_id, "giftCardCode": gift_card_code, "amount": amount, "currency": currency}
        return _run_reviewed_write(
            ctx=ctx,
            headers=headers,
            auth_mode=auth_mode,
            method_name="order-billing.redeem-gift-card",
            path="/ecom/v1/order-billing/redeem-gift-card",
            body=body,
            order_id=order_id,
            requires_ack=True,
            proposed_changes=[
                {
                    "operation": "redeem-gift-card",
                    "giftCardCode": gift_card_code,
                    "amount": amount,
                    "currency": currency,
                }
            ],
            verification_plan={
                "type": "provider-response-plus-readback",
                "notes": "Verify redeem response fields and reread current refundability for the same order.",
            },
            verification_mode="provider-response-plus-readback",
            risk_reasons=["wix-order-billing-write", "irreversible", "gift-card-balance-consumption"],
            rollback_notes="No automatic rollback. Gift card redemption and remaining-balance recovery are manual only unless separate provider flows exist.",
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="order-billing.redeem-gift-card", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "order-billing.redeem-gift-card",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.redeem-gift-card",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "order-billing.refund-payments",
            }
        )
        return 1
