from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

request_json = api_runtime.request_json


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    invoice = obj.get("Invoice")
    if not isinstance(invoice, dict):
        raise ValidationError("JSON file must contain a top-level Invoice object")
    return path, obj, invoice


def _load_payload_file_optional(
    path_str: str,
) -> tuple[Path | None, dict[str, Any] | None, dict[str, Any] | None]:
    path_text = str(path_str or "").strip()
    if not path_text:
        return None, None, None
    return _load_payload_file(path_text)


def _extract_document_number_from_payload(invoice: dict[str, Any]) -> str | None:
    raw = invoice.get("DocumentNumber")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _extract_document_number_from_response(body: dict[str, Any] | None) -> str | None:
    if not isinstance(body, dict):
        return None
    invoice = body.get("Invoice")
    if not isinstance(invoice, dict):
        return None
    return _extract_document_number_from_payload(invoice)


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
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
        ]
        + (["payload_sha256 must match"] if payload_file is not None else []),
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
    if payload_file is None:
        if baseline.get("payload_sha256"):
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        expected = str(baseline.get("payload_sha256") or "").strip()
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


def _verify_present(*, ctx: dict[str, Any], document_number: str) -> dict[str, Any]:
    path = f"/invoices/{document_number}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _extract_invoice(verification: dict[str, Any]) -> dict[str, Any] | None:
    if not bool(verification.get("ok")):
        return None
    data = verification.get("data")
    if not isinstance(data, dict):
        return None
    invoice = data.get("Invoice")
    if not isinstance(invoice, dict):
        return None
    return invoice


def _verification_has_booked_true(verification: dict[str, Any]) -> bool:
    invoice = _extract_invoice(verification)
    if not isinstance(invoice, dict):
        return False
    return bool(invoice.get("Booked") is True)


def _verification_has_cancelled_true(verification: dict[str, Any]) -> bool:
    invoice = _extract_invoice(verification)
    if not isinstance(invoice, dict):
        return False
    return bool(invoice.get("Cancelled") is True)


def _verification_has_credit_reference(verification: dict[str, Any]) -> bool:
    invoice = _extract_invoice(verification)
    if not isinstance(invoice, dict):
        return False
    if not bool(invoice.get("Credit") is True):
        return False
    credit_reference = invoice.get("CreditReference")
    if isinstance(credit_reference, int):
        return True
    if isinstance(credit_reference, str):
        return bool(credit_reference.strip())
    return False


def _verification_has_warehouseready_true(verification: dict[str, Any]) -> bool:
    invoice = _extract_invoice(verification)
    if not isinstance(invoice, dict):
        return False
    return bool(invoice.get("WarehouseReady") is True)


def _verification_has_sent_true(verification: dict[str, Any]) -> bool:
    invoice = _extract_invoice(verification)
    if not isinstance(invoice, dict):
        return False
    return bool(invoice.get("Sent") is True)


def _run_invoices_state_action(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    endpoint: str,
    verification_check: Any,
    audit_plan_key: str,
    audit_apply_key: str,
    risk_reasons: list[str],
    expected_check: str,
    http_method: str = "PUT",
) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    payload_file, payload_obj, invoice = _load_payload_file_optional(str(getattr(args, "json_file", "") or "").strip())
    payload_document_number = _extract_document_number_from_payload(invoice) if invoice is not None else None
    if payload_document_number and payload_document_number != document_number:
        raise ValidationError("Invoice.DocumentNumber in the JSON file must match --document-number")
    selector = {
        "kind": "invoice",
        "action": action,
        "path": f"/invoices/{document_number}/{endpoint}",
        "document_number": document_number,
    }
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=risk_reasons,
        verification_plan={"type": "read-after-write", "path": f"/invoices/{document_number}"},
        rollback_notes="No generic rollback. Use the official Fortnox reversal flow when available if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(audit_plan_key, {"plan_out": plan_path, "document_number": document_number})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {action} on an invoice requires --apply --yes")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method=http_method,
        path=f"/invoices/{document_number}/{endpoint}",
        json_body=payload_obj,
        expect_json=True,
    )
    verification = _verify_present(ctx=ctx, document_number=document_number)
    verification_ok = verification_check(verification)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_document_number": document_number,
        "verification": verification,
        f"verification_{expected_check}": verification_ok,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verification_ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_apply_key, {"receipt_out": receipt_path, "verified": verification_ok})
    ctx["out"].emit(out)
    return 0 if verification_ok else 1


def cmd_invoices_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, invoice = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {
        "kind": "invoice",
        "action": "create",
        "path": "/invoices",
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "invoice-create"],
        verification_plan={"type": "read-after-write", "path_template": "/invoices/{DocumentNumber}"},
        rollback_notes="No generic rollback. Recreate or update the invoice explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("invoices.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/invoices", json_body=payload_obj, expect_json=True)
    document_number = (
        _extract_document_number_from_response(payload["body"])
        or _extract_document_number_from_payload(invoice)
    )
    if not document_number:
        raise ValidationError("Could not determine DocumentNumber for create verification")
    verification = _verify_present(ctx=ctx, document_number=document_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_document_number": document_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("invoices.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_invoices_update(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    payload_file, payload_obj, invoice = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    payload_document_number = _extract_document_number_from_payload(invoice)
    if payload_document_number and payload_document_number != document_number:
        raise ValidationError("Invoice.DocumentNumber in the JSON file must match --document-number")
    selector = {
        "kind": "invoice",
        "action": "update",
        "path": f"/invoices/{document_number}",
        "document_number": document_number,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "invoice-update"],
        verification_plan={"type": "read-after-write", "path": f"/invoices/{document_number}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("invoices.update.plan", {"plan_out": plan_path, "document_number": document_number})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/invoices/{document_number}",
        json_body=payload_obj,
        expect_json=True,
    )
    verification = _verify_present(ctx=ctx, document_number=document_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_document_number": document_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("invoices.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_invoices_bookkeep(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="bookkeep",
        endpoint="bookkeep",
        verification_check=_verification_has_booked_true,
        audit_plan_key="invoices.bookkeep.plan",
        audit_apply_key="invoices.bookkeep.apply",
        risk_reasons=["fortnox-write", "invoice-bookkeep", "status-change"],
        expected_check="booked_true",
    )


def cmd_invoices_cancel(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="cancel",
        endpoint="cancel",
        verification_check=_verification_has_cancelled_true,
        audit_plan_key="invoices.cancel.plan",
        audit_apply_key="invoices.cancel.apply",
        risk_reasons=["fortnox-write", "invoice-cancel", "status-change"],
        expected_check="cancelled_true",
    )


def cmd_invoices_credit(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="credit",
        endpoint="credit",
        verification_check=_verification_has_credit_reference,
        audit_plan_key="invoices.credit.plan",
        audit_apply_key="invoices.credit.apply",
        risk_reasons=["fortnox-write", "invoice-credit", "status-change"],
        expected_check="credit_reference_present",
    )


def cmd_invoices_warehouseready(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="warehouseready",
        endpoint="warehouseready",
        verification_check=_verification_has_warehouseready_true,
        audit_plan_key="invoices.warehouseready.plan",
        audit_apply_key="invoices.warehouseready.apply",
        risk_reasons=["fortnox-write", "invoice-warehouseready", "status-change"],
        expected_check="warehouseready_true",
    )


def cmd_invoices_externalprint(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="externalprint",
        endpoint="externalprint",
        verification_check=_verification_has_sent_true,
        audit_plan_key="invoices.externalprint.plan",
        audit_apply_key="invoices.externalprint.apply",
        risk_reasons=["fortnox-write", "invoice-externalprint", "status-change"],
        expected_check="sent_true",
    )


def cmd_invoices_send_as_e_invoice(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="send-as-e-invoice",
        endpoint="einvoice",
        verification_check=_verification_has_sent_true,
        audit_plan_key="invoices.send_as_e_invoice.plan",
        audit_apply_key="invoices.send_as_e_invoice.apply",
        risk_reasons=["fortnox-write", "invoice-send-einvoice", "delivery-trigger"],
        expected_check="sent_true",
        http_method="GET",
    )


def cmd_invoices_send_as_e_print(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="send-as-e-print",
        endpoint="eprint",
        verification_check=_verification_has_sent_true,
        audit_plan_key="invoices.send_as_e_print.plan",
        audit_apply_key="invoices.send_as_e_print.apply",
        risk_reasons=["fortnox-write", "invoice-send-eprint", "delivery-trigger"],
        expected_check="sent_true",
        http_method="GET",
    )


def cmd_invoices_send_as_email(args: Any, ctx: dict[str, Any]) -> int:
    return _run_invoices_state_action(
        args=args,
        ctx=ctx,
        action="send-as-email",
        endpoint="email",
        verification_check=_verification_has_sent_true,
        audit_plan_key="invoices.send_as_email.plan",
        audit_apply_key="invoices.send_as_email.apply",
        risk_reasons=["fortnox-write", "invoice-send-email", "delivery-trigger"],
        expected_check="sent_true",
        http_method="GET",
    )
