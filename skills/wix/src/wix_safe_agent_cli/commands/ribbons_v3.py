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


def _coerce_ribbon_id(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --ribbon-id")
    if not isinstance(raw, str):
        raise ValidationError("--ribbon-id must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("Missing --ribbon-id")
    return value


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


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _coerce_json_array(raw: Any, *, field: str) -> list[Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _normalize_ribbon_body(raw: Any, *, ribbon_id: str | None = None, require_revision: bool = False) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="ribbon-json")
    body = dict(payload) if "ribbon" in payload else {"ribbon": payload}
    ribbon = body.get("ribbon")
    if not isinstance(ribbon, dict) or not ribbon:
        raise ValidationError("--ribbon-json must include a non-empty ribbon object")
    if ribbon_id is not None:
        payload_id = ribbon.get("id")
        if payload_id is not None and str(payload_id).strip() != ribbon_id:
            raise SafetyError("Refused: ribbon id in body does not match --ribbon-id")
        ribbon.setdefault("id", ribbon_id)
    if require_revision:
        revision = ribbon.get("revision")
        if revision is None or (isinstance(revision, str) and not revision.strip()):
            raise ValidationError("--ribbon-json ribbon.revision is required for update")
    return body


def _normalize_ribbons_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        ribbons = body.get("ribbons")
    elif isinstance(payload, list):
        ribbons = payload
        body = {"ribbons": ribbons}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(ribbons, list) or not ribbons:
        raise ValidationError(f"--{field} must include a non-empty ribbons array")
    if require_revision:
        for index, ribbon in enumerate(ribbons):
            if not isinstance(ribbon, dict):
                raise ValidationError(f"--{field} ribbons[{index}] must be an object")
            revision = ribbon.get("revision")
            if revision is None or (isinstance(revision, str) and not revision.strip()):
                raise ValidationError(f"--{field} ribbons[{index}].revision is required for bulk update")
    return body


def _normalize_ribbon_names_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        names = body.get("ribbonNames")
    elif isinstance(payload, list):
        names = payload
        body = {"ribbonNames": names}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(names, list) or not names:
        raise ValidationError(f"--{field} must include a non-empty ribbonNames array")
    return body


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


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _resolve_ribbons_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="ribbons-v3",
    )
    return auth["headers"], auth["mode"]


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="ribbons-v3")


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    requires_ack: bool = False,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in --apply --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector},
        "proposed_changes": [{"operation": selector["operation"], "request": request}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Ribbons V3 apply is verified from the provider response in this boundary; run a follow-up get or query when a live account is available.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Create a new reviewed plan to reverse the ribbon change when possible."},
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


def _emit_safety_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
    ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
    return 0


def _run_plan_first_write(
    *,
    args: Any,
    ctx: dict[str, Any],
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    requires_ack: bool = False,
) -> int:
    headers, auth_mode = _resolve_ribbons_v3_auth(ctx=ctx)
    request = {"method": http_method, "path": path}
    if body:
        request["body"] = body
    plan_in = ctx.get("plan_in")
    plan = (
        _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
        if plan_in
        else _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["wix-stores-ribbon-write"],
            requires_ack=requires_ack,
        )
    )
    if not _should_apply(ctx, requires_ack=requires_ack):
        ctx["out"].emit({"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        json_body=body if body else None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    verification = {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider accepted the Ribbons V3 request. Follow-up get/query is recommended for live verification.",
    }
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
        "verification": verification,
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "rollback_plan": None,
    }
    ctx["out"].emit({"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
    return 0


def cmd_ribbons_v3_get(args, ctx) -> int:
    try:
        ribbon_id = _coerce_ribbon_id(getattr(args, "ribbon_id", None))
        headers, auth_mode = _resolve_ribbons_v3_auth(ctx=ctx)
        request_path = f"/stores/v3/ribbons/{ribbon_id}"
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
            method="ribbons-v3.get",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.get"})
        return 1


def cmd_ribbons_v3_query(args, ctx) -> int:
    try:
        body = _coerce_query_payload(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_ribbons_v3_auth(ctx=ctx)
        request_path = "/stores/v3/ribbons/query"
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
            method="ribbons-v3.query",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.query"})
        return 1


def cmd_ribbons_v3_create(args, ctx) -> int:
    try:
        body = _normalize_ribbon_body(getattr(args, "ribbon_json", None))
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.create",
            http_method="POST",
            path="/stores/v3/ribbons",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "create"},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.create"})
        return 1


def cmd_ribbons_v3_update(args, ctx) -> int:
    try:
        ribbon_id = _coerce_ribbon_id(getattr(args, "ribbon_id", None))
        body = _normalize_ribbon_body(getattr(args, "ribbon_json", None), ribbon_id=ribbon_id, require_revision=True)
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.update",
            http_method="PATCH",
            path=f"/stores/v3/ribbons/{ribbon_id}",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "update", "ribbon_id": ribbon_id},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.update"})
        return 1


def cmd_ribbons_v3_delete(args, ctx) -> int:
    try:
        ribbon_id = _coerce_ribbon_id(getattr(args, "ribbon_id", None))
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.delete",
            http_method="DELETE",
            path=f"/stores/v3/ribbons/{ribbon_id}",
            body={},
            selector={"kind": "wix-stores-ribbon-v3", "operation": "delete", "ribbon_id": ribbon_id},
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.delete"})
        return 1


def cmd_ribbons_v3_bulk_create(args, ctx) -> int:
    try:
        body = _normalize_ribbons_body(getattr(args, "ribbons_json", None), field="ribbons-json")
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.bulk-create",
            http_method="POST",
            path="/stores/v3/bulk/ribbons/create",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "bulk-create"},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.bulk-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.bulk-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.bulk-create"})
        return 1


def cmd_ribbons_v3_bulk_delete(args, ctx) -> int:
    try:
        ids = _coerce_json_array(getattr(args, "ribbon_ids_json", None), field="ribbon-ids-json")
        body = {"ribbonIds": ids}
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.bulk-delete",
            http_method="POST",
            path="/stores/v3/bulk/ribbons/delete",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "bulk-delete", "ribbon_ids": ids},
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.bulk-delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.bulk-delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.bulk-delete"})
        return 1


def cmd_ribbons_v3_bulk_update(args, ctx) -> int:
    try:
        body = _normalize_ribbons_body(getattr(args, "ribbons_json", None), field="ribbons-json", require_revision=True)
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.bulk-update",
            http_method="POST",
            path="/stores/v3/bulk/ribbons/update",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "bulk-update"},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.bulk-update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.bulk-update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.bulk-update"})
        return 1


def cmd_ribbons_v3_get_or_create(args, ctx) -> int:
    try:
        ribbon_name = getattr(args, "ribbon_name", None)
        if not isinstance(ribbon_name, str) or not ribbon_name.strip():
            raise ValidationError("Missing --ribbon-name")
        body = {"ribbonName": ribbon_name.strip()}
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.get-or-create",
            http_method="POST",
            path="/stores/v3/ribbons/get-or-create",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "get-or-create", "ribbon_name": ribbon_name.strip()},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.get-or-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.get-or-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.get-or-create"})
        return 1


def cmd_ribbons_v3_bulk_get_or_create(args, ctx) -> int:
    try:
        body = _normalize_ribbon_names_body(getattr(args, "ribbon_names_json", None), field="ribbon-names-json")
        return _run_plan_first_write(
            args=args,
            ctx=ctx,
            method_name="ribbons-v3.bulk-get-or-create",
            http_method="POST",
            path="/stores/v3/bulk/ribbons/get-or-create",
            body=body,
            selector={"kind": "wix-stores-ribbon-v3", "operation": "bulk-get-or-create", "ribbon_names": body["ribbonNames"]},
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="ribbons-v3.bulk-get-or-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "ribbons-v3.bulk-get-or-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "ribbons-v3.bulk-get-or-create"})
        return 1
