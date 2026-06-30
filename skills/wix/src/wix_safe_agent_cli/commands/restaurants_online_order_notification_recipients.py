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


COMMAND_FAMILY = "restaurants-online-order-notification-recipients"
BASE_PATH = "/rest-notification-recipients/v1"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
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
    if not allow_empty and not payload:
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
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
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
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
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
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


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
        "state_capture": {"before_state_available": False, "notes": "Restaurants Online Orders Notification Recipients plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with restaurants-online-order-notification-recipients get/query and the Wix dashboard when needed."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
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
    requires_ack: bool = False,
    risk_reasons: list[str] | None = None,
    verification_notes: str = "Provider response confirms the Restaurants Online Orders Notification Recipients request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-restaurants-online-order-notification-recipients-write"],
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
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
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def _notification_recipients_path(recipient_id: str | None = None) -> str:
    base = f"{BASE_PATH}/recipients"
    if recipient_id is None:
        return base
    return f"{base}/{recipient_id}"


def _require_revision(body: dict[str, Any], *, field: str) -> None:
    recipient = body.get("recipient")
    if not isinstance(recipient, dict):
        raise ValidationError(f"--{field} must include a recipient object")
    if not str(recipient.get("revision") or "").strip():
        raise ValidationError(f"--{field} recipient.revision is required by Wix")


def _require_bulk_revisions(body: dict[str, Any], *, field: str) -> None:
    notification_recipients = body.get("recipients")
    if not isinstance(notification_recipients, list) or not notification_recipients:
        raise ValidationError(f"--{field} must include a non-empty recipients array")
    for index, entry in enumerate(notification_recipients):
        if not isinstance(entry, dict) or not str(entry.get("revision") or "").strip():
            raise ValidationError(f"--{field} recipients[{index}].revision is required by Wix")


def _validate_tag_request(body: dict[str, Any], *, field: str, by_filter: bool) -> None:
    assign = body.get("assignTags") or body.get("assign")
    unassign = body.get("unassignTags") or body.get("unassign")
    if assign is not None and not isinstance(assign, list):
        raise ValidationError(f"--{field} assignTags must be a JSON array when provided")
    if unassign is not None and not isinstance(unassign, list):
        raise ValidationError(f"--{field} unassignTags must be a JSON array when provided")
    if assign == [] and unassign == []:
        raise ValidationError(f"--{field} cannot have both assignTags and unassignTags empty")
    if by_filter:
        return
    ids = body.get("ids")
    recipient_ids = body.get("recipientIds")
    if ids is not None:
        if not isinstance(ids, list) or not ids:
            raise ValidationError(f"--{field} must include a non-empty ids array")
    if recipient_ids is not None:
        if not isinstance(recipient_ids, list) or not recipient_ids:
            raise ValidationError(f"--{field} must include a non-empty recipientIds array")
    if ids is None and recipient_ids is None:
        raise ValidationError(f"--{field} must include a non-empty ids or recipientIds array")


def cmd_restaurants_online_order_notification_recipients_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        recipient_id = _coerce_text(getattr(args, "recipient_id", None), field="recipient-id")
        return _run_read(method_name=method, http_method="GET", path=_notification_recipients_path(recipient_id), params=None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{_notification_recipients_path()}/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "recipient_json", None), field="recipient-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=_notification_recipients_path(),
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-notification-recipient", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-create"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _read_json_arg(getattr(args, "recipients_json", None), field="recipients-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/recipients",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create-notification-recipients", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-bulk-create", "multi-notification-recipient-change"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        recipient_id = _coerce_text(getattr(args, "recipient_id", None), field="recipient-id")
        body = _read_json_arg(getattr(args, "recipient_json", None), field="recipient-json")
        _require_revision(body, field="recipient-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=_notification_recipients_path(recipient_id),
            body=body,
            selector={"kind": COMMAND_FAMILY, "recipient_id": recipient_id, "operation": "update"},
            proposed_changes=[{"operation": "update-notification-recipient", "recipient_id": recipient_id, "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-update", "requires-current-revision"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "recipients_json", None), field="recipients-json")
        _require_bulk_revisions(body, field="recipients-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/recipients/update",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update-notification-recipients", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-bulk-update", "requires-current-revisions"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        recipient_id = _coerce_text(getattr(args, "recipient_id", None), field="recipient-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=_notification_recipients_path(recipient_id),
            body=None,
            selector={"kind": COMMAND_FAMILY, "recipient_id": recipient_id, "operation": "delete"},
            proposed_changes=[{"operation": "delete-notification-recipient", "recipient_id": recipient_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-delete", "deletes-notification-recipient"],
            verification_notes="Provider response confirms the Notification Recipient delete request was accepted; verify with restaurants-online-order-notification-recipients get/query.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _read_json_arg(getattr(args, "recipients_json", None), field="recipients-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/recipients/delete",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete"},
            proposed_changes=[{"operation": "bulk-delete-notification-recipients", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-bulk-delete", "deletes-notification-recipients"],
            verification_notes="Provider response confirms the bulk Notification Recipients delete request was accepted; verify with restaurants-online-order-notification-recipients query.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        _validate_tag_request(body, field="tags-json", by_filter=False)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/recipients/update-tags",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-tags"},
            proposed_changes=[{"operation": "bulk-update-notification-recipient-tags", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-online-order-notification-recipient-bulk-update-tags", "multi-notification-recipient-tag-change"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_online_order_notification_recipients_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        _validate_tag_request(body, field="filter-json", by_filter=True)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/recipients/update-tags-by-filter",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-tags-by-filter"},
            proposed_changes=[{"operation": "bulk-update-notification-recipient-tags-by-filter", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[
                "wix-restaurants-online-order-notification-recipient-bulk-update-tags-by-filter",
                "empty-filter-can-update-all-notification-recipients",
                "large-scale-tag-change",
            ],
            verification_notes="Provider response confirms the bulk notification recipients tag update-by-filter request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
