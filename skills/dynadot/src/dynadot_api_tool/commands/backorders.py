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


def cmd_backorders_requests_list(args: Any, ctx: dict[str, Any]) -> int:
    start_date = _parse_date_yyyy_m_d(getattr(args, "start_date", None), flag="--start-date")
    end_date = _parse_date_yyyy_m_d(getattr(args, "end_date", None), flag="--end-date")

    params: dict[str, Any] = {
        # Dynadot docs list params as start_date/end_date, but their own request examples use startDate/endDate.
        "startDate": start_date,
        "endDate": end_date,
    }

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="backorder_request_list", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="backorder_request_list", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "backorder_request_list",
        "start_date": start_date,
        "end_date": end_date,
        "out_path": export_written,
        "dynadot": {
            "command": "backorder_request_list",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write(
        "backorders.requests.list",
        {"start_date": start_date, "end_date": end_date, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def register_backorders(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    backorders = subparsers.add_parser("backorders", help="Backorder requests reads (read-only)")
    backorders_sub = backorders.add_subparsers(dest="backorders_cmd", required=True, parser_class=parser_class)

    requests = backorders_sub.add_parser("requests", help="Backorder requests (read-only)")
    requests_sub = requests.add_subparsers(dest="backorders_requests_cmd", required=True, parser_class=parser_class)

    list_p = requests_sub.add_parser("list", help="List backorder requests (read-only)")
    list_p.add_argument("--start-date", required=True, help="Start drop date (YYYY-MM-DD; accepts YYYY-M-D)")
    list_p.add_argument("--end-date", required=True, help="End drop date (YYYY-MM-DD; accepts YYYY-M-D)")
    list_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    list_p.set_defaults(func=cmd_backorders_requests_list, write_capable=False)

