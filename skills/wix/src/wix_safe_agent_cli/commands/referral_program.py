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


COMMAND_FAMILY = "referral-program"
BASE_PATH = "/_api/referral-programs/v1/program"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
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
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _program_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="program-json")
    program = payload.get("program")
    referral_program = payload.get("referralProgram")
    candidate = program if isinstance(program, dict) else referral_program
    if not isinstance(candidate, dict):
        candidate = payload
    if candidate.get("revision") is None:
        raise ValidationError("--program-json must include the current program revision")
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
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _read(*, method_name: str, path: str, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method="GET", path=path, headers=auth["headers"], json_body=None, ctx=ctx)
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": {"method": "GET", "path": path}, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    operation: str,
    request: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    selector = {"kind": COMMAND_FAMILY, "operation": operation}
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
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Referral Program plans do not capture a before-state snapshot in this slice."},
        "proposed_changes": [{"operation": operation, "request": request}],
        "verification_plan": {"type": "provider-response-plus-reread", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Reapply the prior referral program settings manually if needed."},
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


def _write(
    *,
    method_name: str,
    operation: str,
    path: str,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": "PATCH" if operation in {"activate", "pause", "update"} else "POST", "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        operation=operation,
        request=request,
        ctx=ctx,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    selector = {"kind": COMMAND_FAMILY, "operation": operation}
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=request["method"], path=path, headers=auth["headers"], json_body=body, ctx=ctx)
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
        "verification": {"ok": True, "type": "provider-response-plus-reread", "notes": verification_notes},
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


def cmd_referral_program_get(args, ctx) -> int:
    _ = args
    try:
        return _read(method_name="referralProgram.getReferralProgram", path=BASE_PATH, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method="referralProgram.getReferralProgram", exc=exc)


def cmd_referral_program_get_premium_features(args, ctx) -> int:
    _ = args
    try:
        return _read(method_name="referralProgram.getReferralProgramPremiumFeatures", path=f"{BASE_PATH}/premium-features", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method="referralProgram.getReferralProgramPremiumFeatures", exc=exc)


def cmd_referral_program_get_ai_social_media_posts_suggestions(args, ctx) -> int:
    _ = args
    try:
        return _read(method_name="referralProgram.getAISocialMediaPostsSuggestions", path=f"{BASE_PATH}/ai-social-media-posts-suggestions", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method="referralProgram.getAISocialMediaPostsSuggestions", exc=exc)


def cmd_referral_program_activate(args, ctx) -> int:
    _ = args
    method = "referralProgram.activateReferralProgram"
    try:
        return _write(
            method_name=method,
            operation="activate",
            path=f"{BASE_PATH}/activate",
            body=None,
            ctx=ctx,
            risk_reasons=["referral-program-status-change", "site-referral-program-becomes-active"],
            verification_notes="Provider response confirms Wix accepted activation. Rerun referral-program get to verify status ACTIVE.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referral_program_pause(args, ctx) -> int:
    _ = args
    method = "referralProgram.pauseReferralProgram"
    try:
        return _write(
            method_name=method,
            operation="pause",
            path=f"{BASE_PATH}/pause",
            body=None,
            ctx=ctx,
            risk_reasons=["referral-program-status-change", "site-referral-program-paused"],
            verification_notes="Provider response confirms Wix accepted pause. Rerun referral-program get to verify status PAUSED.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referral_program_generate_ai_social_media_posts_suggestions(args, ctx) -> int:
    _ = args
    method = "referralProgram.generateAISocialMediaPostsSuggestions"
    try:
        return _write(
            method_name=method,
            operation="generate-ai-social-media-posts-suggestions",
            path=f"{BASE_PATH}/ai-social-media-posts-suggestions",
            body=None,
            ctx=ctx,
            risk_reasons=["ai-content-generation", "replaces-or-refreshes-referral-social-suggestions"],
            verification_notes="Provider response confirms Wix accepted generation. Rerun get-ai-social-media-posts-suggestions to inspect returned suggestions.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referral_program_update(args, ctx) -> int:
    method = "referralProgram.updateReferralProgram"
    try:
        body = _program_body(getattr(args, "program_json", None))
        return _write(
            method_name=method,
            operation="update",
            path=BASE_PATH,
            body=body,
            ctx=ctx,
            risk_reasons=["referral-program-settings-update", "requires-current-revision"],
            verification_notes="Provider response confirms Wix accepted the update. Rerun referral-program get to verify the referral program.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
