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


def _parse_domain(value: Any) -> str:
    d = str(value or "").strip().lower().rstrip(".")
    if not d:
        raise ValidationError("Missing --domain")
    return d


def cmd_dns_get(args: Any, ctx: dict[str, Any]) -> int:
    domain = _parse_domain(getattr(args, "domain", None))

    _require_api_key(ctx)
    api = _api(ctx)
    params: dict[str, Any] = {"domain": domain}
    res = api.call(command="get_dns", params=params)
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="get_dns", params=dict(params), response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_dns",
        "domain": domain,
        "out_path": export_written,
        "dynadot": {
            "command": "get_dns",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("dns.get", {"domain": domain, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_dns(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    dns = subparsers.add_parser("dns", help="DNS reads (read-only)")
    dns_sub = dns.add_subparsers(dest="dns_cmd", required=True, parser_class=parser_class)

    get_p = dns_sub.add_parser("get", help="Get DNS settings for a domain (read-only)")
    get_p.add_argument("--domain", required=True, help="Domain name")
    get_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    get_p.set_defaults(func=cmd_dns_get, write_capable=False)

