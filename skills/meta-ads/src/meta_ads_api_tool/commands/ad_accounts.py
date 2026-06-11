from __future__ import annotations

from ..config import normalize_ad_account_id
from ..errors import ValidationError
from ..graph import _parse_kv_pairs


def cmd_ad_accounts_list(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)
    params.setdefault("limit", str(getattr(args, "limit", 100) or 100))

    res = graph.list_me_adaccounts(
        params=params,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )
    out_obj = {
        "ok": True,
        "ad_accounts_list": {"params": params},
        "data": res.data,
        "count": len(res.data),
        "paging": res.paging,
        "pages_fetched": res.raw_pages,
    }
    audit.write("ad_accounts.list", {"count": len(res.data), "params": list(params.keys())})
    out.emit(out_obj)
    return 0


def cmd_ad_accounts_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]
    cfg = ctx.get("cfg")

    raw = getattr(args, "ad_account_id", None) or (cfg.ad_account_id if cfg else None)
    ad_account_id = normalize_ad_account_id(raw)
    if not ad_account_id:
        raise ValidationError("Missing --ad-account-id (or META_ADS_AD_ACCOUNT_ID)")

    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)

    payload = graph.get_ad_account(ad_account_id, params=params or None)
    out_obj = {"ok": True, "ad_accounts_get": {"ad_account_id": ad_account_id, "params": params}, "data": payload}
    audit.write("ad_accounts.get", {"ad_account_id": ad_account_id, "params": list(params.keys())})
    out.emit(out_obj)
    return 0

