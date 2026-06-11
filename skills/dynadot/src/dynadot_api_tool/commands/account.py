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


def cmd_account_info(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="account_info")
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="account_info", params={}, response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "account_info",
        "out_path": export_written,
        "dynadot": {
            "command": "account_info",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("account.info", {"out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_account_balance(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_account_balance")
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="get_account_balance", params={}, response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_account_balance",
        "out_path": export_written,
        "dynadot": {
            "command": "get_account_balance",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("account.balance", {"out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_account_coupons(args: Any, ctx: dict[str, Any]) -> int:
    coupon_type = str(getattr(args, "coupon_type", "") or "").strip().lower()
    if coupon_type not in {"registration", "renewal", "transfer"}:
        raise ValidationError("--coupon-type must be one of: registration, renewal, transfer")

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="list_coupons", params={"coupon_type": coupon_type})
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="list_coupons", params={"coupon_type": coupon_type}, response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "list_coupons",
        "coupon_type": coupon_type,
        "out_path": export_written,
        "dynadot": {
            "command": "list_coupons",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("account.coupons", {"coupon_type": coupon_type, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_account(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    account = subparsers.add_parser("account", help="Account and billing reads (read-only)")
    account_sub = account.add_subparsers(dest="account_cmd", required=True, parser_class=parser_class)

    info = account_sub.add_parser("info", help="Get account info (read-only)")
    info.add_argument("--out", default=None, help="Write full JSON export to a file")
    info.set_defaults(func=cmd_account_info, write_capable=False)

    balance = account_sub.add_parser("balance", help="Get account balance (read-only)")
    balance.add_argument("--out", default=None, help="Write full JSON export to a file")
    balance.set_defaults(func=cmd_account_balance, write_capable=False)

    coupons = account_sub.add_parser("coupons", help="List coupons (read-only)")
    coupons.add_argument(
        "--coupon-type",
        dest="coupon_type",
        required=True,
        choices=("registration", "renewal", "transfer"),
        help="Coupon type",
    )
    coupons.add_argument("--out", default=None, help="Write full JSON export to a file")
    coupons.set_defaults(func=cmd_account_coupons, write_capable=False)
