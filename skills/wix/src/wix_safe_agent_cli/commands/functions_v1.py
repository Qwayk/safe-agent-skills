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


COMMAND_FAMILY = "functions-v1"
BASE_PATH = "/functions/v1/functions"


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
            "notes": "Functions V1 plans do not capture a full before-state snapshot in this slice.",
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


def _function_body(raw: Any, *, field: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field=field)
    body = dict(payload) if "function" in payload else {"function": payload}
    function = body.get("function")
    if not isinstance(function, dict) or not function:
        raise ValidationError(f"--{field} must include a non-empty function object")
    return body, function


def _function_id_and_revision(function: dict[str, Any], *, field: str) -> str:
    function_id = _coerce_text(function.get("id"), field=f"{field} function.id")
    _coerce_text(function.get("revision"), field=f"{field} function.revision")
    return function_id


def cmd_functions_v1_create(args, ctx) -> int:
    method = "functionsV1.createFunction"
    try:
        body, function = _function_body(args.function_json, field="function-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"function": function},
            proposed_changes=[{"operation": "create-function", "function": function}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-functions-create"],
            verification_notes="Inspect the provider response, then use functions-v1 get or query to verify the function.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_get(args, ctx) -> int:
    method = "functionsV1.getFunction"
    try:
        function_id = _coerce_text(args.function_id, field="function-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{function_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_update(args, ctx) -> int:
    method = "functionsV1.updateFunction"
    try:
        body, function = _function_body(args.function_json, field="function-json")
        function_id = _function_id_and_revision(function, field="function-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{function_id}",
            body=body,
            selector={"function": function},
            proposed_changes=[{"operation": "update-function", "function": function}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-functions-update", "requires-current-revision"],
            verification_notes="Inspect the provider response, then use functions-v1 get to verify the function.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_delete(args, ctx) -> int:
    method = "functionsV1.deleteFunction"
    try:
        function_id = _coerce_text(args.function_id, field="function-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{function_id}",
            body=None,
            selector={"functionId": function_id},
            proposed_changes=[{"operation": "delete-function", "functionId": function_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-functions-delete", "irreversible"],
            verification_notes="Inspect the provider response, then use functions-v1 get or query to confirm removal.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_query(args, ctx) -> int:
    method = "functionsV1.queryFunctions"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_bulk_update_tags(args, ctx) -> int:
    method = "functionsV1.bulkUpdateFunctionTags"
    try:
        body = _read_json_arg(args.tags_json, field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/functions/v1/bulk/functions/bulk-update-tags",
            body=body,
            selector={"bulkUpdateTags": body},
            proposed_changes=[{"operation": "bulk-update-function-tags", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-functions-bulk-update-tags"],
            verification_notes="Inspect the provider response, then query the targeted functions to verify tags.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_functions_v1_bulk_update_tags_by_filter(args, ctx) -> int:
    method = "functionsV1.bulkUpdateFunctionTagsByFilter"
    try:
        body = _read_json_arg(args.tags_json, field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/functions/v1/bulk/functions/update-tags-by-filter",
            body=body,
            selector={"bulkUpdateTagsByFilter": body},
            proposed_changes=[{"operation": "bulk-update-function-tags-by-filter", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-functions-bulk-update-tags-by-filter", "empty-filter-can-update-all-functions"],
            verification_notes="Inspect the provider response, then query matching functions or the returned job result when available.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
