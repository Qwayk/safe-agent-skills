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


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str) -> Any | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValidationError(f"--{field} file is empty: {path}")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_dynamic_values(raw: Any) -> dict[str, dict[str, Any]] | None:
    values = _read_json_arg(raw, field="dynamic-values-json")
    if values is None:
        return None
    if not isinstance(values, dict):
        raise ValidationError("--dynamic-values-json must be a JSON object")

    normalized: dict[str, dict[str, Any]] = {}
    for placeholder_raw, payload in values.items():
        if not isinstance(placeholder_raw, str):
            raise ValidationError("--dynamic-values-json keys must be placeholder strings")

        placeholder = placeholder_raw.strip()
        if not placeholder:
            raise ValidationError("--dynamic-values-json cannot use an empty placeholder")

        if not isinstance(payload, dict):
            raise ValidationError(f"--dynamic-values-json[{placeholder}] must be an object")

        text = payload.get("text")
        if not isinstance(text, str):
            raise ValidationError(f"--dynamic-values-json[{placeholder}].text must be a string")

        text = text.strip()
        if not text:
            raise ValidationError(f"--dynamic-values-json[{placeholder}].text cannot be empty")

        normalized[placeholder] = {"text": text}

    return normalized


def _coerce_notify_json(raw: Any) -> dict[str, Any] | None:
    values = _read_json_arg(raw, field="notify-json")
    if values is None:
        return None
    if not isinstance(values, dict):
        raise ValidationError("--notify-json must be a JSON object")
    return values


def _normalize_request(
    *,
    notification_template_id: str,
    dynamic_values: dict[str, dict[str, Any]] | None,
    notify_json: dict[str, Any] | None,
) -> dict[str, Any]:
    if notify_json is not None:
        if dynamic_values is not None:
            raise ValidationError("Use either --notify-json or --dynamic-values-json, not both")

        body = dict(notify_json)
    else:
        body = {"notificationTemplateId": notification_template_id}
        if dynamic_values is not None:
            body["dynamicValues"] = dynamic_values

    return {
        "method": "POST",
        "path": "/notifications/v3/notify",
        "body": body,
    }


def _coerce_request_template_id(*, request: dict[str, Any], field: str) -> str:
    template_id = request.get("body", {}).get("notificationTemplateId")
    if template_id is None:
        raise ValidationError(f"Missing notificationTemplateId in --{field}")
    if not isinstance(template_id, str):
        raise ValidationError("notificationTemplateId must be a string")
    template_id = template_id.strip()
    if not template_id:
        raise ValidationError("notificationTemplateId cannot be empty")
    return template_id


def _resolve_notifications_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="notifications",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _build_selector(
    *,
    notification_template_id: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kind": "wix-notification",
        "operation": "notify",
        "notificationTemplateId": notification_template_id,
        "body_signature": json.dumps(request.get("body", {}), sort_keys=True),
    }


def _build_plan(*, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "notifications.notify",
        "risk_level": "medium",
        "risk_reasons": ["notification-send"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
            "up to 100,000 calls per month per site",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "note": "No snapshot is available for notification send flow.",
        },
        "proposed_changes": [
            {
                "operation": "send-notification",
                "templateId": selector.get("notificationTemplateId"),
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "No full delivery proof is available from this endpoint; response only confirms the notificationBatchId",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
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
        raise SafetyError("Refused: plan missing baseline")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="notifications")


def _verify_response(*, response: dict[str, Any]) -> dict[str, Any]:
    batch_id = str(response.get("notificationBatchId") or "").strip()
    if not batch_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": (
                "Response is missing notificationBatchId. This endpoint only returns a batch id and does not verify delivery "
                "to recipients."
            ),
            "response": response,
        }

    return {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider accepted the request and returned notificationBatchId; delivery proof is not available here.",
        "notificationBatchId": batch_id,
        "response": response,
    }


def _build_receipt(
    *,
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "notifications.notify",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_notifications_notify(args, ctx) -> int:
    try:
        template_id_arg = _coerce_required_text(getattr(args, "notification_template_id", None), field="notification-template-id")
        dynamic_values = _coerce_dynamic_values(getattr(args, "dynamic_values_json", None))
        notify_json = _coerce_notify_json(getattr(args, "notify_json", None))

        request = _normalize_request(
            notification_template_id=template_id_arg,
            dynamic_values=dynamic_values,
            notify_json=notify_json,
        )
        template_id = _coerce_request_template_id(request=request, field="notification-template-id")
        selector = _build_selector(notification_template_id=template_id, request=request)

        auth_headers, auth_mode = _resolve_notifications_auth(ctx=ctx)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="notifications.notify",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(request=request, selector=selector, ctx=ctx)

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "notifications.notify",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="notifications.notify",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        response = _request_json(
            method=request["method"],
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = _verify_response(response=response)
        receipt = _build_receipt(
            request=request,
            response=response,
            verification=verification,
            selector=selector,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "notifications.notify",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "notifications.notify",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "dry_run": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "notifications.notify",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "dry_run": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "notifications.notify",
        }
        ctx["out"].emit(out)
        return 1
