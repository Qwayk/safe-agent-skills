from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-group-members"
BASE_PATH = "/social-groups-proxy/members/v2"


def _group_id(raw) -> str:
    return _groups._coerce_text(raw, field="group-id")


def _member_id(raw) -> str:
    return _groups._coerce_text(raw, field="member-id")


def _params_body(raw) -> dict:
    return _groups._read_object(raw, field="params-json", allow_empty=True)


def _query_body(raw) -> dict:
    body = _groups._read_object(raw, field="query-json", allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def _members_body(raw) -> dict:
    return _groups._read_object(raw, field="members-json")


def cmd_community_group_members_list(args, ctx) -> int:
    method = "community-group-members.list"
    try:
        group_id = _group_id(args.group_id)
        params = _params_body(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/groups/{group_id}/members",
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_members_list_memberships(args, ctx) -> int:
    method = "community-group-members.list-memberships"
    try:
        member_id = _member_id(args.member_id)
        params = _params_body(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/members/{member_id}/memberships",
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_members_query(args, ctx) -> int:
    method = "community-group-members.query"
    try:
        group_id = _group_id(args.group_id)
        body = _query_body(args.query_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/groups/{group_id}/members/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_members_query_memberships(args, ctx) -> int:
    method = "community-group-members.query-memberships"
    try:
        member_id = _member_id(args.member_id)
        body = _query_body(args.query_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/members/{member_id}/memberships/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_members_add(args, ctx) -> int:
    method = "community-group-members.add"
    try:
        group_id = _group_id(args.group_id)
        body = _members_body(args.members_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/groups/{group_id}/members",
            body=body,
            selector={"groupId": group_id, "members": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["add-community-group-members"],
            verification_notes="Provider response only. Official docs say public members are added right away, while private members receive an invitation to join the group.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_members_remove(args, ctx) -> int:
    method = "community-group-members.remove"
    try:
        group_id = _group_id(args.group_id)
        body = _members_body(args.members_json)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/groups/{group_id}/members",
            body=body,
            selector={"groupId": group_id, "members": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["remove-community-group-members"],
            verification_notes="Provider response only. Official docs say this removes site members from a specific group and triggers Member Removed.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
