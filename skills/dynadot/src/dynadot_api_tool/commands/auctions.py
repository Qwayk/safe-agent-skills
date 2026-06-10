from __future__ import annotations

import argparse
import datetime as _dt
import re
import time
from typing import Any, Type

from ..dynadot_api import DynadotApi
from ..errors import ValidationError
from ..http import HttpClient
from ..json_files import write_json_file


_DATE_YYYY_M_D_RE = re.compile(r"^(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})$")
_CURRENCIES = {"USD", "EUR", "CNY"}
_OPEN_AUCTION_TYPES = {"expired", "user", "backorder", "registry_expired", "registrar"}


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


def _parse_page(value: Any) -> int:
    page = int(value or 1)
    if page < 1:
        raise ValidationError("--page must be >= 1")
    return page


def _parse_page_size(value: Any, *, max_size: int | None = None) -> int | None:
    if value is None:
        return None
    page_size = int(value)
    if page_size < 1:
        raise ValidationError("--page-size must be >= 1")
    if max_size is not None and page_size > max_size:
        raise ValidationError(f"--page-size must be <= {max_size}")
    return page_size


def _parse_open_auction_types(values: Any) -> tuple[list[str], str | None]:
    if values is None:
        return ([], None)
    raw_list = values if isinstance(values, list) else [values]
    cleaned: list[str] = []
    for raw in raw_list:
        s = str(raw or "").strip()
        if not s:
            continue
        s2 = s.lower()
        if s2 not in _OPEN_AUCTION_TYPES:
            allowed = ", ".join(sorted(_OPEN_AUCTION_TYPES))
            raise ValidationError(f"--type must be one of: {allowed}")
        cleaned.append(s2)
    if not cleaned:
        return ([], None)
    return (cleaned, ",".join(cleaned))


def _parse_currency(value: Any) -> tuple[str | None, str | None]:
    currency = str(value or "").strip().upper() or None
    if currency is None:
        return (None, None)
    if currency not in _CURRENCIES:
        allowed = ", ".join(sorted(_CURRENCIES))
        raise ValidationError(f"--currency must be one of: {allowed}")
    return (currency, currency.lower())


def _parse_date_yyyy_m_d(value: Any, *, flag: str) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError(f"Missing {flag}")
    m = _DATE_YYYY_M_D_RE.match(s)
    if not m:
        raise ValidationError(f"{flag} must be in YYYY-M-D or YYYY-MM-DD format (dash-separated; no slashes)")
    year = int(m.group("y"))
    month = int(m.group("m"))
    day = int(m.group("d"))
    try:
        d = _dt.date(year, month, day)
    except ValueError as e:
        raise ValidationError(f"{flag} is not a valid date") from e
    return d.strftime("%Y-%m-%d")


def _normalize_domain(value: Any, *, flag: str) -> str:
    s = str(value or "").strip().lower().rstrip(".")
    if not s:
        raise ValidationError(f"Missing {flag}")
    return s


def _parse_domains(values: Any) -> tuple[list[str], str]:
    if values is None:
        raise ValidationError("Missing --domain")
    raw_list = values if isinstance(values, list) else [values]
    domains: list[str] = []
    for raw in raw_list:
        parts = [p.strip() for p in str(raw or "").split(",")]
        for p in parts:
            if not p:
                continue
            domains.append(_normalize_domain(p, flag="--domain"))
    if not domains:
        raise ValidationError("Missing --domain")
    return (domains, ",".join(domains))


def cmd_auctions_open(args: Any, ctx: dict[str, Any]) -> int:
    page = _parse_page(getattr(args, "page", 1))
    page_size = _parse_page_size(getattr(args, "page_size", None), max_size=50)
    types_list, types_joined = _parse_open_auction_types(getattr(args, "type", None))
    currency, currency_param = _parse_currency(getattr(args, "currency", None))

    params: dict[str, Any] = {"page_index": page}
    if page_size is not None:
        params["count_per_page"] = page_size
    if types_joined is not None:
        params["type"] = types_joined
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_open_auctions", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_open_auctions", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_open_auctions",
        "page": page,
        "page_size": page_size,
        "types": types_list,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_open_auctions",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "auctions.open",
        {"page": page, "page_size": page_size, "types": types_list, "currency": currency, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def cmd_auctions_closed(args: Any, ctx: dict[str, Any]) -> int:
    start_date = _parse_date_yyyy_m_d(getattr(args, "start_date", None), flag="--start-date")
    end_date = _parse_date_yyyy_m_d(getattr(args, "end_date", None), flag="--end-date")
    currency, currency_param = _parse_currency(getattr(args, "currency", None))

    params: dict[str, Any] = {"startDate": start_date, "endDate": end_date}
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_closed_auctions", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_closed_auctions", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_closed_auctions",
        "start_date": start_date,
        "end_date": end_date,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_closed_auctions",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "auctions.closed",
        {
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency,
            "out_path": export_written,
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_auctions_details(args: Any, ctx: dict[str, Any]) -> int:
    domains, domains_joined = _parse_domains(getattr(args, "domain", None))
    currency, currency_param = _parse_currency(getattr(args, "currency", None))
    params: dict[str, Any] = {"domain": domains_joined}
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_auction_details", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_auction_details", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_auction_details",
        "domains": domains,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_auction_details",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("auctions.details", {"domains": domains, "currency": currency, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_auctions_bids(args: Any, ctx: dict[str, Any]) -> int:
    page = _parse_page(getattr(args, "page", 1))
    page_size = _parse_page_size(getattr(args, "page_size", None), max_size=50)
    currency, currency_param = _parse_currency(getattr(args, "currency", None))

    params: dict[str, Any] = {"page_index": page}
    if page_size is not None:
        params["count_per_page"] = page_size
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_auction_bids", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_auction_bids", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_auction_bids",
        "page": page,
        "page_size": page_size,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_auction_bids",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "auctions.bids",
        {"page": page, "page_size": page_size, "currency": currency, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def register_auctions(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    auctions = subparsers.add_parser("auctions", help="Auctions reads (read-only)")
    auctions_sub = auctions.add_subparsers(dest="auctions_cmd", required=True, parser_class=parser_class)

    open_p = auctions_sub.add_parser("open", help="List open auctions (read-only)")
    open_p.add_argument("--page", type=int, default=1, help="Page index (default: 1)")
    open_p.add_argument("--page-size", type=int, default=None, help="Entities per page (default: API default; max: 50)")
    open_p.add_argument(
        "--type",
        action="append",
        default=None,
        help="Optional type filter (repeatable; joined by comma)",
    )
    open_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    open_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    open_p.set_defaults(func=cmd_auctions_open, write_capable=False)

    closed_p = auctions_sub.add_parser("closed", help="List closed auctions (read-only)")
    closed_p.add_argument("--start-date", dest="start_date", required=True, help="Start date (YYYY-M-D or YYYY-MM-DD)")
    closed_p.add_argument("--end-date", dest="end_date", required=True, help="End date (YYYY-M-D or YYYY-MM-DD)")
    closed_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    closed_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    closed_p.set_defaults(func=cmd_auctions_closed, write_capable=False)

    details_p = auctions_sub.add_parser("details", help="Get auction details (read-only)")
    details_p.add_argument("--domain", action="append", required=True, help="Domain name (repeatable; supports commas)")
    details_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    details_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    details_p.set_defaults(func=cmd_auctions_details, write_capable=False)

    bids_p = auctions_sub.add_parser("bids", help="Get auction bids (read-only)")
    bids_p.add_argument("--page", type=int, default=1, help="Page index (default: 1)")
    bids_p.add_argument("--page-size", type=int, default=None, help="Entities per page (default: API default; max: 50)")
    bids_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    bids_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    bids_p.set_defaults(func=cmd_auctions_bids, write_capable=False)
