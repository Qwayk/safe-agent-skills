from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-moderation-rules"
BASE_PATH = "/moderation/v1/rules"


def _rule_id(raw) -> str:
    return _groups._coerce_text(raw, field="rule-id")


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _rule_body(raw) -> dict:
    return _object_body(raw, field="rule-json")


def _request_body(raw) -> dict:
    return _object_body(raw, field="request-json", allow_empty=True)


def cmd_community_moderation_rules_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _rule_body(args.rule_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-moderation-rule", "rule": body.get("rule", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-community-moderation-rule"],
            verification_notes="Provider response only. Official docs say moderation rules automate content moderation and each namespace can have up to 20 rules.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_moderation_rules_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        rule_id = _rule_id(args.rule_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{rule_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_moderation_rules_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        rule_id = _rule_id(args.rule_id)
        body = _rule_body(args.rule_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{rule_id}",
            body=body,
            selector={"ruleId": rule_id, "rule": body.get("rule", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-community-moderation-rule"],
            verification_notes="Provider response only. Official docs say Update Rule requires the current revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_moderation_rules_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        rule_id = _rule_id(args.rule_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{rule_id}",
            body=None,
            selector={"ruleId": rule_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-community-moderation-rule"],
            verification_notes="Provider response only. Official docs say Delete Rule deletes one moderation rule.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_moderation_rules_query(args, ctx) -> int:
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


def cmd_community_moderation_rules_check_content(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.check-content"
    try:
        body = _request_body(args.request_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/check",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
