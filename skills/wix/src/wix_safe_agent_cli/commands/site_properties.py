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
        raise ValidationError(f"Missing --{field}")
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


def _coerce_field_paths(raw: Any) -> list[str] | None:
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValidationError("--field-path must be repeatable")

    seen: set[str] = set()
    paths: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, str):
            raise ValidationError(f"--field-path[{index}] must be a string")
        value = item.strip()
        if not value:
            raise ValidationError(f"--field-path[{index}] cannot be empty")
        if value in seen:
            continue
        seen.add(value)
        paths.append(value)
    return paths


def _coerce_resource_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = raw if isinstance(raw, dict) else _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    for key in value:
        if not isinstance(key, str) or not key.strip():
            raise ValidationError(f"--{field} keys must be non-empty strings")
    return value


def _resolve_site_properties_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="site-properties",
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


def _coerce_paths_from_payload(*, payload: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in payload.keys():
        if not isinstance(key, str):
            raise ValidationError("Payload keys must be strings")
        value = key.strip()
        if not value:
            raise ValidationError("Payload keys cannot be empty")
        paths.append(value)

    if not paths:
        raise ValidationError("Payload cannot be empty")
    return paths


def _build_query_params(field_paths: list[str] | None) -> dict[str, Any] | None:
    if not field_paths:
        return None
    return {"fields.paths": field_paths}


def _get_site_properties(*, ctx: dict[str, Any], headers: dict[str, str], field_paths: list[str] | None) -> dict[str, Any]:
    params = _build_query_params(field_paths)
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/site-properties/v4/properties",
        headers=headers,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _extract_section(*, properties: dict[str, Any], section: str, keys: list[str]) -> dict[str, Any]:
    section_obj = properties.get(section)
    if not isinstance(section_obj, dict):
        return {}
    output: dict[str, Any] = {}
    for key in keys:
        if not isinstance(key, str):
            continue
        output[key] = section_obj.get(key)
    return output


def _build_plan(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], before_state: dict[str, Any], proposed_changes: dict[str, Any], verification_plan: dict[str, Any], risk_note: str | None = None) -> dict[str, Any]:
    preconditions: list[str] = [
        "env_fingerprint must match",
        "selector must match",
        "before-state must be captured from site-properties get",
        "apply requires --apply and --yes",
    ]
    risk_reasons = ["site-properties-write"]
    if risk_note:
        risk_reasons.append(risk_note)

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "proposed_changes": [proposed_changes],
        "verification_plan": verification_plan,
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="site-properties")


def _assert_no_property_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if baseline_state != current_state:
        raise SafetyError("Refused: properties changed since plan was created")


def _build_receipt(*, method: str, selector: dict[str, Any], request: dict[str, Any], response: dict[str, Any], verification: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _build_update_verification(*, expected: dict[str, Any], before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    all_ok = True
    for key in expected:
        checked = key in after and after[key] == expected[key]
        checks.append({"field": key, "expected": expected[key], "actual": after.get(key)})
        if not checked:
            all_ok = False

    return {
        "ok": all_ok,
        "type": "read-after-write",
        "path": "/site-properties/v4/properties",
        "method": "GET",
        "before": before,
        "after": after,
        "checks": checks,
    }


def _run_site_properties_update(
    *,
    args,
    ctx: dict[str, Any],
    payload_field: str,
    payload_key: str,
    method_name: str,
    request_path: str,
    risk_note: str | None = None,
) -> int:
    try:
        payload = _coerce_resource_payload(getattr(args, payload_field), field=payload_field)
        field_paths = _coerce_paths_from_payload(payload=payload)

        auth_headers, auth_mode = _resolve_site_properties_auth(ctx=ctx)
        before_properties = _get_site_properties(ctx=ctx, headers=auth_headers, field_paths=None)
        before_section = _extract_section(properties=before_properties, section=payload_key, keys=field_paths)

        request_body = {payload_key: payload}
        request: dict[str, Any] = {"method": "POST", "path": request_path, "body": request_body}
        selector = {"kind": "site-properties", "operation": method_name, "resource": payload_key}
        planned_changes = {"operation": method_name, "resource": payload_key, "fields": field_paths}
        plan_in = ctx.get("plan_in")

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
                before_state={payload_key: before_section},
                proposed_changes=planned_changes,
                verification_plan={"type": "read-after-write", "notes": "Verify target fields in site-properties get"},
                risk_note=risk_note,
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method=method_name,
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else plan
        )
        _assert_no_property_state_drift(plan=loaded_plan, current_state={payload_key: before_section})

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth_headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_properties = _get_site_properties(ctx=ctx, headers=auth_headers, field_paths=field_paths)
        after_section = _extract_section(properties=after_properties, section=payload_key, keys=field_paths)
        verification = _build_update_verification(expected=payload, before=before_section, after=after_section)

        receipt = _build_receipt(
            method=method_name,
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )

        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": method_name,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method_name}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method_name}
        ctx["out"].emit(out)
        return 1


def cmd_site_properties_get(args, ctx) -> int:
    try:
        field_paths = _coerce_field_paths(getattr(args, "field_path", None))
        auth_headers, auth_mode = _resolve_site_properties_auth(ctx=ctx)

        payload = _get_site_properties(
            ctx=ctx,
            headers=auth_headers,
            field_paths=field_paths,
        )

        request = {"method": "GET", "path": "/site-properties/v4/properties"}
        params = _build_query_params(field_paths)
        if params is not None:
            request["params"] = params

        out = {
            "ok": True,
            "method": "site-properties.get",
            "auth_mode": auth_mode,
            "request": request,
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-properties.get"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "site-properties.get"}
        ctx["out"].emit(out)
        return 1


def cmd_site_properties_update_business_contact(args, ctx) -> int:
    return _run_site_properties_update(
        args=args,
        ctx=ctx,
        payload_field="contact_json",
        payload_key="businessContact",
        method_name="site-properties.update-business-contact",
        request_path="/site-properties/v4/properties/business-contact",
    )


def cmd_site_properties_update_business_profile(args, ctx) -> int:
    return _run_site_properties_update(
        args=args,
        ctx=ctx,
        payload_field="profile_json",
        payload_key="businessProfile",
        method_name="site-properties.update-business-profile",
        request_path="/site-properties/v4/properties/business-profile",
    )


def cmd_site_properties_update_business_schedule(args, ctx) -> int:
    return _run_site_properties_update(
        args=args,
        ctx=ctx,
        payload_field="schedule_json",
        payload_key="businessSchedule",
        method_name="site-properties.update-business-schedule",
        request_path="/site-properties/v4/properties/business-schedule",
        risk_note="business-schedule update overwrites the existing businessSchedule",
    )


def cmd_site_properties_update_consent_policy(args, ctx) -> int:
    return _run_site_properties_update(
        args=args,
        ctx=ctx,
        payload_field="consent_json",
        payload_key="consentPolicy",
        method_name="site-properties.update-consent-policy",
        request_path="/site-properties/v4/properties/policy",
    )
