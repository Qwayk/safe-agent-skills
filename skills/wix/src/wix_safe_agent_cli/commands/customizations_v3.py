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


def _coerce_customization_id(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --customization-id")
    if not isinstance(raw, str):
        raise ValidationError("--customization-id must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("Missing --customization-id")
    return value


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _require_revision(raw: Any, *, field: str) -> None:
    if raw is None:
        raise ValidationError(f"--{field} revision is required")
    if isinstance(raw, str) and not raw.strip():
        raise ValidationError(f"--{field} revision cannot be empty")


def _normalize_customization_body(raw: Any, *, field: str, customization_id: str | None = None, require_revision: bool = False) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field=field)
    body = dict(payload) if "customization" in payload else {"customization": payload}
    customization = body.get("customization")
    if not isinstance(customization, dict) or not customization:
        raise ValidationError(f"--{field} must include a non-empty customization object")
    if customization_id is not None:
        payload_id = customization.get("id")
        if payload_id is not None and str(payload_id).strip() != customization_id:
            raise SafetyError("Refused: customization id in body does not match --customization-id")
        customization.setdefault("id", customization_id)
    if require_revision:
        _require_revision(customization.get("revision"), field=field)
    return body


def _normalize_customizations_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        customizations = body.get("customizations")
    elif isinstance(payload, list):
        customizations = payload
        body = {"customizations": customizations}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(customizations, list) or not customizations:
        raise ValidationError(f"--{field} must include a non-empty customizations array")
    if require_revision:
        for index, customization in enumerate(customizations):
            if not isinstance(customization, dict):
                raise ValidationError(f"--{field} customizations[{index}] must be an object")
            try:
                _require_revision(customization.get("revision"), field=field)
            except ValidationError as exc:
                raise ValidationError(f"--{field} customizations[{index}].revision is required for bulk update") from exc
    return body


def _normalize_choices_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        choices = body.get("choices")
    elif isinstance(payload, list):
        choices = payload
        body = {"choices": choices}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(choices, list) or not choices:
        raise ValidationError(f"--{field} must include a non-empty choices array")
    return body


def _normalize_bulk_choices_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        customizations = body.get("customizations")
    elif isinstance(payload, list):
        customizations = payload
        body = {"customizations": customizations}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(customizations, list) or not customizations:
        raise ValidationError(f"--{field} must include a non-empty customizations array")
    return body


def _coerce_query_payload(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="query-json")
    if not isinstance(payload, dict):
        raise ValidationError("--query-json must be a JSON object")
    if "query" in payload:
        nested = payload.get("query")
        if not isinstance(nested, dict):
            raise ValidationError("--query-json query must be a JSON object")
        return payload
    return {"query": payload}


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
    if json_body is not None:
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
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


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in --apply --yes",
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
        "risk_reasons": ["wix-stores-customization-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": {},
        },
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot exists for this Customizations V3 write in the current boundary.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary; run follow-up get or query for live verification.",
        },
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Recovery is manual and may require new reviewed plans.",
        },
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="customizations-v3")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
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
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": False,
            "notes": "Receipt is linked to a reviewed plan, but no useful before-state snapshot was available.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only and may require new reviewed plans.",
        },
    }


def _emit_safety_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
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


def _run_customization_write(
    *,
    ctx: dict[str, Any],
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
) -> int:
    headers, auth_mode = _resolve_customizations_v3_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not plan_in:
        _should_apply(ctx, requires_ack=requires_ack)
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    if plan_in:
        plan = _load_plan(
            plan_in=str(plan_in),
            expected_method=method_name,
            expected_selector=selector,
            ctx=ctx,
        )
    else:
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=proposed_changes,
            requires_ack=requires_ack,
        )
    if not _should_apply(ctx, requires_ack=requires_ack):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0
    loaded_plan = _load_plan(
        plan_in=str(plan_in),
        expected_method=method_name,
        expected_selector=selector,
        ctx=ctx,
    )
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    verification = {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider accepted the Customizations V3 request. Follow-up get or query is recommended for live verification.",
    }
    receipt = _build_receipt(
        method=method_name,
        selector=selector,
        request=request,
        response=response,
        verification=verification,
        plan=loaded_plan,
        ctx=ctx,
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _resolve_customizations_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="customizations-v3",
    )
    return auth["headers"], auth["mode"]


def cmd_customizations_v3_get(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        headers, auth_mode = _resolve_customizations_v3_auth(ctx=ctx)
        request_path = f"/stores/v3/customizations/{customization_id}"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="customizations-v3.get",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.get"}
        )
        return 1


def cmd_customizations_v3_query(args, ctx) -> int:
    try:
        body = _coerce_query_payload(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_customizations_v3_auth(ctx=ctx)
        request_path = "/stores/v3/customizations/query"
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="customizations-v3.query",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.query"}
        )
        return 1


def cmd_customizations_v3_create(args, ctx) -> int:
    try:
        body = _normalize_customization_body(getattr(args, "customization_json", None), field="customization-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.create",
            http_method="POST",
            path="/stores/v3/customizations",
            body=body,
            selector={"operation": "create"},
            proposed_changes=[{"action": "create_customization", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.create"})
        return 1


def cmd_customizations_v3_update(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        body = _normalize_customization_body(
            getattr(args, "customization_json", None),
            field="customization-json",
            customization_id=customization_id,
            require_revision=True,
        )
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.update",
            http_method="PATCH",
            path=f"/stores/v3/customizations/{customization_id}",
            body=body,
            selector={"customization_id": customization_id},
            proposed_changes=[{"action": "update_customization", "customization_id": customization_id, "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.update"})
        return 1


def cmd_customizations_v3_delete(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.delete",
            http_method="DELETE",
            path=f"/stores/v3/customizations/{customization_id}",
            body=None,
            selector={"customization_id": customization_id},
            proposed_changes=[{"action": "delete_customization", "customization_id": customization_id}],
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.delete"})
        return 1


def cmd_customizations_v3_bulk_create(args, ctx) -> int:
    try:
        body = _normalize_customizations_body(getattr(args, "customizations_json", None), field="customizations-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.bulk-create",
            http_method="POST",
            path="/stores/v3/bulk/customizations/create",
            body=body,
            selector={"operation": "bulk-create"},
            proposed_changes=[{"action": "bulk_create_customizations", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.bulk-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.bulk-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.bulk-create"})
        return 1


def cmd_customizations_v3_bulk_update(args, ctx) -> int:
    try:
        body = _normalize_customizations_body(
            getattr(args, "customizations_json", None),
            field="customizations-json",
            require_revision=True,
        )
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.bulk-update",
            http_method="POST",
            path="/stores/v3/bulk/customizations/update",
            body=body,
            selector={"operation": "bulk-update"},
            proposed_changes=[{"action": "bulk_update_customizations", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.bulk-update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.bulk-update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.bulk-update"})
        return 1


def cmd_customizations_v3_add_choices(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        body = _normalize_choices_body(getattr(args, "choices_json", None), field="choices-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.add-choices",
            http_method="POST",
            path=f"/stores/v3/customizations/{customization_id}/add-choices",
            body=body,
            selector={"customization_id": customization_id},
            proposed_changes=[{"action": "add_customization_choices", "customization_id": customization_id, "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.add-choices", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.add-choices"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.add-choices"})
        return 1


def cmd_customizations_v3_bulk_add_choices(args, ctx) -> int:
    try:
        body = _normalize_bulk_choices_body(getattr(args, "customizations_json", None), field="customizations-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.bulk-add-choices",
            http_method="POST",
            path="/stores/v3/bulk/customizations/add-choices",
            body=body,
            selector={"operation": "bulk-add-choices"},
            proposed_changes=[{"action": "bulk_add_customization_choices", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.bulk-add-choices", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.bulk-add-choices"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.bulk-add-choices"})
        return 1


def cmd_customizations_v3_remove_choices(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        body = _normalize_choices_body(getattr(args, "choices_json", None), field="choices-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.remove-choices",
            http_method="POST",
            path=f"/stores/v3/customizations/{customization_id}/remove-choices",
            body=body,
            selector={"customization_id": customization_id},
            proposed_changes=[{"action": "remove_customization_choices", "customization_id": customization_id, "body": body}],
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.remove-choices", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.remove-choices"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.remove-choices"})
        return 1


def cmd_customizations_v3_set_choices(args, ctx) -> int:
    try:
        customization_id = _coerce_customization_id(getattr(args, "customization_id", None))
        body = _normalize_choices_body(getattr(args, "choices_json", None), field="choices-json")
        return _run_customization_write(
            ctx=ctx,
            method_name="customizations-v3.set-choices",
            http_method="POST",
            path=f"/stores/v3/customizations/{customization_id}/set-choices",
            body=body,
            selector={"customization_id": customization_id},
            proposed_changes=[{"action": "set_customization_choices", "customization_id": customization_id, "body": body}],
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="customizations-v3.set-choices", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "customizations-v3.set-choices"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "customizations-v3.set-choices"})
        return 1
