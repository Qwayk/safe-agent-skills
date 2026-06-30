from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-checkout-discounts"
BASE_PATH = "/loyalty-checkout-exchange/v1/loyalty-checkout-discounts"
APPLY_PATH = "/loyalty-checkout-exchange/v1/loyalty-checkout-discount"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    query = body.setdefault("query", {})
    if not isinstance(query, dict):
        raise _groups.ValidationError("--query-json query must be a JSON object")
    paging = query.setdefault("paging", {})
    if not isinstance(paging, dict):
        raise _groups.ValidationError("--query-json query.paging must be a JSON object")
    paging.setdefault("limit", 50)
    query.setdefault("sort", [{"fieldName": "createdDate", "order": "DESC"}])
    return body


def _apply_body(raw) -> dict:
    body = _object_body(raw, field="discount-json")
    checkout_id = body.get("checkoutId")
    if not isinstance(checkout_id, str) or not checkout_id.strip():
        raise _groups.ValidationError("--discount-json must include checkoutId")
    selectors = [name for name in ("rewardId", "loyaltyCouponId", "referralRewardId") if body.get(name)]
    if len(selectors) != 1:
        raise _groups.ValidationError(
            "--discount-json must include exactly one of rewardId, loyaltyCouponId, or referralRewardId"
        )
    return body


def cmd_loyalty_checkout_discounts_query(args, ctx) -> int:
    try:
        body = _query_body(getattr(args, "query_json", "{}"))
        return _groups._run_read(
            method_name="loyalty-checkout-discounts.query",
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-checkout-discounts.query", exc=exc)


def cmd_loyalty_checkout_discounts_apply(args, ctx) -> int:
    try:
        body = _apply_body(getattr(args, "discount_json", None))
        discount_selector = {
            name: body[name]
            for name in ("rewardId", "loyaltyCouponId", "referralRewardId")
            if body.get(name)
        }
        return _groups._run_write(
            method_name="loyalty-checkout-discounts.apply",
            http_method="POST",
            path=APPLY_PATH,
            body=body,
            selector={
                "kind": "loyalty-checkout-discount",
                "checkout_id": body["checkoutId"],
                "operation": "apply",
                **discount_selector,
            },
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["loyalty-checkout-discount-apply", "can-redeem-points-or-apply-customer-reward"],
            verification_notes="Verify with loyalty-checkout-discounts query for the checkout ID and inspect the eCommerce checkout discounts.",
        )
    except _groups.ValidationError as exc:
        return _groups._emit_error(ctx, method="loyalty-checkout-discounts.apply", exc=exc)
