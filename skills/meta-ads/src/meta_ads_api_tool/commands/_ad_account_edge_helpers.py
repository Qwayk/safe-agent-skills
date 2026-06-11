from __future__ import annotations

from ..config import normalize_ad_account_id
from ..errors import ValidationError
from ..graph import _parse_kv_pairs


def _edge_list_common(args) -> tuple[str | None, dict[str, str]]:
    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)
    limit = getattr(args, "limit", None)
    if limit is not None:
        params.setdefault("limit", str(limit))
    return fields, params


def _required_ad_account_id(args, ctx) -> str:
    cfg = ctx.get("cfg")
    raw = getattr(args, "ad_account_id", None) or (cfg.ad_account_id if cfg else None)
    aid = normalize_ad_account_id(raw)
    if not aid:
        raise ValidationError("Missing --ad-account-id (or META_ADS_AD_ACCOUNT_ID)")
    return aid

