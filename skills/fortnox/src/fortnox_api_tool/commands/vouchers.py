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
    voucher = obj.get("Voucher")
    if not isinstance(voucher, dict):
        raise ValidationError("JSON file must contain a top-level Voucher object")
    return path, obj, voucher


def _extract_str_from_payload(voucher: dict[str, Any], key: str) -> str | None:
    raw = voucher.get(key)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _extract_financial_year_from_payload(voucher: dict[str, Any]) -> int | None:
    raw = voucher.get("FinancialYear")
    if raw is None:
        return None
    value = str(raw).strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _extract_voucher_from_response(body: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    voucher = body.get("Voucher")
    if not isinstance(voucher, dict):
        return None
    return voucher


def _extract_voucher_series_from_response(body: dict[str, Any] | None) -> str | None:
    voucher = _extract_voucher_from_response(body)
    if voucher is None:
        return None
    return _extract_str_from_payload(voucher, "VoucherSeries")


def _extract_voucher_number_from_response(body: dict[str, Any] | None) -> str | None:
    voucher = _extract_voucher_from_response(body)
    if voucher is None:
        return None
    return _extract_str_from_payload(voucher, "VoucherNumber")


def _extract_financial_year_from_response(body: dict[str, Any] | None) -> int | None:
    voucher = _extract_voucher_from_response(body)
    if voucher is None:
        return None
    return _extract_financial_year_from_payload(voucher)


def _build_query(financial_year: int | None) -> dict[str, int] | None:
    if financial_year is None:
        return None
    return {"financialyear": financial_year}


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


def _resolve_verification_keys(
    *,
    response_body: dict[str, Any] | None,
    voucher: dict[str, Any],
    requested_financial_year: int | None,
) -> tuple[str, str, int]:
    voucher_series = _extract_voucher_series_from_response(response_body) or _extract_str_from_payload(voucher, "VoucherSeries")
    voucher_number = _extract_voucher_number_from_response(response_body) or _extract_str_from_payload(voucher, "VoucherNumber")
    financial_year = (
        _extract_financial_year_from_response(response_body)
        or _extract_financial_year_from_payload(voucher)
        or requested_financial_year
    )
    if not voucher_series or not voucher_number or financial_year is None:
        raise ValidationError("Could not determine VoucherSeries, VoucherNumber, and FinancialYear for create verification")
    return voucher_series, voucher_number, financial_year


def _verify_present(*, ctx: dict[str, Any], voucher_series: str, voucher_number: str, financial_year: int) -> dict[str, Any]:
    path = f"/vouchers/{voucher_series}/{voucher_number}"
    query_params = _build_query(financial_year)
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


def cmd_vouchers_create(args: Any, ctx: dict[str, Any]) -> int:
    financial_year_arg = getattr(args, "financial_year", None)
    payload_file, payload_obj, voucher = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {
        "kind": "voucher",
        "action": "create",
        "path": "/vouchers",
        "financial_year": financial_year_arg,
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "voucher-create"],
        verification_plan={"type": "read-after-write", "path_template": "/vouchers/{VoucherSeries}/{VoucherNumber}"},
        rollback_notes="No generic rollback. Recreate or reverse the voucher explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("vouchers.create.plan", {"plan_out": plan_path, "financial_year": financial_year_arg})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path="/vouchers",
        query_params=_build_query(financial_year_arg),
        json_body=payload_obj,
        expect_json=True,
    )
    voucher_series, voucher_number, financial_year = _resolve_verification_keys(
        response_body=payload.get("body"),
        voucher=voucher,
        requested_financial_year=financial_year_arg,
    )
    verification = _verify_present(
        ctx=ctx,
        voucher_series=voucher_series,
        voucher_number=voucher_number,
        financial_year=financial_year,
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
        "target_voucher_series": voucher_series,
        "target_voucher_number": voucher_number,
        "target_financial_year": financial_year,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("vouchers.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
