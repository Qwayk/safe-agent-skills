from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-comments"
BASE_PATH = "/comments/v1/comments"
BULK_BASE_PATH = "/comments/v1/bulk/comments"


def _comment_id(raw) -> str:
    return _groups._coerce_text(raw, field="comment-id")


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _read_params(raw) -> dict:
    return _object_body(raw, field="params-json", allow_empty=True)


def _request_body(raw) -> dict:
    return _object_body(raw, field="request-json", allow_empty=True)


def _comment_body(raw) -> dict:
    return _object_body(raw, field="comment-json")


def _run_comment_action(args, ctx, *, command: str, http_method: str, suffix: str, risk: str, note: str) -> int:
    method = f"{COMMAND_FAMILY}.{command}"
    try:
        comment_id = _comment_id(args.comment_id)
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method=http_method,
            path=f"{BASE_PATH}/{comment_id}/{suffix}",
            body=body,
            selector={"commentId": comment_id, "operation": command},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[risk],
            verification_notes=note,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def _run_bulk_action(args, ctx, *, command: str, http_method: str, suffix: str, risk: str, note: str) -> int:
    method = f"{COMMAND_FAMILY}.{command}"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method=http_method,
            path=f"{BULK_BASE_PATH}/{suffix}",
            body=body,
            selector={"operation": command, "filter": body.get("filter", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[risk],
            verification_notes=note,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _comment_body(args.comment_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-comment", "comment": body.get("comment", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["create-community-comment"],
            verification_notes="Provider response only. Official docs say Create Comment creates and publishes a comment.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        comment_id = _comment_id(args.comment_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{comment_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        comment_id = _comment_id(args.comment_id)
        body = _comment_body(args.comment_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{comment_id}",
            body=body,
            selector={"commentId": comment_id, "comment": body.get("comment", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["update-community-comment"],
            verification_notes="Provider response only. Official docs say Update Comment requires the current revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        comment_id = _comment_id(args.comment_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{comment_id}",
            body=None,
            selector={"commentId": comment_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-community-comment"],
            verification_notes="Provider response only. Official docs say Delete Comment deletes the comment content and sets status to DELETED.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_moderate_draft_content(args, ctx) -> int:
    return _run_comment_action(
        args,
        ctx,
        command="moderate-draft-content",
        http_method="POST",
        suffix="moderate",
        risk="moderate-community-comment-draft",
        note="Provider response only. Official docs say Moderate Draft Content applies a draft content moderation action.",
    )


def cmd_community_comments_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _request_body(args.request_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/query-cursor",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_mark(args, ctx) -> int:
    return _run_comment_action(
        args,
        ctx,
        command="mark",
        http_method="PUT",
        suffix="mark",
        risk="mark-community-comment",
        note="Provider response only. Official docs say Mark Comment marks one comment.",
    )


def cmd_community_comments_unmark(args, ctx) -> int:
    return _run_comment_action(
        args,
        ctx,
        command="unmark",
        http_method="PUT",
        suffix="unmark",
        risk="unmark-community-comment",
        note="Provider response only. Official docs say Unmark Comment unmarks one comment.",
    )


def cmd_community_comments_hide(args, ctx) -> int:
    return _run_comment_action(
        args,
        ctx,
        command="hide",
        http_method="PUT",
        suffix="hide",
        risk="hide-community-comment",
        note="Provider response only. Official docs say Hide Comment hides one comment.",
    )


def cmd_community_comments_publish(args, ctx) -> int:
    return _run_comment_action(
        args,
        ctx,
        command="publish",
        http_method="PUT",
        suffix="publish",
        risk="publish-community-comment",
        note="Provider response only. Official docs say Publish Comment publishes one comment.",
    )


def cmd_community_comments_count(args, ctx) -> int:
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


def cmd_community_comments_list_by_resource(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-by-resource"
    try:
        params = _read_params(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/list-by-resource",
            params=params,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_get_thread(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-thread"
    try:
        comment_id = _comment_id(args.comment_id)
        params = _read_params(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{comment_id}/thread",
            params=params,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_comments_bulk_publish(args, ctx) -> int:
    return _run_bulk_action(
        args,
        ctx,
        command="bulk-publish",
        http_method="POST",
        suffix="publish-by-filter",
        risk="bulk-publish-community-comments",
        note="Provider response only. Official docs say Bulk Publish Comment publishes multiple comments by filter.",
    )


def cmd_community_comments_bulk_hide(args, ctx) -> int:
    return _run_bulk_action(
        args,
        ctx,
        command="bulk-hide",
        http_method="PUT",
        suffix="hide-by-filter",
        risk="bulk-hide-community-comments",
        note="Provider response only. Official docs say Bulk Hide Comment hides multiple comments by filter.",
    )


def cmd_community_comments_bulk_delete(args, ctx) -> int:
    return _run_bulk_action(
        args,
        ctx,
        command="bulk-delete",
        http_method="PUT",
        suffix="delete-by-filter",
        risk="bulk-delete-community-comments",
        note="Provider response only. Official docs say Bulk Delete Comment deletes multiple comments by filter.",
    )


def cmd_community_comments_bulk_moderate_draft_content(args, ctx) -> int:
    return _run_bulk_action(
        args,
        ctx,
        command="bulk-moderate-draft-content",
        http_method="POST",
        suffix="moderate-by-filter",
        risk="bulk-moderate-community-comment-drafts",
        note="Provider response only. Official docs say Bulk Moderate Draft Content moderates multiple comments by filter.",
    )


def cmd_community_comments_bulk_move_by_filter(args, ctx) -> int:
    return _run_bulk_action(
        args,
        ctx,
        command="bulk-move-by-filter",
        http_method="PUT",
        suffix="move-by-filter",
        risk="bulk-move-community-comments",
        note="Provider response only. Official docs say Bulk Move Comment By Filter moves multiple comments to another resource.",
    )
