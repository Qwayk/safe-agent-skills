from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-group-roles"
BASE_PATH = "/social-groups-proxy/roles/v2/groups"


def _group_id(raw) -> str:
    return _groups._coerce_text(raw, field="group-id")


def _role_body(raw) -> dict:
    return _groups._read_object(raw, field="role-json")


def cmd_community_group_roles_assign(args, ctx) -> int:
    method = "community-group-roles.assign"
    try:
        group_id = _group_id(args.group_id)
        body = _role_body(args.role_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/roles/assign",
            body=body,
            selector={"groupId": group_id, "role": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["assign-community-group-role"],
            verification_notes="Provider response only. Official docs say assigning a role overrides the group member's current role.value and triggers Role Assigned To Group Member.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_roles_unassign(args, ctx) -> int:
    method = "community-group-roles.unassign"
    try:
        group_id = _group_id(args.group_id)
        body = _role_body(args.role_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/roles/unassign",
            body=body,
            selector={"groupId": group_id, "role": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["unassign-community-group-role"],
            verification_notes="Provider response only. Official docs say only ADMIN roles can be unassigned and this triggers Role Unassigned From Group Member.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
