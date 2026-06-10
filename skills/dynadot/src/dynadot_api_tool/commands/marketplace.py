from __future__ import annotations

import argparse
import time
from typing import Any, Type

from ..dynadot_api import DynadotApi
from ..errors import ValidationError
from ..http import HttpClient
from ..json_files import write_json_file


_CURRENCIES = {"USD", "EUR", "CNY"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _api(ctx: dict[str, Any]) -> DynadotApi:
    injected = ctx.get("api")
    if injected is not None:
        return injected  # type: ignore[return-value]
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]), user_agent="dynadot-api-tool")
    return DynadotApi(base_url=cfg.base_url, api_key=cfg.api_key, http=http)


def _require_api_key(ctx: dict[str, Any]) -> None:
    if not ctx["cfg"].api_key:
        raise ValidationError("Missing DYNADOT_API_KEY")


def _export_obj(ctx: dict[str, Any], *, command: str, params: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": command,
        "params": params,
        "response": response,
    }


def _normalize_domain(value: Any) -> str:
    s = str(value or "").strip().lower().rstrip(".")
    if not s:
        raise ValidationError("Missing --domain")
    return s


def _parse_currency(value: Any) -> tuple[str | None, str | None]:
    currency = str(value or "").strip().upper() or None
    if currency is None:
        return (None, None)
    if currency not in _CURRENCIES:
        allowed = ", ".join(sorted(_CURRENCIES))
        raise ValidationError(f"--currency must be one of: {allowed}")
    return (currency, currency.lower())


def cmd_marketplace_listings_list(args: Any, ctx: dict[str, Any]) -> int:
    page = int(getattr(args, "page", 1) or 1)
    if page < 1:
        raise ValidationError("--page must be >= 1")
    page_size_raw = getattr(args, "page_size", None)
    page_size = int(page_size_raw) if page_size_raw is not None else None
    if page_size is not None and page_size < 1:
        raise ValidationError("--page-size must be >= 1")

    currency, currency_param = _parse_currency(getattr(args, "currency", None))
    exclude_pending_sale = bool(getattr(args, "exclude_pending_sale", False))
    show_other_registrar = bool(getattr(args, "show_other_registrar", False))

    params: dict[str, Any] = {"page_index": page}
    if page_size is not None:
        params["count_per_page"] = page_size
    if currency_param is not None:
        params["currency"] = currency_param
    if exclude_pending_sale:
        params["exclude_pending_sale"] = "yes"
    if show_other_registrar:
        params["show_other_registrar"] = "yes"

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_listings", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="get_listings", params=dict(params), response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_listings",
        "page": page,
        "page_size": page_size,
        "currency": currency,
        "exclude_pending_sale": exclude_pending_sale,
        "show_other_registrar": show_other_registrar,
        "out_path": export_written,
        "dynadot": {
            "command": "get_listings",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "marketplace.listings.list",
        {
            "page": page,
            "page_size": page_size,
            "currency": currency,
            "exclude_pending_sale": exclude_pending_sale,
            "show_other_registrar": show_other_registrar,
            "out_path": export_written,
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_marketplace_listings_get(args: Any, ctx: dict[str, Any]) -> int:
    domain = _normalize_domain(getattr(args, "domain", None))
    params: dict[str, Any] = {"domain": domain}
    currency, currency_param = _parse_currency(getattr(args, "currency", None))
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_listing_item", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_listing_item", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_listing_item",
        "domain": domain,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_listing_item",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("marketplace.listings.get", {"domain": domain, "currency": currency, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_marketplace(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    marketplace = subparsers.add_parser("marketplace", help="Marketplace reads (read-only)")
    marketplace_sub = marketplace.add_subparsers(dest="marketplace_cmd", required=True, parser_class=parser_class)

    listings = marketplace_sub.add_parser("listings", help="Marketplace listings (read-only)")
    listings_sub = listings.add_subparsers(dest="marketplace_listings_cmd", required=True, parser_class=parser_class)

    list_p = listings_sub.add_parser("list", help="List marketplace listings (read-only)")
    list_p.add_argument("--page", type=int, default=1, help="Page index (default: 1)")
    list_p.add_argument("--page-size", type=int, default=None, help="Entities per page (default: API default)")
    list_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    list_p.add_argument("--exclude-pending-sale", dest="exclude_pending_sale", action="store_true", help="Exclude pending sales")
    list_p.add_argument("--show-other-registrar", dest="show_other_registrar", action="store_true", help="Show other registrar listings")
    list_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    list_p.set_defaults(func=cmd_marketplace_listings_list, write_capable=False)

    get_p = listings_sub.add_parser("get", help="Get a marketplace listing item (read-only)")
    get_p.add_argument("--domain", required=True, help="Domain name")
    get_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    get_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    get_p.set_defaults(func=cmd_marketplace_listings_get, write_capable=False)
