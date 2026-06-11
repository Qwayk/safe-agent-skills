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


def cmd_backorder_auctions_closed(args: Any, ctx: dict[str, Any]) -> int:
    start_date = _parse_date_yyyy_m_d(getattr(args, "start_date", None), flag="--start-date")
    end_date = _parse_date_yyyy_m_d(getattr(args, "end_date", None), flag="--end-date")
    currency, currency_param = _parse_currency(getattr(args, "currency", None))

    params: dict[str, Any] = {"startDate": start_date, "endDate": end_date}
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_closed_backorder_auctions", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_closed_backorder_auctions", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_closed_backorder_auctions",
        "start_date": start_date,
        "end_date": end_date,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_closed_backorder_auctions",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "backorder_auctions.closed",
        {"start_date": start_date, "end_date": end_date, "currency": currency, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def cmd_backorder_auctions_details(args: Any, ctx: dict[str, Any]) -> int:
    domain = _normalize_domain(getattr(args, "domain", None), flag="--domain")
    currency, currency_param = _parse_currency(getattr(args, "currency", None))
    params: dict[str, Any] = {"domain": domain}
    if currency_param is not None:
        params["currency"] = currency_param

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_backorder_auction_details", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_backorder_auction_details", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_backorder_auction_details",
        "domain": domain,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "get_backorder_auction_details",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "backorder_auctions.details",
        {"domain": domain, "currency": currency, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def register_backorder_auctions(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    backorder = subparsers.add_parser("backorder-auctions", help="Backorder auctions reads (read-only)")
    backorder_sub = backorder.add_subparsers(dest="backorder_auctions_cmd", required=True, parser_class=parser_class)

    closed_p = backorder_sub.add_parser("closed", help="List closed backorder auctions (read-only)")
    closed_p.add_argument("--start-date", dest="start_date", required=True, help="Start date (YYYY-M-D or YYYY-MM-DD)")
    closed_p.add_argument("--end-date", dest="end_date", required=True, help="End date (YYYY-M-D or YYYY-MM-DD)")
    closed_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    closed_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    closed_p.set_defaults(func=cmd_backorder_auctions_closed, write_capable=False)

    details_p = backorder_sub.add_parser("details", help="Get backorder auction details (read-only)")
    details_p.add_argument("--domain", required=True, help="Domain name")
    details_p.add_argument("--currency", default=None, help="Currency: USD, EUR, or CNY (case-insensitive)")
    details_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    details_p.set_defaults(func=cmd_backorder_auctions_details, write_capable=False)
