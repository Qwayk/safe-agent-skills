from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-coupons"
BASE_PATH = "/loyalty-coupons/v1/coupons"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _coupon_id(raw) -> str:
    return _groups._coerce_text(raw, field="coupon-id")


def _query_body(raw) -> dict:
    return _object_body(raw, field="query-json", allow_empty=True)


def _redeem_body(raw, *, field: str) -> dict:
    body = _object_body(raw, field=field)
    reward_id = body.get("rewardId")
    if reward_id is not None and (not isinstance(reward_id, str) or not reward_id.strip()):
        raise _groups.ValidationError(f"--{field} rewardId must be a non-empty string when provided")
    return body


def cmd_loyalty_coupons_get(args, ctx) -> int:
    try:
        coupon_id = _coupon_id(getattr(args, "coupon_id", None))
        return _groups._run_read(
            method_name="loyalty-coupons.get",
            http_method="GET",
            path=f"{BASE_PATH}/{quote(coupon_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.get", exc=exc)


def cmd_loyalty_coupons_query(args, ctx) -> int:
    try:
        body = _query_body(getattr(args, "query_json", "{}"))
        return _groups._run_read(
            method_name="loyalty-coupons.query",
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.query", exc=exc)


def cmd_loyalty_coupons_get_current_member(args, ctx) -> int:
    try:
        _ = args
        return _groups._run_read(
            method_name="loyalty-coupons.get-current-member",
            http_method="GET",
            path=f"{BASE_PATH}/my-coupons",
            params=None,
            body=None,
            ctx=ctx,
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.get-current-member", exc=exc)


def cmd_loyalty_coupons_redeem_current_member(args, ctx) -> int:
    try:
        body = _redeem_body(getattr(args, "redeem_json", None), field="redeem-json")
        return _groups._run_write(
            method_name="loyalty-coupons.redeem-current-member",
            http_method="POST",
            path=f"{BASE_PATH}/redeem-my-coupon",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "redeem-current-member", "body": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["loyalty-coupon-redeem-current-member", "redeems-loyalty-points"],
            verification_notes="Verify with loyalty-coupons get-current-member and inspect the corresponding reference coupon.",
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.redeem-current-member", exc=exc)


def cmd_loyalty_coupons_redeem(args, ctx) -> int:
    try:
        body = _redeem_body(getattr(args, "redeem_json", None), field="redeem-json")
        return _groups._run_write(
            method_name="loyalty-coupons.redeem",
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "redeem", "body": body},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["loyalty-coupon-redeem", "redeems-customer-loyalty-points"],
            verification_notes="Verify with loyalty-coupons query/get and inspect the corresponding reference coupon.",
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.redeem", exc=exc)


def cmd_loyalty_coupons_delete(args, ctx) -> int:
    try:
        coupon_id = _coupon_id(getattr(args, "coupon_id", None))
        return _groups._run_write(
            method_name="loyalty-coupons.delete",
            http_method="DELETE",
            path=f"{BASE_PATH}/{quote(coupon_id, safe='')}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "coupon_id": coupon_id, "operation": "delete"},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["loyalty-coupon-delete"],
            verification_notes="Verify with loyalty-coupons get/query. Official docs say deleting the loyalty coupon does not affect the corresponding reference coupon.",
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-coupons.delete", exc=exc)
