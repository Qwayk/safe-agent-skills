from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_json = api_runtime.request_json

RESPONSE_KEY = "NoxFinansInvoice"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _emit_read(ctx: dict[str, Any], *, audit_key: str, path: str, payload: dict[str, Any]) -> int:
    out = {
        "ok": True,
        "path": path,
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
            "http_status": payload["status"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    nox_finans_invoice = obj.get(RESPONSE_KEY)
    if not isinstance(nox_finans_invoice, dict):
        raise ValidationError("JSON file must contain a top-level NoxFinansInvoice object")
    return path, obj, nox_finans_invoice


def _load_payload_file_optional(
    path_str: str,
) -> tuple[Path | None, dict[str, Any] | None, dict[str, Any] | None]:
    path_text = str(path_str or "").strip()
    if not path_text:
        return None, None, None
    return _load_payload_file(path_text)


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_invoice_number_from_payload(nox_finans_invoice: dict[str, Any]) -> str | None:
    return _string_value(nox_finans_invoice.get("InvoiceNumber"))


def _extract_invoice_number_from_response(body: dict[str, Any] | None) -> str | None:
    if not isinstance(body, dict):
        return None
    nox_finans_invoice = body.get(RESPONSE_KEY)
    if not isinstance(nox_finans_invoice, dict):
        return None
    return _extract_invoice_number_from_payload(nox_finans_invoice)


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


def _verify_present(*, ctx: dict[str, Any], invoice_number: str) -> dict[str, Any]:
    path = f"/noxfinansinvoices/{invoice_number}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "invoice_number": invoice_number, "error": str(e)}
    returned_invoice_number = _extract_invoice_number_from_response(payload["body"])
    present = returned_invoice_number == invoice_number
    verification = {
        "ok": present,
        "path": path,
        "http_status": payload["status"],
        "invoice_number": invoice_number,
        "data": payload["body"],
    }
    if not present:
        verification["error"] = "Expected Fortnox Finans invoice to be present after write verification"
    return verification


def cmd_fortnox_finans_get(args: Any, ctx: dict[str, Any]) -> int:
    invoice_number = str(getattr(args, "invoice_number", "") or "").strip()
    path = f"/noxfinansinvoices/{invoice_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="fortnox_finans.get", path=path, payload=payload)


def cmd_fortnox_finans_send_an_invoice_with_fortnox_finans(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, nox_finans_invoice = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "fortnox-finans-invoice", "action": "send-an-invoice-with-fortnox-finans", "path": "/noxfinansinvoices"}
    plan = _build_plan(
        action="send-an-invoice-with-fortnox-finans",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=["fortnox-write", "fortnox-finans-send-invoice", "status-change"],
        verification_plan={"type": "read-after-write", "path_template": "/noxfinansinvoices/{InvoiceNumber}"},
        rollback_notes="No generic rollback. Use the official Fortnox Finans flow to reverse or stop the invoice if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("fortnox_finans.send.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: send-an-invoice-with-fortnox-finans requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="send-an-invoice-with-fortnox-finans", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/noxfinansinvoices", json_body=payload_obj, expect_json=True)
    invoice_number = _extract_invoice_number_from_response(payload["body"]) or _extract_invoice_number_from_payload(nox_finans_invoice)
    if not invoice_number:
        raise ValidationError("Could not determine InvoiceNumber for create verification")
    verification = _verify_present(ctx=ctx, invoice_number=invoice_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_invoice_number": invoice_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("fortnox_finans.send.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def _run_fortnox_finans_action(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    endpoint: str,
    audit_plan_key: str,
    audit_apply_key: str,
    risk_reasons: list[str],
) -> int:
    invoice_number = str(getattr(args, "invoice_number", "") or "").strip()
    payload_file, payload_obj, nox_finans_invoice = _load_payload_file_optional(str(getattr(args, "json_file", "") or "").strip())
    payload_invoice_number = _extract_invoice_number_from_payload(nox_finans_invoice) if nox_finans_invoice is not None else None
    if payload_invoice_number and payload_invoice_number != invoice_number:
        raise ValidationError("NoxFinansInvoice.InvoiceNumber in the JSON file must match --invoice-number")
    selector = {
        "kind": "fortnox-finans-invoice",
        "action": action,
        "path": f"/noxfinansinvoices/{invoice_number}/{endpoint}",
        "invoice_number": invoice_number,
    }
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=risk_reasons,
        verification_plan={"type": "read-after-write", "path": f"/noxfinansinvoices/{invoice_number}"},
        rollback_notes="No generic rollback. Use the official Fortnox Finans reversal flow when available if you need to undo this action.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(audit_plan_key, {"plan_out": plan_path, "invoice_number": invoice_number})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {action} on a Fortnox Finans invoice requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/noxfinansinvoices/{invoice_number}/{endpoint}",
        json_body=payload_obj,
        expect_json=True,
    )
    verification = _verify_present(ctx=ctx, invoice_number=invoice_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_invoice_number": invoice_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_apply_key, {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_fortnox_finans_action_pause(args: Any, ctx: dict[str, Any]) -> int:
    return _run_fortnox_finans_action(
        args=args,
        ctx=ctx,
        action="action-pause",
        endpoint="pause",
        audit_plan_key="fortnox_finans.action_pause.plan",
        audit_apply_key="fortnox_finans.action_pause.apply",
        risk_reasons=["fortnox-write", "fortnox-finans-pause", "status-change"],
    )


def cmd_fortnox_finans_action_report_payment(args: Any, ctx: dict[str, Any]) -> int:
    return _run_fortnox_finans_action(
        args=args,
        ctx=ctx,
        action="action-report-payment",
        endpoint="report-payment",
        audit_plan_key="fortnox_finans.action_report_payment.plan",
        audit_apply_key="fortnox_finans.action_report_payment.apply",
        risk_reasons=["fortnox-write", "fortnox-finans-report-payment", "status-change"],
    )


def cmd_fortnox_finans_action_stop(args: Any, ctx: dict[str, Any]) -> int:
    return _run_fortnox_finans_action(
        args=args,
        ctx=ctx,
        action="action-stop",
        endpoint="stop",
        audit_plan_key="fortnox_finans.action_stop.plan",
        audit_apply_key="fortnox_finans.action_stop.apply",
        risk_reasons=["fortnox-write", "fortnox-finans-stop", "status-change"],
    )


def cmd_fortnox_finans_action_take_fees(args: Any, ctx: dict[str, Any]) -> int:
    return _run_fortnox_finans_action(
        args=args,
        ctx=ctx,
        action="action-take-fees",
        endpoint="take-fees",
        audit_plan_key="fortnox_finans.action_take_fees.plan",
        audit_apply_key="fortnox_finans.action_take_fees.apply",
        risk_reasons=["fortnox-write", "fortnox-finans-take-fees", "status-change"],
    )


def cmd_fortnox_finans_action_unpause(args: Any, ctx: dict[str, Any]) -> int:
    return _run_fortnox_finans_action(
        args=args,
        ctx=ctx,
        action="action-unpause",
        endpoint="unpause",
        audit_plan_key="fortnox_finans.action_unpause.plan",
        audit_apply_key="fortnox_finans.action_unpause.apply",
        risk_reasons=["fortnox-write", "fortnox-finans-unpause", "status-change"],
    )
