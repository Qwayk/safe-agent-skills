from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..write_safety import enforce_write_apply_contract

request_json = api_runtime.request_json


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_required_fields(contract: dict[str, Any]) -> None:
    required = ("CustomerNumber", "InvoiceRows", "PeriodEnd")
    missing = [key for key in required if contract.get(key) is None]
    if missing:
        raise ValidationError("Contract JSON payload is missing required fields: " + ", ".join(missing))


def _load_payload_file(path_str: str, *, required_fields: bool) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    contract = obj.get("Contract")
    if not isinstance(contract, dict):
        raise ValidationError("JSON file must contain a top-level Contract object")
    if required_fields:
        _validate_required_fields(contract)
    return path, obj, contract


def _load_payload_file_optional(
    path_str: str,
) -> tuple[Path | None, dict[str, Any] | None, dict[str, Any] | None]:
    path_text = str(path_str or "").strip()
    if not path_text:
        return None, None, None
    return _load_payload_file(path_text, required_fields=False)


def _extract_document_number_from_payload(contract: dict[str, Any]) -> str | None:
    raw = contract.get("DocumentNumber")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _extract_document_number_from_response(body: dict[str, Any] | None) -> str | None:
    if not isinstance(body, dict):
        return None
    contract = body.get("Contract")
    if not isinstance(contract, dict):
        return None
    return _extract_document_number_from_payload(contract)


def _extract_contract_from_verification(verification: dict[str, Any]) -> dict[str, Any] | None:
    if not bool(verification.get("ok")):
        return None
    data = verification.get("data")
    if not isinstance(data, dict):
        return None
    contract = data.get("Contract")
    if not isinstance(contract, dict):
        return None
    return contract


def _extract_str_from_contract(contract: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(contract, dict):
        return None
    raw = contract.get(key)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        text = str(value).strip()
        if not text:
            return None
        return int(text)
    except ValueError:
        return None


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


def _verify_present(*, ctx: dict[str, Any], document_number: str) -> dict[str, Any]:
    path = f"/contracts/{document_number}"
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


def _build_list_query(args: Any) -> dict[str, Any] | None:
    query: dict[str, Any] = {}
    for attr, key in (
        ("period_start", "periodstart"),
        ("period_end", "periodend"),
        ("filter", "filter"),
        ("document_number", "documentnumber"),
        ("customer_number", "customernumber"),
        ("template_number", "templatenumber"),
        ("invoices_remaining", "invoicesremaining"),
        ("last_modified", "lastmodified"),
    ):
        value = getattr(args, attr, None)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            query[key] = text
    return query or None


def _build_action_query(*, invoice_date: str | None) -> dict[str, Any] | None:
    if not invoice_date:
        return None
    value = str(invoice_date).strip()
    if not value:
        return None
    return {"invoicedate": value}


def _verification_has_invoices_remaining_decreased(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_contract = _extract_contract_from_verification(before)
    after_contract = _extract_contract_from_verification(after)
    before_remaining = _parse_int(before_contract.get("InvoicesRemaining")) if before_contract else None
    after_remaining = _parse_int(after_contract.get("InvoicesRemaining")) if after_contract else None
    if before_remaining is None or after_remaining is None:
        return False
    return after_remaining == before_remaining - 1


def _verification_has_invoices_remaining_increased(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_contract = _extract_contract_from_verification(before)
    after_contract = _extract_contract_from_verification(after)
    before_remaining = _parse_int(before_contract.get("InvoicesRemaining")) if before_contract else None
    after_remaining = _parse_int(after_contract.get("InvoicesRemaining")) if after_contract else None
    if before_remaining is None or after_remaining is None:
        return False
    return after_remaining == before_remaining + 1


def _verification_has_last_invoice_date_match(after: dict[str, Any], *, invoice_date: str | None) -> bool:
    if not invoice_date:
        return False
    after_contract = _extract_contract_from_verification(after)
    after_last_invoice_date = _extract_str_from_contract(after_contract, "LastInvoiceDate")
    return after_last_invoice_date == invoice_date


def _verification_has_last_invoice_date_changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_contract = _extract_contract_from_verification(before)
    after_contract = _extract_contract_from_verification(after)
    before_last = _extract_str_from_contract(before_contract, "LastInvoiceDate")
    after_last = _extract_str_from_contract(after_contract, "LastInvoiceDate")
    if before_last is None or after_last is None:
        return False
    return before_last != after_last


def _verification_has_active_false(after: dict[str, Any]) -> bool:
    after_contract = _extract_contract_from_verification(after)
    if not isinstance(after_contract, dict):
        return False
    active = after_contract.get("Active")
    if active is False:
        return True
    if isinstance(active, str):
        return active.strip().lower() == "false"
    return False


def cmd_contracts_list(args: Any, ctx: dict[str, Any]) -> int:
    path = "/contracts"
    payload = request_json(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=_build_list_query(args),
        expect_json=True,
    )
    return _emit_read(ctx, audit_key="contracts.list", path=path, payload=payload)


def cmd_contracts_get(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    path = f"/contracts/{document_number}"
    payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    return _emit_read(ctx, audit_key="contracts.get", path=path, payload=payload)


def _run_contract_create_or_update(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    audit_plan_key: str,
    audit_apply_key: str,
    method: str,
) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip() if action == "update" else None
    payload_file, payload_obj, contract = _load_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        required_fields=True,
    )
    payload_document_number = _extract_document_number_from_payload(contract)
    if action == "update" and payload_document_number and payload_document_number != document_number:
        raise ValidationError("Contract.DocumentNumber in the JSON file must match --document-number")
    selector = {
        "kind": "contract",
        "action": action,
        "path": "/contracts" if action == "create" else f"/contracts/{document_number}",
    }
    if document_number is not None:
        selector["document_number"] = document_number
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", f"contract-{action}"],
        verification_plan={
            "type": "read-after-write",
            "path_template": "/contracts/{DocumentNumber}",
        },
        rollback_notes="No generic rollback. Re-run the write with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(audit_plan_key, {"plan_out": plan_path, "document_number": document_number})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    path = "/contracts" if action == "create" else f"/contracts/{document_number}"
    payload = request_json(ctx=ctx, method=method, path=path, json_body=payload_obj, expect_json=True)
    target_document_number = _extract_document_number_from_response(payload.get("body")) or payload_document_number
    if not target_document_number and action == "update":
        target_document_number = document_number
    if not target_document_number:
        raise ValidationError("Could not determine DocumentNumber for write verification")
    verification = _verify_present(ctx=ctx, document_number=target_document_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_document_number": target_document_number,
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


def _run_contract_state_action(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    endpoint: str,
    audit_plan_key: str,
    audit_apply_key: str,
    risk_reasons: list[str],
    invoice_date: str | None = None,
) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    payload_file, payload_obj, contract = _load_payload_file_optional(str(getattr(args, "json_file", "") or "").strip())
    payload_document_number = _extract_document_number_from_payload(contract) if contract is not None else None
    if payload_document_number and payload_document_number != document_number:
        raise ValidationError("Contract.DocumentNumber in the JSON file must match --document-number")
    query_params = _build_action_query(invoice_date=invoice_date)
    selector = {
        "kind": "contract",
        "action": action,
        "path": f"/contracts/{document_number}/{endpoint}",
        "document_number": document_number,
    }
    if query_params is not None:
        selector["query_params"] = query_params
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=risk_reasons,
        verification_plan={"type": "read-after-write", "path": f"/contracts/{document_number}"},
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
        raise SafetyError(f"Refused: {action} on a contract requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    enforce_write_apply_contract(ctx=ctx, method="PUT", path=f"/contracts/{document_number}/{endpoint}")
    before = _verify_present(ctx=ctx, document_number=document_number)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/contracts/{document_number}/{endpoint}",
        query_params=query_params,
        json_body=payload_obj,
        expect_json=True,
    )
    after = _verify_present(ctx=ctx, document_number=document_number)

    verification_flags = {
        "verification_invoices_remaining_decreased": False,
        "verification_invoices_remaining_increased": False,
        "verification_last_invoice_date_matches": False,
        "verification_last_invoice_date_changed": False,
        "verification_active_false": False,
    }
    verification_ok = False

    if action == "create-invoice":
        verification_flags["verification_invoices_remaining_decreased"] = _verification_has_invoices_remaining_decreased(
            before,
            after,
        )
        verification_flags["verification_last_invoice_date_matches"] = _verification_has_last_invoice_date_match(
            after,
            invoice_date=invoice_date,
        )
        verification_flags["verification_last_invoice_date_changed"] = _verification_has_last_invoice_date_changed(
            before,
            after,
        )
        verification_ok = any(
            (
                verification_flags["verification_invoices_remaining_decreased"],
                verification_flags["verification_last_invoice_date_matches"],
                verification_flags["verification_last_invoice_date_changed"],
            )
        )
    elif action == "increase-invoice-count":
        verification_flags["verification_invoices_remaining_increased"] = _verification_has_invoices_remaining_increased(
            before,
            after,
        )
        verification_ok = verification_flags["verification_invoices_remaining_increased"]
    elif action == "finish":
        verification_flags["verification_active_false"] = _verification_has_active_false(after)
        verification_ok = verification_flags["verification_active_false"]
    else:
        verification_ok = bool(after.get("ok"))

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
        "verification_before": before,
        "verification": after,
        **verification_flags,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verification_ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_apply_key, {"receipt_out": receipt_path, "verified": verification_ok})
    ctx["out"].emit(out)
    return 0 if verification_ok else 1


def cmd_contracts_create(args: Any, ctx: dict[str, Any]) -> int:
    return _run_contract_create_or_update(
        args=args,
        ctx=ctx,
        action="create",
        audit_plan_key="contracts.create.plan",
        audit_apply_key="contracts.create.apply",
        method="POST",
    )


def cmd_contracts_update(args: Any, ctx: dict[str, Any]) -> int:
    return _run_contract_create_or_update(
        args=args,
        ctx=ctx,
        action="update",
        audit_plan_key="contracts.update.plan",
        audit_apply_key="contracts.update.apply",
        method="PUT",
    )


def cmd_contracts_createinvoice(args: Any, ctx: dict[str, Any]) -> int:
    invoice_date = str(getattr(args, "invoice_date", "") or "").strip() or None
    return _run_contract_state_action(
        args=args,
        ctx=ctx,
        action="create-invoice",
        endpoint="createinvoice",
        audit_plan_key="contracts.createinvoice.plan",
        audit_apply_key="contracts.createinvoice.apply",
        risk_reasons=["fortnox-write", "contract-create-invoice", "status-change"],
        invoice_date=invoice_date,
    )


def cmd_contracts_increaseinvoicecount(args: Any, ctx: dict[str, Any]) -> int:
    return _run_contract_state_action(
        args=args,
        ctx=ctx,
        action="increase-invoice-count",
        endpoint="increaseinvoicecount",
        audit_plan_key="contracts.increaseinvoicecount.plan",
        audit_apply_key="contracts.increaseinvoicecount.apply",
        risk_reasons=["fortnox-write", "contract-increase-invoice-count", "status-change"],
    )


def cmd_contracts_finish(args: Any, ctx: dict[str, Any]) -> int:
    return _run_contract_state_action(
        args=args,
        ctx=ctx,
        action="finish",
        endpoint="finish",
        audit_plan_key="contracts.finish.plan",
        audit_apply_key="contracts.finish.apply",
        risk_reasons=["fortnox-write", "contract-finish", "status-change"],
    )
