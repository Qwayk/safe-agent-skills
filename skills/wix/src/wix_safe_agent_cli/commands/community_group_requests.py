from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-group-requests"
BASE_PATH = "/_api/social-groups-proxy/group-requests/v2/group-requests"


def _params_body(raw) -> dict:
    return _groups._read_object(raw, field="params-json", allow_empty=True)


def _query_body(raw) -> dict:
    body = _groups._read_object(raw, field="query-json", allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def _request_body(raw) -> dict:
    return _groups._read_object(raw, field="request-json")


def cmd_community_group_requests_list(args, ctx) -> int:
    method = "community-group-requests.list"
    try:
        params = _params_body(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_requests_query(args, ctx) -> int:
    method = "community-group-requests.query"
    try:
        body = _query_body(args.query_json)
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


def cmd_community_group_requests_approve(args, ctx) -> int:
    method = "community-group-requests.approve"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/approve",
            body=body,
            selector={"request": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["approve-community-group-create-requests"],
            verification_notes="Provider response only. Official docs say this approves group creation requests and triggers Group Request Approved.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_group_requests_reject(args, ctx) -> int:
    method = "community-group-requests.reject"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/reject",
            body=body,
            selector={"request": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["reject-community-group-create-requests"],
            verification_notes="Provider response only. Official docs say this rejects group creation requests and triggers Group Request Rejected.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
