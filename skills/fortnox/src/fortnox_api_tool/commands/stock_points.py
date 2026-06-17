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


def _load_raw_array_payload_file(path_str: str, *, label: str) -> tuple[Path, list[dict[str, Any]]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, list):
        if isinstance(obj, dict) and set(obj.keys()) == {"stockLocations"}:
            raise ValidationError(
                f"JSON file for {label} must be a raw top-level array, not wrapped inside stockLocations"
            )
        raise ValidationError(f"JSON file for {label} must contain a top-level array")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(obj):
        if not isinstance(item, dict):
            raise ValidationError(f"JSON file for {label} must contain only objects (bad item at index {index})")
        rows.append(item)
    return path, rows


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


def _emit_refusal(ctx: dict[str, Any], reasons: list[str]) -> int:
    ctx["out"].emit({"ok": True, "refused": True, "reasons": reasons})
    return 0


def _extract_stock_point_id(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("id")) or _string_value(payload.get("Id"))


def _extract_stock_point_code(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("code")) or _string_value(payload.get("Code"))


def _extract_stock_location_code(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("code")) or _string_value(payload.get("Code"))


def _extract_stock_location_codes(body: Any) -> list[str]:
    if isinstance(body, list):
        return [code for code in (_extract_stock_location_code(item) for item in body if isinstance(item, dict)) if code]
    return []


def _verify_present(*, ctx: dict[str, Any], stock_point_ref: str) -> dict[str, Any]:
    path = f"/api/warehouse/stockpoints-v1/{stock_point_ref}"
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


def _verify_stock_locations(
    *,
    ctx: dict[str, Any],
    stock_point_ref: str,
    query_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = f"/api/warehouse/stockpoints-v1/{stock_point_ref}/stocklocations"
    try:
        payload = request_data(
            ctx=ctx,
            method="GET",
            path=path,
            query_params=query_params,
            expect_json=True,
            expect_json_object=False,
        )
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "query_params": query_params, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _location_codes_present(verification: dict[str, Any], expected_codes: list[str]) -> bool:
    if not bool(verification.get("ok")):
        return False
    actual = set(_extract_stock_location_codes(verification.get("data")))
    return all(code in actual for code in expected_codes)


def _stock_point_fields_match(verification: dict[str, Any], expected: dict[str, Any], fields: list[str]) -> bool:
    if not bool(verification.get("ok")):
        return False
    data = verification.get("data")
    if not isinstance(data, dict):
        return False
    for field in fields:
        if field in expected and data.get(field) != expected.get(field):
            return False
    return True


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


def _query_q(args: Any) -> dict[str, Any] | None:
    query_params: dict[str, Any] = {}
    q = _string_value(getattr(args, "q", None))
    if q:
        query_params["q"] = q
    state = _string_value(getattr(args, "state", None))
    if state:
        query_params["state"] = state
    return query_params or None


def cmd_stock_points_list(args: Any, ctx: dict[str, Any]) -> int:
    query_params = _query_q(args)
    path = "/api/warehouse/stockpoints-v1"
    payload = request_data(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=query_params,
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(ctx, audit_key="stock_points.list", path=path, payload=payload, query_params=query_params)


def cmd_stock_points_list_multi(args: Any, ctx: dict[str, Any]) -> int:
    ids = [item for item in (str(value).strip() for value in getattr(args, "id", []) or []) if item]
    if not ids:
        raise ValidationError("At least one --id is required")
    query_params: dict[str, Any] = {"ids": ",".join(ids)}
    state = _string_value(getattr(args, "state", None))
    if state:
        query_params["state"] = state
    path = "/api/warehouse/stockpoints-v1/multi"
    payload = request_data(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=query_params,
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(
        ctx,
        audit_key="stock_points.list_multi",
        path=path,
        payload=payload,
        query_params=query_params,
    )


def cmd_stock_points_get(args: Any, ctx: dict[str, Any]) -> int:
    stock_point_ref = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/stockpoints-v1/{stock_point_ref}"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="stock_points.get", path=path, payload=payload)


def cmd_stock_points_get_stock_locations(args: Any, ctx: dict[str, Any]) -> int:
    stock_point_ref = str(getattr(args, "id", "") or "").strip()
    query_params: dict[str, Any] = {}
    q = _string_value(getattr(args, "q", None))
    if q:
        query_params["q"] = q
    path = f"/api/warehouse/stockpoints-v1/{stock_point_ref}/stocklocations"
    payload = request_data(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=query_params or None,
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(
        ctx,
        audit_key="stock_points.get_stock_locations",
        path=path,
        payload=payload,
        query_params=query_params or None,
    )


def cmd_stock_points_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockPoint",
        forbidden_wrapper="StockPoint",
    )
    selector = {"kind": "stock-point", "action": "create", "path": "/api/warehouse/stockpoints-v1"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-point-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stockpoints-v1/{id_or_code}"},
        rollback_notes="No generic rollback. Delete the stock point only if it is still allowed and safe to do so.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_points.create.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/stockpoints-v1",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    response_obj = payload.get("body") if isinstance(payload.get("body"), dict) else None
    stock_point_ref = (
        _extract_stock_point_id(response_obj) or _extract_stock_point_code(response_obj) or _extract_stock_point_code(payload_obj)
    )
    if not stock_point_ref:
        raise ValidationError("Could not determine stock point id or code for create verification")
    verification = _verify_present(ctx=ctx, stock_point_ref=stock_point_ref)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_points.create.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id_or_code": stock_point_ref},
    )


def cmd_stock_points_update(args: Any, ctx: dict[str, Any]) -> int:
    stock_point_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockPoint",
        forbidden_wrapper="StockPoint",
    )
    payload_id = _extract_stock_point_id(payload_obj)
    if payload_id and payload_id != stock_point_id:
        raise ValidationError("StockPoint id in JSON payload must match --id")
    selector = {
        "kind": "stock-point",
        "id": stock_point_id,
        "action": "update",
        "path": f"/api/warehouse/stockpoints-v1/{stock_point_id}",
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-point-update"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stockpoints-v1/{id}"},
        rollback_notes="No generic rollback. Update the stock point again with corrected values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_points.update.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stockpoints-v1/{stock_point_id}",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_point_ref=stock_point_id)
    verification["verification_selected_fields_match"] = _stock_point_fields_match(
        verification,
        payload_obj,
        ["code", "name", "active", "usingCompanyAddress"],
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_points.update.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification.get("ok")) and bool(verification["verification_selected_fields_match"]),
        extra_receipt={"target_id": stock_point_id},
    )


def cmd_stock_points_append_stock_locations(args: Any, ctx: dict[str, Any]) -> int:
    stock_point_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_rows = _load_raw_array_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockLocations",
    )
    selector = {
        "kind": "stock-point",
        "id": stock_point_id,
        "action": "append-stock-locations",
        "path": f"/api/warehouse/stockpoints-v1/{stock_point_id}",
    }
    plan = _build_plan(
        action="append-stock-locations",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_rows,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-point-append-stock-locations"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stockpoints-v1/{id}/stocklocations"},
        rollback_notes="No generic rollback. Remove the appended stock locations only if a separate documented removal path is available later.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_points.append_stock_locations.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="append-stock-locations", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path=f"/api/warehouse/stockpoints-v1/{stock_point_id}",
        json_body=payload_rows,
        expect_json=True,
        expect_json_object=False,
    )
    expected_codes = [code for code in (_extract_stock_location_code(item) for item in payload_rows) if code]
    verification = _verify_stock_locations(ctx=ctx, stock_point_ref=stock_point_id)
    if expected_codes:
        verification["verification_stock_location_codes_present"] = _location_codes_present(verification, expected_codes)
    verified_ok = bool(verification.get("ok")) and (
        not expected_codes or bool(verification.get("verification_stock_location_codes_present"))
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_points.append_stock_locations.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=verified_ok,
        extra_receipt={"target_id": stock_point_id, "target_stock_location_codes": expected_codes},
    )


def cmd_stock_points_delete(args: Any, ctx: dict[str, Any]) -> int:
    stock_point_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-point",
        "id": stock_point_id,
        "action": "delete",
        "path": f"/api/warehouse/stockpoints-v1/{stock_point_id}",
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-point-delete", "irreversible"],
        verification_plan={"type": "absence-check", "path_template": "/api/warehouse/stockpoints-v1/{id}"},
        rollback_notes="No generic rollback. Delete permanently removes the stock point if Fortnox allows the operation.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_points.delete.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    reasons: list[str] = []
    if not bool(ctx.get("yes")):
        reasons.append("Refused: rerun with --apply --yes after plan review")
    if not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: rerun with --ack-irreversible because delete permanently removes the stock point")
    if reasons:
        return _emit_refusal(ctx, reasons)

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/api/warehouse/stockpoints-v1/{stock_point_id}",
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_point_ref=stock_point_id)
    verification["verification_absent"] = not bool(verification.get("ok"))
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_points.delete.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification["verification_absent"]),
        extra_receipt={"target_id": stock_point_id},
    )
