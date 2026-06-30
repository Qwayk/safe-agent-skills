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


COMMAND_FAMILY = "bookings-waitlist"
BASE_PATH = "/bookings/v1/waitlist"


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string or @file path")
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


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _split_csv(raw: Any, *, field: str) -> list[str]:
    value = _coerce_non_empty_text(raw, field=field)
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise ValidationError(f"--{field} must include at least one value")
    return items


def _require_event_session_ack(args: Any) -> None:
    if not bool(getattr(args, "ack_event_session", False)):
        raise SafetyError("Refused: Waitlist writes require --ack-event-session because Wix currently limits Waitlist to sessions with type = EVENT")


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


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool,
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-bookings-waitlist-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot is captured for this Bookings Waitlist provider-response write.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary. Run list to inspect the waitlist state after live apply.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual through the Waitlist or Bookings APIs."},
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=COMMAND_FAMILY)


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
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
        "verification": {"ok": True, "type": "provider-response"},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot was available for this Bookings Waitlist write.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(*, method_name: str, path: str, params: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=auth["headers"],
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    _emit_success(method=method_name, auth_mode=auth["mode"], request={"method": "GET", "path": path, "params": params}, response=payload, ctx=ctx)
    return 0


def _run_write(
    *,
    method_name: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": "POST", "path": path, "body": body}
    plan_in = ctx.get("plan_in")
    apply_allowed = bool(ctx.get("apply")) and bool(ctx.get("yes")) and _should_apply(ctx, requires_ack=requires_ack)
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=proposed_changes,
            requires_ack=requires_ack,
        )
    if not apply_allowed:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth["mode"],
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=auth["headers"],
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(method=method_name, selector=selector, request=request, response=response, plan=loaded_plan, ctx=ctx)
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth["mode"],
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def cmd_bookings_waitlist_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        waiting_resources = _split_csv(getattr(args, "waiting_resources", None), field="waiting-resources")
        return _run_read(
            method_name=method,
            path=f"{BASE_PATH}/list",
            params={"waitingResources": waiting_resources},
            ctx=ctx,
        )
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_waitlist_register(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.register"
    try:
        _require_event_session_ack(args)
        body = _coerce_json_object(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/register",
            body=body,
            selector={"kind": "bookings-waitlist", "operation": "register"},
            proposed_changes=[{"operation": "register", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_waitlist_leave(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.leave"
    try:
        _require_event_session_ack(args)
        body = _coerce_json_object(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/leave",
            body=body,
            selector={"kind": "bookings-waitlist", "operation": "leave"},
            proposed_changes=[{"operation": "leave", "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_waitlist_book(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.book"
    try:
        _require_event_session_ack(args)
        body = _coerce_json_object(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/enroll",
            body=body,
            selector={"kind": "bookings-waitlist", "operation": "book"},
            proposed_changes=[{"operation": "book", "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)
