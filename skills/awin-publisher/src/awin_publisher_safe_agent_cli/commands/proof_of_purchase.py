from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .common import (
    load_json_file,
    normalize_optional_str,
    require_proof_of_purchase_api_key,
    request_json,
    sha256_of_file,
    write_json_file,
)
from ..errors import SafetyError, ValidationError


_ORDERS_CREATE_PATH = "/publishers/{publisher_id}/advertiser/{advertiser_id}/orders"
_CUSTOMER_ACQUISITION_VALUES = {"NEW", "RETURNING"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_orders_payload(path_raw: str | None) -> tuple[dict[str, Any], Path]:
    payload, source_path = load_json_file(path_raw, label="--orders-file")
    if isinstance(payload, list):
        normalized = {"orders": payload}
    elif isinstance(payload, dict):
        normalized = payload
    else:
        raise ValidationError("--orders-file must be a JSON object with an orders array or a JSON array")

    orders = normalized.get("orders")
    if not isinstance(orders, list):
        raise ValidationError("--orders-file must contain an orders array")
    if not orders:
        raise ValidationError("--orders-file must contain at least one order")
    if len(orders) > 1000:
        raise ValidationError("Proof of purchase supports at most 1000 orders per request")

    for idx, order in enumerate(orders, start=1):
        if not isinstance(order, dict):
            raise ValidationError(f"Order #{idx} must be a JSON object")
        for field in ("orderReference", "amount", "currency", "transactionTime"):
            if field not in order:
                raise ValidationError(f"Order #{idx} is missing required field: {field}")
        customer_acquisition = normalize_optional_str(order.get("customerAcquisition"))
        if customer_acquisition and customer_acquisition not in _CUSTOMER_ACQUISITION_VALUES:
            raise ValidationError(f"Order #{idx} has invalid customerAcquisition. Use NEW or RETURNING")
    return normalized, source_path


def _build_plan(*, ctx: dict[str, Any], publisher_id: str, advertiser_id: str, orders_path: Path, order_count: int) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].api_host,
        "command": ctx.get("command_str"),
        "selector": {
            "publisher_id": publisher_id,
            "advertiser_id": advertiser_id,
        },
        "risk_level": "high",
        "risk_reasons": ["remote-write", "proof-of-purchase-orders"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].api_host,
            "orders_file": str(orders_path),
            "orders_file_sha256": sha256_of_file(orders_path),
        },
        "proposed_changes": [
            {
                "resource": "awin-proof-of-purchase-orders",
                "action": "create",
                "publisher_id": publisher_id,
                "advertiser_id": advertiser_id,
                "orders_count": order_count,
            }
        ],
        "verification_plan": {
            "type": "provider-acceptance",
            "notes": "Verify the API accepted the batch and review the returned payload for order-level errors.",
        },
        "rollback": {
            "supported": False,
            "notes": "The provider docs do not define a rollback endpoint for submitted proof-of-purchase orders.",
        },
    }


def _validate_plan(plan_obj: object, *, ctx: dict[str, Any], publisher_id: str, advertiser_id: str, orders_path: Path) -> None:
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in must contain a JSON object")
    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("--plan-in is missing the baseline object")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].api_host):
        raise SafetyError("Refused: --plan-in env_fingerprint does not match the current environment")

    selector = plan_obj.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("--plan-in is missing the selector object")
    if str(selector.get("publisher_id") or "") != publisher_id or str(selector.get("advertiser_id") or "") != advertiser_id:
        raise SafetyError("Refused: --plan-in does not match the requested publisher/advertiser ids")

    expected_sha = str(baseline.get("orders_file_sha256") or "")
    actual_sha = sha256_of_file(orders_path)
    if not expected_sha or expected_sha != actual_sha:
        raise SafetyError("Refused: orders file changed since the plan was created")


def cmd_proof_of_purchase_orders_create(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    api_key = require_proof_of_purchase_api_key(cfg)

    publisher_id = str(args.publisher_id).strip()
    advertiser_id = str(args.advertiser_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    payload, orders_path = _load_orders_payload(getattr(args, "orders_file", None))
    order_count = len(payload["orders"])
    plan = _build_plan(
        ctx=ctx,
        publisher_id=publisher_id,
        advertiser_id=advertiser_id,
        orders_path=orders_path,
        order_count=order_count,
    )

    if not bool(ctx.get("apply")):
        plan_out = write_json_file(ctx.get("plan_out"), plan)
        out = {
            "ok": True,
            "dry_run": True,
            "operation": "proof-of-purchase.orders.create",
            "plan": plan,
            "plan_out": plan_out,
            "metadata": {
                "publisher_id": publisher_id,
                "advertiser_id": advertiser_id,
                "orders_count": order_count,
                "orders_file": str(orders_path),
            },
        }
        ctx["audit"].write("proof-of-purchase.orders.create.plan", out)
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: proof-of-purchase order creation requires --apply --yes")

    plan_in = ctx.get("plan_in")
    if not plan_in:
        raise SafetyError("Refused: proof-of-purchase order creation requires --apply --yes --plan-in")

    plan_obj, _ = load_json_file(plan_in, label="--plan-in")
    _validate_plan(
        plan_obj,
        ctx=ctx,
        publisher_id=publisher_id,
        advertiser_id=advertiser_id,
        orders_path=orders_path,
    )

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
    }
    result, status_code = request_json(
        http,
        method="POST",
        url=f"{cfg.api_host}{_ORDERS_CREATE_PATH.format(publisher_id=publisher_id, advertiser_id=advertiser_id)}",
        headers=headers,
        json_body=payload,
        label="proof of purchase orders create",
    )

    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].api_host,
        "command": ctx.get("command_str"),
        "selector": {
            "publisher_id": publisher_id,
            "advertiser_id": advertiser_id,
        },
        "changed": True,
        "verification": {
            "ok": status_code == 200,
            "details": {
                "response_status": status_code,
                "orders_count": order_count,
                "orders_file_sha256": sha256_of_file(orders_path),
            },
        },
        "diff_applied": [
            {
                "resource": "awin-proof-of-purchase-orders",
                "action": "created",
                "publisher_id": publisher_id,
                "advertiser_id": advertiser_id,
                "orders_count": order_count,
            }
        ],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = write_json_file(ctx.get("receipt_out"), receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "operation": "proof-of-purchase.orders.create",
        "result": result,
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    ctx["audit"].write("proof-of-purchase.orders.create.apply", out)
    ctx["out"].emit(out)
    return 0
