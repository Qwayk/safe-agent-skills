from __future__ import annotations

from typing import Any

from . import online_programs_programs as _programs


COMMAND_FAMILY = "online-programs-instructor-v2"
BASE_PATH = "/_api/instructors-service/v2"


ValidationError = _programs.ValidationError


def _method(name: str) -> str:
    return f"{COMMAND_FAMILY}.{name}"


def _body(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    return _programs._object_arg(raw, field=field, allow_empty=allow_empty)


def _text(raw: Any, *, field: str) -> str:
    return _programs._text(raw, field=field)


def _with_action_id(body: dict[str, Any], action_id: str | None) -> dict[str, Any]:
    if action_id:
        body = dict(body)
        body["actionId"] = action_id
    return body


def _instructor_body(raw: Any, *, field: str) -> dict[str, Any]:
    body = _body(raw, field=field)
    return body if "instructor" in body else {"instructor": body}


def _instructor_id_from_body(body: dict[str, Any], *, field: str) -> str:
    instructor = body.get("instructor")
    if not isinstance(instructor, dict):
        raise ValidationError(f"--{field} must include instructor")
    value = instructor.get("id") or instructor.get("_id")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"--{field} must include instructor.id")
    return value.strip()


def _create_body(args: Any) -> dict[str, Any]:
    body = _instructor_body(getattr(args, "instructor_json", None), field="instructor-json")
    instructor = body.get("instructor")
    if not isinstance(instructor, dict) or not str(instructor.get("name") or "").strip():
        raise ValidationError("--instructor-json must include instructor.name")
    return _with_action_id(body, getattr(args, "action_id", None))


def _update_body(args: Any) -> tuple[str, dict[str, Any]]:
    body = _with_action_id(_instructor_body(getattr(args, "instructor_json", None), field="instructor-json"), getattr(args, "action_id", None))
    return _instructor_id_from_body(body, field="instructor-json"), body


def _read(method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    return _programs._read(method_name, http_method, path, body, ctx)


def _write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    return _programs._write(
        method_name=method_name,
        http_method=http_method,
        path=path,
        body=body,
        selector=selector,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    return _programs._emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_create(args, ctx) -> int:
    method = _method("create")
    try:
        body = _create_body(args)
        selector = {"operation": "create", "name": body.get("instructor", {}).get("name")}
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/instructors", body=body, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["online-programs-instructor-create"], verification_notes="Inspect returned instructor id.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_update(args, ctx) -> int:
    method = _method("update")
    try:
        instructor_id, body = _update_body(args)
        return _write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/instructors/{instructor_id}", body=body, selector={"instructorId": instructor_id}, ctx=ctx, requires_ack=False, risk_reasons=["online-programs-instructor-update"], verification_notes="Inspect returned instructor and query/list instructors if needed.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_query(args, ctx) -> int:
    method = _method("query")
    try:
        body = _body(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _read(method, "POST", f"{BASE_PATH}/instructors/query", body if "query" in body else {"query": body}, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _program_assignment_body(args: Any) -> tuple[str, dict[str, Any]]:
    instructor_id = _text(getattr(args, "instructor_id", None), field="instructor-id")
    program_id = _text(getattr(args, "program_id", None), field="program-id")
    body = _with_action_id({"programId": program_id}, getattr(args, "action_id", None))
    return instructor_id, body


def cmd_online_programs_instructor_v2_assign(args, ctx) -> int:
    method = _method("assign")
    try:
        instructor_id, body = _program_assignment_body(args)
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/instructors/{instructor_id}/assign", body=body, selector={"instructorId": instructor_id, "programId": body["programId"]}, ctx=ctx, requires_ack=False, risk_reasons=["online-programs-instructor-assign"], verification_notes="Query instructors or list program instructors to inspect the assignment.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_change_program_instructors(args, ctx) -> int:
    method = _method("change-program-instructors")
    try:
        body = _body(getattr(args, "assignment_json", None), field="assignment-json")
        program_id = body.get("programId")
        if not isinstance(program_id, str) or not program_id.strip():
            raise ValidationError("--assignment-json must include programId")
        for field in ("assignInstructorIds", "unassignInstructorIds"):
            value = body.get(field)
            if value is not None and (not isinstance(value, list) or len(value) > 10):
                raise ValidationError(f"--assignment-json {field} must be an array with at most 10 items")
        body = _with_action_id(body, getattr(args, "action_id", None))
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/assignments", body=body, selector={"programId": program_id, "assignCount": len(body.get("assignInstructorIds") or []), "unassignCount": len(body.get("unassignInstructorIds") or [])}, ctx=ctx, requires_ack=True, risk_reasons=["online-programs-instructor-assignment-change", "multi-assignment-write"], verification_notes="Query instructors by programIds to inspect assignment changes.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_invite(args, ctx) -> int:
    method = _method("invite")
    try:
        email = _text(getattr(args, "email", None), field="email")
        body = {"email": email}
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/instructors/invite", body=body, selector={"email": email}, ctx=ctx, requires_ack=True, risk_reasons=["online-programs-instructor-invite", "sends-email"], verification_notes="Provider response only; email delivery is outside this CLI.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_list(args, ctx) -> int:
    method = _method("list")
    try:
        body = _body(getattr(args, "list_json", "{}"), field="list-json", allow_empty=True)
        return _read(method, "POST", f"{BASE_PATH}/instructors/list", body, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_instructor_v2_unassign(args, ctx) -> int:
    method = _method("unassign")
    try:
        instructor_id, body = _program_assignment_body(args)
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/instructors/{instructor_id}/unassign", body=body, selector={"instructorId": instructor_id, "programId": body["programId"]}, ctx=ctx, requires_ack=True, risk_reasons=["online-programs-instructor-unassign", "removes-program-assignment"], verification_notes="Query instructors by programIds to inspect the assignment removal.")
    except (ValidationError, _programs.SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)
