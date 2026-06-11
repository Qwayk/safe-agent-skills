from __future__ import annotations

import time
from typing import Any

from ..runtime import get_api


def add_tier_commands(tier_sub) -> None:
    tier_list = tier_sub.add_parser("list", help="List tiers")
    tier_list.add_argument("--limit", type=int, default=50)
    tier_list.add_argument("--page", type=int, default=None, help="Page number (default: fetch all pages)")
    tier_list.add_argument("--order", default=None)
    tier_list.add_argument("--filter", default=None)
    tier_list.add_argument("--fields", default=None)
    tier_list.add_argument("--include", default=None, help="Comma-separated include (e.g. monthly_price,yearly_price,benefits)")
    tier_list.set_defaults(func=cmd_tier_list)

    tier_get = tier_sub.add_parser("get", help="Get a tier by id")
    tier_get.add_argument("--id", required=True)
    tier_get.add_argument("--include", default=None)
    tier_get.set_defaults(func=cmd_tier_get)

    tier_create = tier_sub.add_parser("create", help="Create a tier (dry-run by default)")
    tier_create.add_argument("--name", required=True)
    tier_create.add_argument("--description", default=None)
    tier_create.add_argument("--welcome-page-url", default=None)
    tier_create.add_argument("--visibility", choices=("public", "none"), default=None)
    tier_create.add_argument("--monthly-price", type=int, default=None, help="Price in smallest currency unit (e.g. cents)")
    tier_create.add_argument("--yearly-price", type=int, default=None, help="Price in smallest currency unit (e.g. cents)")
    tier_create.add_argument("--currency", default=None, help="Three-letter ISO code (e.g. usd)")
    tier_create.add_argument("--benefit", action="append", default=[], help="Benefit line (repeatable)")
    tier_create.set_defaults(func=cmd_tier_create)

    tier_update = tier_sub.add_parser("update", help="Update a tier (dry-run by default)")
    tier_update.add_argument("--id", required=True)
    tier_update.add_argument("--name", default=None, help="If omitted, keeps current name (required by API)")
    tier_update.add_argument("--description", default=None)
    tier_update.add_argument("--welcome-page-url", default=None)
    tier_update.add_argument("--visibility", choices=("public", "none"), default=None)
    tier_update.add_argument("--active", type=str, default=None, help="true|false (archive/unarchive tier)")
    tier_update.add_argument("--monthly-price", type=int, default=None)
    tier_update.add_argument("--yearly-price", type=int, default=None)
    tier_update.add_argument("--currency", default=None)
    tier_update.add_argument("--benefit", action="append", default=None, help="Replace benefits list (repeatable)")
    tier_update.set_defaults(func=cmd_tier_update)


def _parse_boolish(value: str | None) -> bool | None:
    if value is None:
        return None
    s = value.strip().lower()
    if s in ("true", "1", "yes", "y", "on"):
        return True
    if s in ("false", "0", "no", "n", "off"):
        return False
    raise RuntimeError(f"Invalid boolean value: {value!r} (expected true/false)")


def _browse_all(api, *, params: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    tiers: list[dict[str, Any]] = []
    meta: dict[str, Any] | None = None
    page = 1
    limit = int(params.get("limit") or 50)
    while True:
        res = api.tiers_browse(params={**params, "page": page, "limit": limit})
        batch = res.get("tiers")
        if not isinstance(batch, list):
            raise RuntimeError(f"Unexpected response (missing tiers list): {res}")
        for t in batch:
            if isinstance(t, dict):
                tiers.append(t)
        meta = res.get("meta") if isinstance(res.get("meta"), dict) else meta
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        next_page = pagination.get("next") if isinstance(pagination, dict) else None
        if not next_page:
            break
        page = int(next_page)
    return tiers, meta


def _extract_tier_from_read(obj: dict[str, Any], *, tier_id: str) -> dict[str, Any]:
    tiers = obj.get("tiers") or []
    if not isinstance(tiers, list) or not tiers or not isinstance(tiers[0], dict):
        raise RuntimeError(f"Tier not found: {tier_id}")
    return tiers[0]


def _verify_requested_fields(*, verified_tier: dict[str, Any], requested: dict[str, Any]) -> None:
    for key, value in requested.items():
        if verified_tier.get(key) != value:
            raise RuntimeError(f"Verification failed: {key} mismatch")


def cmd_tier_list(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit}
    if args.order:
        params["order"] = args.order
    if args.filter:
        params["filter"] = args.filter
    if args.fields:
        params["fields"] = args.fields
    if args.include:
        params["include"] = args.include

    if args.page is not None:
        params["page"] = args.page
        res = api.tiers_browse(params=params)
        ctx["out"].print(res)
        return 0

    tiers, meta = _browse_all(api, params=params)
    ctx["out"].print({"tiers": tiers, "meta": meta, "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(tiers)}})
    return 0


def cmd_tier_get(args, ctx) -> int:
    api = get_api(ctx)
    res = api.tiers_read_by_id(args.id, params={"include": args.include} if args.include else None)
    ctx["out"].print(res)
    return 0


def cmd_tier_create(args, ctx) -> int:
    tier: dict[str, Any] = {"name": args.name}
    if args.description is not None:
        tier["description"] = args.description
    if args.welcome_page_url is not None:
        tier["welcome_page_url"] = args.welcome_page_url
    if args.visibility is not None:
        tier["visibility"] = args.visibility
    if args.monthly_price is not None:
        tier["monthly_price"] = int(args.monthly_price)
    if args.yearly_price is not None:
        tier["yearly_price"] = int(args.yearly_price)
    if args.currency is not None:
        tier["currency"] = args.currency
    benefits = [b for b in (args.benefit or []) if isinstance(b, str) and b.strip()]
    if benefits:
        tier["benefits"] = benefits

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "create": tier})
        return 0

    api = get_api(ctx)
    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-tier.create"
        backup.write_before_after(
            kind="tier",
            resource_id=f"name:{args.name}",
            slug=None,
            action="tier.create",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "create": {"name": args.name}},
        )

    res = api.tiers_create({"tiers": [tier]})
    created = _extract_tier_from_read(res, tier_id="(created)")
    tier_id = created.get("id") if isinstance(created.get("id"), str) else None
    verified = api.tiers_read_by_id(tier_id) if isinstance(tier_id, str) and tier_id else res
    v_tier = _extract_tier_from_read(verified, tier_id=str(tier_id or "(created)"))
    _verify_requested_fields(verified_tier=v_tier, requested=tier)

    ctx["audit"].write("tier.create", {"apply": True, "name": args.name})
    if backup is not None:
        backup.write_before_after(
            kind="tier",
            resource_id=f"id:{tier_id}" if isinstance(tier_id, str) else f"name:{args.name}",
            slug=None,
            action="tier.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id},
        )

    ctx["out"].print({"ok": True, "tier_id": tier_id, "created": {"name": args.name}})
    return 0


def cmd_tier_update(args, ctx) -> int:
    api = get_api(ctx)
    current = api.tiers_read_by_id(args.id)
    cur = _extract_tier_from_read(current, tier_id=args.id)

    patch: dict[str, Any] = {}
    if args.name is not None:
        patch["name"] = args.name
    if args.description is not None:
        patch["description"] = args.description
    if args.welcome_page_url is not None:
        patch["welcome_page_url"] = args.welcome_page_url
    if args.visibility is not None:
        patch["visibility"] = args.visibility
    b = _parse_boolish(args.active)
    if b is not None:
        patch["active"] = b
    if args.monthly_price is not None:
        patch["monthly_price"] = int(args.monthly_price)
    if args.yearly_price is not None:
        patch["yearly_price"] = int(args.yearly_price)
    if args.currency is not None:
        patch["currency"] = args.currency
    if args.benefit is not None:
        benefits = [b for b in (args.benefit or []) if isinstance(b, str) and b.strip()]
        patch["benefits"] = benefits

    if not patch:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    # Required by API; if not set explicitly, preserve current name.
    patch.setdefault("name", cur.get("name"))
    if not isinstance(patch.get("name"), str) or not str(patch.get("name") or "").strip():
        raise RuntimeError("Tier name is required")

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "tier_id": args.id, "planned": {"fields": sorted(patch.keys())}})
        return 0

    payload = {"tiers": [{**patch, "id": args.id, "updated_at": cur.get("updated_at")}]}

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-tier.update"
        backup.write_before_after(
            kind="tier",
            resource_id=f"id:{args.id}",
            slug=None,
            action="tier.update",
            before=current,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    _ = api.tiers_update(args.id, payload)
    verified = api.tiers_read_by_id(args.id)
    v_tier = _extract_tier_from_read(verified, tier_id=args.id)
    _verify_requested_fields(verified_tier=v_tier, requested=patch)

    ctx["audit"].write("tier.update", {"apply": True, "tier_id": args.id, "fields": sorted(patch.keys())})
    if backup is not None:
        backup.write_before_after(
            kind="tier",
            resource_id=f"id:{args.id}",
            slug=None,
            action="tier.update",
            before=current,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    ctx["out"].print({"ok": True, "tier_id": args.id, "updated_fields": sorted(patch.keys())})
    return 0
