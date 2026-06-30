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


def _coerce_component_id(raw: Any) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError("--component-id must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("--component-id cannot be empty")
    return value


def _coerce_bool_string(raw: Any, *, field: str) -> bool:
    if isinstance(raw, bool):
        return raw
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be true or false")
    value = raw.strip().lower()
    if value not in {"true", "false"}:
        raise ValidationError(f"--{field} must be true or false")
    return value == "true"


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


def _coerce_parameters(raw: Any) -> dict[str, str] | None:
    payload = _read_json_arg(raw, field="parameters-json")
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValidationError("--parameters-json must be a JSON object")

    normalized: dict[str, str] = {}
    for key_raw, value_raw in payload.items():
        if not isinstance(key_raw, str):
            raise ValidationError("--parameters-json keys must be strings")
        key = key_raw.strip()
        if not key:
            raise ValidationError("--parameters-json cannot contain an empty key")
        if not isinstance(value_raw, str):
            raise ValidationError(f"--parameters-json[{key}] must be a string")
        normalized[key] = value_raw
    return normalized


def _resolve_embedded_scripts_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="embedded-scripts",
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


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _request_params(*, component_id: str | None) -> dict[str, Any] | None:
    return {"componentId": component_id} if component_id is not None else None


def _build_embed_request(*, component_id: str | None, disabled: bool, parameters: dict[str, str] | None) -> dict[str, Any]:
    body: dict[str, Any] = {"disabled": disabled}
    if parameters is not None:
        body["parameters"] = parameters
    if component_id is not None:
        body["componentId"] = component_id
    return {"method": "POST", "path": "/apps/v1/scripts", "body": body}


def _get_script_state(
    *,
    component_id: str | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/apps/v1/scripts",
        headers=headers,
        params=_request_params(component_id=component_id),
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _build_selector(*, component_id: str | None, request: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "wix-embedded-script",
        "componentId": component_id,
        "body_signature": json.dumps(request.get("body", {}), sort_keys=True),
    }


def _build_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    before_state: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    body = request.get("body", {})
    disabled = body.get("disabled")
    parameters = body.get("parameters", {})
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "embedded-scripts.embed",
        "risk_level": "high",
        "risk_reasons": ["site-script-write"],
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
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": True,
            "notes": "Plan includes the current embedded script state from Get Embedded Script.",
        },
        "proposed_changes": [
            {
                "operation": "embed-script",
                "componentId": selector.get("componentId"),
                "disabled": disabled,
                "parameters": parameters,
            }
        ],
        "verification_plan": {
            "type": "read-after-write",
            "notes": "Re-read the embedded script state with Get Embedded Script and compare disabled plus parameter values.",
        },
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use the saved before-state snapshot as a manual recovery reference.",
        },
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


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: embedded script state changed since plan was created")


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
    return reviewed_plan_apply_requested(ctx, requires_ack=False, command_label="embedded-scripts")


def _extract_after_script(after_state: dict[str, Any]) -> dict[str, Any]:
    script = after_state.get("script")
    if isinstance(script, dict):
        return script
    return after_state


def _build_verification(
    *,
    request: dict[str, Any],
    after_state: dict[str, Any],
    component_id: str | None,
) -> dict[str, Any]:
    expected_body = request.get("body", {})
    after_script = _extract_after_script(after_state)
    checks = [
        {
            "field": "disabled",
            "expected": expected_body.get("disabled", False),
            "actual": after_script.get("disabled"),
        }
    ]
    if "parameters" in expected_body:
        checks.append(
            {
                "field": "parameters",
                "expected": expected_body.get("parameters", {}),
                "actual": after_script.get("parameters", {}),
            }
        )
    if component_id is not None:
        checks.append(
            {
                "field": "componentId",
                "expected": component_id,
                "actual": after_script.get("componentId"),
            }
        )
    return {
        "ok": all(item["expected"] == item["actual"] for item in checks),
        "type": "read-after-write",
        "path": "/apps/v1/scripts",
        "method": "GET",
        "checks": checks,
        "after": after_state,
    }


def _build_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "embedded-scripts.embed",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": bool(before_state),
            "notes": "Receipt is linked to a reviewed plan snapshot from Get Embedded Script.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only. Use the reviewed plan snapshot as a reference.",
        },
    }


def cmd_embedded_scripts_get(args, ctx) -> int:
    try:
        component_id = _coerce_component_id(getattr(args, "component_id", None))
        headers, auth_mode = _resolve_embedded_scripts_auth(ctx=ctx)
        params = _request_params(component_id=component_id)
        request_path = "/apps/v1/scripts"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "embedded-scripts.get",
            "auth_mode": auth_mode,
            "request": {
                "method": "GET",
                "path": request_path,
                "params": params or {},
            },
            "response": payload,
        }
        ctx["audit"].write("embedded-scripts.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "embedded-scripts.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "embedded-scripts.get"})
        return 1


def cmd_embedded_scripts_embed(args, ctx) -> int:
    try:
        component_id = _coerce_component_id(getattr(args, "component_id", None))
        disabled = _coerce_bool_string(getattr(args, "disabled", "false"), field="disabled")
        parameters = _coerce_parameters(getattr(args, "parameters_json", None))
        headers, auth_mode = _resolve_embedded_scripts_auth(ctx=ctx)

        request = _build_embed_request(component_id=component_id, disabled=disabled, parameters=parameters)
        selector = _build_selector(component_id=component_id, request=request)
        before_state = _get_script_state(component_id=component_id, ctx=ctx, headers=headers)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="embedded-scripts.embed",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(request=request, selector=selector, before_state=before_state, ctx=ctx)

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "embedded-scripts.embed",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="embedded-scripts.embed",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_state_drift(plan=loaded_plan, current_state=before_state)

        response = _request_json(
            method=request["method"],
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _get_script_state(component_id=component_id, ctx=ctx, headers=headers)
        verification = _build_verification(request=request, after_state=after_state, component_id=component_id)
        receipt = _build_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "embedded-scripts.embed",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "embedded-scripts.embed",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "embedded-scripts.embed",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "embedded-scripts.embed",
            }
        )
        return 1
