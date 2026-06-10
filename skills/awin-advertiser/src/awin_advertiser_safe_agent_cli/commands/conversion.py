from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .read_api import redact_error, require_read_context


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


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _load_orders_payload(path_raw: str | None) -> tuple[dict[str, Any], Path, int]:
    source_path = Path(path_raw) if path_raw else Path("")
    payload = read_json_file(source_path)
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
    return payload_obj, source_path, len(orders)


def _build_plan(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], source_path: Path, webhook_url: str | None) -> dict[str, Any]:
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
            "orders_file": str(source_path),
            "orders_file_sha256": _sha256_of_file(source_path),
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
            "notes": "Refuse only on transport or validation failure; review apply summary and receipt summary",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current conversion API docs",
        },
    }


def _validate_plan(
    *,
    advertiser_id: str,
    plan_obj: Any,
    source_path: Path,
    webhook_url: str | None,
    ctx: dict[str, Any],
) -> None:
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in must contain a JSON object")

    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("--plan-in is missing baseline")

    baseline_env = str(baseline.get("env_fingerprint") or "")
    if baseline_env != ctx["cfg"].base_url:
        raise SafetyError("Refused: --plan-in env_fingerprint does not match the current environment")

    selector = plan_obj.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("--plan-in is missing selector")

    if str(selector.get("advertiser_id") or "") != advertiser_id:
        raise SafetyError("Refused: --plan-in selector does not match requested advertiser id")

    expected_sha = str(baseline.get("orders_file_sha256") or "")
    if not expected_sha:
        raise ValidationError("--plan-in is missing orders_file_sha256")
    current_sha = _sha256_of_file(source_path)
    if expected_sha and expected_sha != current_sha:
        raise SafetyError("Refused: orders file changed since --plan-in was created")

    expected_webhook = selector.get("webhook_url")
    current_webhook = _strip_value(webhook_url) or None
    if _strip_value(expected_webhook) != _strip_value(current_webhook):
        raise SafetyError("Refused: --plan-in webhook does not match --webhook-url")


def _build_request_payload(*, orders_payload: dict[str, Any], webhook_url: str | None) -> dict[str, Any]:
    payload = {"orders": orders_payload.get("orders") or []}
    if webhook_url:
        payload["webhook"] = {"url": webhook_url}
    return payload


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], response_status: int, source_path: Path) -> dict[str, Any]:
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
        "changed": True,
        "verification": {
            "ok": 200 <= int(response_status) < 300,
            "details": {
                "response_status": response_status,
                "orders_count": len(payload.get("orders") or []),
                "orders_file_sha256": _sha256_of_file(source_path),
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

    orders_payload, source_path, order_count = _load_orders_payload(getattr(args, "orders_file", None))
    webhook_url = _strip_value(getattr(args, "webhook_url", None)) or None

    plan = _build_plan(
        ctx=ctx,
        advertiser_id=advertiser_id,
        payload=orders_payload,
        source_path=source_path,
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

    plan_in = ctx.get("plan_in")
    if plan_in:
        _plan_from_file = read_json_file(plan_in)
        _validate_plan(
            ctx=ctx,
            plan_obj=_plan_from_file,
            advertiser_id=advertiser_id,
            source_path=source_path,
            webhook_url=webhook_url,
        )

    request_payload = _build_request_payload(orders_payload=orders_payload, webhook_url=webhook_url)
    headers = {
        "x-api-key": cfg.token,
        "content-type": "application/json",
    }
    endpoint = f"s2s/advertiser/{advertiser_id}/orders"

    http = ctx["http_client"]
    try:
        response = http.request(
            "POST",
            f"{cfg.base_url.rstrip('/')}/{endpoint}",
            headers=headers,
            params={},
            json_body=request_payload,
        )
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), cfg.token)
        raise ValidationError(f"conversion orders create request failed: {message}") from exc

    receipt = _build_receipt(
        ctx=ctx,
        advertiser_id=advertiser_id,
        payload=request_payload,
        response_status=response.status,
        source_path=source_path,
    )

    if bool(ctx.get("receipt_out")):
        receipt_out = write_json_file(ctx["receipt_out"], receipt)
    else:
        receipt_out = None

    result = {
        "ok": True,
        "dry_run": False,
        "operation": "conversion orders create",
        "advertiser_id": advertiser_id,
        "endpoint": f"/s2s/advertiser/{advertiser_id}/orders",
        "method": "POST",
        "status": response.status,
        "orders_count": len(request_payload.get("orders") or []),
        "has_webhook": bool(webhook_url),
        "result": {"response_status": response.status},
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    ctx["audit"].write("conversion.orders.create.apply", result)
    ctx["out"].emit(result)
    return 0
