from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-join-requests"
BASE_PATH = "/social-groups-proxy/join/v2/groups"


def _group_id(raw) -> str:
    return _groups._coerce_text(raw, field="group-id")


def _params_body(raw) -> dict:
    return _groups._read_object(raw, field="params-json", allow_empty=True)


def _query_body(raw) -> dict:
    body = _groups._read_object(raw, field="query-json", allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def _request_body(raw) -> dict:
    return _groups._read_object(raw, field="request-json")


def cmd_community_join_requests_list(args, ctx) -> int:
    method = "community-join-requests.list"
    try:
        group_id = _group_id(args.group_id)
        params = _params_body(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{group_id}/join-requests",
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_join_requests_query(args, ctx) -> int:
    method = "community-join-requests.query"
    try:
        group_id = _group_id(args.group_id)
        body = _query_body(args.query_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/join-requests/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_join_requests_approve(args, ctx) -> int:
    method = "community-join-requests.approve"
    try:
        group_id = _group_id(args.group_id)
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/join-requests/approve",
            body=body,
            selector={"groupId": group_id, "request": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["approve-community-join-requests"],
            verification_notes="Provider response only. Official docs say approval adds the site member to the private group and triggers Join Group Request Approved.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_join_requests_reject(args, ctx) -> int:
    method = "community-join-requests.reject"
    try:
        group_id = _group_id(args.group_id)
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/join-requests/reject",
            body=body,
            selector={"groupId": group_id, "request": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["reject-community-join-requests"],
            verification_notes="Provider response only. Official docs say rejection decides pending requests and triggers Join Group Request Rejected.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
