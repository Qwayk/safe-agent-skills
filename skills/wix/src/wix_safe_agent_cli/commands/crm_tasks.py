from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "crm-tasks"
BASE_PATH = "/crm/tasks/v2/tasks"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _task_id(raw) -> str:
    return _groups._coerce_text(raw, field="task-id")


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    if body:
        return body
    return {"query": {"sort": [{"fieldName": "createdDate", "order": "DESC"}]}}


def _count_body(raw) -> dict:
    body = _object_body(raw, field="filter-json", allow_empty=True)
    if not body:
        return {}
    if "filter" in body:
        return body
    return {"filter": body}


def _require_task_body(body: dict, *, field: str) -> dict:
    task = body.get("task")
    if not isinstance(task, dict) or not task:
        raise _groups.ValidationError(f"--{field} must include task")
    return task


def _task_id_from_body(body: dict, *, field: str) -> str:
    task = _require_task_body(body, field=field)
    value = task.get("id")
    if not isinstance(value, str) or not value.strip():
        raise _groups.ValidationError(f"--{field} must include task.id")
    return value.strip()


def _require_revision(body: dict, *, field: str) -> None:
    task = _require_task_body(body, field=field)
    if task.get("revision") in (None, ""):
        raise _groups.ValidationError(f"--{field} must include task.revision")


def cmd_crm_tasks_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _object_body(args.task_json, field="task-json")
        task = _require_task_body(body, field="task-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"task": task},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-task-create"],
            verification_notes="Inspect provider response, then use crm-tasks get or query to verify the saved task.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_tasks_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        task_id = _task_id(args.task_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(task_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_tasks_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _object_body(args.task_json, field="task-json")
        task_id = _task_id_from_body(body, field="task-json")
        _require_revision(body, field="task-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{quote(task_id, safe='')}",
            body=body,
            selector={"taskId": task_id},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-task-update", "requires-current-revision"],
            verification_notes="Inspect provider response, then use crm-tasks get to verify the saved task revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_tasks_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        task_id = _task_id(args.task_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{quote(task_id, safe='')}",
            body=None,
            selector={"taskId": task_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-crm-task-delete", "task-removal"],
            verification_notes="Inspect provider response, then use crm-tasks get or query to confirm the task is gone.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_tasks_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
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


def cmd_crm_tasks_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _count_body(args.filter_json)
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


def cmd_crm_tasks_move_after(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.move-after"
    try:
        task_id = _task_id(args.task_id)
        body = _object_body(args.move_json, field="move-json", allow_empty=True)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{quote(task_id, safe='')}/move-after",
            body=body,
            selector={"taskId": task_id, "beforeTaskId": body.get("beforeTaskId")},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-task-display-order-change"],
            verification_notes="Inspect provider response, then use crm-tasks query to verify the display order.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
