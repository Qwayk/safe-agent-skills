from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-reviews"
BASE_PATH = "/reviews/v1/reviews"
BULK_BASE_PATH = "/reviews/v1/bulk/reviews"


def _review_id(raw) -> str:
    return _groups._coerce_text(raw, field="review-id")


def _status(raw) -> str:
    return _groups._coerce_text(raw, field="status")


def _message(raw) -> str:
    return _groups._coerce_text(raw, field="message")


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _request_body(raw) -> dict:
    return _object_body(raw, field="request-json", allow_empty=True)


def _review_body(raw) -> dict:
    return _object_body(raw, field="review-json")


def _params(raw) -> dict:
    return _object_body(raw, field="params-json", allow_empty=True)


def cmd_community_reviews_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        review_id = _review_id(args.review_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{review_id}",
            params=_params(args.params_json),
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        review_id = _review_id(args.review_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{review_id}",
            body=None,
            selector={"reviewId": review_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-community-review"],
            verification_notes="Provider response only. Official docs say Delete Review deletes one review.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _review_body(args.review_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-review", "review": body.get("review", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["create-community-review"],
            verification_notes="Provider response only. Official docs say Create Review creates a review and may trigger moderation.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/create",
            body=body,
            selector={"operation": "bulk-create-reviews", "reviews": body.get("reviews", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-create-community-reviews"],
            verification_notes="Provider response only. Official docs say Bulk Create Review creates multiple reviews.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        review_id = _review_id(args.review_id)
        body = _review_body(args.review_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{review_id}",
            body=body,
            selector={"reviewId": review_id, "review": body.get("review", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["update-community-review"],
            verification_notes="Provider response only. Official docs say Update Review requires the current revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _object_body(args.filter_json, field="filter-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/delete",
            body=body,
            selector={"operation": "bulk-delete-reviews", "filter": body.get("filter", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-delete-community-reviews"],
            verification_notes="Provider response only. Official docs say Bulk Delete Reviews deletes multiple reviews by filter.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_query(args, ctx) -> int:
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


def cmd_community_reviews_remove_reply(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.remove-reply"
    try:
        review_id = _review_id(args.review_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{review_id}/reply",
            body=None,
            selector={"reviewId": review_id, "operation": "remove-reply"},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["remove-community-review-reply"],
            verification_notes="Provider response only. Official docs say Remove Reply deletes the reply from a review.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_set_reply(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.set-reply"
    try:
        review_id = _review_id(args.review_id)
        body = {"message": _message(args.message)}
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{review_id}/reply",
            body=body,
            selector={"reviewId": review_id, "operation": "set-reply"},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["set-community-review-reply"],
            verification_notes="Provider response only. Official docs say Set Reply sets a direct reply on a review.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_update_moderation_status(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-moderation-status"
    try:
        review_id = _review_id(args.review_id)
        body = {"status": _status(args.status)}
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{review_id}/moderate",
            body=body,
            selector={"reviewId": review_id, "status": body["status"]},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-community-review-moderation-status"],
            verification_notes="Provider response only. Official docs say Update Moderation Status changes the review moderation status.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_bulk_update_moderation_status(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-moderation-status"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/moderate",
            body=body,
            selector={"operation": "bulk-update-review-moderation-status", "filter": body.get("filter", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-update-community-review-moderation-status"],
            verification_notes="Provider response only. Official docs say Bulk Update Moderation Status changes moderation status for multiple reviews by filter.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reviews_count(args, ctx) -> int:
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
