from __future__ import annotations

from typing import Any

from . import community_groups as _groups


COMMAND_FAMILY = "analytics-sessions"
BASE_PATH = "/analytics/v1/sessions"


def _object_body(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _coerce_text(raw: Any, *, field: str) -> str:
    return _groups._coerce_text(raw, field=field)


def _coerce_int(raw: Any, *, field: str, minimum: int, maximum: int | None = None) -> int:
    value = _coerce_text(raw, field=field)
    try:
        parsed = int(value)
    except ValueError as exc:
        raise _groups.ValidationError(f"--{field} must be an integer") from exc
    if parsed < minimum:
        raise _groups.ValidationError(f"--{field} must be at least {minimum}")
    if maximum is not None and parsed > maximum:
        raise _groups.ValidationError(f"--{field} must be at most {maximum}")
    return parsed


def _list_sessions_body(raw: Any) -> dict[str, Any]:
    body = _object_body(raw, field="sessions-json")
    session_filters = {"navigationFlow", "conversionFunnel", "deviceType"}
    time_filters = {"customTimePeriod", "predefinedTimePeriod"}
    if not any(key in body for key in session_filters):
        raise _groups.ValidationError(
            "--sessions-json must include one session filter: navigationFlow, conversionFunnel, or deviceType"
        )
    if not any(key in body for key in time_filters):
        raise _groups.ValidationError(
            "--sessions-json must include customTimePeriod or predefinedTimePeriod"
        )
    return body


def _session_ids_body(raw: Any) -> dict[str, Any]:
    body = _object_body(raw, field="session-ids-json")
    session_ids = body.get("sessionIds")
    if not isinstance(session_ids, list) or not session_ids:
        raise _groups.ValidationError("--session-ids-json must include non-empty sessionIds")
    if len(session_ids) > 100:
        raise _groups.ValidationError("--session-ids-json cannot include more than 100 sessionIds")
    if not all(isinstance(value, str) and value.strip() for value in session_ids):
        raise _groups.ValidationError("--session-ids-json sessionIds must be non-empty strings")
    return body


def cmd_analytics_sessions_get_list_job_result(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-list-job-result"
    try:
        job_id = _coerce_text(getattr(args, "job_id", None), field="job-id")
        limit = _coerce_int(getattr(args, "limit", None), field="limit", minimum=1, maximum=1000)
        offset = _coerce_int(getattr(args, "offset", None), field="offset", minimum=0)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/list/result",
            params={"jobId": job_id, "limit": limit, "offset": offset},
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_analytics_sessions_list_async(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-async"
    try:
        body = _list_sessions_body(getattr(args, "sessions_json", None))
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/list/async",
            body=body,
            selector={"sessionFilter": sorted(key for key in ("navigationFlow", "conversionFunnel", "deviceType") if key in body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-analytics-sessions-async-job", "starts-provider-job"],
            verification_notes="Use analytics-sessions get-list-job-result with the returned jobId, limit, and offset.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_analytics_sessions_mark_recordings_deleted(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.mark-recordings-deleted"
    try:
        body = _session_ids_body(getattr(args, "session_ids_json", None))
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/recordings-deleted",
            body=body,
            selector={"sessionIds": body["sessionIds"]},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-analytics-recording-delete-marker", "marks-session-recordings-deleted"],
            verification_notes="Inspect the provider response. Wix returns an empty object when recordings were marked deleted.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_analytics_sessions_mark_session_recorded(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.mark-session-recorded"
    try:
        session_id = _coerce_text(getattr(args, "session_id", None), field="session-id")
        body = {"sessionId": session_id}
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/session-recorded",
            body=body,
            selector={"sessionId": session_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-analytics-session-recorded-marker", "changes-session-recording-state"],
            verification_notes="Inspect the provider response. Wix returns an empty object when the session was marked recorded.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
