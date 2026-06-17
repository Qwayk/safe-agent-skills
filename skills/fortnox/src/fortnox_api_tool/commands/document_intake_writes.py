from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

request_data = api_runtime.request_data
request_json = api_runtime.request_json
request_multipart_file = api_runtime.request_multipart_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_raw_payload_file(path_str: str, *, label: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError(f"JSON file for {label} must contain a top-level object")
    return path, obj


def _load_wrapped_payload_file(path_str: str, *, wrapper: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path, obj = _load_raw_payload_file(path_str, label=wrapper)
    payload = obj.get(wrapper)
    if not isinstance(payload, dict):
        raise ValidationError(f"JSON file must contain a top-level {wrapper} object")
    return path, obj, payload


def _load_binary_payload_file(path_str: str, *, label: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"{label} file not found: {path}")
    if not path.is_file():
        raise ValidationError(f"{label} path must be a file: {path}")
    return path


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_reference_type(payload: dict[str, Any]) -> str | None:
    return _string_value(payload.get("referenceType")) or _string_value(payload.get("type"))


def _extract_document_id(payload: dict[str, Any]) -> str | None:
    return _string_value(payload.get("id")) or _string_value(payload.get("Id"))


def _extract_trusted_sender_email(payload: dict[str, Any]) -> str | None:
    return _string_value(payload.get("Email")) or _string_value(payload.get("email"))


def _extract_trusted_sender_id(payload: dict[str, Any]) -> str | None:
    return _string_value(payload.get("Id")) or _string_value(payload.get("id"))


def _extract_trusted_sender_from_response(body: Any) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    trusted_sender = body.get("TrustedSender")
    if not isinstance(trusted_sender, dict):
        return None
    return trusted_sender


def _extract_uploaded_file_from_response(body: Any) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    file_item = body.get("File")
    if not isinstance(file_item, dict):
        return None
    return file_item


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


def _verify_present(*, ctx: dict[str, Any], path: str, query_params: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, query_params=query_params, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "query_params": query_params, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _verify_absent(*, ctx: dict[str, Any], path: str, query_params: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, query_params=query_params, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": True, "path": path, "query_params": query_params, "absent": True, "error": str(e)}
    return {
        "ok": False,
        "path": path,
        "query_params": query_params,
        "absent": False,
        "http_status": payload["status"],
        "data": payload["body"],
        "error": "Expected target to be absent after delete verification",
    }


def _verify_email_sender_list(*, ctx: dict[str, Any]) -> dict[str, Any]:
    return _verify_present(ctx=ctx, path="/emailsenders")


def _trusted_senders_from_list(verification: dict[str, Any]) -> list[dict[str, Any]]:
    if not bool(verification.get("ok")):
        return []
    data = verification.get("data")
    if not isinstance(data, dict):
        return []
    email_senders = data.get("EmailSenders")
    if not isinstance(email_senders, dict):
        return []
    trusted = email_senders.get("TrustedSenders")
    if not isinstance(trusted, list):
        return []
    return [item for item in trusted if isinstance(item, dict)]


def _verify_email_sender_present(*, ctx: dict[str, Any], sender_id: str | None, email: str | None) -> dict[str, Any]:
    verification = _verify_email_sender_list(ctx=ctx)
    trusted_senders = _trusted_senders_from_list(verification)
    target_email = email.strip().lower() if isinstance(email, str) else None
    target_id = sender_id.strip() if isinstance(sender_id, str) else None
    found = False
    for item in trusted_senders:
        item_email = _string_value(item.get("Email"))
        item_id = _string_value(item.get("Id"))
        if target_id and item_id == target_id:
            found = True
            break
        if target_email and item_email and item_email.lower() == target_email:
            found = True
            break
    verification["trusted_sender_present"] = found
    verification["target_email"] = email
    verification["target_id"] = sender_id
    if not found and verification.get("ok"):
        verification["ok"] = False
        verification["error"] = "Expected trusted sender to be present after add verification"
    return verification


def _verify_email_sender_absent(*, ctx: dict[str, Any], sender_id: str) -> dict[str, Any]:
    verification = _verify_email_sender_list(ctx=ctx)
    trusted_senders = _trusted_senders_from_list(verification)
    absent = all(_string_value(item.get("Id")) != sender_id for item in trusted_senders)
    verification["trusted_sender_absent"] = absent
    verification["target_id"] = sender_id
    if not absent and verification.get("ok"):
        verification["ok"] = False
        verification["error"] = "Expected trusted sender to be absent after delete verification"
    return verification


def _write_dry_run(
    *,
    ctx: dict[str, Any],
    plan: dict[str, Any],
    plan_path: str | None,
    audit_key: str,
    audit_data: dict[str, Any] | None = None,
) -> int:
    out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
    ctx["audit"].write(audit_key, {"plan_out": plan_path, **(audit_data or {})})
    ctx["out"].emit(out)
    return 0


def _write_apply_result(
    *,
    ctx: dict[str, Any],
    receipt: dict[str, Any],
    receipt_path: str | None,
    audit_key: str,
    verified: bool,
) -> int:
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_key, {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def _require_yes_for_action(ctx: dict[str, Any], *, message: str) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError(message)


def _require_ack_for_action(ctx: dict[str, Any], *, message: str) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError(message)


def _require_matching_payload_id(payload: dict[str, Any], *, flag_id: str, field_name: str = "id") -> None:
    payload_id = _extract_document_id(payload)
    if payload_id and payload_id != flag_id:
        raise ValidationError(f"{field_name} in the JSON file must match --id")


def _require_matching_custom_payload(payload: dict[str, Any], *, doc_type: str, document_id: str) -> None:
    payload_type = _extract_reference_type(payload)
    payload_id = _extract_document_id(payload)
    if payload_type and payload_type != doc_type:
        raise ValidationError("Document type in the JSON file must match --type")
    if payload_id and payload_id != document_id:
        raise ValidationError("Document id in the JSON file must match --id")


def cmd_custom_document_types_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip(), label="custom document type")
    reference_type = _extract_reference_type(payload_obj)
    if not reference_type:
        raise ValidationError("JSON file must contain referenceType for custom document type verification")
    selector = {
        "kind": "custom-document-type",
        "action": "create",
        "path": "/api/warehouse/documentdeliveries/custom/documenttypes-v1",
        "reference_type": reference_type,
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-custom-document-type-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/documentdeliveries/custom/documenttypes-v1/{type}"},
        rollback_notes="No generic rollback. Remove or replace the custom document type explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="custom_document_types.create.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/documentdeliveries/custom/documenttypes-v1",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(
        ctx=ctx,
        path=f"/api/warehouse/documentdeliveries/custom/documenttypes-v1/{reference_type}",
    )
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "response_body": payload.get("body"),
        "target_reference_type": reference_type,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="custom_document_types.create.apply",
        verified=bool(verification.get("ok")),
    )


def _run_custom_document_mutation(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    path_suffix: str,
    audit_key_prefix: str,
    family_slug: str,
    kind_label: str,
    verification_flag: str | None = None,
    require_yes: bool = False,
    require_ack: bool = False,
) -> int:
    doc_type = str(getattr(args, "doc_type", "") or "").strip()
    document_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip(), label=kind_label)
    _require_matching_custom_payload(payload_obj, doc_type=doc_type, document_id=document_id)
    path = f"/api/warehouse/documentdeliveries/custom/{family_slug}/{doc_type}/{document_id}{path_suffix}"
    selector = {
        "kind": kind_label,
        "action": action,
        "path": path,
        "type": doc_type,
        "id": document_id,
    }
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high" if require_yes or require_ack else "medium",
        risk_reasons=["fortnox-write", f"{kind_label}-{action}"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/documentdeliveries/custom/{family_slug}/{doc_type}/{document_id}"},
        rollback_notes="No generic rollback. Use the documented Fortnox warehouse flow for follow-up changes if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key=f"{audit_key_prefix}.plan")

    if require_yes:
        _require_yes_for_action(ctx, message=f"Refused: {action} on this {kind_label} requires --apply --yes")
    if require_ack:
        _require_ack_for_action(ctx, message=f"Refused: {action} on this {kind_label} requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="PUT", path=path, json_body=payload_obj, expect_json=True)
    verification = _verify_present(ctx=ctx, path=f"/api/warehouse/documentdeliveries/custom/{family_slug}/{doc_type}/{document_id}")
    verification_ok = bool(verification.get("ok"))
    if verification_flag:
        data = verification.get("data")
        verification_ok = verification_ok and isinstance(data, dict) and bool(data.get(verification_flag) is True)
        verification[f"verification_{verification_flag}_true"] = verification_ok
        if bool(verification.get("ok")) and not verification_ok:
            verification["ok"] = False
            verification["error"] = f"Expected {verification_flag}=true after {action} verification"
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_type": doc_type,
        "target_id": document_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key=f"{audit_key_prefix}.apply",
        verified=verification_ok,
    )


def cmd_custom_inbound_documents_save(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="save",
        path_suffix="",
        audit_key_prefix="custom_inbound_documents.save",
        family_slug="inbound-v1",
        kind_label="custom-inbound-document",
    )


def cmd_custom_inbound_documents_release(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="release",
        path_suffix="/release",
        audit_key_prefix="custom_inbound_documents.release",
        family_slug="inbound-v1",
        kind_label="custom-inbound-document",
        verification_flag="released",
        require_yes=True,
    )


def cmd_custom_inbound_documents_void(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="void",
        path_suffix="/void",
        audit_key_prefix="custom_inbound_documents.void",
        family_slug="inbound-v1",
        kind_label="custom-inbound-document",
        verification_flag="voided",
        require_yes=True,
        require_ack=True,
    )


def cmd_custom_outbound_documents_save(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="save",
        path_suffix="",
        audit_key_prefix="custom_outbound_documents.save",
        family_slug="outbound-v1",
        kind_label="custom-outbound-document",
    )


def cmd_custom_outbound_documents_release(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="release",
        path_suffix="/release",
        audit_key_prefix="custom_outbound_documents.release",
        family_slug="outbound-v1",
        kind_label="custom-outbound-document",
        verification_flag="released",
        require_yes=True,
    )


def cmd_custom_outbound_documents_void(args: Any, ctx: dict[str, Any]) -> int:
    return _run_custom_document_mutation(
        args=args,
        ctx=ctx,
        action="void",
        path_suffix="/void",
        audit_key_prefix="custom_outbound_documents.void",
        family_slug="outbound-v1",
        kind_label="custom-outbound-document",
        verification_flag="voided",
        require_yes=True,
        require_ack=True,
    )


def cmd_manual_inbound_documents_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip(), label="manual inbound document")
    selector = {
        "kind": "manual-inbound-document",
        "action": "create",
        "path": "/api/warehouse/deliveries-v1/inbounddeliveries",
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-manual-inbound-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/deliveries-v1/inbounddeliveries/{id}"},
        rollback_notes="No generic rollback. Void or update the created manual inbound document explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="manual_inbound_documents.create.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/deliveries-v1/inbounddeliveries",
        json_body=payload_obj,
        expect_json=True,
    )
    created_id = _extract_document_id(payload.get("body"))
    if not created_id:
        raise ValidationError("Could not determine id for manual inbound create verification")
    verification = _verify_present(ctx=ctx, path=f"/api/warehouse/deliveries-v1/inbounddeliveries/{created_id}")
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": created_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="manual_inbound_documents.create.apply",
        verified=bool(verification.get("ok")),
    )


def _run_manual_document_mutation(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    family_slug: str,
    path_suffix: str,
    audit_key_prefix: str,
    kind_label: str,
    verify_flag: str | None = None,
    method: str = "PUT",
    require_yes: bool = False,
    require_ack: bool = False,
    verify_note: bool = False,
) -> int:
    document_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip(), label=kind_label)
    _require_matching_payload_id(payload_obj, flag_id=document_id)
    path = f"/api/warehouse/deliveries-v1/{family_slug}/{document_id}{path_suffix}"
    selector = {
        "kind": kind_label,
        "action": action,
        "path": path,
        "id": document_id,
    }
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high" if require_yes or require_ack else "medium",
        risk_reasons=["fortnox-write", f"{kind_label}-{action}"],
        verification_plan={"type": "read-after-write", "path": f"/api/warehouse/deliveries-v1/{family_slug}/{document_id}"},
        rollback_notes="No generic rollback. Use the documented Fortnox warehouse flow for follow-up changes if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key=f"{audit_key_prefix}.plan")

    if require_yes:
        _require_yes_for_action(ctx, message=f"Refused: {action} on this {kind_label} requires --apply --yes")
    if require_ack:
        _require_ack_for_action(ctx, message=f"Refused: {action} on this {kind_label} requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method=method, path=path, json_body=payload_obj, expect_json=True)
    verification = _verify_present(ctx=ctx, path=f"/api/warehouse/deliveries-v1/{family_slug}/{document_id}")
    verification_ok = bool(verification.get("ok"))
    data = verification.get("data")
    if verify_flag:
        verification_ok = verification_ok and isinstance(data, dict) and bool(data.get(verify_flag) is True)
        verification[f"verification_{verify_flag}_true"] = verification_ok
        if bool(verification.get("ok")) and not verification_ok:
            verification["ok"] = False
            verification["error"] = f"Expected {verify_flag}=true after {action} verification"
    if verify_note:
        expected_note = payload_obj.get("note")
        verification_ok = verification_ok and isinstance(data, dict) and data.get("note") == expected_note
        verification["verification_note_matches"] = verification_ok
        if bool(verification.get("ok")) and not verification_ok:
            verification["ok"] = False
            verification["error"] = "Expected note to match after update-note verification"
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": document_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key=f"{audit_key_prefix}.apply",
        verified=verification_ok,
    )


def cmd_manual_inbound_documents_update(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="update",
        family_slug="inbounddeliveries",
        path_suffix="",
        audit_key_prefix="manual_inbound_documents.update",
        kind_label="manual-inbound-document",
    )


def cmd_manual_inbound_documents_update_note(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="update-note",
        family_slug="inbounddeliveries",
        path_suffix="",
        audit_key_prefix="manual_inbound_documents.update_note",
        kind_label="manual-inbound-document",
        method="PATCH",
        verify_note=True,
    )


def cmd_manual_inbound_documents_release(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="release",
        family_slug="inbounddeliveries",
        path_suffix="/release",
        audit_key_prefix="manual_inbound_documents.release",
        kind_label="manual-inbound-document",
        verify_flag="released",
        require_yes=True,
    )


def cmd_manual_inbound_documents_void(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="void",
        family_slug="inbounddeliveries",
        path_suffix="/void",
        audit_key_prefix="manual_inbound_documents.void",
        kind_label="manual-inbound-document",
        verify_flag="voided",
        require_yes=True,
        require_ack=True,
    )


def cmd_manual_outbound_documents_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip(), label="manual outbound document")
    selector = {
        "kind": "manual-outbound-document",
        "action": "create",
        "path": "/api/warehouse/deliveries-v1/outbounddeliveries",
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-manual-outbound-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/deliveries-v1/outbounddeliveries/{id}"},
        rollback_notes="No generic rollback. Void or update the created manual outbound document explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="manual_outbound_documents.create.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/deliveries-v1/outbounddeliveries",
        json_body=payload_obj,
        expect_json=True,
    )
    created_id = _extract_document_id(payload.get("body"))
    if not created_id:
        raise ValidationError("Could not determine id for manual outbound create verification")
    verification = _verify_present(ctx=ctx, path=f"/api/warehouse/deliveries-v1/outbounddeliveries/{created_id}")
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": created_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="manual_outbound_documents.create.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_manual_outbound_documents_update(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="update",
        family_slug="outbounddeliveries",
        path_suffix="",
        audit_key_prefix="manual_outbound_documents.update",
        kind_label="manual-outbound-document",
    )


def cmd_manual_outbound_documents_update_note(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="update-note",
        family_slug="outbounddeliveries",
        path_suffix="",
        audit_key_prefix="manual_outbound_documents.update_note",
        kind_label="manual-outbound-document",
        method="PATCH",
        verify_note=True,
    )


def cmd_manual_outbound_documents_release(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="release",
        family_slug="outbounddeliveries",
        path_suffix="/release",
        audit_key_prefix="manual_outbound_documents.release",
        kind_label="manual-outbound-document",
        verify_flag="released",
        require_yes=True,
    )


def cmd_manual_outbound_documents_void(args: Any, ctx: dict[str, Any]) -> int:
    return _run_manual_document_mutation(
        args=args,
        ctx=ctx,
        action="void",
        family_slug="outbounddeliveries",
        path_suffix="/void",
        audit_key_prefix="manual_outbound_documents.void",
        kind_label="manual-outbound-document",
        verify_flag="voided",
        require_yes=True,
        require_ack=True,
    )


def cmd_email_senders_add_trusted(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, trusted_sender = _load_wrapped_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        wrapper="TrustedSender",
    )
    email = _extract_trusted_sender_email(trusted_sender)
    if not email:
        raise ValidationError("TrustedSender.Email is required for trusted sender verification")
    selector = {
        "kind": "trusted-email-sender",
        "action": "add",
        "path": "/emailsenders/trusted",
        "email": email,
    }
    plan = _build_plan(
        action="add",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "trusted-email-sender-add"],
        verification_plan={"type": "list-after-write", "path": "/emailsenders"},
        rollback_notes="Delete the trusted sender explicitly if you need to undo the add.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="email_senders.add_trusted.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="add", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/emailsenders/trusted",
        json_body=payload_obj,
        expect_json=False,
        expect_json_object=False,
    )
    trusted_sender_response = _extract_trusted_sender_from_response(payload.get("body"))
    sender_id = _extract_trusted_sender_id(trusted_sender_response or {}) or _extract_trusted_sender_id(trusted_sender)
    verification = _verify_email_sender_present(ctx=ctx, sender_id=sender_id, email=email)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_email": email,
        "target_id": sender_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="email_senders.add_trusted.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_email_senders_delete(args: Any, ctx: dict[str, Any]) -> int:
    sender_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "trusted-email-sender",
        "action": "delete",
        "path": f"/emailsenders/trusted/{sender_id}",
        "id": sender_id,
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="medium",
        risk_reasons=["fortnox-write", "trusted-email-sender-delete"],
        verification_plan={"type": "list-after-write", "path": "/emailsenders"},
        rollback_notes="Re-add the trusted sender explicitly if you need to undo the delete.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="email_senders.delete.plan")

    _require_yes_for_action(ctx, message="Refused: deleting a trusted email sender requires --apply --yes")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/emailsenders/trusted/{sender_id}",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_email_sender_absent(ctx=ctx, sender_id=sender_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": sender_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="email_senders.delete.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_archive_delete(args: Any, ctx: dict[str, Any]) -> int:
    archive_id = str(getattr(args, "id", "") or "").strip()
    archive_path = _string_value(getattr(args, "path", None))
    selector = {
        "kind": "archive-file",
        "action": "delete",
        "path": f"/archive/{archive_id}",
        "id": archive_id,
        "archive_path": archive_path,
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "archive-delete", "irreversible"],
        verification_plan={"type": "absence-after-delete", "path": f"/archive/{archive_id}"},
        rollback_notes="Re-upload the file explicitly if you need to restore it.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="archive.delete.plan")

    _require_yes_for_action(ctx, message="Refused: archive delete requires --apply --yes")
    _require_ack_for_action(ctx, message="Refused: archive delete requires --ack-irreversible")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    query_params = {"path": archive_path} if archive_path else None
    payload = request_data(ctx=ctx, method="DELETE", path=f"/archive/{archive_id}", query_params=query_params, expect_json=False, expect_json_object=False)
    verification = _verify_absent(ctx=ctx, path=f"/archive/{archive_id}", query_params=query_params)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": archive_id,
        "target_path": archive_path,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="archive.delete.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_archive_remove(args: Any, ctx: dict[str, Any]) -> int:
    archive_path = _string_value(getattr(args, "path", None))
    if not archive_path:
        raise ValidationError("archive remove requires --path so the CLI can target one explicit folder or file path")
    selector = {
        "kind": "archive-path",
        "action": "remove",
        "path": "/archive",
        "archive_path": archive_path,
    }
    plan = _build_plan(
        action="remove",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "archive-remove", "irreversible"],
        verification_plan={"type": "absence-after-delete", "path": "/archive", "query": {"path": archive_path}},
        rollback_notes="Recreate or re-upload the removed archive content explicitly if you need to restore it.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="archive.remove.plan")

    _require_yes_for_action(ctx, message="Refused: archive remove requires --apply --yes")
    _require_ack_for_action(ctx, message="Refused: archive remove requires --ack-irreversible")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="remove", selector=selector, payload_file=None, ctx=ctx)
    query_params = {"path": archive_path}
    payload = request_data(ctx=ctx, method="DELETE", path="/archive", query_params=query_params, expect_json=False, expect_json_object=False)
    verification = _verify_absent(ctx=ctx, path="/archive", query_params=query_params)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_path": archive_path,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="archive.remove.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_archive_upload(args: Any, ctx: dict[str, Any]) -> int:
    upload_file = _load_binary_payload_file(str(getattr(args, "file", "") or "").strip(), label="archive upload")
    archive_path = _string_value(getattr(args, "path", None))
    folder_id = _string_value(getattr(args, "folder_id", None))
    if not archive_path and not folder_id:
        raise ValidationError("archive upload requires --path or --folder-id so the target subdirectory stays explicit")
    selector = {
        "kind": "archive-upload",
        "action": "upload",
        "path": "/archive",
        "archive_path": archive_path,
        "folder_id": folder_id,
        "file_name": upload_file.name,
    }
    payload_obj = {
        "file_name": upload_file.name,
        "size_bytes": upload_file.stat().st_size,
        "archive_path": archive_path,
        "folder_id": folder_id,
    }
    plan = _build_plan(
        action="upload",
        selector=selector,
        payload_file=upload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "archive-upload"],
        verification_plan={"type": "read-after-write", "path_template": "/archive/{id}"},
        rollback_notes="Delete the uploaded archive file explicitly if you need to undo the upload.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="archive.upload.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="upload", selector=selector, payload_file=upload_file, ctx=ctx)
    query_params: dict[str, Any] = {}
    if folder_id:
        query_params["folderid"] = folder_id
    if archive_path:
        query_params["path"] = archive_path
    payload = request_multipart_file(
        ctx=ctx,
        method="POST",
        path="/archive",
        file_path=str(upload_file),
        query_params=query_params or None,
    )
    uploaded_file = _extract_uploaded_file_from_response(payload.get("body"))
    uploaded_id = _string_value((uploaded_file or {}).get("Id"))
    if not uploaded_id:
        raise ValidationError("Could not determine archive file id for upload verification")
    verification_query = {"path": archive_path} if archive_path else None
    verification = _verify_present(ctx=ctx, path=f"/archive/{uploaded_id}", query_params=verification_query)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": uploaded_id,
        "target_name": _string_value((uploaded_file or {}).get("Name")) or upload_file.name,
        "target_path": _string_value((uploaded_file or {}).get("Path")) or archive_path,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="archive.upload.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_inbox_remove(args: Any, ctx: dict[str, Any]) -> int:
    inbox_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "inbox-file-or-folder",
        "action": "remove",
        "path": f"/inbox/{inbox_id}",
        "id": inbox_id,
    }
    plan = _build_plan(
        action="remove",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "inbox-remove", "irreversible"],
        verification_plan={"type": "absence-after-delete", "path": f"/inbox/{inbox_id}"},
        rollback_notes="Re-upload the file explicitly if you need to restore it.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="inbox.remove.plan")

    _require_yes_for_action(ctx, message="Refused: inbox remove requires --apply --yes")
    _require_ack_for_action(ctx, message="Refused: inbox remove requires --ack-irreversible")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="remove", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(ctx=ctx, method="DELETE", path=f"/inbox/{inbox_id}", expect_json=False, expect_json_object=False)
    verification = _verify_absent(ctx=ctx, path=f"/inbox/{inbox_id}")
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": inbox_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="inbox.remove.apply",
        verified=bool(verification.get("ok")),
    )


def cmd_inbox_upload(args: Any, ctx: dict[str, Any]) -> int:
    upload_file = _load_binary_payload_file(str(getattr(args, "file", "") or "").strip(), label="inbox upload")
    inbox_path = _string_value(getattr(args, "path", None))
    folder_id = _string_value(getattr(args, "folder_id", None))
    selector = {
        "kind": "inbox-upload",
        "action": "upload",
        "path": "/inbox",
        "inbox_path": inbox_path,
        "folder_id": folder_id,
        "file_name": upload_file.name,
    }
    payload_obj = {
        "file_name": upload_file.name,
        "size_bytes": upload_file.stat().st_size,
        "inbox_path": inbox_path,
        "folder_id": folder_id,
    }
    plan = _build_plan(
        action="upload",
        selector=selector,
        payload_file=upload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "inbox-upload"],
        verification_plan={"type": "read-after-write", "path_template": "/inbox/{id}"},
        rollback_notes="Delete the uploaded inbox file explicitly if you need to undo the upload.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        return _write_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, audit_key="inbox.upload.plan")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="upload", selector=selector, payload_file=upload_file, ctx=ctx)
    query_params: dict[str, Any] = {}
    if folder_id:
        query_params["folderId"] = folder_id
    if inbox_path:
        query_params["path"] = inbox_path
    payload = request_multipart_file(
        ctx=ctx,
        method="POST",
        path="/inbox",
        file_path=str(upload_file),
        query_params=query_params or None,
    )
    uploaded_file = _extract_uploaded_file_from_response(payload.get("body"))
    uploaded_id = _string_value((uploaded_file or {}).get("Id"))
    if not uploaded_id:
        raise ValidationError("Could not determine inbox file id for upload verification")
    verification = _verify_present(ctx=ctx, path=f"/inbox/{uploaded_id}")
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": uploaded_id,
        "target_name": _string_value((uploaded_file or {}).get("Name")) or upload_file.name,
        "target_path": _string_value((uploaded_file or {}).get("Path")) or inbox_path,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    return _write_apply_result(
        ctx=ctx,
        receipt=receipt,
        receipt_path=receipt_path,
        audit_key="inbox.upload.apply",
        verified=bool(verification.get("ok")),
    )
