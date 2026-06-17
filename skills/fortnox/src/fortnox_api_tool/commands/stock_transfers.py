from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
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


def _extract_stock_transfer_id(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("id")) or _string_value(payload.get("Id"))


def _extract_stock_transfer_from_body(body: Any) -> dict[str, Any] | None:
    if isinstance(body, dict):
        stock_transfer = body.get("StockTransfer")
        if isinstance(stock_transfer, dict):
            return stock_transfer
        return body
    return None


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


def _verify_present(*, ctx: dict[str, Any], stock_transfer_id: str) -> dict[str, Any]:
    path = f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}"
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


def _write_receipt_and_emit(
    *,
    ctx: dict[str, Any],
    audit_key: str,
    selector: dict[str, Any],
    payload: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    verified_ok: bool | None = None,
    extra_receipt: dict[str, Any] | None = None,
) -> int:
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    if extra_receipt:
        receipt.update(extra_receipt)
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    ok = bool(verification.get("ok")) if verified_ok is None else bool(verified_ok)
    out = {"ok": ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_key, {"receipt_out": receipt_path, "verified": ok})
    ctx["out"].emit(out)
    return 0 if ok else 1


def _emit_refusal(ctx: dict[str, Any], reasons: list[str]) -> int:
    ctx["out"].emit({"ok": True, "refused": True, "reasons": reasons})
    return 0


def cmd_stock_transfers_get(args: Any, ctx: dict[str, Any]) -> int:
    stock_transfer_id = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="stock_transfers.get", path=path, payload=payload)


def cmd_stock_transfers_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockTransfer",
        forbidden_wrapper="StockTransfer",
    )
    selector = {"kind": "stock-transfer", "action": "create", "path": "/api/warehouse/stocktransfer-v1"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-transfer-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktransfer-v1/{id}"},
        rollback_notes="No generic rollback. Update or void the stock transfer if appropriate.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_transfers.create.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/stocktransfer-v1",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    stock_transfer_id = _extract_stock_transfer_id(_extract_stock_transfer_from_body(payload.get("body"))) or _extract_stock_transfer_id(payload_obj)
    if not stock_transfer_id:
        raise ValidationError("Could not determine id for create verification")
    verification = _verify_present(ctx=ctx, stock_transfer_id=stock_transfer_id)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_transfers.create.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id": stock_transfer_id},
    )


def cmd_stock_transfers_update(args: Any, ctx: dict[str, Any]) -> int:
    stock_transfer_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockTransfer",
        forbidden_wrapper="StockTransfer",
    )
    payload_id = _extract_stock_transfer_id(payload_obj)
    if payload_id and payload_id != stock_transfer_id:
        raise ValidationError("StockTransfer id in JSON payload must match --id")
    selector = {
        "kind": "stock-transfer",
        "id": stock_transfer_id,
        "action": "update",
        "path": f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}",
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-transfer-update"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktransfer-v1/{id}"},
        rollback_notes="No generic rollback. Update the stock transfer again with corrected values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_transfers.update.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_transfer_id=stock_transfer_id)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_transfers.update.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id": stock_transfer_id},
    )


def cmd_stock_transfers_release(args: Any, ctx: dict[str, Any]) -> int:
    stock_transfer_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-transfer",
        "id": stock_transfer_id,
        "action": "release",
        "path": f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}/release",
    }
    plan = _build_plan(
        action="release",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-transfer-release", "stock-affecting"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktransfer-v1/{id}"},
        rollback_notes="No generic rollback. Release finalizes the transfer and affects stock.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_transfers.release.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    if not bool(ctx.get("yes")):
        return _emit_refusal(
            ctx,
            ["Refused: release affects stock; rerun with --apply --yes after plan review"],
        )

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="release", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}/release",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_transfer_id=stock_transfer_id)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_transfers.release.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id": stock_transfer_id},
    )


def cmd_stock_transfers_void(args: Any, ctx: dict[str, Any]) -> int:
    stock_transfer_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-transfer",
        "id": stock_transfer_id,
        "action": "void",
        "path": f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}/void",
    }
    plan = _build_plan(
        action="void",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-transfer-void", "irreversible"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktransfer-v1/{id}"},
        rollback_notes="No generic rollback. Void is the terminal reversal path for stock transfers.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_transfers.void.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    reasons: list[str] = []
    if not bool(ctx.get("yes")):
        reasons.append("Refused: rerun with --apply --yes after plan review")
    if not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: rerun with --ack-irreversible because void is intended as irreversible")
    if reasons:
        return _emit_refusal(ctx, reasons)

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="void", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stocktransfer-v1/{stock_transfer_id}/void",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_transfer_id=stock_transfer_id)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_transfers.void.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id": stock_transfer_id},
    )
