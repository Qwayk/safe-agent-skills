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
        if isinstance(obj, dict) and set(obj.keys()) == {"rows"}:
            raise ValidationError(f"JSON file for {label} must be a raw top-level array, not wrapped inside rows")
        raise ValidationError(f"JSON file for {label} must contain a top-level array")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(obj):
        if not isinstance(item, dict):
            raise ValidationError(f"JSON file for {label} must contain only objects (bad item at index {index})")
        rows.append(item)
    return path, rows


def _normalize_date(value: Any) -> str:
    text = _string_value(value)
    if not text:
        raise ValidationError("Date must use YYYY-MM-DD")
    parts = text.split("-")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValidationError("Date must use YYYY-MM-DD")
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        raise ValidationError("Date must use YYYY-MM-DD")
    return text


def _flatten_list(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        for piece in str(value).split(","):
            text = piece.strip()
            if text:
                out.append(text)
    return out


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


def _extract_stock_taking_id(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return _string_value(payload.get("id")) or _string_value(payload.get("Id"))


def _extract_stock_taking_from_body(body: Any) -> dict[str, Any] | None:
    if isinstance(body, dict):
        stock_taking = body.get("StockTaking")
        if isinstance(stock_taking, dict):
            return stock_taking
        return body
    return None


def _extract_row_objects(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    if isinstance(body, dict):
        rows = body.get("rows")
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, dict)]
    return []


def _extract_stock_taking_row_id(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return (
        _string_value(payload.get("stockTakingRowId"))
        or _string_value(payload.get("rowId"))
        or _string_value(payload.get("id"))
        or _string_value(payload.get("Id"))
    )


def _extract_row_ids(body: Any) -> list[str]:
    row_ids: list[str] = []
    for row in _extract_row_objects(body):
        row_id = _extract_stock_taking_row_id(row)
        if row_id:
            row_ids.append(row_id)
    return row_ids


def _stock_taking_state(body: Any) -> str | None:
    stock_taking = _extract_stock_taking_from_body(body)
    if not isinstance(stock_taking, dict):
        return None
    return _string_value(stock_taking.get("state")) or _string_value(stock_taking.get("State"))


def _verify_present(*, ctx: dict[str, Any], stock_taking_id: str) -> dict[str, Any]:
    path = f"/api/warehouse/stocktaking-v1/{stock_taking_id}"
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


def _verify_rows(
    *,
    ctx: dict[str, Any],
    stock_taking_id: str,
    query_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows"
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


def _row_ids_present(verification: dict[str, Any], expected_row_ids: list[str]) -> bool:
    if not bool(verification.get("ok")):
        return False
    actual = set(_extract_row_ids(verification.get("data")))
    return all(row_id in actual for row_id in expected_row_ids)


def _row_ids_absent(verification: dict[str, Any], expected_row_ids: list[str]) -> bool:
    if not bool(verification.get("ok")):
        return False
    actual = set(_extract_row_ids(verification.get("data")))
    return all(row_id not in actual for row_id in expected_row_ids)


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


def _build_filter_query(
    args: Any,
    *,
    include_non_inbound_field: str | None = None,
    exclude_non_inbound_field: str | None = None,
    include_rows_extras: bool = False,
) -> dict[str, Any]:
    query_params: dict[str, Any] = {}
    array_specs = (
        ("item_id", "itemIds"),
        ("supplier_number", "supplierNumbers"),
        ("stock_point_id", "stockPointIds"),
        ("stock_location_id", "stockLocationIds"),
    )
    for attr_name, query_name in array_specs:
        values = _flatten_list(getattr(args, attr_name, None))
        if values:
            query_params[query_name] = values

    if getattr(args, "transaction_date", None):
        query_params["transactionDate"] = _normalize_date(getattr(args, "transaction_date"))
    item_id_search = _string_value(getattr(args, "item_id_search", None))
    if item_id_search:
        query_params["itemIdSearch"] = item_id_search
    item_description_search = _string_value(getattr(args, "item_description_search", None))
    if item_description_search:
        query_params["itemDescriptionSearch"] = item_description_search
    if bool(getattr(args, "exclude_zero_balance_items", False)):
        query_params["excludeZeroBalanceItems"] = True

    if include_non_inbound_field and bool(getattr(args, "include_non_inbound_items", False)):
        query_params[include_non_inbound_field] = True
    if exclude_non_inbound_field and bool(getattr(args, "exclude_non_inbound_items", False)):
        query_params[exclude_non_inbound_field] = True

    if include_rows_extras:
        secondary_sort_by = _string_value(getattr(args, "secondary_sort_by", None))
        if secondary_sort_by:
            query_params["secondarysortby"] = secondary_sort_by
        secondary_order = _string_value(getattr(args, "secondary_order", None))
        if secondary_order:
            query_params["secondaryorder"] = secondary_order
        state_filter = _string_value(getattr(args, "state_filter", None))
        if state_filter:
            query_params["stateFilter"] = state_filter
        starting_row_no = getattr(args, "starting_row_no", None)
        if starting_row_no is not None:
            query_params["startingRowNo"] = int(starting_row_no)
        starting_item_id = _string_value(getattr(args, "starting_item_id", None))
        if starting_item_id:
            query_params["startingItemId"] = starting_item_id

    return query_params


def cmd_stock_taking_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/api/warehouse/stocktaking-v1"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="stock_taking.list", path=path, payload=payload)


def cmd_stock_taking_get(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    path = f"/api/warehouse/stocktaking-v1/{stock_taking_id}"
    payload = request_data(ctx=ctx, method="GET", path=path, expect_json=True, expect_json_object=False)
    return _emit_read(ctx, audit_key="stock_taking.get", path=path, payload=payload)


def cmd_stock_taking_get_candidate_rows(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    query_params = _build_filter_query(args, include_non_inbound_field="includeNonInboundItems")
    path = f"/api/warehouse/stocktaking-v1/{stock_taking_id}/candidates"
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
        audit_key="stock_taking.get_candidate_rows",
        path=path,
        payload=payload,
        query_params=query_params or None,
    )


def cmd_stock_taking_get_rows(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    query_params = _build_filter_query(args, include_rows_extras=True)
    path = f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows"
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
        audit_key="stock_taking.get_rows",
        path=path,
        payload=payload,
        query_params=query_params or None,
    )


def cmd_stock_taking_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockTaking",
        forbidden_wrapper="StockTaking",
    )
    selector = {"kind": "stock-taking", "action": "create", "path": "/api/warehouse/stocktaking-v1"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-create"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}"},
        rollback_notes="No generic rollback. Delete or void the stock-taking document if that is still allowed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.create.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/warehouse/stocktaking-v1",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    stock_taking_id = _extract_stock_taking_id(_extract_stock_taking_from_body(payload.get("body"))) or _extract_stock_taking_id(payload_obj)
    if not stock_taking_id:
        raise ValidationError("Could not determine id for create verification")
    verification = _verify_present(ctx=ctx, stock_taking_id=stock_taking_id)
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.create.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        extra_receipt={"target_id": stock_taking_id},
    )


def cmd_stock_taking_update(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj = _load_raw_object_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockTaking",
        forbidden_wrapper="StockTaking",
    )
    payload_id = _extract_stock_taking_id(payload_obj)
    if payload_id and payload_id != stock_taking_id:
        raise ValidationError("StockTaking id in JSON payload must match --id")
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "update",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}",
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-update"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}"},
        rollback_notes="No generic rollback. Update the stock-taking document again with corrected values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.update.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}",
        json_body=payload_obj,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_taking_id=stock_taking_id)
    expected_state = _string_value(payload_obj.get("state"))
    if expected_state:
        verification["verification_state"] = _stock_taking_state(verification.get("data"))
        verification["verification_state_matches"] = verification["verification_state"] == expected_state
    verified_ok = bool(verification.get("ok")) and (
        expected_state is None or bool(verification.get("verification_state_matches"))
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.update.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=verified_ok,
        extra_receipt={"target_id": stock_taking_id},
    )


def cmd_stock_taking_add_rows(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_rows = _load_raw_array_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        label="StockTakingRows",
    )
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "add-rows",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows",
    }
    plan = _build_plan(
        action="add-rows",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_rows,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-add-rows"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}/rows"},
        rollback_notes="No generic rollback. Remove the added rows explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.add_rows.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="add-rows", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows",
        json_body=payload_rows,
        expect_json=False,
        expect_json_object=False,
    )
    expected_row_ids = [row_id for row_id in (_extract_stock_taking_row_id(row) for row in payload_rows) if row_id]
    verification = _verify_rows(ctx=ctx, stock_taking_id=stock_taking_id)
    if expected_row_ids:
        verification["verification_row_ids_present"] = _row_ids_present(verification, expected_row_ids)
    verified_ok = bool(verification.get("ok")) and (
        not expected_row_ids or bool(verification.get("verification_row_ids_present"))
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.add_rows.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=verified_ok,
        extra_receipt={"target_id": stock_taking_id, "target_row_ids": expected_row_ids},
    )


def cmd_stock_taking_add_rows_by_filter(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    query_params = _build_filter_query(args, exclude_non_inbound_field="excludeNonInboundItems")
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "add-rows-by-filter",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/addrows",
        "query_params": query_params,
    }
    plan = _build_plan(
        action="add-rows-by-filter",
        selector=selector,
        payload_file=None,
        payload_obj=query_params,
        risk_level="medium",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-add-rows-by-filter"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}/rows"},
        rollback_notes="No generic rollback. Remove the added rows explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.add_rows_by_filter.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="add-rows-by-filter", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/addrows",
        query_params=query_params or None,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_rows(ctx=ctx, stock_taking_id=stock_taking_id)
    expected_row_ids = _extract_row_ids(payload.get("body"))
    if expected_row_ids:
        verification["verification_row_ids_present"] = _row_ids_present(verification, expected_row_ids)
    verified_ok = bool(verification.get("ok")) and (
        not expected_row_ids or bool(verification.get("verification_row_ids_present"))
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.add_rows_by_filter.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=verified_ok,
        extra_receipt={"target_id": stock_taking_id, "target_row_ids": expected_row_ids},
    )


def cmd_stock_taking_delete(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "delete",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}",
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-delete", "irreversible"],
        verification_plan={"type": "absence-check", "path_template": "/api/warehouse/stocktaking-v1/{id}"},
        rollback_notes="No generic rollback. Delete permanently removes the stock-taking document and its rows.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.delete.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    reasons: list[str] = []
    if not bool(ctx.get("yes")):
        reasons.append("Refused: rerun with --apply --yes after plan review")
    if not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: rerun with --ack-irreversible because delete permanently removes the document")
    if reasons:
        return _emit_refusal(ctx, reasons)

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_taking_id=stock_taking_id)
    verification["verification_absent"] = not bool(verification.get("ok"))
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.delete.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification["verification_absent"]),
        extra_receipt={"target_id": stock_taking_id},
    )


def cmd_stock_taking_delete_row(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    row_id = str(getattr(args, "row_id", "") or "").strip()
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "row_id": row_id,
        "action": "delete-row",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows/{row_id}",
    }
    plan = _build_plan(
        action="delete-row",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-delete-row", "irreversible"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}/rows"},
        rollback_notes="No generic rollback. Re-add the removed row if it is still a valid candidate.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.delete_row.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    reasons: list[str] = []
    if not bool(ctx.get("yes")):
        reasons.append("Refused: rerun with --apply --yes after plan review")
    if not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: rerun with --ack-irreversible because row delete removes counted stock-taking data")
    if reasons:
        return _emit_refusal(ctx, reasons)

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete-row", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows/{row_id}",
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_rows(ctx=ctx, stock_taking_id=stock_taking_id)
    verification["verification_row_absent"] = _row_ids_absent(verification, [row_id])
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.delete_row.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification.get("verification_row_absent")),
        extra_receipt={"target_id": stock_taking_id, "target_row_id": row_id},
    )


def cmd_stock_taking_delete_rows(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    query_params = _build_filter_query(args)
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "delete-rows",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows",
        "query_params": query_params,
    }
    plan = _build_plan(
        action="delete-rows",
        selector=selector,
        payload_file=None,
        payload_obj=query_params,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-delete-rows", "irreversible"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}/rows"},
        rollback_notes="No generic rollback. Re-add the removed rows if they are still valid candidates.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.delete_rows.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    reasons: list[str] = []
    if not bool(ctx.get("yes")):
        reasons.append("Refused: rerun with --apply --yes after plan review")
    if not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: rerun with --ack-irreversible because row deletion removes counted stock-taking data")
    if reasons:
        return _emit_refusal(ctx, reasons)

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete-rows", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/rows",
        query_params=query_params or None,
        expect_json=True,
        expect_json_object=False,
    )
    verification = _verify_rows(ctx=ctx, stock_taking_id=stock_taking_id)
    expected_row_ids = _extract_row_ids(payload.get("body"))
    if expected_row_ids:
        verification["verification_row_ids_absent"] = _row_ids_absent(verification, expected_row_ids)
    verified_ok = bool(verification.get("ok")) and (
        not expected_row_ids or bool(verification.get("verification_row_ids_absent"))
    )
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.delete_rows.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=verified_ok,
        extra_receipt={"target_id": stock_taking_id, "target_row_ids": expected_row_ids},
    )


def cmd_stock_taking_release(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "release",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/release",
    }
    plan = _build_plan(
        action="release",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-release", "bookkeeping-finalize"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}"},
        rollback_notes="No generic rollback. Release completes the stock taking and adjusts stock amounts.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.release.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0
    if not bool(ctx.get("yes")):
        return _emit_refusal(ctx, ["Refused: release adjusts stock and bookkeeps the document; rerun with --apply --yes after plan review"])

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="release", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/release",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_taking_id=stock_taking_id)
    verification["verification_state"] = _stock_taking_state(verification.get("data"))
    verification["verification_completed_state"] = verification["verification_state"] == "completed"
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.release.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification.get("ok")) and bool(verification["verification_completed_state"]),
        extra_receipt={"target_id": stock_taking_id},
    )


def cmd_stock_taking_void(args: Any, ctx: dict[str, Any]) -> int:
    stock_taking_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "stock-taking",
        "id": stock_taking_id,
        "action": "void",
        "path": f"/api/warehouse/stocktaking-v1/{stock_taking_id}/void",
    }
    plan = _build_plan(
        action="void",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "warehouse-write", "stock-taking-void", "irreversible"],
        verification_plan={"type": "read-after-write", "path_template": "/api/warehouse/stocktaking-v1/{id}"},
        rollback_notes="No generic rollback. Void is the terminal reversal path for planning or started stock takings.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        ctx["audit"].write("stock_taking.void.plan", {"plan_out": plan_path})
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
        path=f"/api/warehouse/stocktaking-v1/{stock_taking_id}/void",
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_present(ctx=ctx, stock_taking_id=stock_taking_id)
    verification["verification_state"] = _stock_taking_state(verification.get("data"))
    verification["verification_voided_state"] = verification["verification_state"] == "voided"
    return _write_receipt_and_emit(
        ctx=ctx,
        audit_key="stock_taking.void.apply",
        selector=selector,
        payload=payload,
        verification=verification,
        plan=plan,
        verified_ok=bool(verification.get("ok")) and bool(verification["verification_voided_state"]),
        extra_receipt={"target_id": stock_taking_id},
    )
