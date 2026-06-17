from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .. import api_runtime
from ..auth_runtime import resolve_access_token
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file

request_data = api_runtime.request_data


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_request_url(base_url: str, path: str) -> str:
    if path.startswith("https://") or path.startswith("http://"):
        return path
    if path.startswith("/api/"):
        parts = urlsplit(base_url)
        if not parts.scheme or not parts.netloc:
            raise ValidationError("FORTNOX_API_BASE_URL must be an absolute URL")
        return f"{parts.scheme}://{parts.netloc}{path}"
    return f"{base_url}{path}"


def _load_raw_object_payload_file(
    path_str: str,
    *,
    label: str,
    forbidden_wrapper: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError(f"JSON file for {label} must contain a top-level object")
    if forbidden_wrapper and len(obj) == 1 and forbidden_wrapper in obj:
        raise ValidationError(
            f"JSON file for {label} must be a raw top-level object, not wrapped inside {forbidden_wrapper}"
        )
    return path, obj


def _extract_purchase_order_id(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("id")) or _string_value(payload.get("Id"))


def _extract_purchase_order_from_body(body: Any) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    purchase_order = body.get("PurchaseOrder")
    if isinstance(purchase_order, dict):
        return purchase_order
    return body


def _purchase_order_state(order: dict[str, Any] | None) -> str | None:
    if not isinstance(order, dict):
        return None
    return _string_value(order.get("purchaseOrderState")) or _string_value(order.get("state"))


def _response_state(order: dict[str, Any] | None) -> str | None:
    if not isinstance(order, dict):
        return None
    return _string_value(order.get("responseState")) or _string_value(order.get("ResponseState"))


def _emit_read(
    ctx: dict[str, Any],
    *,
    audit_key: str,
    path: str,
    payload: dict[str, Any],
    query_params: dict[str, Any] | None = None,
) -> int:
    out = {
        "ok": True,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        audit_key,
        {
            "ok": True,
            "path": path,
            "query_params": query_params,
            "http_status": payload["status"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: Any,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _verify_present(*, ctx: dict[str, Any], purchase_order_id: str) -> dict[str, Any]:
    path = f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"
    try:
        payload = request_data(
            ctx=ctx,
            method="GET",
            path=path,
            expect_json=True,
            expect_json_object=False,
        )
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _verify_many_present(*, ctx: dict[str, Any], purchase_order_ids: list[str]) -> list[dict[str, Any]]:
    return [_verify_present(ctx=ctx, purchase_order_id=purchase_order_id) for purchase_order_id in purchase_order_ids]


def _verification_has_response_state(verification: dict[str, Any], expected_response_state: str) -> bool:
    if not bool(verification.get("ok")):
        return False
    order = _extract_purchase_order_from_body(verification.get("data"))
    return _response_state(order) == expected_response_state


def _verification_has_sent_state(verification: dict[str, Any]) -> bool:
    if not bool(verification.get("ok")):
        return False
    order = _extract_purchase_order_from_body(verification.get("data"))
    state = (_purchase_order_state(order) or "").upper()
    return state == "SENT"


def _verification_has_void_state(verification: dict[str, Any]) -> bool:
    if not bool(verification.get("ok")):
        return False
    order = _extract_purchase_order_from_body(verification.get("data"))
    state = (_purchase_order_state(order) or "").upper()
    return "VOID" in state


def _verification_has_manual_completion(verification: dict[str, Any], *, action_body: Any = None) -> bool:
    if bool(verification.get("ok")):
        order = _extract_purchase_order_from_body(verification.get("data"))
        if isinstance(order, dict):
            if order.get("manuallyCompleted") is True:
                return True
            state = (_purchase_order_state(order) or "").upper()
            if "COMPLETE" in state:
                return True
    action_order = _extract_purchase_order_from_body(action_body)
    if isinstance(action_order, dict):
        if action_order.get("manuallyCompleted") is True:
            return True
        if action_order.get("releasedParentOrder") is True:
            return True
        state = (_purchase_order_state(action_order) or "").upper()
        if "COMPLETE" in state:
            return True
    return False


def _csv_request(ctx: dict[str, Any], *, path: str) -> dict[str, Any]:
    cfg = ctx["cfg"]
    resolved = resolve_access_token(cfg=cfg, env_file=ctx["env_file"])
    if not resolved.token:
        raise ValidationError("No Fortnox access token is available. Run `fortnox-api-tool auth login` first.")
    if resolved.expired is True and resolved.source == "token_file":
        raise ValidationError("Stored Fortnox access token looks expired. Run `fortnox-api-tool auth refresh` first.")
    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    url = _build_request_url(cfg.base_url, path)
    resp = client.request(
        "GET",
        url,
        headers={
            "Authorization": f"Bearer {resolved.token}",
            "Accept": "text/csv, text/plain;q=0.9, application/json;q=0.5",
        },
    )
    return {
        "status": resp.status,
        "url": resp.url,
        "token_source": resolved.source,
        "token_expired": resolved.expired,
        "content_type": resp.headers.get("content-type"),
        "body": resp.text(),
    }


def _require_yes(ctx: dict[str, Any], *, message: str) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError(message)


def _require_ack(ctx: dict[str, Any], *, message: str) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError(message)


def _load_ids(args: Any) -> list[str]:
    values = getattr(args, "id", None)
    if not isinstance(values, list):
        raise ValidationError("At least one --id is required")
    ids = [str(value).strip() for value in values if str(value).strip()]
    if not ids:
        raise ValidationError("At least one --id is required")
    return ids


def cmd_purchase_orders_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/api/warehouse/purchaseorders-v1"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="purchase_orders.list", path=path, payload=payload)


def cmd_purchase_orders_get(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="purchase_orders.get", path=path, payload=payload)


def cmd_purchase_orders_get_csv(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/api/warehouse/purchaseorders-v1/csv"
    payload = _csv_request(ctx, path=path)
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "content_type": payload["content_type"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        "purchase_orders.get_csv",
        {
            "ok": True,
            "path": path,
            "http_status": payload["status"],
            "content_type": payload["content_type"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_purchase_orders_get_note(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/notes"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="purchase_orders.get_note", path=path, payload=payload)


def cmd_purchase_orders_list_matches(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/matches"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="purchase_orders.list_matches", path=path, payload=payload)


def cmd_purchase_orders_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PurchaseOrder",
        forbidden_wrapper="PurchaseOrder",
    )
    selector = {"kind": "purchase_order", "action": "create", "path": "/api/warehouse/purchaseorders-v1"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "purchase-order-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/purchaseorders-v1/{id}"},
        rollback_notes="No generic rollback. Use the official Fortnox purchase-order update or void flow if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/purchaseorders-v1",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    purchase_order_id = _extract_purchase_order_id(_extract_purchase_order_from_body(payload.get("body"))) or _extract_purchase_order_id(payload_obj)
    if not purchase_order_id:
        raise ValidationError("Could not determine purchase-order id for create verification")
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_purchase_orders_update(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PurchaseOrder",
        forbidden_wrapper="PurchaseOrder",
    )
    payload_id = _extract_purchase_order_id(payload_obj)
    if payload_id and payload_id != purchase_order_id:
        raise ValidationError("PurchaseOrder.id in the JSON file must match --id")
    selector = {
        "kind": "purchase_order",
        "action": "update",
        "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}",
        "purchase_order_id": purchase_order_id,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "purchase-order-update"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.update.plan", {"plan_out": plan_path, "purchase_order_id": purchase_order_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_purchase_orders_partial_update(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PartialPurchaseOrder",
        forbidden_wrapper="PartialPurchaseOrder",
    )
    payload_id = _extract_purchase_order_id(payload_obj)
    if payload_id and payload_id != purchase_order_id:
        raise ValidationError("PartialPurchaseOrder.id in the JSON file must match --id")
    selector = {
        "kind": "purchase_order",
        "action": "partial-update",
        "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/partial",
        "purchase_order_id": purchase_order_id,
    }
    plan = _build_plan(
        action="partial-update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "purchase-order-partial-update"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"},
        rollback_notes="No generic rollback. Re-run a partial update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.partial_update.plan", {"plan_out": plan_path, "purchase_order_id": purchase_order_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="partial-update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PATCH",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/partial",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.partial_update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def _run_no_payload_action(
    *,
    ctx: dict[str, Any],
    purchase_order_id: str,
    action: str,
    path: str,
    method: str,
    audit_plan_key: str,
    audit_apply_key: str,
    risk_reasons: list[str],
    yes_message: str,
    ack_message: str | None = None,
    expect_json: bool,
    verification_check: Any,
) -> int:
    selector = {
        "kind": "purchase_order",
        "action": action,
        "path": path,
        "purchase_order_id": purchase_order_id,
    }
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=risk_reasons,
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"},
        rollback_notes="No generic rollback. Use the official Fortnox purchase-order flow for reversal where available.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(audit_plan_key, {"plan_out": plan_path, "purchase_order_id": purchase_order_id})
        ctx["out"].emit(out)
        return 0

    _require_yes(ctx, message=yes_message)
    if ack_message is not None:
        _require_ack(ctx, message=ack_message)
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method=method,
        path=path,
        expect_json=expect_json,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    verified = bool(verification_check(verification, action_body=payload.get("body")))
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_apply_key, {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_purchase_orders_manually_complete_dropship_order(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    return _run_no_payload_action(
        ctx=ctx,
        purchase_order_id=purchase_order_id,
        action="manually-complete-dropship-order",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/dropshipcomplete",
        method="PUT",
        audit_plan_key="purchase_orders.manually_complete_dropship_order.plan",
        audit_apply_key="purchase_orders.manually_complete_dropship_order.apply",
        risk_reasons=["fortnox-write", "purchase-order-manual-complete", "dropship-complete"],
        yes_message="Refused: manually completing a dropship purchase order requires --apply --yes",
        ack_message=None,
        expect_json=True,
        verification_check=_verification_has_manual_completion,
    )


def cmd_purchase_orders_manually_complete_purchase_order(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    return _run_no_payload_action(
        ctx=ctx,
        purchase_order_id=purchase_order_id,
        action="manually-complete-purchase-order",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/complete",
        method="PUT",
        audit_plan_key="purchase_orders.manually_complete_purchase_order.plan",
        audit_apply_key="purchase_orders.manually_complete_purchase_order.apply",
        risk_reasons=["fortnox-write", "purchase-order-manual-complete"],
        yes_message="Refused: manually completing a purchase order requires --apply --yes",
        ack_message=None,
        expect_json=False,
        verification_check=_verification_has_manual_completion,
    )


def cmd_purchase_orders_send_via_email(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PurchaseOrderMailSettings",
        forbidden_wrapper="PurchaseOrderMailSettings",
    )
    selector = {
        "kind": "purchase_order",
        "action": "send-via-email",
        "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/send",
        "purchase_order_id": purchase_order_id,
    }
    plan = _build_plan(
        action="send-via-email",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=["fortnox-write", "purchase-order-send-email"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"},
        rollback_notes="No generic rollback. Email sends and state transitions are not automatically reversible.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.send_via_email.plan", {"plan_out": plan_path, "purchase_order_id": purchase_order_id})
        ctx["out"].emit(out)
        return 0

    _require_yes(ctx, message="Refused: sending a purchase order via email requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="send-via-email", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/send",
        json_body=payload_obj,
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    verified = _verification_has_sent_state(verification)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.send_via_email.apply", {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_purchase_orders_send_many_via_email(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_ids = _load_ids(args)
    selector = {
        "kind": "purchase_order",
        "action": "send-many-via-email",
        "path": "/api/warehouse/purchaseorders-v1/sendpurchaseorders",
        "purchase_order_ids": purchase_order_ids,
    }
    plan = _build_plan(
        action="send-many-via-email",
        selector=selector,
        payload_file=None,
        payload_obj=purchase_order_ids,
        risk_level="high",
        risk_reasons=["fortnox-write", "purchase-order-send-email", "batch-action"],
        verification_plan={"type": "read-after-write", "paths": [f"/api/warehouse/purchaseorders-v1/{item}" for item in purchase_order_ids]},
        rollback_notes="No generic rollback. Email sends and state transitions are not automatically reversible.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.send_many_via_email.plan", {"plan_out": plan_path, "purchase_order_ids": purchase_order_ids})
        ctx["out"].emit(out)
        return 0

    _require_yes(ctx, message="Refused: sending multiple purchase orders via email requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="send-many-via-email", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/purchaseorders-v1/sendpurchaseorders",
        json_body=purchase_order_ids,  # type: ignore[arg-type]
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_many_present(ctx=ctx, purchase_order_ids=purchase_order_ids)
    verified = all(_verification_has_sent_state(item) for item in verification)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_ids": purchase_order_ids,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.send_many_via_email.apply", {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_purchase_orders_update_response(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PurchaseOrderResponseState",
        forbidden_wrapper="PurchaseOrderResponseState",
    )
    expected_response_state = _response_state(payload_obj)
    if not expected_response_state:
        raise ValidationError("JSON file for PurchaseOrderResponseState must contain responseState")
    selector = {
        "kind": "purchase_order",
        "action": "update-response",
        "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/response",
        "purchase_order_id": purchase_order_id,
    }
    plan = _build_plan(
        action="update-response",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=["fortnox-write", "purchase-order-response-state"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/purchaseorders-v1/{purchase_order_id}"},
        rollback_notes="No generic rollback. Re-run the response-state update if you need to change it again.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.update_response.plan", {"plan_out": plan_path, "purchase_order_id": purchase_order_id})
        ctx["out"].emit(out)
        return 0

    _require_yes(ctx, message="Refused: updating a purchase-order response state requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update-response", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/response",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, purchase_order_id=purchase_order_id)
    verified = _verification_has_response_state(verification, expected_response_state)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_id": purchase_order_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.update_response.apply", {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_purchase_orders_update_response_bulk(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_ids = _load_ids(args)
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="PurchaseOrderResponseState",
        forbidden_wrapper="PurchaseOrderResponseState",
    )
    expected_response_state = _response_state(payload_obj)
    if not expected_response_state:
        raise ValidationError("JSON file for PurchaseOrderResponseState must contain responseState")
    selector = {
        "kind": "purchase_order",
        "action": "update-response-bulk",
        "path": "/api/warehouse/purchaseorders-v1/response",
        "purchase_order_ids": purchase_order_ids,
    }
    plan = _build_plan(
        action="update-response-bulk",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=["fortnox-write", "purchase-order-response-state", "batch-action"],
        verification_plan={"type": "read-after-write", "paths": [f"/api/warehouse/purchaseorders-v1/{item}" for item in purchase_order_ids]},
        rollback_notes="No generic rollback. Re-run the response-state update if you need to change it again.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("purchase_orders.update_response_bulk.plan", {"plan_out": plan_path, "purchase_order_ids": purchase_order_ids})
        ctx["out"].emit(out)
        return 0

    _require_yes(ctx, message="Refused: bulk response-state updates require --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update-response-bulk", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path="/api/warehouse/purchaseorders-v1/response",
        query_params={"ids": ",".join(purchase_order_ids)},
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_many_present(ctx=ctx, purchase_order_ids=purchase_order_ids)
    verified = all(_verification_has_response_state(item, expected_response_state) for item in verification)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_purchase_order_ids": purchase_order_ids,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("purchase_orders.update_response_bulk.apply", {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_purchase_orders_void(args: Any, ctx: dict[str, Any]) -> int:
    purchase_order_id = str(getattr(args, "id", "") or "").strip()
    return _run_no_payload_action(
        ctx=ctx,
        purchase_order_id=purchase_order_id,
        action="void",
        path=f"/api/warehouse/purchaseorders-v1/{purchase_order_id}/void",
        method="PUT",
        audit_plan_key="purchase_orders.void.plan",
        audit_apply_key="purchase_orders.void.apply",
        risk_reasons=["fortnox-write", "purchase-order-void", "irreversible"],
        yes_message="Refused: voiding a purchase order requires --apply --yes",
        ack_message="Refused: voiding a purchase order requires --ack-irreversible",
        expect_json=False,
        verification_check=lambda verification, action_body=None: _verification_has_void_state(verification),
    )
