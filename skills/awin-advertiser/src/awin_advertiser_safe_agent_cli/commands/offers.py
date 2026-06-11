from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .read_api import redact_error, require_read_context


_REQUIRED_FIELDS = {
    "title",
    "description",
    "terms",
    "type",
    "url",
    "startDate",
    "endDate",
    "appliesToAllRegions",
    "promotionCategories",
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strip(value: Any) -> str:
    return str(value or "").strip()


def _validate_offer(*, offer: dict[str, Any], offer_num: int = 1) -> None:
    if not isinstance(offer, dict):
        raise ValidationError(f"Offer #{offer_num} must be a JSON object")

    missing = [field for field in sorted(_REQUIRED_FIELDS) if field not in offer]
    if missing:
        raise ValidationError(
            f"Offer #{offer_num} is missing required field(s): {', '.join(missing)}"
        )

    offer_type = str(offer.get("type") or "").strip()
    if offer_type not in {"promotion", "voucher"}:
        raise ValidationError("Offer type must be one of promotion|voucher")

    if offer_type == "voucher" and not _strip(offer.get("voucherCode")):
        raise ValidationError("voucher type requires voucherCode")

    url = _strip(offer.get("url"))
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValidationError("Offer url must start with http:// or https://")

    title = _strip(offer.get("title"))
    if not title or not (1 <= len(title) <= 300):
        raise ValidationError("Offer title must be 1-300 characters")

    description = _strip(offer.get("description"))
    if not description or not (1 <= len(description) <= 500):
        raise ValidationError("Offer description must be 1-500 characters")

    terms = _strip(offer.get("terms"))
    if not terms or not (1 <= len(terms) <= 10000):
        raise ValidationError("Offer terms must be 1-10000 characters")

    start_date = _strip(offer.get("startDate"))
    end_date = _strip(offer.get("endDate"))
    if not start_date or not end_date:
        raise ValidationError("Offer startDate and endDate are required")
    if len(start_date) != 10 or len(end_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
        raise ValidationError("startDate and endDate must be YYYY-MM-DD")

    if offer.get("appliesToAllRegions") not in {True, False}:
        raise ValidationError("offers.create requires appliesToAllRegions to be true or false")

    if offer.get("appliesToAllRegions") is False:
        regions = offer.get("regions")
        if not isinstance(regions, list) or not regions:
            raise ValidationError("appliesToAllRegions=false requires regions list")

    promo_categories = offer.get("promotionCategories")
    if not isinstance(promo_categories, list) or not promo_categories:
        raise ValidationError("promotionCategories is required")


def _load_offer_payload(path_raw: str | None) -> tuple[dict[str, Any], Path]:
    source_path = Path(path_raw) if path_raw else Path("")
    payload = read_json_file(source_path)
    if not isinstance(payload, dict):
        raise ValidationError("--offer-file must contain one offer object")

    _validate_offer(offer=payload)
    return payload, source_path


def _build_plan(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], source_path: Path) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": "promotion/advertiser/{advertiser_id}".format(advertiser_id=advertiser_id),
        },
        "risk_level": "high",
        "risk_reasons": ["offers create"],
        "preconditions": ["Dry-run only by default", "Apply requires --apply --yes --ack-irreversible"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "offer_file": str(source_path),
            "offer_file_sha256": _sha256_of_file(source_path),
            "offer_type": payload.get("type"),
        },
        "proposed_changes": [
            {
                "resource": "offers",
                "action": "create",
                "advertiser_id": advertiser_id,
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Refuse only on transport or validation failure; review apply receipt",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current offer docs",
        },
    }


def _validate_plan(
    *,
    advertiser_id: str,
    plan_obj: Any,
    source_path: Path,
    ctx: dict[str, Any],
) -> None:
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in must contain a JSON object")

    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("--plan-in is missing baseline")

    expected_env = str(baseline.get("env_fingerprint") or "")
    if expected_env != ctx["cfg"].base_url:
        raise SafetyError("Refused: --plan-in env_fingerprint does not match the current environment")

    selector = plan_obj.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("--plan-in is missing selector")

    if str(selector.get("advertiser_id") or "") != advertiser_id:
        raise SafetyError("Refused: --plan-in selector does not match requested advertiser id")

    expected_sha = str(baseline.get("offer_file_sha256") or "")
    if not expected_sha:
        raise ValidationError("--plan-in is missing offer_file_sha256")
    if expected_sha != _sha256_of_file(source_path):
        raise SafetyError("Refused: offer file changed since --plan-in was created")


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str, response_status: int) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": "promotion/advertiser/{advertiser_id}".format(advertiser_id=advertiser_id),
        },
        "changed": True,
        "verification": {
            "ok": 200 <= int(response_status) < 300,
            "details": {
                "response_status": response_status,
            },
        },
        "diff_applied": [
            {
                "resource": "offers",
                "action": "created",
                "advertiser_id": advertiser_id,
            }
        ],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_offers_create(args, ctx) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    offer_payload, source_path = _load_offer_payload(getattr(args, "offer_file", None))

    plan = _build_plan(ctx=ctx, advertiser_id=advertiser_id, payload=offer_payload, source_path=source_path)

    if not bool(ctx.get("apply")):
        plan_path = None
        if isinstance(ctx.get("plan_out"), str):
            plan_path = write_json_file(ctx["plan_out"], plan)

        out = {
            "ok": True,
            "dry_run": True,
            "operation": "offers create",
            "advertiser_id": advertiser_id,
            "endpoint": "/promotion/advertiser/{advertiser_id}".format(advertiser_id=advertiser_id),
            "method": "POST",
            "request_payload": {"offer_type": offer_payload.get("type")},
            "plan": plan,
            "plan_out": plan_path if isinstance(ctx.get("plan_out"), str) else None,
        }
        ctx["out"].emit(out)
        ctx["audit"].write("offers.create.plan", out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: offers create requires --apply with --plan-in")

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: offers create requires --apply --yes")

    if not bool(ctx.get("ack_irreversible", False)):
        raise SafetyError("Refused: offers create requires --apply --yes --ack-irreversible")

    _validate_plan(
        advertiser_id=advertiser_id,
        plan_obj=read_json_file(ctx["plan_in"]),
        source_path=source_path,
        ctx=ctx,
    )

    headers = {"Authorization": f"Bearer {cfg.token}", "content-type": "application/json"}
    endpoint = f"promotion/advertiser/{advertiser_id}"
    http = ctx["http_client"]
    try:
        response = http.request(
            "POST",
            f"{cfg.base_url.rstrip('/')}/{endpoint}",
            headers=headers,
            params={},
            json_body=offer_payload,
        )
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), cfg.token)
        raise ValidationError(f"offers create request failed: {message}") from exc

    receipt = _build_receipt(
        ctx=ctx,
        advertiser_id=advertiser_id,
        response_status=response.status,
    )

    if bool(ctx.get("receipt_out")):
        receipt_out = write_json_file(ctx["receipt_out"], receipt)
    else:
        receipt_out = None

    result = {
        "ok": True,
        "dry_run": False,
        "operation": "offers create",
        "advertiser_id": advertiser_id,
        "endpoint": f"/promotion/advertiser/{advertiser_id}",
        "method": "POST",
        "status": response.status,
        "result": {"response_status": response.status},
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    ctx["audit"].write("offers.create.apply", result)
    ctx["out"].emit(result)
    return 0
