from __future__ import annotations

from typing import Any

from ..api import PinterestApi, resolve_access_token


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, Any]:
    if not pairs:
        return {}
    out: dict[str, Any] = {}
    for raw in pairs:
        s = (raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise RuntimeError(f"Invalid --param (expected key=value): {raw}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise RuntimeError(f"Invalid --param (empty key): {raw}")
        if k in out:
            prev = out[k]
            if isinstance(prev, list):
                prev.append(v)
            else:
                out[k] = [prev, v]
        else:
            out[k] = v
    return out


def _require_id(v: Any, *, flag: str) -> str:
    s = str(v or "").strip()
    if not s:
        raise RuntimeError(f"{flag} is required")
    return s


def _list_business_access(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    business_id = _require_id(getattr(args, "business_id", None), flag="--business-id")
    params = _parse_kv_pairs(getattr(args, "param", None))

    formatted_path = path.format(
        business_id=business_id,
        asset_id=getattr(args, "asset_id", None),
        member_id=getattr(args, "member_id", None),
        partner_id=getattr(args, "partner_id", None),
    )
    items, bookmark, pages = api.list_all(
        formatted_path,
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "business_id": business_id,
        "path": formatted_path,
        "params": params,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(stage, {"business_id": business_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_business_assets_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_business_access(args, ctx, stage="business_access.assets.list", path="/businesses/{business_id}/assets")


def cmd_business_members_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_business_access(args, ctx, stage="business_access.members.list", path="/businesses/{business_id}/members")


def cmd_business_partners_list(args: Any, ctx: dict[str, Any]) -> int:
    return _list_business_access(args, ctx, stage="business_access.partners.list", path="/businesses/{business_id}/partners")


def cmd_business_asset_members_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_id(getattr(args, "asset_id", None), flag="--asset-id")
    return _list_business_access(
        args,
        ctx,
        stage="business_access.asset_members.list",
        path="/businesses/{business_id}/assets/{asset_id}/members",
    )


def cmd_business_asset_partners_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_id(getattr(args, "asset_id", None), flag="--asset-id")
    return _list_business_access(
        args,
        ctx,
        stage="business_access.asset_partners.list",
        path="/businesses/{business_id}/assets/{asset_id}/partners",
    )


def cmd_business_member_assets_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_id(getattr(args, "member_id", None), flag="--member-id")
    return _list_business_access(
        args,
        ctx,
        stage="business_access.member_assets.list",
        path="/businesses/{business_id}/members/{member_id}/assets",
    )


def cmd_business_partner_assets_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_id(getattr(args, "partner_id", None), flag="--partner-id")
    return _list_business_access(
        args,
        ctx,
        stage="business_access.partner_assets.list",
        path="/businesses/{business_id}/partners/{partner_id}/assets",
    )

