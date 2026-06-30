from __future__ import annotations

import time
from typing import Any

from . import online_programs_programs as _shared
from ..authz import resolve_auth_mode
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "partner-profiles"
BASE_PATH = "/partners/profile/v1/partner-profiles"

ValidationError = _shared.ValidationError
SafetyError = _shared.SafetyError


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, method: str, path: str, headers: dict[str, str], json_body: dict[str, Any] | None, ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    if json_body is not None:
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
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


def _read(method_name: str, http_method: str, path: str, ctx: dict[str, Any], *, public: bool = False) -> int:
    auth = {"headers": {}, "mode": "none"} if public else _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=None, ctx=ctx)
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": {"method": http_method, "path": path}, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _profile_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    body = _shared._object_arg(raw, field=field)
    if "partnerProfile" not in body:
        body = {"partnerProfile": body}
    profile = body.get("partnerProfile")
    if not isinstance(profile, dict) or not profile:
        raise ValidationError(f"--{field} must include partnerProfile")
    if require_revision and not str(profile.get("revision") or "").strip():
        raise ValidationError(f"--{field} must include partnerProfile.revision")
    return body


def _plan(*, method_name: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], requires_ack: bool, risk_reasons: list[str], verification_notes: str) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Partner profile writes enter Wix verification and do not capture full before-state in this slice."},
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response-and-follow-up-read", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use get-current and a new reviewed update plan when recovery is possible."},
    }


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _write(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, selector: dict[str, Any], ctx: dict[str, Any], requires_ack: bool, risk_reasons: list[str], verification_notes: str) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _plan(method_name=method_name, request=request, selector=selector, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons, verification_notes=verification_notes)
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    loaded_plan = _load_plan(ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": request,
        "response": response,
        "verified": {"type": "provider-response-and-follow-up-read", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def cmd_partner_profiles_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _profile_body(getattr(args, "profile_json", None), field="profile-json")
        selector = {"operation": "create", "businessName": body.get("partnerProfile", {}).get("professionalInformation", {}).get("businessName")}
        return _write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["partner-profile-create", "developer-preview", "enters-verification"], verification_notes="Inspect returned PartnerProfile id, revision, and validation status; public projection appears only after Wix verification.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_partner_profiles_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _profile_body(getattr(args, "profile_json", None), field="profile-json", require_revision=True)
        profile = body["partnerProfile"]
        selector = {"operation": "update", "profileId": profile.get("id"), "revision": profile.get("revision")}
        return _write(method_name=method, http_method="PATCH", path=BASE_PATH, body=body, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["partner-profile-update", "developer-preview", "enters-verification"], verification_notes="Inspect returned PartnerProfile revision and validation status; public projection changes only after Wix verification.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_partner_profiles_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        _ = args
        return _write(method_name=method, http_method="DELETE", path=BASE_PATH, body=None, selector={"operation": "delete-current-profile"}, ctx=ctx, requires_ack=True, risk_reasons=["partner-profile-delete", "developer-preview", "removes-public-directory-profile"], verification_notes="Provider response is deletion proof; get-current should stop returning the deleted profile and the public profile is removed by Wix.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_partner_profiles_get_current(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-current"
    try:
        _ = args
        return _read(method, "GET", f"{BASE_PATH}/current", ctx)
    except (ValidationError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_partner_profiles_get_public(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-public"
    try:
        partner_id = _shared._text(getattr(args, "partner_id", None), field="partner-id")
        return _read(method, "GET", f"{BASE_PATH}/{partner_id}/public", ctx, public=True)
    except (ValidationError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_partner_profiles_find_public_by_slug(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.find-public-by-slug"
    try:
        slug = _shared._text(getattr(args, "slug", None), field="slug")
        return _read(method, "GET", f"{BASE_PATH}/slug/{slug}/public", ctx, public=True)
    except (ValidationError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)
