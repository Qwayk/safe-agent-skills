from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, read_json_input, write_json_file
from .read_api import require_read_context
from .write_api import check_plan, credential_fingerprint, finish_write, post_write, response_object


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


def _load_offer_payload(path_raw: str | None) -> tuple[dict[str, Any], Path, str]:
    source_path = Path(path_raw) if path_raw else Path("")
    payload, file_digest = read_json_input(source_path)
    if not isinstance(payload, dict):
        raise ValidationError("--offer-file must contain one offer object")

    _validate_offer(offer=payload)
    return payload, source_path, file_digest


def _build_plan(*, ctx: dict[str, Any], advertiser_id: str, payload: dict[str, Any], source_path: Path, file_digest: str) -> dict[str, Any]:
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
            "credential_fingerprint": credential_fingerprint(ctx["cfg"]),
            "offer_file": str(source_path),
            "offer_file_sha256": file_digest,
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
            "notes": "Check whether Awin confirmed the offer.",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current offer docs",
        },
    }


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str) -> dict[str, Any]:
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
        "verification": {"details": {}},
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

    offer_payload, source_path, file_digest = _load_offer_payload(getattr(args, "offer_file", None))

    plan = _build_plan(ctx=ctx, advertiser_id=advertiser_id, payload=offer_payload, source_path=source_path, file_digest=file_digest)

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

    endpoint = f"promotion/advertiser/{advertiser_id}"
    check_plan(
        read_json_file(ctx["plan_in"]), cfg=cfg, advertiser_id=advertiser_id, endpoint=endpoint,
        file_field="offer_file_sha256", file_digest=file_digest, file_description="offer file",
    )

    response, details = post_write(
        ctx, endpoint, headers={"Authorization": f"Bearer {cfg.token}", "content-type": "application/json"},
        params={}, json_body=offer_payload,
    )
    if response is not None:
        data = response_object(response)
        if data and (data.get("error") or data.get("errors") or data.get("success") is False):
            details.update(state="rejected", error="Awin reported an offer error.")
        elif response.status == 200 and (not response.body.strip() or data is not None):
            details["state"] = "confirmed"
        elif response.status == 202:
            details["state"] = "pending"
        else:
            details["state"] = "unknown"

    return finish_write(
        ctx, operation="offers create", event="offers.create.apply",
        receipt=_build_receipt(ctx=ctx, advertiser_id=advertiser_id),
        details=details, next_step="Check MyOffers in Awin before creating the offer again.", fields={},
    )
