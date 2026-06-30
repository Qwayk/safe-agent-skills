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


COMMAND_FAMILY = "receipts"
BASE_PATH = "/receipts/v1/receipts"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload and not allow_empty:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    params: dict[str, Any] | None = None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
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
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, params=params, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    if params:
        request["params"] = params
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _receipt_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field="receipt-json")
    body = dict(payload) if "receipt" in payload else {"receipt": payload}
    receipt = body.get("receipt")
    if not isinstance(receipt, dict) or not receipt:
        raise ValidationError("--receipt-json must include a non-empty receipt object")
    return body, receipt


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Receipts plans do not capture a full before-state snapshot in this slice.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response-plus-readback", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual only."},
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
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


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": {"ok": True, "type": "provider-response-plus-readback", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.receipt", out)
    ctx["out"].emit(out)
    return 0


def cmd_receipts_create(args, ctx) -> int:
    method = "receipts.createReceipt"
    try:
        body, receipt = _receipt_body(args.receipt_json)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"receipt": receipt},
            proposed_changes=[{"operation": "create-receipt", "receipt": receipt}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-receipt-create", "only-one-receipt-per-transaction", "receipts-cannot-be-deleted"],
            verification_notes="Inspect the provider response, then use receipts get to verify the generated receipt and document status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_get(args, ctx) -> int:
    method = "receipts.getReceipt"
    try:
        receipt_id = _coerce_text(args.receipt_id, field="receipt-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{receipt_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_query(args, ctx) -> int:
    method = "receipts.queryReceipts"
    try:
        raw_query = getattr(args, "query_json", None)
        body = _read_json_arg(raw_query, field="query-json", allow_empty=True) if raw_query is not None else {}
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_get_latest_number(args, ctx) -> int:
    method = "receipts.getLatestReceiptNumber"
    try:
        raw_prefix = getattr(args, "prefix", None)
        params = {"prefix": _coerce_text(raw_prefix, field="prefix")} if raw_prefix else None
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/get-latest-number", body=None, params=params, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_regenerate_document(args, ctx) -> int:
    method = "receipts.regenerateReceiptDocument"
    try:
        receipt_id = _coerce_text(args.receipt_id, field="receipt-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{receipt_id}/regenerate-receipt-document",
            body=None,
            selector={"receiptId": receipt_id},
            proposed_changes=[{"operation": "regenerate-receipt-document", "receiptId": receipt_id}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-receipt-document-regenerate", "for-failed-or-stuck-documents"],
            verification_notes="Inspect the provider response, wait if needed, then use receipts get to verify document status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_send_email(args, ctx) -> int:
    method = "receipts.sendReceiptEmail"
    try:
        receipt_id = _coerce_text(args.receipt_id, field="receipt-id")
        raw_send = getattr(args, "send_json", None)
        body = _read_json_arg(raw_send, field="send-json", allow_empty=True) if raw_send is not None else {}
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{receipt_id}/send-email",
            body=body,
            selector={"receiptId": receipt_id},
            proposed_changes=[{"operation": "send-receipt-email", "receiptId": receipt_id, "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-receipt-send-email", "customer-email-notification"],
            verification_notes="Inspect the provider response and, when possible, use receipts get to verify receipt state.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_update_extended_fields(args, ctx) -> int:
    method = "receipts.updateExtendedFields"
    try:
        receipt_id = _coerce_text(args.receipt_id, field="receipt-id")
        body = _read_json_arg(args.extended_fields_json, field="extended-fields-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{receipt_id}/update-extended-fields",
            body=body,
            selector={"receiptId": receipt_id},
            proposed_changes=[{"operation": "update-receipt-extended-fields", "receiptId": receipt_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-receipt-update-extended-fields", "does-not-increment-revision"],
            verification_notes="Inspect the provider response, then use receipts get to verify extended fields.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
