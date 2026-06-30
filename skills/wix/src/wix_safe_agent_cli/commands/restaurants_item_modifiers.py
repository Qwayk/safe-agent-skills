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


COMMAND_FAMILY = "restaurants-item-modifiers"
BASE_PATH = "/restaurants/item-modifiers/v1"


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
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
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
    if params:
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
        "state_capture": {"before_state_available": False, "notes": "Restaurants Item Modifiers plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with restaurants-item-modifiers get/list and the Wix dashboard when needed."},
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
    verification_notes: str = "Provider response confirms the Restaurants Item Modifiers request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-restaurants-item-modifier-write"],
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
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def _modifiers_path(modifier_id: str | None = None) -> str:
    if modifier_id is None:
        return f"{BASE_PATH}/modifiers"
    return f"{BASE_PATH}/modifiers/{modifier_id}"


def _require_revision(body: dict[str, Any], *, field: str) -> None:
    modifier = body.get("modifier")
    if not isinstance(modifier, dict):
        raise ValidationError(f"--{field} must include a modifier object")
    if not str(modifier.get("revision") or "").strip():
        raise ValidationError(f"--{field} modifier.revision is required by Wix")


def _require_bulk_revisions(body: dict[str, Any], *, field: str) -> None:
    modifiers = body.get("modifiers")
    if not isinstance(modifiers, list) or not modifiers:
        raise ValidationError(f"--{field} must include a non-empty modifiers array")
    for index, entry in enumerate(modifiers):
        modifier = entry.get("modifier") if isinstance(entry, dict) else None
        if not isinstance(modifier, dict) or not str(modifier.get("revision") or "").strip():
            raise ValidationError(f"--{field} modifiers[{index}].modifier.revision is required by Wix")


def cmd_restaurants_item_modifiers_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=_modifiers_path(), params=params or None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        modifier_id = _coerce_text(getattr(args, "modifier_id", None), field="modifier-id")
        return _run_read(method_name=method, http_method="GET", path=_modifiers_path(modifier_id), params=None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{_modifiers_path()}/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _read_json_arg(getattr(args, "filter_json", "{}"), field="filter-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{_modifiers_path()}/count", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "modifier_json", None), field="modifier-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=_modifiers_path(),
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-item-modifier", "body": body}],
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        modifier_id = _coerce_text(getattr(args, "modifier_id", None), field="modifier-id")
        body = _read_json_arg(getattr(args, "modifier_json", None), field="modifier-json")
        _require_revision(body, field="modifier-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=_modifiers_path(modifier_id),
            body=body,
            selector={"kind": COMMAND_FAMILY, "modifier_id": modifier_id, "operation": "update"},
            proposed_changes=[{"operation": "update-item-modifier", "modifier_id": modifier_id, "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-item-modifier-update", "requires-current-revision"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        modifier_id = _coerce_text(getattr(args, "modifier_id", None), field="modifier-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=_modifiers_path(modifier_id),
            body=None,
            selector={"kind": COMMAND_FAMILY, "modifier_id": modifier_id, "operation": "delete"},
            proposed_changes=[{"operation": "delete-item-modifier", "modifier_id": modifier_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-restaurants-item-modifier-delete", "permanently-removes-item-modifier"],
            verification_notes="Provider response confirms the Restaurants Item Modifiers delete request was accepted; verify with restaurants-item-modifiers get/list.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _read_json_arg(getattr(args, "modifiers_json", None), field="modifiers-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/modifiers/create",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create-item-modifiers", "body": body}],
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _read_json_arg(getattr(args, "modifiers_json", None), field="modifiers-json")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/bulk/modifiers/delete",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete"},
            proposed_changes=[{"operation": "bulk-delete-item-modifiers", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-restaurants-item-modifier-bulk-delete", "permanently-removes-item-modifiers"],
            verification_notes="Provider response confirms the Restaurants Item Modifiers bulk delete request was accepted; verify with restaurants-item-modifiers list.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_item_modifiers_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "modifiers_json", None), field="modifiers-json")
        _require_bulk_revisions(body, field="modifiers-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/modifiers/update",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update-item-modifiers", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-restaurants-item-modifier-bulk-update", "requires-current-revision"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
