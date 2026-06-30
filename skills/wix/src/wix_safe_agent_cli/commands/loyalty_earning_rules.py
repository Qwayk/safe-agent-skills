from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-earning-rules"
BASE_PATH = "/_api/loyalty-earning-rules/v1/earning-rules"
BULK_BASE_PATH = "/_api/loyalty-earning-rules/v1/bulk/earning-rules"
AUTOMATION_BASE_PATH = "/_api/loyalty-earning-rules/v1/automation-earning-rules"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _rule_id(raw) -> str:
    return _groups._coerce_text(raw, field="rule-id")


def _revision(raw) -> str:
    return _groups._coerce_text(raw, field="revision")


def _params(raw) -> dict:
    return _object_body(raw, field="params-json", allow_empty=True)


def _earning_rule_body(raw, *, field: str = "rule-json") -> dict:
    body = _object_body(raw, field=field)
    if not isinstance(body.get("earningRule"), dict):
        raise _groups.ValidationError(f"--{field} must include earningRule")
    return body


def _bulk_create_body(raw) -> dict:
    body = _object_body(raw, field="rules-json")
    rules = body.get("earningRules")
    if not isinstance(rules, list) or not rules:
        raise _groups.ValidationError("--rules-json must include a non-empty earningRules array")
    return body


def _custom_body(raw) -> dict:
    body = _object_body(raw, field="request-json")
    if not isinstance(body.get("type"), str) or not body["type"].strip():
        raise _groups.ValidationError("--request-json must include type")
    if not isinstance(body.get("earningRule"), dict):
        raise _groups.ValidationError("--request-json must include earningRule")
    return body


def cmd_loyalty_earning_rules_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _params(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/rules",
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_get(args, ctx) -> int:
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


def cmd_loyalty_earning_rules_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _earning_rule_body(args.rule_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-loyalty-earning-rule", "earningRule": body.get("earningRule")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-earning-rule"],
            verification_notes="Provider response only. Official docs say Create Loyalty Earning Rule creates a non-automated earning rule.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        rule_id = _rule_id(args.rule_id)
        body = _earning_rule_body(args.rule_json)
        rule = body["earningRule"]
        if "revision" not in rule:
            raise _groups.ValidationError("--rule-json must include earningRule.revision")
        return _groups._run_write(
            method_name=method,
            http_method="PUT",
            path=f"{BASE_PATH}/{rule_id}",
            body=body,
            selector={"ruleId": rule_id, "earningRule": rule},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-loyalty-earning-rule"],
            verification_notes="Provider response only. Official docs say Update Loyalty Earning Rule supports partial updates and requires the current revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        rule_id = _rule_id(args.rule_id)
        revision = _revision(args.revision)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{rule_id}?revision={quote(revision, safe='')}",
            body=None,
            selector={"ruleId": rule_id, "revision": revision},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-loyalty-earning-rule"],
            verification_notes="Provider response only. Official docs say Delete Loyalty Earning Rule deletes a non-automated earning rule.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _bulk_create_body(args.rules_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/create",
            body=body,
            selector={"operation": "bulk-create-loyalty-earning-rules", "earningRules": body.get("earningRules")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-create-loyalty-earning-rules"],
            verification_notes="Provider response only. Official docs say Bulk Create Loyalty Earning Rules creates multiple non-automated earning rules.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_create_custom(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create-custom"
    try:
        body = _custom_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/custom",
            body=body,
            selector={"operation": "create-custom-loyalty-earning-rule", "type": body.get("type")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-custom-loyalty-earning-rule"],
            verification_notes="Provider response only. Official docs say Create Custom Loyalty Earning Rule creates a custom automated earning rule.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_earning_rules_delete_automation(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete-automation"
    try:
        rule_id = _rule_id(args.rule_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{AUTOMATION_BASE_PATH}/{rule_id}",
            body=None,
            selector={"ruleId": rule_id, "operation": "delete-automation-earning-rule"},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-automation-earning-rule"],
            verification_notes="Provider response only. Official docs say Delete Automation Earning Rule deletes a custom automated earning rule; pre-installed automated rules can only be paused.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
