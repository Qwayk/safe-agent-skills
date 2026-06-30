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


COMMAND_FAMILY = "payment-link-payments"
BASE_PATH = "/payment-links/v1/payment-link-payments"


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
        params=None,
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
    path: str,
    body: dict[str, Any],
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method="POST", path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    request = {"method": "POST", "path": path, "body": body}
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": ["wix-payment-link-payment-issue-receipt", "creates-get-paid-receipt"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Payment Link Payments plans do not capture a full before-state snapshot in this slice.",
        },
        "proposed_changes": [{"operation": "issue-payment-link-payment-receipt", **selector}],
        "verification_plan": {
            "type": "provider-response-plus-query",
            "notes": "Inspect the provider response, then query or search payment link payments for the receiptId.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Receipt recovery is manual only."},
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


def cmd_payment_link_payments_query(args, ctx) -> int:
    method = "paymentLinkPayments.queryPaymentLinkPayments"
    try:
        raw_query = getattr(args, "query_json", None)
        body = _read_json_arg(raw_query, field="query-json", allow_empty=True) if raw_query is not None else {}
        return _run_read(method_name=method, path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_link_payments_search(args, ctx) -> int:
    method = "paymentLinkPayments.searchPaymentLinkPayments"
    try:
        raw_search = getattr(args, "search_json", None)
        body = _read_json_arg(raw_search, field="search-json", allow_empty=True) if raw_search is not None else {}
        return _run_read(method_name=method, path=f"{BASE_PATH}/search", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_link_payments_issue_receipt(args, ctx) -> int:
    method = "paymentLinkPayments.issueReceipt"
    try:
        payment_id = _coerce_text(args.payment_link_payment_id, field="payment-link-payment-id")
        selector = {"paymentLinkPaymentId": payment_id}
        path = f"{BASE_PATH}/{payment_id}/issue-receipt"
        request = {"method": "POST", "path": path}
        auth = _resolve_auth(ctx)
        plan = _build_plan(method_name=method, request=request, selector=selector, ctx=ctx)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method):
            out = {"ok": True, "dry_run": True, "method": method, "auth_mode": auth["mode"], "plan": plan}
            if not ctx.get("apply") and ctx.get("plan_out"):
                out["plan_out"] = write_json_file(ctx["plan_out"], plan)
            ctx["audit"].write(f"{method}.plan", out)
            ctx["out"].emit(out)
            return 0
        loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method, expected_selector=selector, ctx=ctx)
        response = _request_json(method="POST", path=path, headers=auth["headers"], json_body=None, ctx=ctx)
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": method,
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": {
                "ok": True,
                "type": "provider-response-plus-query",
                "notes": "Provider accepted the receipt request. Query or search payment link payments to verify receiptId.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
            "recovery": {"automatic": False, "notes": "Recovery is manual only."},
        }
        out = {"ok": True, "dry_run": False, "method": method, "auth_mode": auth["mode"], "receipt": receipt}
        if ctx.get("receipt_out"):
            out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
        ctx["audit"].write(f"{method}.receipt", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
