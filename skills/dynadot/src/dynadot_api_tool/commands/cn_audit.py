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


def _normalize_contact_id(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError("Missing --contact-id")
    return s


def cmd_cn_audit_status(args: Any, ctx: dict[str, Any]) -> int:
    contact_id = _normalize_contact_id(getattr(args, "contact_id", None))
    gtld = bool(getattr(args, "gtld", False))

    params: dict[str, Any] = {"contact_id": contact_id}
    if gtld:
        params["gtld"] = 1

    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="get_cn_audit_status", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(
            out_path,
            _export_obj(ctx, command="get_cn_audit_status", params=dict(params), response=res.response),
        )
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_cn_audit_status",
        "contact_id": contact_id,
        "gtld": gtld,
        "out_path": export_written,
        "dynadot": {
            "command": "get_cn_audit_status",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("cn_audit.status", {"contact_id": contact_id, "gtld": gtld, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_cn_audit(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    cn_audit = subparsers.add_parser("cn-audit", help="CN audit reads (read-only)")
    cn_audit_sub = cn_audit.add_subparsers(dest="cn_audit_cmd", required=True, parser_class=parser_class)

    status_p = cn_audit_sub.add_parser("status", help="Get CN audit status for a contact (read-only)")
    status_p.add_argument("--contact-id", required=True, help="Contact record id")
    status_p.add_argument("--gtld", action="store_true", help="Set gtld=1 (query cnnic-gtld audit result)")
    status_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    status_p.set_defaults(func=cmd_cn_audit_status, write_capable=False)

