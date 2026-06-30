from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from . import community_groups as _groups


COMMAND_FAMILY = "community-membership-questions"
BASE_PATH = "/social-groups-proxy/questions/v2/membership-questions"


def _group_id(raw) -> str:
    return _groups._coerce_text(raw, field="group-id")


def _read_json(raw, *, field: str) -> Any:
    value = _groups._coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _read_string_array(raw, *, field: str) -> list[str]:
    payload = _read_json(raw, field=field)
    if not isinstance(payload, list):
        raise ValidationError(f"--{field} must be a JSON array")
    for index, item in enumerate(payload):
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field}[{index}] must be a non-empty string")
    return payload


def _read_optional_object(raw, *, field: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    payload = _read_json(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _list_answers_body(args) -> dict[str, Any]:
    body: dict[str, Any] = {}
    member_ids_json = getattr(args, "member_ids_json", None)
    paging_json = getattr(args, "paging_json", None)
    if member_ids_json is not None:
        body["memberIds"] = _read_string_array(member_ids_json, field="member-ids-json")
    paging = _read_optional_object(paging_json, field="paging-json")
    if paging is not None:
        body["paging"] = paging
    return body


def _questions_body(raw) -> dict[str, Any]:
    payload = _read_json(raw, field="questions-json")
    if isinstance(payload, dict) and payload:
        questions = payload.get("questions")
        if not isinstance(questions, list):
            raise ValidationError("--questions-json object must include a questions array")
    elif isinstance(payload, dict):
        raise ValidationError("--questions-json cannot be an empty JSON object; use {\"questions\":[]} to remove all questions")
    else:
        raise ValidationError("--questions-json must be a JSON object with a questions array")
    for index, question in enumerate(questions):
        if not isinstance(question, dict) or not question:
            raise ValidationError(f"--questions-json questions[{index}] must be a non-empty object")
    return {"questions": questions}


def cmd_community_membership_questions_list(args, ctx) -> int:
    method = "community-membership-questions.list"
    try:
        group_id = _group_id(args.group_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{group_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_membership_questions_list_answers(args, ctx) -> int:
    method = "community-membership-questions.list-answers"
    try:
        group_id = _group_id(args.group_id)
        body = _list_answers_body(args)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{group_id}/answers",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_membership_questions_create_or_replace(args, ctx) -> int:
    method = "community-membership-questions.create-or-replace"
    try:
        group_id = _group_id(args.group_id)
        body = _questions_body(args.questions_json)
        return _groups._run_write(
            method_name=method,
            http_method="PUT",
            path=f"{BASE_PATH}/{group_id}",
            body=body,
            selector={"groupId": group_id, "questions": body["questions"]},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["replace-community-membership-questions"],
            verification_notes="Provider response only. Official docs say this creates questions if none exist, otherwise replaces all existing membership questions; an empty questions array removes all questions.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
