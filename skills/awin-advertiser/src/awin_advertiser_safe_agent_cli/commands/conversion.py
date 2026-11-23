from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, read_json_input, write_json_file
from .read_api import redact_error, require_read_context
from .write_api import check_plan, credential_fingerprint, finish_write, post_write, response_object


_ORDER_REQUIRED_FIELDS = {
    "orderReference",
    "amount",
    "channel",
    "currency",
    "commissionGroups",
}

_MAX_ORDERS = 1000


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _strip_value(value: Any) -> str:
    return str(value or "").strip()


def _validate_commission_groups(*, order: dict[str, Any], order_num: int) -> None:
    groups = order.get("commissionGroups")
    if not isinstance(groups, list) or not groups:
        raise ValidationError(f"Order #{order_num} commissionGroups must be a non-empty list")

    for idx, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            raise ValidationError(f"Order #{order_num} commissionGroups[{idx}] must be an object")
        if "code" not in group:
            raise ValidationError(f"Order #{order_num} commissionGroups[{idx}] is missing required field: code")
        if "amount" not in group:
            raise ValidationError(f"Order #{order_num} commissionGroups[{idx}] is missing required field: amount")


def _validate_order_identity(*, order: dict[str, Any], order_num: int) -> None:
    has_awc = bool(_strip_value(order.get("awc")))
    has_pub = bool(_strip_value(order.get("publisherId")))
    has_click = bool(_strip_value(order.get("clickTime")))

    if not has_awc and not (has_pub and has_click):
        raise ValidationError(
            f"Order #{order_num} must include either awc, or both publisherId and clickTime"
        )


def _validate_order(*, order: dict[str, Any], order_num: int) -> None:
    if not isinstance(order, dict):
        raise ValidationError(f"Order #{order_num} must be a JSON object")

    missing = [key for key in sorted(_ORDER_REQUIRED_FIELDS) if key not in order]
    if missing:
        raise ValidationError(f"Order #{order_num} is missing required field(s): {', '.join(missing)}")

    _validate_commission_groups(order=order, order_num=order_num)
    _validate_order_identity(order=order, order_num=order_num)


def _load_orders_payload(path_raw: str | None) -> tuple[dict[str, Any], Path, int, str]:
    source_path = Path(path_raw) if path_raw else Path("")
    payload, file_digest = read_json_input(source_path)
    if isinstance(payload, list):
        payload_obj = {"orders": payload}
    elif isinstance(payload, dict):
        payload_obj = payload
        if "webhook" in payload_obj:
            raise ValidationError(
                "--orders-file must not include a top-level webhook object; pass --webhook-url instead"
            )
    else:
        raise ValidationError("--orders-file must be a JSON object with an orders array or a JSON array")

    orders = payload_obj.get("orders")
    if not isinstance(orders, list):
        raise ValidationError("--orders-file must include an orders array")
    if not orders:
        raise ValidationError("--orders-file must include at least one order")
    if len(orders) > _MAX_ORDERS:
        raise ValidationError(f"Maximum supported order batch is {_MAX_ORDERS}")

    for idx, order in enumerate(orders, start=1):
        _validate_order(order=order, order_num=idx)

    payload_obj["orders"] = list(orders)
    return payload_obj, source_path, len(orders), file_digest


def _build_plan(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], source_path: Path, file_digest: str, webhook_url: str | None) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": "s2s/advertiser/{advertiser_id}/orders".format(advertiser_id=advertiser_id),
            "webhook_url": webhook_url,
        },
        "risk_level": "high",
        "risk_reasons": ["conversion orders create"],
        "preconditions": ["Dry-run only by default", "Apply requires --apply --yes --ack-irreversible"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "credential_fingerprint": credential_fingerprint(ctx["cfg"]),
            "orders_file": str(source_path),
            "orders_file_sha256": file_digest,
            "orders_count": len(payload.get("orders") or []),
        },
        "proposed_changes": [
            {
                "resource": "conversion.orders",
                "action": "create",
                "advertiser_id": advertiser_id,
                "orders_count": len(payload.get("orders") or []),
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Check which orders Awin registered and which need follow-up.",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current conversion API docs",
        },
    }


def _build_request_payload(*, orders_payload: dict[str, Any], webhook_url: str | None) -> dict[str, Any]:
    payload = {"orders": orders_payload.get("orders") or []}
    if webhook_url:
        payload["webhook"] = {"url": webhook_url}
    return payload


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], file_digest: str) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": f"s2s/advertiser/{advertiser_id}/orders",
        },
        "verification": {
            "details": {
                "orders_count": len(payload.get("orders") or []),
                "orders_file_sha256": file_digest,
            },
        },
        "diff_applied": [
            {
                "resource": "conversion.orders",
                "action": "created",
                "advertiser_id": advertiser_id,
                "orders_count": len(payload.get("orders") or []),
            }
        ],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_conversion_orders_create(args, ctx) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    orders_payload, source_path, order_count, file_digest = _load_orders_payload(getattr(args, "orders_file", None))
    webhook_url = _strip_value(getattr(args, "webhook_url", None)) or None

    plan = _build_plan(
        ctx=ctx,
        advertiser_id=advertiser_id,
        payload=orders_payload,
        source_path=source_path,
        file_digest=file_digest,
        webhook_url=webhook_url,
    )

    if not bool(ctx.get("apply")):
        request_payload = _build_request_payload(orders_payload=orders_payload, webhook_url=webhook_url)
        plan_path = None
        if isinstance(ctx.get("plan_out"), str):
            plan_path = write_json_file(ctx["plan_out"], plan)

        out = {
            "ok": True,
            "dry_run": True,
            "operation": "conversion orders create",
            "advertiser_id": advertiser_id,
            "endpoint": "/s2s/advertiser/{advertiser_id}/orders".format(advertiser_id=advertiser_id),
            "method": "POST",
            "orders_count": order_count,
            "request_payload": {
                "orders_count": len(request_payload.get("orders") or []),
                "has_webhook": bool(webhook_url),
            },
            "plan": plan,
            "plan_out": plan_path if isinstance(ctx.get("plan_out"), str) else None,
        }
        ctx["out"].emit(out)
        ctx["audit"].write("conversion.orders.create.plan", out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: conversion orders create requires --apply with --plan-in")

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: conversion orders create requires --apply --yes")

    if not bool(ctx.get("ack_irreversible", False)):
        raise SafetyError("Refused: conversion orders create requires --apply --yes --ack-irreversible")

    endpoint = f"s2s/advertiser/{advertiser_id}/orders"
    selector = check_plan(
        read_json_file(ctx["plan_in"]), cfg=cfg, advertiser_id=advertiser_id, endpoint=endpoint,
        file_field="orders_file_sha256", file_digest=file_digest, file_description="orders file",
    )
    if (_strip_value(selector.get("webhook_url")) or None) != webhook_url:
        raise SafetyError("Refused: --plan-in webhook does not match --webhook-url")

    request_payload = _build_request_payload(orders_payload=orders_payload, webhook_url=webhook_url)
    response, details = post_write(
        ctx, endpoint, headers={"x-api-key": cfg.token, "content-type": "application/json"},
        params={}, json_body=request_payload,
    )
    if response is not None:
        payload = response_object(response)
        details.update(_conversion_result(response.status, payload, order_count, cfg.token))

    return finish_write(
        ctx, operation="conversion orders create", event="conversion.orders.create.apply",
        receipt=_build_receipt(
            ctx=ctx, advertiser_id=advertiser_id, payload=request_payload,
            file_digest=file_digest,
        ),
        details=details,
        next_step="Check these orders in Awin or check the webhook you supplied before sending any again.",
        fields={"orders_count": order_count, "has_webhook": bool(webhook_url)},
    )


def _conversion_result(status: int, payload: dict | None, order_count: int, token: str | None) -> dict[str, Any]:
    data = payload or {}
    details: dict[str, Any] = {"state": "unknown"}
    for source, field in (("successfulOrders", "successful_orders"), ("pendingOrders", "pending_orders"), ("failedOrders", "failed_orders")):
        if isinstance(data.get(source), list):
            details[field] = len(data[source])
    if isinstance(data.get("batchId"), str):
        details["batch_id"] = redact_error(data["batchId"], token)
    failed = data.get("failedOrders")
    if isinstance(failed, list):
        details["failed_order_references"] = [
            redact_error(order["orderReference"], token)
            for item in failed if isinstance(item, dict)
            for order in [item.get("order", item)]
            if isinstance(order, dict) and isinstance(order.get("orderReference"), str)
        ]

    if status == 206 or details.get("failed_orders"):
        details["state"] = "partial" if status == 206 or details.get("successful_orders") else "rejected"
    elif status == 202 or details.get("pending_orders"):
        details["state"] = "pending"
    elif status == 200 and details.get("successful_orders") == order_count:
        details["state"] = "confirmed"
    return details
