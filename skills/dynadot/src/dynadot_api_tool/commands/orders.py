from __future__ import annotations

import argparse
import re
import time
from typing import Any, Type

from ..dynadot_api import DynadotApi
from ..errors import ValidationError
from ..http import HttpClient
from ..json_files import write_json_file


_YYYY_MM_DD_SLASH_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")


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


def _parse_search_by(value: Any) -> str:
    v = str(value or "").strip().lower()
    if v not in {"date_range", "domain", "order_id"}:
        raise ValidationError("--search-by must be one of: date_range, domain, order_id")
    return v


def _parse_yyyy_mm_dd_slash(value: Any, *, flag: str) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError(f"Missing {flag}")
    if not _YYYY_MM_DD_SLASH_RE.match(s):
        raise ValidationError(f"{flag} must be in yyyy/MM/dd format")
    return s


def cmd_orders_list(args: Any, ctx: dict[str, Any]) -> int:
    search_by = _parse_search_by(getattr(args, "search_by", None))
    start_date = _parse_yyyy_mm_dd_slash(getattr(args, "start_date", None), flag="--start-date")
    end_date = _parse_yyyy_mm_dd_slash(getattr(args, "end_date", None), flag="--end-date")
    payment_method = str(getattr(args, "payment_method", "") or "").strip() or None

    _require_api_key(ctx)
    api = _api(ctx)
    params: dict[str, Any] = {
        "search_by": search_by,
        "start_date": start_date,
        "end_date": end_date,
    }
    if payment_method:
        params["payment_method"] = payment_method
    res = api.call(command="order_list", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="order_list", params=dict(params), response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "order_list",
        "search_by": search_by,
        "start_date": start_date,
        "end_date": end_date,
        "payment_method": payment_method,
        "out_path": export_written,
        "dynadot": {
            "command": "order_list",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "orders.list",
        {
            "search_by": search_by,
            "start_date": start_date,
            "end_date": end_date,
            "payment_method": payment_method,
            "out_path": export_written,
        },
    )
    ctx["out"].emit(out)
    return 0


def _parse_order_id(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError("Missing --order-id")
    if not s.isdigit():
        raise ValidationError("--order-id must be numeric")
    return s


def cmd_orders_status(args: Any, ctx: dict[str, Any]) -> int:
    order_id = _parse_order_id(getattr(args, "order_id", None))

    _require_api_key(ctx)
    api = _api(ctx)
    params = {"order_id": order_id}
    res = api.call(command="get_order_status", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_order_status", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_order_status",
        "order_id": order_id,
        "out_path": export_written,
        "dynadot": {
            "command": "get_order_status",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("orders.status", {"order_id": order_id, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_orders(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    orders = subparsers.add_parser("orders", help="Order reads (read-only)")
    orders_sub = orders.add_subparsers(dest="orders_cmd", required=True, parser_class=parser_class)

    list_p = orders_sub.add_parser("list", help="List orders (read-only)")
    list_p.add_argument(
        "--search-by",
        dest="search_by",
        required=True,
        choices=("date_range", "domain", "order_id"),
        help="Search mode (per Dynadot docs)",
    )
    list_p.add_argument("--start-date", dest="start_date", required=True, help="Start date (yyyy/MM/dd)")
    list_p.add_argument("--end-date", dest="end_date", required=True, help="End date (yyyy/MM/dd)")
    list_p.add_argument(
        "--payment-method",
        dest="payment_method",
        default=None,
        help="Comma-separated payment methods (optional, per Dynadot docs)",
    )
    list_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    list_p.set_defaults(func=cmd_orders_list, write_capable=False)

    status = orders_sub.add_parser("status", help="Get order status (read-only)")
    status.add_argument("--order-id", dest="order_id", required=True, help="Order id")
    status.add_argument("--out", default=None, help="Write full JSON export to a file")
    status.set_defaults(func=cmd_orders_status, write_capable=False)
