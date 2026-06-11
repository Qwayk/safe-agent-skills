from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..skimlinks import (
    PRODUCT_SCOPE,
    SkimlinksClient,
    clean_params,
    make_http_client,
    require_publisher_id,
)


def _client(ctx: dict[str, Any]) -> SkimlinksClient:
    return SkimlinksClient(cfg=ctx["cfg"], http=make_http_client(ctx))


def _emit(ctx: dict[str, Any], event: str, out: dict[str, Any]) -> int:
    ctx["audit"].write(event, {"ok": out.get("ok"), "path": out.get("path"), "params": out.get("params")})
    ctx["out"].emit(out)
    return 0


def _params(args: Any, names: list[str]) -> dict[str, Any]:
    return clean_params({name: getattr(args, name, None) for name in names})


def _split_values(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        for item in str(value).split(","):
            clean = item.strip()
            if clean:
                out.append(clean)
    return out


def _require_publisher_domain_id(ctx: dict[str, Any], params: dict[str, Any]) -> None:
    if params.get("publisher_domain_id"):
        return
    cfg_domain_id = ctx["cfg"].publisher_domain_id
    if cfg_domain_id:
        params["publisher_domain_id"] = cfg_domain_id
        return
    raise ValidationError(
        "Missing Product Key publisher domain ID. Set SKIMLINKS_PUBLISHER_DOMAIN_ID "
        "or pass --publisher-domain-id."
    )


def cmd_product_get(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    publisher_id = require_publisher_id(cfg, getattr(args, "publisher_id", None))
    params = _params(
        args,
        [
            "publisher_domain_id",
            "product_url",
            "product_keywords",
            "upc",
            "alternative_country_code",
            "country_code",
            "product_id",
            "product_id_type",
            "merchant_type",
            "domains",
            "exclude_domains",
            "referrer_url",
            "per_merchant_limit",
            "alternatives_size",
            "sort_desc",
            "sort_by",
        ],
    )
    _require_publisher_domain_id(ctx, params)
    if not any(params.get(key) for key in ("product_url", "product_keywords", "upc", "product_id")):
        raise ValidationError("Pass one of --product-url, --product-keywords, --upc, or --product-id.")

    out = _client(ctx).get_json(
        base_url=cfg.product_base_url,
        path=f"/v2/publisher/{publisher_id}/product",
        params=params,
        scope=PRODUCT_SCOPE,
    )
    out.update(
        {
            "family": "product_key",
            "operation": "product.get",
            "official_aliases": [
                f"/publisher/{publisher_id}/product",
                f"/v2/publisher/{publisher_id}/get-products",
            ],
        }
    )
    return _emit(ctx, "product_key.product.get", out)


def cmd_products_get(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    publisher_id = require_publisher_id(cfg, getattr(args, "publisher_id", None))
    params = _params(
        args,
        [
            "publisher_domain_id",
            "alternative_country_code",
            "country_code",
            "product_id_type",
            "merchant_type",
            "domains",
            "exclude_domains",
            "referrer_url",
            "per_merchant_limit",
            "alternatives_size",
            "sort_desc",
            "sort_by",
        ],
    )
    _require_publisher_domain_id(ctx, params)

    product_urls = _split_values(getattr(args, "product_url", None))
    product_ids = _split_values(getattr(args, "product_id", None))
    if not product_urls and not product_ids:
        raise ValidationError("Pass at least one --product-url or --product-id.")
    body: dict[str, Any] = {}
    if product_urls:
        body["product_urls"] = product_urls
    if product_ids:
        body["product_ids"] = product_ids

    out = _client(ctx).post_json(
        base_url=cfg.product_base_url,
        path=f"/v1/publisher/{publisher_id}/products",
        params=params,
        body=body,
        scope=PRODUCT_SCOPE,
    )
    out.update(
        {
            "family": "product_key",
            "operation": "products.get",
            "body_keys": sorted(body),
        }
    )
    return _emit(ctx, "product_key.products.get", out)
