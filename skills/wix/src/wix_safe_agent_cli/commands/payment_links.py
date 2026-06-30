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


COMMAND_FAMILY = "payment-links"
BASE_PATH = "/payment-links/v1/payment-links"
BULK_BASE_PATH = "/payment-links/v1/bulk/payment-links"


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
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _payment_link_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field="payment-link-json")
    body = dict(payload) if "paymentLink" in payload else {"paymentLink": payload}
    payment_link = body.get("paymentLink")
    if not isinstance(payment_link, dict) or not payment_link:
        raise ValidationError("--payment-link-json must include a non-empty paymentLink object")
    return body, payment_link


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
            "notes": "Payment Links plans do not capture a full before-state snapshot in this slice.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
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
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
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


def cmd_payment_links_create(args, ctx) -> int:
    method = "paymentLinks.createPaymentLink"
    try:
        body, payment_link = _payment_link_body(args.payment_link_json)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"paymentLink": payment_link},
            proposed_changes=[{"operation": "create-payment-link", "paymentLink": payment_link}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-payment-link-create", "payment-values-immutable-after-creation"],
            verification_notes="Inspect the provider response, then use payment-links get to verify the created link.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_get(args, ctx) -> int:
    method = "paymentLinks.getPaymentLink"
    try:
        payment_link_id = _coerce_text(args.payment_link_id, field="payment-link-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{payment_link_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_delete(args, ctx) -> int:
    method = "paymentLinks.deletePaymentLink"
    try:
        payment_link_id = _coerce_text(args.payment_link_id, field="payment-link-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{payment_link_id}",
            body=None,
            selector={"paymentLinkId": payment_link_id},
            proposed_changes=[{"operation": "delete-payment-link", "paymentLinkId": payment_link_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-payment-link-delete", "irreversible"],
            verification_notes="Inspect the provider response, then use payment-links get or query to confirm removal.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_query(args, ctx) -> int:
    method = "paymentLinks.queryPaymentLinks"
    try:
        raw_query = getattr(args, "query_json", None)
        body = _read_json_arg(raw_query, field="query-json", allow_empty=True) if raw_query is not None else {}
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_search(args, ctx) -> int:
    method = "paymentLinks.searchPaymentLinks"
    try:
        raw_search = getattr(args, "search_json", None)
        body = _read_json_arg(raw_search, field="search-json", allow_empty=True) if raw_search is not None else {}
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/search", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _link_action(
    *,
    args: Any,
    ctx: dict[str, Any],
    method_name: str,
    action: str,
    request_suffix: str,
    requires_ack: bool,
    risk_reasons: list[str],
    body: dict[str, Any] | None = None,
    verification_notes: str,
) -> int:
    payment_link_id = _coerce_text(args.payment_link_id, field="payment-link-id")
    return _run_write(
        method_name=method_name,
        http_method="POST",
        path=f"{BASE_PATH}/{payment_link_id}/{request_suffix}",
        body=body,
        selector={"paymentLinkId": payment_link_id},
        proposed_changes=[{"operation": action, "paymentLinkId": payment_link_id, "body": body}],
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )


def cmd_payment_links_activate(args, ctx) -> int:
    method = "paymentLinks.activatePaymentLink"
    try:
        return _link_action(
            args=args,
            ctx=ctx,
            method_name=method,
            action="activate-payment-link",
            request_suffix="activate",
            requires_ack=True,
            risk_reasons=["wix-payment-link-activate", "link-will-accept-payments"],
            verification_notes="Inspect the provider response, then use payment-links get to verify ACTIVE status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_deactivate(args, ctx) -> int:
    method = "paymentLinks.deactivatePaymentLink"
    try:
        return _link_action(
            args=args,
            ctx=ctx,
            method_name=method,
            action="deactivate-payment-link",
            request_suffix="deactivate",
            requires_ack=True,
            risk_reasons=["wix-payment-link-deactivate", "link-will-stop-accepting-payments"],
            verification_notes="Inspect the provider response, then use payment-links get to verify INACTIVE status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_initiate_payment(args, ctx) -> int:
    method = "paymentLinks.initiatePayment"
    try:
        return _link_action(
            args=args,
            ctx=ctx,
            method_name=method,
            action="initiate-payment",
            request_suffix="initiate-payment",
            requires_ack=False,
            risk_reasons=["wix-payment-link-initiate-payment", "creates-ecommerce-checkout"],
            verification_notes="Inspect the provider response for the returned checkout URL.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_send(args, ctx) -> int:
    method = "paymentLinks.sendPaymentLink"
    try:
        body = _read_json_arg(args.send_json, field="send-json")
        return _link_action(
            args=args,
            ctx=ctx,
            method_name=method,
            action="send-payment-link",
            request_suffix="send",
            requires_ack=True,
            risk_reasons=["wix-payment-link-send", "can-notify-up-to-50-recipients"],
            body=body,
            verification_notes="Inspect the provider response, then use payment-links get to review recipients and status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_set_note(args, ctx) -> int:
    method = "paymentLinks.setNote"
    try:
        body = _read_json_arg(args.note_json, field="note-json")
        return _link_action(
            args=args,
            ctx=ctx,
            method_name=method,
            action="set-payment-link-note",
            request_suffix="set-note",
            requires_ack=False,
            risk_reasons=["wix-payment-link-set-note"],
            body=body,
            verification_notes="Inspect the provider response, then use payment-links get to verify the note.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_update_extended_fields(args, ctx) -> int:
    method = "paymentLinks.updateExtendedFields"
    try:
        payment_link_id = _coerce_text(args.payment_link_id, field="payment-link-id")
        body = _read_json_arg(args.extended_fields_json, field="extended-fields-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{payment_link_id}/update-extended-fields",
            body=body,
            selector={"paymentLinkId": payment_link_id},
            proposed_changes=[{"operation": "update-payment-link-extended-fields", "paymentLinkId": payment_link_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-payment-link-update-extended-fields"],
            verification_notes="Inspect the provider response, then use payment-links get to verify extended fields.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_bulk_update_tags(args, ctx) -> int:
    method = "paymentLinks.bulkUpdatePaymentLinkTags"
    try:
        body = _read_json_arg(args.tags_json, field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk-update-tags",
            body=body,
            selector={"scope": "bulk-update-payment-link-tags", "body": body},
            proposed_changes=[{"operation": "bulk-update-payment-link-tags", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-payment-links-bulk-update-tags"],
            verification_notes="Inspect the provider response, then use payment-links query to verify tag changes.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_payment_links_bulk_update_tags_by_filter(args, ctx) -> int:
    method = "paymentLinks.bulkUpdatePaymentLinkTagsByFilter"
    try:
        body = _read_json_arg(args.tags_json, field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/update-tags-by-filter",
            body=body,
            selector={"scope": "bulk-update-payment-link-tags-by-filter", "body": body},
            proposed_changes=[{"operation": "bulk-update-payment-link-tags-by-filter", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-payment-links-bulk-update-tags-by-filter", "empty-filter-can-update-all-payment-links"],
            verification_notes="Provider returns a job ID. Track it with the named async-job command if available, then query payment links to verify tag changes.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
