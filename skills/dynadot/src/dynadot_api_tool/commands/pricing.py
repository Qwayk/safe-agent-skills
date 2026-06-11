from __future__ import annotations

import argparse
import time
from typing import Any, Type

from ..dynadot_api import DynadotApi
from ..errors import ValidationError
from ..http import HttpClient
from ..json_files import write_json_file


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


def cmd_pricing_tld_price(args: Any, ctx: dict[str, Any]) -> int:
    page = int(getattr(args, "page", 1) or 1)
    if page < 1:
        raise ValidationError("--page must be >= 1")
    page_size_raw = getattr(args, "page_size", None)
    page_size = int(page_size_raw) if page_size_raw is not None else None
    if page_size is not None and page_size < 1:
        raise ValidationError("--page-size must be >= 1")

    currency = str(getattr(args, "currency", "") or "").strip().upper() or None
    if currency is not None and currency not in {"USD", "EUR", "CNY"}:
        raise ValidationError("--currency must be one of: USD, EUR, CNY")

    params: dict[str, Any] = {"page_index": page}
    if page_size is not None:
        params["count_per_page"] = page_size
    if currency is not None:
        params["currency"] = currency.lower()

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="tld_price", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="tld_price", params=params, response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "tld_price",
        "page": page,
        "page_size": page_size,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "tld_price",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("pricing.tld_price", {"page": page, "page_size": page_size, "currency": currency, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_pricing(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    pricing = subparsers.add_parser("pricing", help="Pricing reads (read-only)")
    pricing_sub = pricing.add_subparsers(dest="pricing_cmd", required=True, parser_class=parser_class)

    tld_price = pricing_sub.add_parser("tld-price", help="TLD pricing (read-only)")
    tld_price.add_argument("--currency", default=None, choices=("USD", "EUR", "CNY"), help="Currency (default: API default)")
    tld_price.add_argument("--page", type=int, default=1, help="Page index (default: 1)")
    tld_price.add_argument("--page-size", type=int, default=None, help="Entities per page (default: API default)")
    tld_price.add_argument("--out", default=None, help="Write full JSON export to a file")
    tld_price.set_defaults(func=cmd_pricing_tld_price, write_capable=False)
