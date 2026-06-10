from __future__ import annotations

from typing import Any

from ..skimlinks import SkimlinksClient, clean_params, make_http_client, require_publisher_id


def _client(ctx: dict[str, Any]) -> SkimlinksClient:
    return SkimlinksClient(cfg=ctx["cfg"], http=make_http_client(ctx))


def _emit(ctx: dict[str, Any], event: str, out: dict[str, Any]) -> int:
    ctx["audit"].write(event, {"ok": out.get("ok"), "path": out.get("path"), "params": out.get("params")})
    ctx["out"].emit(out)
    return 0


def _shared_query(args: Any, names: list[str]) -> dict[str, Any]:
    return clean_params({name: getattr(args, name, None) for name in names})


def cmd_merchants_list(args: Any, ctx: dict[str, Any]) -> int:
    publisher_id = require_publisher_id(ctx["cfg"], getattr(args, "publisher_id", None))
    params = _shared_query(
        args,
        [
            "publisher_domain_id",
            "search",
            "vertical",
            "id",
            "country",
            "favourite_type",
            "limit",
            "offset",
            "sort_by",
            "sort_dir",
            "a_id",
            "merchant_id",
            "alternative_vertical_id",
            "alternative_vertical_taxonomy",
            "alternative_vertical_country",
        ],
    )
    if not params.get("publisher_domain_id") and ctx["cfg"].publisher_domain_id:
        params["publisher_domain_id"] = ctx["cfg"].publisher_domain_id
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].merchant_base_url,
        path=f"/v4/publisher/{publisher_id}/merchants",
        params=params,
    )
    out.update({"family": "merchant", "operation": "merchants.list"})
    return _emit(ctx, "merchant.merchants.list", out)


def cmd_domains_list(args: Any, ctx: dict[str, Any]) -> int:
    publisher_id = require_publisher_id(ctx["cfg"], getattr(args, "publisher_id", None))
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].merchant_base_url,
        path=f"/v4/publisher/{publisher_id}/domains",
        params={},
    )
    out.update({"family": "merchant", "operation": "domains.list"})
    return _emit(ctx, "merchant.domains.list", out)


def cmd_verticals_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].merchant_base_url,
        path="/v4/verticals",
        params={},
        scope=None,
    )
    out.update({"family": "merchant", "operation": "verticals.list"})
    return _emit(ctx, "merchant.verticals.list", out)


def cmd_alternative_verticals_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].merchant_base_url,
        path="/v4/alternative_verticals",
        params={},
        scope=None,
    )
    out.update({"family": "merchant", "operation": "alternative_verticals.list"})
    return _emit(ctx, "merchant.alternative_verticals.list", out)


def cmd_offers_list(args: Any, ctx: dict[str, Any]) -> int:
    publisher_id = require_publisher_id(ctx["cfg"], getattr(args, "publisher_id", None))
    params = _shared_query(
        args,
        [
            "search",
            "merchant_id",
            "vertical",
            "country",
            "period",
            "favourite_type",
            "limit",
            "offset",
            "sort_by",
            "sort_dir",
            "a_id",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].merchant_base_url,
        path=f"/v4/publisher/{publisher_id}/offers",
        params=params,
    )
    out.update({"family": "merchant", "operation": "offers.list"})
    return _emit(ctx, "merchant.offers.list", out)
