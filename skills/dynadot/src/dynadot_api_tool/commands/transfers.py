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


def cmd_transfers_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="transfer_domain_list")
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="transfer_domain_list", params={}, response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "transfer_domain_list",
        "out_path": export_written,
        "dynadot": {
            "command": "transfer_domain_list",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("transfers.list", {"out_path": export_written})
    ctx["out"].emit(out)
    return 0


def _parse_domain(value: Any, *, flag: str) -> str:
    d = str(value or "").strip().lower().rstrip(".")
    if not d:
        raise ValidationError(f"Missing {flag}")
    return d


def _parse_transfer_type(value: Any) -> str:
    v = str(value or "").strip().lower()
    if v == "out":
        v = "away"
    if v not in {"in", "away"}:
        raise ValidationError("--transfer-type must be one of: in, away")
    return v


def cmd_transfers_status(args: Any, ctx: dict[str, Any]) -> int:
    domain = _parse_domain(getattr(args, "domain", None), flag="--domain")
    transfer_type = _parse_transfer_type(getattr(args, "transfer_type", None))

    _require_api_key(ctx)
    api = _api(ctx)
    params = {"domain": domain, "transfer_type": transfer_type}
    res = api.call(command="get_transfer_status", params=params)
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_transfer_status", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_transfer_status",
        "domain": domain,
        "transfer_type": transfer_type,
        "out_path": export_written,
        "dynadot": {
            "command": "get_transfer_status",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("transfers.status", {"domain": domain, "transfer_type": transfer_type, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_transfers_auth_code(args: Any, ctx: dict[str, Any]) -> int:
    domain = _parse_domain(getattr(args, "domain", None), flag="--domain")

    _require_api_key(ctx)
    api = _api(ctx)
    params: dict[str, Any] = {"domain": domain}

    res = api.call(command="get_transfer_auth_code", params=params)
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_transfer_auth_code", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_transfer_auth_code",
        "domain": domain,
        "out_path": export_written,
        "dynadot": {
            "command": "get_transfer_auth_code",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("transfers.auth_code", {"domain": domain, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_transfers(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    transfers = subparsers.add_parser("transfers", help="Transfer reads (read-only)")
    transfers_sub = transfers.add_subparsers(dest="transfers_cmd", required=True, parser_class=parser_class)

    list_p = transfers_sub.add_parser("list", help="List processing transfer-out domains (read-only)")
    list_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    list_p.set_defaults(func=cmd_transfers_list, write_capable=False)

    status = transfers_sub.add_parser("status", help="Get transfer status for a domain (read-only)")
    status.add_argument("--domain", required=True, help="Domain name")
    status.add_argument(
        "--transfer-type",
        dest="transfer_type",
        required=True,
        choices=("in", "away", "out"),
        help="Transfer type ('out' is treated as 'away')",
    )
    status.add_argument("--out", default=None, help="Write full JSON export to a file")
    status.set_defaults(func=cmd_transfers_status, write_capable=False)

    auth = transfers_sub.add_parser("auth-code", help="Get transfer auth code for a domain (read-only)")
    auth.add_argument("--domain", required=True, help="Domain name")
    auth.add_argument("--out", default=None, help="Write full JSON export to a file")
    auth.set_defaults(func=cmd_transfers_auth_code, write_capable=False)
