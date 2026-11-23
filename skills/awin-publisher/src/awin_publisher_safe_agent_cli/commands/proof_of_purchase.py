from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .common import (
    load_json_file,
    normalize_optional_str,
    require_proof_of_purchase_api_key,
    sha256_of_bytes,
    write_json_file,
)
from ..errors import SafetyError, ValidationError
from ..http import HttpStatusError


_ORDERS_CREATE_PATH = "/publishers/{publisher_id}/advertiser/{advertiser_id}/orders"
_CUSTOMER_ACQUISITION_VALUES = {"NEW", "RETURNING"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_orders_payload(path_raw: str | None) -> tuple[dict[str, Any], Path, str]:
    if not path_raw or not path_raw.strip():
        raise ValidationError("Missing --orders-file")
    source_path = Path(path_raw).expanduser()
    if not source_path.is_file():
        raise ValidationError(f"Orders file not found: {source_path}")
    data = source_path.read_bytes()
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValidationError(f"Orders file is not valid JSON: {source_path}") from None
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
    return normalized, source_path, sha256_of_bytes(data)


def _build_plan(*, ctx: dict[str, Any], publisher_id: str, advertiser_id: str, orders_path: Path, order_count: int,
                orders_hash: str, connection: str) -> dict[str, Any]:
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
            "orders_file_sha256": orders_hash,
            "connection_fingerprint": connection,
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
            "notes": "Check Awin’s reply for errors, then check the pending orders in Awin before calling them verified.",
        },
        "rollback": {
            "supported": False,
            "notes": "The provider docs do not define a rollback endpoint for submitted proof-of-purchase orders.",
        },
    }


def _validate_plan(plan_obj: object, *, ctx: dict[str, Any], publisher_id: str, advertiser_id: str,
                   orders_hash: str, connection: str) -> None:
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in must contain a JSON object")
    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("--plan-in is missing the baseline object")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].api_host):
        raise SafetyError("Refused: --plan-in env_fingerprint does not match the current environment")
    if baseline.get("connection_fingerprint") != connection:
        raise SafetyError("Refused: the order submission key differs from the saved plan. Save a new plan and review it first.")

    selector = plan_obj.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("--plan-in is missing the selector object")
    if str(selector.get("publisher_id") or "") != publisher_id or str(selector.get("advertiser_id") or "") != advertiser_id:
        raise SafetyError("Refused: --plan-in does not match the requested publisher/advertiser ids")

    if baseline.get("orders_file_sha256") != orders_hash:
        raise SafetyError("Refused: orders file changed since the plan was created")


def _reports_order_error(result: Any) -> bool:
    if isinstance(result, list):
        return any(_reports_order_error(item) for item in result)
    if not isinstance(result, dict):
        return False
    if result.get("error") or result.get("errors") or result.get("success") is False or result.get("accepted") is False:
        return True
    if str(result.get("status", "")).lower() in {"error", "failed", "rejected"}:
        return True
    return any(_reports_order_error(result.get(key)) for key in ("orders", "results", "result"))


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

    payload, orders_path, orders_hash = _load_orders_payload(getattr(args, "orders_file", None))
    order_count = len(payload["orders"])
    connection = sha256_of_bytes(f"{cfg.api_host}\0{api_key}".encode("utf-8"))
    plan = _build_plan(
        ctx=ctx,
        publisher_id=publisher_id,
        advertiser_id=advertiser_id,
        orders_path=orders_path,
        order_count=order_count,
        orders_hash=orders_hash,
        connection=connection,
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
        orders_hash=orders_hash,
        connection=connection,
    )

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
    }
    result = None
    status_code = None
    outcome = "outcome_unknown"
    try:
        response = http.request(
            "POST",
            f"{cfg.api_host}{_ORDERS_CREATE_PATH.format(publisher_id=publisher_id, advertiser_id=advertiser_id)}",
            headers=headers,
            json_body=payload,
        )
        status_code = response.status
        result = response.json() if response.body.strip() else None
        if _reports_order_error(result):
            outcome = "provider_reported_errors"
        elif status_code == 200:
            outcome = "accepted_pending"
    except HttpStatusError as error:
        if error.status < 500:
            raise
        status_code = error.status
    except (RuntimeError, UnicodeDecodeError, json.JSONDecodeError):
        pass

    accepted = outcome == "accepted_pending"
    outcome_message = {
        "accepted_pending": "Awin accepted the submission. Check the pending orders in Awin before reporting them as verified.",
        "provider_reported_errors": "Awin reported an error. Check which orders reached Awin before sending any again.",
        "outcome_unknown": "Awin did not confirm the submission. Check the orders in Awin before sending them again.",
    }[outcome]

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
        "changed": True if accepted else None,
        "verification": {
            "ok": False,
            "status": outcome,
            "details": {
                "response_status": status_code,
                "orders_count": order_count,
                "orders_file_sha256": orders_hash,
                "next_check": outcome_message,
            },
        },
        "diff_applied": [
            {
                "resource": "awin-proof-of-purchase-orders",
                "action": "submitted",
                "publisher_id": publisher_id,
                "advertiser_id": advertiser_id,
                "orders_count": order_count,
            }
        ] if accepted else [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = write_json_file(ctx.get("receipt_out"), receipt)

    out = {
        "ok": accepted,
        "dry_run": False,
        "operation": "proof-of-purchase.orders.create",
        "result": result if accepted else None,
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    if not accepted:
        out["error"] = outcome_message
        out["error_type"] = "OrderSubmissionUnconfirmed"
    ctx["audit"].write("proof-of-purchase.orders.create.apply", {"receipt": receipt, "receipt_out": receipt_out})
    ctx["out"].emit(out)
    return 0 if accepted else 1
