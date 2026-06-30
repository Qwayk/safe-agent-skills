from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-rewards"
BASE_PATH = "/loyalty-rewards/v1/rewards"
BULK_BASE_PATH = "/loyalty-rewards/v1/bulk/rewards"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _reward_id(raw) -> str:
    return _groups._coerce_text(raw, field="reward-id")


def _params(raw) -> dict:
    return _object_body(raw, field="params-json", allow_empty=True)


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    cursor_paging = body.get("cursorPaging")
    if not isinstance(cursor_paging, dict):
        body["cursorPaging"] = {"limit": 50}
    elif "limit" not in cursor_paging:
        cursor_paging["limit"] = 50
    return body


def _reward_body(raw) -> dict:
    body = _object_body(raw, field="reward-json")
    if not isinstance(body.get("reward"), dict):
        raise _groups.ValidationError("--reward-json must include reward")
    return body


def _reward_body_for_update(raw) -> dict:
    body = _reward_body(raw)
    reward = body.get("reward")
    reward_id = reward.get("id")
    if not isinstance(reward_id, str) or not reward_id.strip():
        raise _groups.ValidationError("--reward-json must include reward.id")
    reward["id"] = reward_id.strip()
    return body


def _rewards_body(raw) -> dict:
    body = _object_body(raw, field="rewards-json")
    rewards = body.get("rewards")
    if not isinstance(rewards, list) or not rewards:
        raise _groups.ValidationError("--rewards-json must include a non-empty rewards array")
    return body


def cmd_loyalty_rewards_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _params(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_rewards_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        reward_id = _reward_id(args.reward_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(reward_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_rewards_query(args, ctx) -> int:
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


def cmd_loyalty_rewards_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _reward_body(args.reward_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-loyalty-reward", "reward": body.get("reward")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-reward"],
            verification_notes=(
                "Provider response only. Official docs say Create Reward creates reward definitions for customer redemption behavior."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_rewards_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _reward_body_for_update(args.reward_json)
        reward_id = body["reward"]["id"]
        return _groups._run_write(
            method_name=method,
            http_method="PUT",
            path=f"{BASE_PATH}/{quote(reward_id, safe='')}",
            body=body,
            selector={"rewardId": reward_id, "reward": body.get("reward")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-loyalty-reward"],
            verification_notes=(
                "Provider response only. Official docs say Update Reward changes reward settings for customer redemption."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_rewards_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        reward_id = _reward_id(args.reward_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{quote(reward_id, safe='')}",
            body=None,
            selector={"rewardId": reward_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-loyalty-reward"],
            verification_notes="Provider response only. Official docs say Delete Reward removes a reward definition.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_rewards_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _rewards_body(args.rewards_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/create",
            body=body,
            selector={"operation": "bulk-create-loyalty-rewards", "rewards": body.get("rewards")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-create-loyalty-rewards"],
            verification_notes="Provider response only. Official docs say Bulk Create Rewards creates multiple reward definitions.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
