from __future__ import annotations

from typing import Any

from . import community_groups as _groups


COMMAND_FAMILY = "automations-v2"
BASE_PATH = "/automations-service/v2/automations"


def _object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _text(raw: Any, *, field: str) -> str:
    return _groups._coerce_text(raw, field=field)


def _automation_body(raw: Any, *, require_revision: bool = False) -> dict[str, Any]:
    body = _object(raw, field="automation-json")
    automation = body.get("automation")
    if not isinstance(automation, dict):
        raise _groups.ValidationError("--automation-json must include automation")
    if require_revision:
        if not isinstance(automation.get("id"), str) or not automation["id"].strip():
            raise _groups.ValidationError("--automation-json automation.id is required")
        if "revision" not in automation:
            raise _groups.ValidationError("--automation-json automation.revision is required")
    return body


def _query_body(raw: Any) -> dict[str, Any]:
    return _object(raw, field="query-json", allow_empty=True)


def _validate_body(raw: Any) -> dict[str, Any]:
    return _automation_body(raw, require_revision=False)


def cmd_automations_v2_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _automation_body(getattr(args, "automation_json", None), require_revision=False)
        automation = body["automation"]
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"name": automation.get("name"), "origin": automation.get("origin")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-automation-create", "can-activate-site-workflow"],
            verification_notes="Use automations-v2 get with the returned automation ID.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automations_v2_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        automation_id = _text(getattr(args, "automation_id", None), field="automation-id")
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{automation_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automations_v2_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _automation_body(getattr(args, "automation_json", None), require_revision=True)
        automation = body["automation"]
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{automation['id']}",
            body=body,
            selector={"automationId": automation["id"], "revision": automation.get("revision")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-automation-update", "can-change-site-workflow"],
            verification_notes="Use automations-v2 get with the automation ID to verify revision and configuration.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automations_v2_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        automation_id = _text(getattr(args, "automation_id", None), field="automation-id")
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{automation_id}",
            body=None,
            selector={"automationId": automation_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-automation-delete", "removes-site-workflow"],
            verification_notes="Use automations-v2 get and expect the provider to report absence or an error.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automations_v2_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _query_body(getattr(args, "query_json", None))
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automations_v2_validate(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.validate"
    try:
        body = _validate_body(getattr(args, "automation_json", None))
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/validate",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
