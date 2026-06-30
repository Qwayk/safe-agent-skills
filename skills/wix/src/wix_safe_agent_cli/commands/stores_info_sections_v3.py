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


def _http_status_from_error(exc: RuntimeError) -> int | None:
    text = str(exc)
    if not text.startswith("HTTP "):
        return None
    parts = text.split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _require_revision(raw: Any) -> None:
    if raw is None:
        raise ValidationError("--info-section-json infoSection.revision is required for update")
    if isinstance(raw, str) and not raw.strip():
        raise ValidationError("--info-section-json infoSection.revision cannot be empty")


def _normalize_query_body(raw: Any) -> dict[str, Any]:
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


def _normalize_create_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="info-section-json")
    body = dict(payload) if "infoSection" in payload else {"infoSection": payload}
    info_section = body.get("infoSection")
    if not isinstance(info_section, dict) or not info_section:
        raise ValidationError("--info-section-json must include a non-empty infoSection object")
    return body


def _normalize_update_body(raw: Any, *, info_section_id: str) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="info-section-json")
    body = dict(payload) if "infoSection" in payload else {"infoSection": payload}
    info_section = body.get("infoSection")
    if not isinstance(info_section, dict) or not info_section:
        raise ValidationError("--info-section-json must include a non-empty infoSection object")
    payload_id = info_section.get("id")
    if payload_id is not None and str(payload_id).strip() != info_section_id:
        raise SafetyError("Refused: info section id in body does not match --info-section-id")
    info_section.setdefault("id", info_section_id)
    _require_revision(info_section.get("revision"))
    return body


def _normalize_info_sections_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        info_sections = body.get("infoSections")
    elif isinstance(payload, list):
        info_sections = payload
        body = {"infoSections": info_sections}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(info_sections, list) or not info_sections:
        raise ValidationError(f"--{field} must include a non-empty infoSections array")
    if require_revision:
        for index, info_section in enumerate(info_sections):
            if not isinstance(info_section, dict):
                raise ValidationError(f"--{field} infoSections[{index}] must be an object")
            try:
                _require_revision(info_section.get("revision"))
            except ValidationError as exc:
                raise ValidationError(f"--{field} infoSections[{index}].revision is required for bulk update") from exc
    return body


def _normalize_info_section_ids_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="info-section-ids-json")
    if isinstance(payload, dict):
        body = dict(payload)
        ids = body.get("infoSectionIds")
    elif isinstance(payload, list):
        ids = payload
        body = {"infoSectionIds": ids}
    else:
        raise ValidationError("--info-section-ids-json must be a JSON object or array")
    if not isinstance(ids, list) or not ids:
        raise ValidationError("--info-section-ids-json must include a non-empty infoSectionIds array")
    for index, raw_id in enumerate(ids):
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise ValidationError(f"--info-section-ids-json infoSectionIds[{index}] must be a non-empty string")
    return body


def _resolve_stores_info_sections_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="stores-info-sections-v3",
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


def _extract_info_section(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    info_section = payload.get("infoSection")
    if not isinstance(info_section, dict):
        raise ValidationError(f"{operation} response did not include an infoSection object")
    return info_section


def _extract_info_section_id(info_section: dict[str, Any], *, operation: str) -> str:
    raw_id = info_section.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable info section id")
    return raw_id.strip()


def _get_info_section(*, info_section_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/stores/v3/info-sections/{info_section_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_info_section(payload, operation="stores-info-sections-v3.get")


def _get_info_section_optional(
    *,
    info_section_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    requires_ack: bool = False,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
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
        "risk_reasons": ["wix-stores-info-section-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                state_capture_notes
                or (
                    "Captured current info section state before planning."
                    if has_before_state
                    else "No useful before-state snapshot exists for this create-style write."
                )
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                rollback_notes
                or (
                    "No automatic rollback. Use the reviewed plan snapshot as a manual reference."
                    if has_before_state
                    else "No automatic rollback and no useful before-state snapshot."
                )
            ),
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
    return reviewed_plan_apply_requested(
        ctx,
        requires_ack=requires_ack,
        command_label="stores-info-sections-v3",
    )


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: info section state changed since plan was created")


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
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
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
            "before_state_available": has_before_state,
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No useful before-state snapshot was available for this create-style write."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the reviewed plan snapshot as a reference."
                if has_before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
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


def _run_provider_response_write(
    *,
    args: Any,
    ctx: dict[str, Any],
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool = False,
) -> int:
    _ = args
    headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not plan_in:
        _should_apply(ctx, requires_ack=requires_ack)
    request = {"method": http_method, "path": path, "body": body}
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
            before_state={},
            proposed_changes=proposed_changes,
            verification_plan={
                "type": "provider-response",
                "notes": "Bulk or get-or-create verification is provider-response-only in this boundary; run follow-up get or query commands for live verification.",
            },
            requires_ack=requires_ack,
            state_capture_notes="No useful before-state snapshot exists for this bulk or get-or-create write.",
            rollback_notes="No automatic rollback. Recovery is manual and may require new reviewed plans.",
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
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    verification = {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider accepted the Info Sections V3 request. Follow-up get or query is recommended for live verification.",
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


def _emit_read_result(*, ctx: dict[str, Any], method: str, path: str, body: dict[str, Any], payload: dict[str, Any], auth_mode: str) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "method": method,
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": path, "body": body},
            "response": payload,
        }
    )
    return 0


def cmd_stores_info_sections_v3_get(args, ctx) -> int:
    try:
        info_section_id = _coerce_non_empty_text(getattr(args, "info_section_id", None), field="info-section-id")
        headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
        info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "stores-info-sections-v3.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/stores/v3/info-sections/{info_section_id}"},
                "response": {"infoSection": info_section},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.get"}
        )
        return 1


def cmd_stores_info_sections_v3_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/info-sections/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-info-sections-v3.query",
            path="/stores/v3/info-sections/query",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.query"}
        )
        return 1


def cmd_stores_info_sections_v3_create(args, ctx) -> int:
    try:
        info_section_json = _normalize_create_body(getattr(args, "info_section_json", None))
        headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
        request = {"method": "POST", "path": "/stores/v3/info-sections", "body": info_section_json}
        selector = {"kind": "wix-stores-info-section-v3", "operation": "create"}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-info-sections-v3.create",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else _build_plan(
                method="stores-info-sections-v3.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": info_section_json}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and reread the created info section.",
                },
                state_capture_notes="No useful before-state snapshot exists before an info section is created.",
            )
        )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-info-sections-v3.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-info-sections-v3.create",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/info-sections",
            headers=headers,
            params=None,
            json_body=info_section_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_info_section = _extract_info_section(response, operation="stores-info-sections-v3.create")
        created_id = _extract_info_section_id(created_info_section, operation="stores-info-sections-v3.create")
        after_info_section = _get_info_section(info_section_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_info_section.get("id") or "") == created_id,
            "type": "read-after-write",
            "path": f"/stores/v3/info-sections/{created_id}",
            "method": "GET",
            "after": after_info_section,
            "checks": [{"field": "id", "expected": created_id, "actual": after_info_section.get("id")}],
            "notes": "Create verification uses response id plus read-back get info section.",
        }
        receipt = _build_receipt(
            method="stores-info-sections-v3.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-info-sections-v3.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.create"}
        )
        return 1


def cmd_stores_info_sections_v3_update(args, ctx) -> int:
    try:
        info_section_id = _coerce_non_empty_text(getattr(args, "info_section_id", None), field="info-section-id")
        info_section_json = _normalize_update_body(
            getattr(args, "info_section_json", None),
            info_section_id=info_section_id,
        )
        headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
        request = {
            "method": "PATCH",
            "path": f"/stores/v3/info-sections/{info_section_id}",
            "body": info_section_json,
        }
        selector = {
            "kind": "wix-stores-info-section-v3",
            "operation": "update",
            "info_section_id": info_section_id,
        }
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-info-sections-v3.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            current_info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="stores-info-sections-v3.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"infoSection": current_info_section},
                proposed_changes=[{"operation": "update", "info_section_id": info_section_id, "body": info_section_json}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the updated info section by rereading the same info section id.",
                },
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-info-sections-v3.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-info-sections-v3.update",
            expected_selector=selector,
            ctx=ctx,
        )
        current_info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"infoSection": current_info_section})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/info-sections/{info_section_id}",
            headers=headers,
            params=None,
            json_body=info_section_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_info_section.get("id") or "") == info_section_id,
            "type": "read-after-write",
            "path": f"/stores/v3/info-sections/{info_section_id}",
            "method": "GET",
            "before": current_info_section,
            "after": after_info_section,
            "checks": [{"field": "id", "expected": info_section_id, "actual": after_info_section.get("id")}],
            "notes": "Update verification uses read-back get info section.",
        }
        receipt = _build_receipt(
            method="stores-info-sections-v3.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-info-sections-v3.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.update"}
        )
        return 1


def cmd_stores_info_sections_v3_delete(args, ctx) -> int:
    try:
        info_section_id = _coerce_non_empty_text(getattr(args, "info_section_id", None), field="info-section-id")
        headers, auth_mode = _resolve_stores_info_sections_v3_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not plan_in:
            _should_apply(ctx, requires_ack=True)
        request = {"method": "DELETE", "path": f"/stores/v3/info-sections/{info_section_id}"}
        selector = {
            "kind": "wix-stores-info-section-v3",
            "operation": "delete",
            "info_section_id": info_section_id,
        }
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-info-sections-v3.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            current_info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="stores-info-sections-v3.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"infoSection": current_info_section},
                proposed_changes=[{"operation": "delete", "info_section_id": info_section_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify delete by expecting get info section to return 404.",
                },
                requires_ack=True,
                rollback_notes="No automatic rollback. Deleting an info section also removes it from products that use it, so recovery is manual only.",
            )
        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-info-sections-v3.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-info-sections-v3.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        current_info_section = _get_info_section(info_section_id=info_section_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"infoSection": current_info_section})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/info-sections/{info_section_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_info_section, after_status = _get_info_section_optional(
            info_section_id=info_section_id,
            ctx=ctx,
            headers=headers,
        )
        verification = {
            "ok": after_status == 404 and after_info_section is None,
            "type": "read-after-write",
            "path": f"/stores/v3/info-sections/{info_section_id}",
            "method": "GET",
            "before": current_info_section,
            "after": after_info_section,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get info section to return 404.",
        }
        receipt = _build_receipt(
            method="stores-info-sections-v3.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-info-sections-v3.delete",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.delete"}
        )
        return 1


def cmd_stores_info_sections_v3_bulk_create(args, ctx) -> int:
    try:
        body = _normalize_info_sections_body(getattr(args, "info_sections_json", None), field="info-sections-json")
        return _run_provider_response_write(
            args=args,
            ctx=ctx,
            method_name="stores-info-sections-v3.bulk-create",
            http_method="POST",
            path="/stores/v3/bulk/info-sections/create",
            body=body,
            selector={"kind": "wix-stores-info-section-v3", "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.bulk-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.bulk-create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.bulk-create"}
        )
        return 1


def cmd_stores_info_sections_v3_bulk_delete(args, ctx) -> int:
    try:
        body = _normalize_info_section_ids_body(getattr(args, "info_section_ids_json", None))
        return _run_provider_response_write(
            args=args,
            ctx=ctx,
            method_name="stores-info-sections-v3.bulk-delete",
            http_method="POST",
            path="/stores/v3/bulk/info-sections/delete",
            body=body,
            selector={
                "kind": "wix-stores-info-section-v3",
                "operation": "bulk-delete",
                "info_section_ids": body["infoSectionIds"],
            },
            proposed_changes=[{"operation": "bulk-delete", "info_section_ids": body["infoSectionIds"]}],
            requires_ack=True,
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.bulk-delete", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.bulk-delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.bulk-delete"}
        )
        return 1


def cmd_stores_info_sections_v3_bulk_update(args, ctx) -> int:
    try:
        body = _normalize_info_sections_body(
            getattr(args, "info_sections_json", None),
            field="info-sections-json",
            require_revision=True,
        )
        return _run_provider_response_write(
            args=args,
            ctx=ctx,
            method_name="stores-info-sections-v3.bulk-update",
            http_method="POST",
            path="/stores/v3/bulk/info-sections/update",
            body=body,
            selector={"kind": "wix-stores-info-section-v3", "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.bulk-update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.bulk-update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.bulk-update"}
        )
        return 1


def cmd_stores_info_sections_v3_get_or_create(args, ctx) -> int:
    try:
        body = _normalize_create_body(getattr(args, "info_section_json", None))
        return _run_provider_response_write(
            args=args,
            ctx=ctx,
            method_name="stores-info-sections-v3.get-or-create",
            http_method="POST",
            path="/stores/v3/info-sections/get-or-create",
            body=body,
            selector={"kind": "wix-stores-info-section-v3", "operation": "get-or-create"},
            proposed_changes=[{"operation": "get-or-create", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.get-or-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.get-or-create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-info-sections-v3.get-or-create"}
        )
        return 1


def cmd_stores_info_sections_v3_bulk_get_or_create(args, ctx) -> int:
    try:
        body = _normalize_info_sections_body(getattr(args, "info_sections_json", None), field="info-sections-json")
        return _run_provider_response_write(
            args=args,
            ctx=ctx,
            method_name="stores-info-sections-v3.bulk-get-or-create",
            http_method="POST",
            path="/stores/v3/bulk/info-sections/get-or-create",
            body=body,
            selector={"kind": "wix-stores-info-section-v3", "operation": "bulk-get-or-create"},
            proposed_changes=[{"operation": "bulk-get-or-create", "body": body}],
        )
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-info-sections-v3.bulk-get-or-create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-info-sections-v3.bulk-get-or-create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "stores-info-sections-v3.bulk-get-or-create",
            }
        )
        return 1
