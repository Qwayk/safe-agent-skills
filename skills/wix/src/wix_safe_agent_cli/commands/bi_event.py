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


def _read_json_arg(raw: Any, field: str) -> Any:
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

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_event_data(raw_json: Any) -> dict[str, Any] | None:
    if raw_json is None:
        return None
    payload = _read_json_arg(raw_json, field="event-data-json")
    if not isinstance(payload, dict):
        raise ValidationError("--event-data-json must be a JSON object")
    return payload


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
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
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _build_selector(*, event_name: str, event_data: dict[str, Any] | None) -> dict[str, Any]:
    selector = {
        "kind": "wix-bi-event",
        "operation": "send",
        "event_name": event_name,
    }
    if event_data is not None:
        selector["event_data"] = event_data
    return selector


def _build_request_body(*, event_name: str, event_data: dict[str, Any] | None) -> dict[str, Any]:
    body = {"eventName": event_name}
    if event_data is not None:
        body["eventData"] = event_data
    return body


def _build_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "bi-event.send",
        "risk_level": "medium",
        "risk_reasons": ["wix-app-write", "analytics-write"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": {},
        },
        "proposed_changes": [
            {
                "operation": "send",
                "event_name": selector["event_name"],
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify the POST returns a 2xx response from /apps/v1/bi-event.",
        },
        "rollback": {"supported": False, "notes": "No rollback exists for a sent BI event."},
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


def _should_apply(ctx: dict[str, Any]) -> bool:
    review_ctx = dict(ctx)
    review_ctx["enforce_reviewed_plan"] = True
    return reviewed_plan_apply_requested(review_ctx, command_label="bi-event")


def _build_receipt(
    *,
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "bi-event.send",
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": False,
            "notes": "No before-state snapshot exists for a BI event send.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only. Sent BI events cannot be unsent.",
        },
    }


def cmd_bi_event_send(args, ctx) -> int:
    try:
        event_name = _coerce_non_empty_text(getattr(args, "event_name", None), field="event-name")
        event_data = _coerce_event_data(getattr(args, "event_data_json", None))
        selector = _build_selector(event_name=event_name, event_data=event_data)
        request = {
            "method": "POST",
            "path": "/apps/v1/bi-event",
            "body": _build_request_body(event_name=event_name, event_data=event_data),
        }

        if not _should_apply(ctx):
            plan = _build_plan(request=request, selector=selector, ctx=ctx)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "bi-event.send",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        plan = _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="bi-event.send", expected_selector=selector, ctx=ctx)
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="bi-event",
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth["headers"],
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "provider-response",
            "path": request["path"],
            "method": "POST",
            "notes": "BI event send returned a successful provider response.",
        }
        receipt = _build_receipt(request=request, response=response, verification=verification, plan=plan, ctx=ctx)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "bi-event.send",
            "auth_mode": auth["mode"],
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "bi-event.send",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "bi-event.send"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "bi-event.send"})
        return 1
