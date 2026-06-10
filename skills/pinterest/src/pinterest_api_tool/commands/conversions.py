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


def cmd_conversions_tags_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")

    params = _parse_kv_pairs(args.param)
    items, bookmark, pages = api.list_all(
        f"/ad_accounts/{ad_account_id}/conversion_tags",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "path": f"/ad_accounts/{ad_account_id}/conversion_tags",
        "params": params,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("ads.conversions.tags.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_conversions_tags_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    tag_id = str(args.id).strip()
    if not tag_id:
        raise RuntimeError("--id is required")

    params = _parse_kv_pairs(args.param)
    data = api.get(f"/ad_accounts/{ad_account_id}/conversion_tags/{tag_id}", params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "conversion_tag_id": tag_id,
        "path": f"/ad_accounts/{ad_account_id}/conversion_tags/{tag_id}",
        "params": params,
        "data": data,
    }
    ctx["audit"].write("ads.conversions.tags.get", {"ad_account_id": ad_account_id, "conversion_tag_id": tag_id})
    ctx["out"].emit(out)
    return 0


def _conversions_get(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    full_path = path.format(ad_account_id=ad_account_id)
    data = api.get(full_path, params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "path": full_path,
        "params": params,
        "data": data,
    }
    ctx["audit"].write(stage, {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_conversions_page_visit(args: Any, ctx: dict[str, Any]) -> int:
    return _conversions_get(
        args,
        ctx,
        stage="ads.conversions.page_visit",
        path="/ad_accounts/{ad_account_id}/conversion_tags/page_visit",
    )


def cmd_conversions_ocpm_eligible(args: Any, ctx: dict[str, Any]) -> int:
    return _conversions_get(
        args,
        ctx,
        stage="ads.conversions.ocpm_eligible",
        path="/ad_accounts/{ad_account_id}/conversion_tags/ocpm_eligible",
    )


def cmd_conversions_eqs(args: Any, ctx: dict[str, Any]) -> int:
    return _conversions_get(args, ctx, stage="ads.conversions.eqs", path="/ad_accounts/{ad_account_id}/conversion_eqs")

