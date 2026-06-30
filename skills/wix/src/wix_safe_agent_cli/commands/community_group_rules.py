from __future__ import annotations

from . import community_groups as _groups
from ..errors import ValidationError


COMMAND_FAMILY = "community-group-rules"
BASE_PATH = "/social-groups/v2/rules"


def _group_id(raw) -> str:
    return _groups._coerce_text(raw, field="group-id")


def _rules_body(raw) -> dict:
    body = _groups._read_object(raw, field="rules-json")
    rules = body.get("rules")
    if not isinstance(rules, list):
        raise ValidationError("--rules-json must include rules")
    if len(rules) > 100:
        raise ValidationError("--rules-json.rules supports at most 100 rules")
    return body


def cmd_community_group_rules_list(args, ctx) -> int:
    method = "community-group-rules.list"
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


def cmd_community_group_rules_create_or_replace(args, ctx) -> int:
    method = "community-group-rules.create-or-replace"
    try:
        group_id = _group_id(args.group_id)
        body = _rules_body(args.rules_json)
        return _groups._run_write(
            method_name=method,
            http_method="PUT",
            path=f"{BASE_PATH}/{group_id}",
            body=body,
            selector={"groupId": group_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["replace-all-community-group-rules"],
            verification_notes="Provider response only. Official docs say this creates rules if none exist or replaces all existing rules.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
