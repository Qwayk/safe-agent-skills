from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "email-subscriptions"
BASE_PATH = "/email-marketing/v1/email-subscriptions"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_VALID_STATUSES = {"UNKNOWN_SUBSCRIPTION_STATUS", "NOT_SET", "SUBSCRIBED", "UNSUBSCRIBED"}


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    if raw is None and allow_empty:
        return {}
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


def _coerce_email(raw: Any, *, field: str = "email") -> str:
    value = _coerce_text(raw, field=field)
    if not _EMAIL_RE.fullmatch(value):
        raise ValidationError(f"--{field} must be a valid email address")
    return value


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
    json_body: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
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


def _run_read(*, method_name: str, path: str, body: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method="POST", path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": "POST", "path": path, "body": body},
        "response": response,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": {"method": "POST", "path": path, "body": body},
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Email Subscriptions plans in this slice do not capture full before-state.",
        },
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use email-subscriptions query to inspect provider state.",
        },
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> None:
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


def _run_write(
    *,
    method_name: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    plan = _build_plan(
        method_name=method_name,
        path=path,
        body=body,
        selector=selector,
        ctx=ctx,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method="POST", path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": "POST", "path": path, "body": body},
        "response": response,
        "verified": {"type": "provider-response", "notes": verification_notes},
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def _query_body(raw: Any) -> dict[str, Any]:
    body = _read_object(raw, field="query-json", allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def _subscription_from_payload(body: dict[str, Any], *, field: str) -> dict[str, Any]:
    subscription = body.get("emailSubscription") or body.get("subscription")
    if not isinstance(subscription, dict):
        subscription = body if "email" in body else None
    if not isinstance(subscription, dict):
        raise ValidationError(f"--{field} must include emailSubscription")
    email = _coerce_email(subscription.get("email"), field=f"{field}.email")
    status = subscription.get("subscriptionStatus")
    if status is not None:
        status = _coerce_text(status, field=f"{field}.subscriptionStatus")
        if status not in _VALID_STATUSES:
            raise ValidationError(f"--{field}.subscriptionStatus must be a valid email subscription status")
    normalized = dict(subscription)
    normalized["email"] = email
    if status is not None:
        normalized["subscriptionStatus"] = status
    return normalized


def _upsert_body(raw: Any) -> dict[str, Any]:
    body = _read_object(raw, field="subscription-json")
    subscription = _subscription_from_payload(body, field="subscription-json")
    return {"emailSubscription": subscription}


def _bulk_upsert_body(raw: Any) -> dict[str, Any]:
    body = _read_object(raw, field="subscriptions-json")
    subscriptions = body.get("emailSubscriptions") or body.get("subscriptions")
    if not isinstance(subscriptions, list) or not subscriptions:
        raise ValidationError("--subscriptions-json must include a non-empty emailSubscriptions array")
    if len(subscriptions) > 100:
        raise ValidationError("--subscriptions-json supports at most 100 email subscriptions")
    normalized = []
    for item in subscriptions:
        if not isinstance(item, dict):
            raise ValidationError("--subscriptions-json.emailSubscriptions entries must be JSON objects")
        normalized.append(_subscription_from_payload(item, field="subscriptions-json.emailSubscriptions"))
    return {"emailSubscriptions": normalized}


def _unsubscribe_link_body(args: Any) -> dict[str, Any]:
    if getattr(args, "request_json", None):
        body = _read_object(args.request_json, field="request-json")
    else:
        body = {"email": _coerce_email(args.email)}
    if "email" in body:
        body["email"] = _coerce_email(body["email"])
    else:
        raise ValidationError("--request-json must include email")
    return body


def cmd_email_subscriptions_query(args, ctx) -> int:
    method = "email-subscriptions.query"
    try:
        return _run_read(method_name=method, path=f"{BASE_PATH}/query", body=_query_body(args.query_json), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_email_subscriptions_upsert(args, ctx) -> int:
    method = "email-subscriptions.upsert"
    try:
        body = _upsert_body(args.subscription_json)
        return _run_write(
            method_name=method,
            path=BASE_PATH,
            body=body,
            selector={"email": body["emailSubscription"]["email"]},
            ctx=ctx,
            risk_reasons=["email-subscription-status-change"],
            verification_notes="Inspect provider response, then use email-subscriptions query to verify the saved subscription.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_email_subscriptions_bulk_upsert(args, ctx) -> int:
    method = "email-subscriptions.bulk-upsert"
    try:
        body = _bulk_upsert_body(args.subscriptions_json)
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/bulk",
            body=body,
            selector={"emails": [item["email"] for item in body["emailSubscriptions"]]},
            ctx=ctx,
            risk_reasons=["bulk-email-subscription-status-change"],
            verification_notes="Inspect provider response, then use email-subscriptions query to verify the saved subscriptions.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_email_subscriptions_generate_unsubscribe_link(args, ctx) -> int:
    method = "email-subscriptions.generate-unsubscribe-link"
    try:
        body = _unsubscribe_link_body(args)
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/unsubscribe-link",
            body=body,
            selector={"email": body["email"]},
            ctx=ctx,
            risk_reasons=["unsubscribe-link-generation"],
            verification_notes="Inspect provider response. The actual unsubscribe status changes only if the recipient uses the link.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
