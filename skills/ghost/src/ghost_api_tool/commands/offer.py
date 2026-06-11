from __future__ import annotations

import time
from typing import Any

from ..runtime import get_api


def add_offer_commands(offer_sub) -> None:
    offer_list = offer_sub.add_parser("list", help="List offers")
    offer_list.add_argument("--limit", type=int, default=50)
    offer_list.add_argument("--page", type=int, default=None)
    offer_list.add_argument("--order", default=None)
    offer_list.add_argument("--filter", default=None)
    offer_list.add_argument("--fields", default=None)
    offer_list.set_defaults(func=cmd_offer_list)

    offer_get = offer_sub.add_parser("get", help="Get an offer by id")
    offer_get.add_argument("--id", required=True)
    offer_get.set_defaults(func=cmd_offer_get)

    offer_create = offer_sub.add_parser("create", help="Create an offer (dry-run by default)")
    offer_create.add_argument("--name", required=True)
    offer_create.add_argument("--code", required=True)
    offer_create.add_argument("--type", choices=("percent", "fixed"), required=True)
    offer_create.add_argument("--cadence", choices=("month", "year"), required=True)
    offer_create.add_argument("--duration", choices=("once", "forever", "repeating"), required=True)
    offer_create.add_argument("--amount", type=int, required=True, help="Discount in smallest currency unit or percent")
    offer_create.add_argument("--tier-id", required=True, help="Tier id to apply the offer to")
    offer_create.add_argument("--display-title", default=None)
    offer_create.add_argument("--display-description", default=None)
    offer_create.add_argument("--duration-in-months", type=int, default=None)
    offer_create.add_argument("--currency", default=None, help="Required when type=fixed; must match tier currency")
    offer_create.add_argument("--currency-restriction", type=str, default=None, help="true|false")
    offer_create.set_defaults(func=cmd_offer_create)

    offer_update = offer_sub.add_parser("update", help="Update an offer (dry-run by default)")
    offer_update.add_argument("--id", required=True)
    offer_update.add_argument("--name", default=None)
    offer_update.add_argument("--code", default=None)
    offer_update.add_argument("--display-title", default=None)
    offer_update.add_argument("--display-description", default=None)
    offer_update.set_defaults(func=cmd_offer_update)


def _parse_boolish(value: str | None) -> bool | None:
    if value is None:
        return None
    s = value.strip().lower()
    if s in ("true", "1", "yes", "y", "on"):
        return True
    if s in ("false", "0", "no", "n", "off"):
        return False
    raise RuntimeError(f"Invalid boolean value: {value!r} (expected true/false)")


def _extract_offer_from_read(obj: dict[str, Any], *, offer_id: str) -> dict[str, Any]:
    offers = obj.get("offers") or []
    if not isinstance(offers, list) or not offers or not isinstance(offers[0], dict):
        raise RuntimeError(f"Offer not found: {offer_id}")
    return offers[0]


def _verify_requested_fields(*, verified_offer: dict[str, Any], requested: dict[str, Any]) -> None:
    for key, value in requested.items():
        if key == "tier":
            want = requested.get("tier") if isinstance(requested.get("tier"), dict) else {}
            got = verified_offer.get("tier") if isinstance(verified_offer.get("tier"), dict) else {}
            if got.get("id") != want.get("id"):
                raise RuntimeError("Verification failed: tier.id mismatch")
            continue
        if verified_offer.get(key) != value:
            raise RuntimeError(f"Verification failed: {key} mismatch")


def cmd_offer_list(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit}
    if args.page is not None:
        params["page"] = args.page
    if args.order:
        params["order"] = args.order
    if args.filter:
        params["filter"] = args.filter
    if args.fields:
        params["fields"] = args.fields
    res = api.offers_browse(params=params)
    ctx["out"].print(res)
    return 0


def cmd_offer_get(args, ctx) -> int:
    api = get_api(ctx)
    res = api.offers_read_by_id(args.id)
    ctx["out"].print(res)
    return 0


def cmd_offer_create(args, ctx) -> int:
    offer: dict[str, Any] = {
        "name": args.name,
        "code": args.code,
        "type": args.type,
        "cadence": args.cadence,
        "duration": args.duration,
        "amount": int(args.amount),
        "tier": {"id": args.tier_id},
    }
    if args.display_title is not None:
        offer["display_title"] = args.display_title
    if args.display_description is not None:
        offer["display_description"] = args.display_description
    if args.duration_in_months is not None:
        offer["duration_in_months"] = int(args.duration_in_months)
    if args.currency is not None:
        offer["currency"] = args.currency
    b = _parse_boolish(args.currency_restriction)
    if b is not None:
        offer["currency_restriction"] = b

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "create": offer})
        return 0

    api = get_api(ctx)
    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-offer.create"
        backup.write_before_after(
            kind="offer",
            resource_id=f"name:{args.name}",
            slug=str(args.code or ""),
            action="offer.create",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "create": {"name": args.name, "code": args.code}},
        )

    res = api.offers_create({"offers": [offer]})
    created = _extract_offer_from_read(res, offer_id="(created)")
    offer_id = created.get("id") if isinstance(created.get("id"), str) else None
    verified = api.offers_read_by_id(offer_id) if isinstance(offer_id, str) and offer_id else res
    v_offer = _extract_offer_from_read(verified, offer_id=str(offer_id or "(created)"))
    _verify_requested_fields(verified_offer=v_offer, requested=offer)

    ctx["audit"].write("offer.create", {"apply": True, "name": args.name, "code": args.code})
    if backup is not None:
        backup.write_before_after(
            kind="offer",
            resource_id=f"id:{offer_id}" if isinstance(offer_id, str) else f"name:{args.name}",
            slug=str(v_offer.get("code") or args.code or ""),
            action="offer.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id},
        )

    ctx["out"].print({"ok": True, "offer_id": offer_id, "created": {"name": args.name, "code": args.code}})
    return 0


def cmd_offer_update(args, ctx) -> int:
    api = get_api(ctx)
    current = api.offers_read_by_id(args.id)
    cur = _extract_offer_from_read(current, offer_id=args.id)

    patch: dict[str, Any] = {}
    if args.name is not None:
        patch["name"] = args.name
    if args.code is not None:
        patch["code"] = args.code
    if args.display_title is not None:
        patch["display_title"] = args.display_title
    if args.display_description is not None:
        patch["display_description"] = args.display_description

    if not patch:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "offer_id": args.id, "planned": {"fields": sorted(patch.keys())}})
        return 0

    payload = {"offers": [{**patch, "id": args.id, "updated_at": cur.get("updated_at")}]}

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-offer.update"
        backup.write_before_after(
            kind="offer",
            resource_id=f"id:{args.id}",
            slug=str(cur.get("code") or ""),
            action="offer.update",
            before=current,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    _ = api.offers_update(args.id, payload)
    verified = api.offers_read_by_id(args.id)
    v_offer = _extract_offer_from_read(verified, offer_id=args.id)
    _verify_requested_fields(verified_offer=v_offer, requested=patch)

    ctx["audit"].write("offer.update", {"apply": True, "offer_id": args.id, "fields": sorted(patch.keys())})
    if backup is not None:
        backup.write_before_after(
            kind="offer",
            resource_id=f"id:{args.id}",
            slug=str(v_offer.get("code") or ""),
            action="offer.update",
            before=current,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    ctx["out"].print({"ok": True, "offer_id": args.id, "updated_fields": sorted(patch.keys())})
    return 0

