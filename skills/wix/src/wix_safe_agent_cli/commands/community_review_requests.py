from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-review-requests"
BASE_PATH = "/reviews/v2/review-requests"
BULK_BASE_PATH = "/reviews/v2/bulk/review-requests"


def _review_request_id(raw) -> str:
    return _groups._coerce_text(raw, field="review-request-id")


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _request_body(raw) -> dict:
    return _object_body(raw, field="request-json", allow_empty=True)


def _review_request_body(raw) -> dict:
    return _object_body(raw, field="review-request-json")


def cmd_community_review_requests_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _review_request_body(args.review_request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-review-request", "reviewRequest": body.get("reviewRequest", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["create-community-review-request"],
            verification_notes="Provider response only. Official docs say Create Review Request creates a request to solicit a review.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_review_requests_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        review_request_id = _review_request_id(args.review_request_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{review_request_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_review_requests_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        review_request_id = _review_request_id(args.review_request_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{review_request_id}",
            body=None,
            selector={"reviewRequestId": review_request_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-community-review-request"],
            verification_notes="Provider response only. Official docs say only review requests with status CANCELED can be deleted.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_review_requests_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _request_body(args.request_json)
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


def cmd_community_review_requests_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _request_body(args.request_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/count",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_review_requests_bulk_cancel_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-cancel-by-filter"
    try:
        body = _object_body(args.filter_json, field="filter-json")
        return _groups._run_write(
            method_name=method,
            http_method="PUT",
            path=f"{BULK_BASE_PATH}/cancel-by-filter",
            body=body,
            selector={"operation": "bulk-cancel-review-requests-by-filter", "filter": body.get("filter", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-cancel-community-review-requests"],
            verification_notes="Provider response only. Official docs say Bulk Cancel Review Requests By Filter starts a bulk job and returns a job ID.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
