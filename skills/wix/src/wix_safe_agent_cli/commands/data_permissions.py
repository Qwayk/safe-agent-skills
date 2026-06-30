from __future__ import annotations

import time
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested

_ALLOWED_COLLECTION_ACCESS = {
    "ANYONE",
    "SITE_MEMBER",
    "SITE_MEMBER_AUTHOR",
    "CMS_EDITOR",
    "PRIVILEGED",
}
_ALLOWED_SPECIAL_ACCESS = {"ALLOWED", "UNSPECIFIED"}


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_collection_access(raw: Any, *, field: str) -> str:
    value = _coerce_required_text(raw, field=field).upper()
    if value not in _ALLOWED_COLLECTION_ACCESS:
        allowed = ", ".join(sorted(_ALLOWED_COLLECTION_ACCESS))
        raise ValidationError(f"--{field} must be one of: {allowed}")
    return value


def _coerce_special_access(raw: Any, *, field: str) -> str:
    value = _coerce_required_text(raw, field=field).upper()
    if value not in _ALLOWED_SPECIAL_ACCESS:
        allowed = ", ".join(sorted(_ALLOWED_SPECIAL_ACCESS))
        raise ValidationError(f"--{field} must be one of: {allowed}")
    return value


def _coerce_identity_selector(*, user_id: Any, policy_id: Any) -> dict[str, str]:
    normalized_user_id = None
    normalized_policy_id = None
    if user_id is not None:
        normalized_user_id = _coerce_required_text(user_id, field="user-id")
    if policy_id is not None:
        normalized_policy_id = _coerce_required_text(policy_id, field="policy-id")

    if bool(normalized_user_id) == bool(normalized_policy_id):
        raise ValidationError("Provide exactly one of --user-id or --policy-id")
    if normalized_user_id:
        return {"userId": normalized_user_id}
    return {"policyId": normalized_policy_id}


def _resolve_data_permissions_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="data-permissions",
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


def _http_status_from_error(exc: RuntimeError) -> int | None:
    text = str(exc)
    if not text.startswith("HTTP "):
        return None
    pieces = text.split()
    if len(pieces) < 2:
        return None
    try:
        return int(pieces[1])
    except ValueError:
        return None


def _extract_data_permissions(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    data_permissions = payload.get("dataPermissions")
    if not isinstance(data_permissions, dict):
        raise ValidationError(f"{operation} response did not include dataPermissions")
    return data_permissions


def _extract_special_permissions(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    special_permissions = payload.get("specialPermissions")
    if not isinstance(special_permissions, dict):
        raise ValidationError(f"{operation} response did not include specialPermissions")
    return special_permissions


def _extract_special_permissions_id(special_permissions: dict[str, Any], *, operation: str) -> str:
    raw_id = special_permissions.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable special permissions id")
    return raw_id.strip()


def _get_permissions(
    *,
    data_collection_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v1/permissions",
        headers=headers,
        params={"dataCollectionId": data_collection_id},
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_data_permissions(payload, operation="data-permissions.get")


def _find_special_permissions(
    *,
    data_permissions: dict[str, Any],
    special_permissions_id: str | None = None,
    identity_selector: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    candidates = data_permissions.get("specialPermissions")
    if not isinstance(candidates, list):
        return None

    for item in candidates:
        if not isinstance(item, dict):
            continue
        if special_permissions_id and item.get("id") == special_permissions_id:
            return item
        if identity_selector:
            if "userId" in identity_selector and item.get("userId") == identity_selector["userId"]:
                return item
            if "policyId" in identity_selector and item.get("policyId") == identity_selector["policyId"]:
                return item
    return None


def _build_selector(*, operation: str, data_collection_id: str, identity_selector: dict[str, str] | None = None, special_permissions_id: str | None = None) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "kind": "wix-data-permissions",
        "operation": operation,
        "data_collection_id": data_collection_id,
    }
    if identity_selector:
        selector["identity"] = identity_selector
    if special_permissions_id:
        selector["special_permissions_id"] = special_permissions_id
    return selector


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any] | None,
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
) -> dict[str, Any]:
    has_before_state = isinstance(before_state, dict) and bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["cms-data-permissions-write", "access-control-change"],
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
            "before_state": before_state or {},
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                "Captured current collection permissions before planning."
                if has_before_state
                else "No useful before-state snapshot was available."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved permissions snapshot as a manual reference."
                if has_before_state
                else "No automatic rollback and no useful before-state snapshot."
            ),
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


def _should_apply(ctx: dict[str, Any]) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=False, command_label="data-permissions")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: collection permissions changed since plan was created")


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
            "before_state_available": bool(before_state),
            "notes": (
                "Receipt is linked to a reviewed before-state snapshot."
                if before_state
                else "Receipt is linked to a reviewed plan with no useful before-state snapshot."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the saved permissions snapshot as a reference."
                if before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
        },
    }


def _verification_collection_levels(*, expected: dict[str, str], after: dict[str, Any]) -> dict[str, Any]:
    checks = []
    for field, expected_value in expected.items():
        checks.append({"field": field, "expected": expected_value, "actual": after.get(field)})
    return {
        "ok": all(item["expected"] == item["actual"] for item in checks),
        "type": "read-after-write",
        "path": "/wix-data/v1/permissions",
        "method": "GET",
        "checks": checks,
        "after": after,
    }


def _verification_special_permissions(
    *,
    expected: dict[str, Any],
    after_permissions: dict[str, Any],
    special_permissions_id: str,
    should_exist: bool,
) -> dict[str, Any]:
    found = _find_special_permissions(
        data_permissions=after_permissions,
        special_permissions_id=special_permissions_id,
    )
    if not should_exist:
        return {
            "ok": found is None,
            "type": "read-after-write",
            "path": "/wix-data/v1/permissions",
            "method": "GET",
            "checks": [{"field": "specialPermissions.id", "expected": None, "actual": found.get("id") if isinstance(found, dict) else None}],
            "after": after_permissions,
        }

    checks = []
    actual_special = found if isinstance(found, dict) else {}
    for field, expected_value in expected.items():
        checks.append({"field": field, "expected": expected_value, "actual": actual_special.get(field)})
    return {
        "ok": bool(found) and all(item["expected"] == item["actual"] for item in checks),
        "type": "read-after-write",
        "path": "/wix-data/v1/permissions",
        "method": "GET",
        "checks": checks,
        "after": after_permissions,
    }


def cmd_data_permissions_get(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        data_permissions = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "data-permissions.get",
            "auth_mode": auth_mode,
            "request": {
                "method": "GET",
                "path": "/wix-data/v1/permissions",
                "params": {"dataCollectionId": data_collection_id},
            },
            "response": {"dataPermissions": data_permissions},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.get"})
        return 1


def cmd_data_permissions_get_my(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/permissions/current",
            headers=headers,
            params={"dataCollectionId": data_collection_id},
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-permissions.get-my",
            "auth_mode": auth_mode,
            "request": {
                "method": "GET",
                "path": "/wix-data/v1/permissions/current",
                "params": {"dataCollectionId": data_collection_id},
            },
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.get-my"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.get-my"})
        return 1


def cmd_data_permissions_update(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        requested = {
            "itemRead": _coerce_collection_access(getattr(args, "item_read", None), field="item-read"),
            "itemInsert": _coerce_collection_access(getattr(args, "item_insert", None), field="item-insert"),
            "itemUpdate": _coerce_collection_access(getattr(args, "item_update", None), field="item-update"),
            "itemRemove": _coerce_collection_access(getattr(args, "item_remove", None), field="item-remove"),
        }
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        before_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": "/wix-data/v1/permissions",
            "body": {"dataPermissions": {"id": data_collection_id, **requested}},
        }
        selector = _build_selector(operation="update", data_collection_id=data_collection_id)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-permissions.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update-collection-permissions", "data_collection_id": data_collection_id, **requested}],
                verification_plan={"type": "read-after-write", "notes": "Verify by rereading the collection permissions."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-permissions.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.update", expected_selector=selector, ctx=ctx)
        current_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state=current_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/permissions",
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        verification = _verification_collection_levels(expected=requested, after=after_state)
        receipt = _build_receipt(
            method="data-permissions.update",
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
            "method": "data-permissions.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-permissions.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.update"})
        return 1


def cmd_data_permissions_add_special(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        identity_selector = _coerce_identity_selector(
            user_id=getattr(args, "user_id", None),
            policy_id=getattr(args, "policy_id", None),
        )
        requested = {
            **identity_selector,
            "itemRead": _coerce_special_access(getattr(args, "item_read", None), field="item-read"),
            "itemInsert": _coerce_special_access(getattr(args, "item_insert", None), field="item-insert"),
            "itemUpdate": _coerce_special_access(getattr(args, "item_update", None), field="item-update"),
            "itemRemove": _coerce_special_access(getattr(args, "item_remove", None), field="item-remove"),
        }
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        before_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        if _find_special_permissions(data_permissions=before_state, identity_selector=identity_selector):
            raise SafetyError("Refused: special permissions already exist for this user or role")
        request = {
            "method": "POST",
            "path": "/wix-data/v1/permissions/special",
            "body": {"dataCollectionId": data_collection_id, "specialPermissions": requested},
        }
        selector = _build_selector(operation="add-special", data_collection_id=data_collection_id, identity_selector=identity_selector)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.add-special", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-permissions.add-special",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "add-special-permissions", "data_collection_id": data_collection_id, **requested}],
                verification_plan={"type": "read-after-write", "notes": "Verify by rereading collection permissions and locating the created special-permissions entry."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-permissions.add-special",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.add-special", expected_selector=selector, ctx=ctx)
        current_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state=current_state)
        if _find_special_permissions(data_permissions=current_state, identity_selector=identity_selector):
            raise SafetyError("Refused: special permissions already exist for this user or role")
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/permissions/special",
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_special = _extract_special_permissions(response, operation="data-permissions.add-special")
        special_permissions_id = _extract_special_permissions_id(created_special, operation="data-permissions.add-special")
        after_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        verification = _verification_special_permissions(
            expected={"id": special_permissions_id, **requested},
            after_permissions=after_state,
            special_permissions_id=special_permissions_id,
            should_exist=True,
        )
        receipt = _build_receipt(
            method="data-permissions.add-special",
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
            "method": "data-permissions.add-special",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-permissions.add-special"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.add-special"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.add-special"})
        return 1


def cmd_data_permissions_update_special(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        special_permissions_id = _coerce_required_text(getattr(args, "special_permissions_id", None), field="special-permissions-id")
        identity_selector = _coerce_identity_selector(
            user_id=getattr(args, "user_id", None),
            policy_id=getattr(args, "policy_id", None),
        )
        requested = {
            "id": special_permissions_id,
            **identity_selector,
            "itemRead": _coerce_special_access(getattr(args, "item_read", None), field="item-read"),
            "itemInsert": _coerce_special_access(getattr(args, "item_insert", None), field="item-insert"),
            "itemUpdate": _coerce_special_access(getattr(args, "item_update", None), field="item-update"),
            "itemRemove": _coerce_special_access(getattr(args, "item_remove", None), field="item-remove"),
        }
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        before_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        existing_special = _find_special_permissions(data_permissions=before_state, special_permissions_id=special_permissions_id)
        if not existing_special:
            raise SafetyError("Refused: special permissions id was not found in this collection")
        request = {
            "method": "POST",
            "path": f"/wix-data/v1/permissions/special/{special_permissions_id}",
            "body": {"specialPermissions": requested},
        }
        selector = _build_selector(
            operation="update-special",
            data_collection_id=data_collection_id,
            identity_selector=identity_selector,
            special_permissions_id=special_permissions_id,
        )
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.update-special", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-permissions.update-special",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update-special-permissions", "data_collection_id": data_collection_id, **requested}],
                verification_plan={"type": "read-after-write", "notes": "Verify by rereading collection permissions and matching the special-permissions id."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-permissions.update-special",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.update-special", expected_selector=selector, ctx=ctx)
        current_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state=current_state)
        if not _find_special_permissions(data_permissions=current_state, special_permissions_id=special_permissions_id):
            raise SafetyError("Refused: special permissions id was not found in this collection")
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v1/permissions/special/{special_permissions_id}",
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        verification = _verification_special_permissions(
            expected=requested,
            after_permissions=after_state,
            special_permissions_id=special_permissions_id,
            should_exist=True,
        )
        receipt = _build_receipt(
            method="data-permissions.update-special",
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
            "method": "data-permissions.update-special",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-permissions.update-special"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.update-special"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.update-special"})
        return 1


def cmd_data_permissions_remove_special(args, ctx) -> int:
    try:
        data_collection_id = _coerce_required_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        special_permissions_id = _coerce_required_text(getattr(args, "special_permissions_id", None), field="special-permissions-id")
        headers, auth_mode = _resolve_data_permissions_auth(ctx=ctx)
        before_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        existing_special = _find_special_permissions(data_permissions=before_state, special_permissions_id=special_permissions_id)
        if not existing_special:
            raise SafetyError("Refused: special permissions id was not found in this collection")
        request = {
            "method": "DELETE",
            "path": f"/wix-data/v1/permissions/special/{special_permissions_id}",
            "body": None,
        }
        selector = _build_selector(
            operation="remove-special",
            data_collection_id=data_collection_id,
            special_permissions_id=special_permissions_id,
        )
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.remove-special", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-permissions.remove-special",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "remove-special-permissions", "data_collection_id": data_collection_id, "special_permissions_id": special_permissions_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify by rereading collection permissions and confirming the special-permissions id is absent."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-permissions.remove-special",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-permissions.remove-special", expected_selector=selector, ctx=ctx)
        current_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state=current_state)
        if not _find_special_permissions(data_permissions=current_state, special_permissions_id=special_permissions_id):
            raise SafetyError("Refused: special permissions id was not found in this collection")
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v1/permissions/special/{special_permissions_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _get_permissions(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        verification = _verification_special_permissions(
            expected={},
            after_permissions=after_state,
            special_permissions_id=special_permissions_id,
            should_exist=False,
        )
        receipt = _build_receipt(
            method="data-permissions.remove-special",
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
            "method": "data-permissions.remove-special",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-permissions.remove-special"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-permissions.remove-special"})
        return 1
    except RuntimeError as exc:
        if _http_status_from_error(exc) == 404:
            ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "NotFound", "method": "data-permissions.remove-special"})
            return 1
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-permissions.remove-special"})
        return 1
