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


COMMAND_FAMILY = "referred-friends"
BASE_PATH = "/referral_friends/v1/referred-friends"


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


def _query_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="query-json")
    query = payload.get("query")
    if not isinstance(query, dict):
        raise ValidationError("--query-json.query must be a JSON object")
    return payload


def _update_body(raw: Any) -> tuple[str, dict[str, Any]]:
    payload = _read_json_arg(raw, field="referred-friend-json")
    referred_friend = payload.get("referredFriend")
    if not isinstance(referred_friend, dict):
        raise ValidationError("--referred-friend-json.referredFriend must be a JSON object")
    referred_friend_id = _coerce_text(referred_friend.get("id"), field="referred-friend-json.referredFriend.id")
    _coerce_text(referred_friend.get("contactId"), field="referred-friend-json.referredFriend.contactId")
    _coerce_text(referred_friend.get("referringCustomerId"), field="referred-friend-json.referredFriend.referringCustomerId")
    _coerce_text(referred_friend.get("revision"), field="referred-friend-json.referredFriend.revision")
    return referred_friend_id, payload


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
    params: dict[str, Any] | None,
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
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _read(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": http_method, "path": path, **({"body": body} if body is not None else {})},
        "response": response,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method_name: str,
    operation: str,
    request: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
    requires_ack: bool,
) -> dict[str, Any]:
    selector = {"kind": COMMAND_FAMILY, "operation": operation}
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
        "state_capture": {"before_state_available": False, "notes": "Referred Friends plans do not capture a before-state snapshot in this slice."},
        "proposed_changes": [{"operation": operation, "request": request}],
        "verification_plan": {"type": "provider-response-plus-reread", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Recreate or update the referred friend manually if needed."},
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
    http_method: str,
    path: str,
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
    requires_ack: bool,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params:
        request["params"] = params
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        operation=operation,
        request=request,
        ctx=ctx,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
        requires_ack=requires_ack,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    selector = {"kind": COMMAND_FAMILY, "operation": operation}
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
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


def cmd_referred_friends_get(args, ctx) -> int:
    method = "referredFriends.getReferredFriend"
    try:
        referred_friend_id = _coerce_text(getattr(args, "referred_friend_id", None), field="referred-friend-id")
        return _read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{referred_friend_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referred_friends_query(args, ctx) -> int:
    method = "referredFriends.queryReferredFriend"
    try:
        body = _query_body(getattr(args, "query_json", None))
        return _read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referred_friends_get_by_contact_id(args, ctx) -> int:
    method = "referredFriends.getReferredFriendByContactId"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        return _read(method_name=method, http_method="GET", path=f"{BASE_PATH}/contact/{contact_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referred_friends_create(args, ctx) -> int:
    method = "referredFriends.createReferredFriend"
    try:
        referral_code = _coerce_text(getattr(args, "referral_code", None), field="referral-code")
        return _write(
            method_name=method,
            operation="create",
            http_method="POST",
            path=BASE_PATH,
            params=None,
            body={"referralCode": referral_code},
            ctx=ctx,
            risk_reasons=["may-create-referred-friend-record", "requires-member-identity", "can-trigger-referred-friend-created-event"],
            verification_notes="Provider response confirms Wix accepted the create request. Rerun referred-friends get or get-by-contact-id to verify the record.",
            requires_ack=False,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referred_friends_update(args, ctx) -> int:
    method = "referredFriends.updateReferredFriend"
    try:
        referred_friend_id, body = _update_body(getattr(args, "referred_friend_json", None))
        return _write(
            method_name=method,
            operation="update",
            http_method="PATCH",
            path=f"{BASE_PATH}/{referred_friend_id}",
            params=None,
            body=body,
            ctx=ctx,
            risk_reasons=["updates-referred-friend-record", "requires-current-revision", "can-trigger-referred-friend-updated-event"],
            verification_notes="Provider response confirms Wix accepted the update. Rerun referred-friends get with the referred friend ID to verify the new revision and status.",
            requires_ack=False,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referred_friends_delete(args, ctx) -> int:
    method = "referredFriends.deleteReferredFriend"
    try:
        referred_friend_id = _coerce_text(getattr(args, "referred_friend_id", None), field="referred-friend-id")
        revision = _coerce_text(getattr(args, "revision", None), field="revision")
        return _write(
            method_name=method,
            operation="delete",
            http_method="DELETE",
            path=f"{BASE_PATH}/{referred_friend_id}",
            params={"revision": revision},
            body=None,
            ctx=ctx,
            risk_reasons=["permanently-deletes-referred-friend", "requires-current-revision", "can-trigger-referred-friend-deleted-event"],
            verification_notes="Provider response confirms Wix accepted deletion. Rerun referred-friends get and expect the record to be absent.",
            requires_ack=True,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
