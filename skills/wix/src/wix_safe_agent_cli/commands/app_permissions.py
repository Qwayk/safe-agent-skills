from __future__ import annotations

import json
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


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_bool(raw: Any, field: str) -> bool | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be true or false")
    normalized = raw.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValidationError(f"--{field} must be true or false")


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


def _build_list_payload(
    *,
    app_id: str,
    consistent: bool | None,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"appId": app_id}
    if consistent is not None:
        params["consistent"] = bool(consistent)
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = int(limit)
    return params


def _extract_permission_id(raw_item: Any) -> str | None:
    if not isinstance(raw_item, dict):
        return None

    direct = raw_item.get("permissionId")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    nested = raw_item.get("permission")
    if not isinstance(nested, dict):
        return None

    nested_id = nested.get("permissionId")
    if isinstance(nested_id, str) and nested_id.strip():
        return nested_id.strip()
    return None


def _has_permission_id(permissions: list[dict[str, Any]], permission_id: str) -> bool:
    wanted = permission_id.strip()
    for item in permissions:
        if _extract_permission_id(item) == wanted:
            return True
    return False


def _list_permissions(
    *,
    app_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
    consistent: bool | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/apps/v1/app-permissions/v1/app-permissions",
        headers=headers,
        params=_build_list_payload(app_id=app_id, consistent=consistent, cursor=cursor, limit=limit),
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    permissions = payload.get("appPermissions")
    if permissions is None:
        raise ValidationError("app-permissions list response did not include an appPermissions array")
    if not isinstance(permissions, list):
        raise ValidationError("app-permissions list response appPermissions must be an array")

    normalized: list[dict[str, Any]] = []
    for item in permissions:
        if isinstance(item, dict):
            normalized.append(item)
    return normalized


def _coerce_app_permission_payload(*, raw_json: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw_json, field="app-permission-json")
    if not isinstance(payload, dict):
        raise ValidationError("--app-permission-json must be a JSON object")

    app_id = _coerce_non_empty_text(payload.get("appId"), field="app-permission-json.appId")
    permission = payload.get("permission")
    if not isinstance(permission, dict):
        raise ValidationError("--app-permission-json.permission must be an object")
    permission_id = _coerce_non_empty_text(
        permission.get("permissionId"),
        field="app-permission-json.permission.permissionId",
    )
    return {"appId": app_id, "permission": {"permissionId": permission_id}}


def _coerce_app_permission_from_args(*, args) -> dict[str, str]:
    app_permission_json = getattr(args, "app_permission_json", None)
    if app_permission_json is not None:
        parsed = _coerce_app_permission_payload(raw_json=app_permission_json)
        return {"appId": parsed["appId"], "permissionId": parsed["permission"]["permissionId"]}

    app_id = _coerce_non_empty_text(getattr(args, "app_id", None), field="app-id")
    permission_id = _coerce_non_empty_text(getattr(args, "permission_id", None), field="permission-id")
    return {"appId": app_id, "permissionId": permission_id}


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
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": "2026-06-23T00:00:00Z",
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-app-permission-write"] + (["irreversible"] if requires_ack else []),
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
            "notes": "No useful before-state snapshot exists for this app permission write.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": rollback_notes or "No automatic rollback and no useful before-state snapshot is available.",
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
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and requires_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: apply requires --ack-irreversible")

    review_ctx = dict(ctx)
    review_ctx["enforce_reviewed_plan"] = True
    return reviewed_plan_apply_requested(
        review_ctx,
        requires_ack=requires_ack,
        command_label="app-permissions",
    )


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
    before_state = plan.get("baseline", {}).get("before_state") if isinstance(plan.get("baseline"), dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": "2026-06-23T00:00:01Z",
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
            "notes": "No useful before-state snapshot is available for this app permission write.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only. No before-state snapshot is available for this write.",
        },
    }


def cmd_app_permissions_list(args, ctx) -> int:
    try:
        app_id = _coerce_non_empty_text(getattr(args, "app_id", None), field="app-id")
        consistent = _coerce_optional_bool(getattr(args, "consistent", None), field="consistent")
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        limit = getattr(args, "limit", None)

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="app-permissions",
        )
        params = _build_list_payload(app_id=app_id, consistent=consistent, cursor=cursor, limit=limit)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/apps/v1/app-permissions/v1/app-permissions",
            headers=auth["headers"],
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        permissions = payload.get("appPermissions")
        if permissions is None:
            raise ValidationError("app-permissions list response did not include an appPermissions array")
        if not isinstance(permissions, list):
            raise ValidationError("app-permissions list response appPermissions must be an array")

        out = {
            "ok": True,
            "method": "app-permissions.list",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": "/apps/v1/app-permissions/v1/app-permissions",
                "params": params,
            },
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-permissions.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-permissions.list"})
        return 1


def cmd_app_permissions_create(args, ctx) -> int:
    try:
        parsed = _coerce_app_permission_from_args(args=args)
        app_id = parsed["appId"]
        permission_id = parsed["permissionId"]

        request_body = {"appPermission": {"appId": app_id, "permission": {"permissionId": permission_id}}}
        request = {
            "method": "POST",
            "path": "/apps/v1/app-permissions/v1/app-permissions",
            "body": request_body,
        }
        selector = {"kind": "wix-app-permission", "operation": "create", "app_id": app_id, "permission_id": permission_id}

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="app-permissions-write",
        )
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="app-permissions.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="app-permissions.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "app_id": app_id, "permission_id": permission_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify the permission appears in a consistent list readback."},
                rollback_notes="No automatic rollback. No before-state snapshot is available for this write.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-permissions.create",
                "auth_mode": auth["mode"],
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-permissions.create",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth["headers"],
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        permissions = _list_permissions(app_id=app_id, ctx=ctx, headers=auth["headers"], consistent=True)
        actual_present = _has_permission_id(permissions, permission_id)
        verification = {
            "ok": actual_present,
            "type": "read-after-write",
            "path": "/apps/v1/app-permissions/v1/app-permissions",
            "method": "GET",
            "checks": [
                {"field": "permissionId", "expected": permission_id, "actual": "present" if actual_present else "absent"}
            ],
            "notes": "Create verification uses read-back list with consistent=true.",
        }
        receipt = _build_receipt(
            method="app-permissions.create",
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
            "method": "app-permissions.create",
            "auth_mode": auth["mode"],
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
            "method": "app-permissions.create",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-permissions.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-permissions.create"})
        return 1


def cmd_app_permissions_delete(args, ctx) -> int:
    try:
        app_id = _coerce_non_empty_text(getattr(args, "app_id", None), field="app-id")
        permission_id = _coerce_non_empty_text(getattr(args, "permission_id", None), field="permission-id")
        request = {
            "method": "DELETE",
            "path": "/apps/v1/app-permissions/v1/app-permissions",
            "params": {"appId": app_id, "permissionId": permission_id},
        }
        selector = {"kind": "wix-app-permission", "operation": "delete", "app_id": app_id, "permission_id": permission_id}

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="app-permissions-write",
        )

        if not bool(ctx.get("apply")):
            permissions = _list_permissions(app_id=app_id, ctx=ctx, headers=auth["headers"])
            if not _has_permission_id(permissions, permission_id):
                raise SafetyError("Refused: target permission is not currently granted and cannot be deleted.")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="app-permissions.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="app-permissions.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "delete", "app_id": app_id, "permission_id": permission_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify the permission is absent in a consistent list readback."},
                requires_ack=True,
                rollback_notes="No automatic rollback. No before-state snapshot is available for this write.",
            )

        if not _should_apply(ctx, requires_ack=True):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-permissions.delete",
                "auth_mode": auth["mode"],
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-permissions.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth["headers"],
            params=request["params"],
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        permissions = _list_permissions(app_id=app_id, ctx=ctx, headers=auth["headers"], consistent=True)
        actual_present = _has_permission_id(permissions, permission_id)
        verification = {
            "ok": not actual_present,
            "type": "read-after-write",
            "path": "/apps/v1/app-permissions/v1/app-permissions",
            "method": "GET",
            "checks": [
                {"field": "permissionId", "expected": permission_id, "actual": "absent" if not actual_present else "present"}
            ],
            "notes": "Delete verification uses read-back list with consistent=true.",
        }
        receipt = _build_receipt(
            method="app-permissions.delete",
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
            "method": "app-permissions.delete",
            "auth_mode": auth["mode"],
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
            "method": "app-permissions.delete",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-permissions.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-permissions.delete"})
        return 1
