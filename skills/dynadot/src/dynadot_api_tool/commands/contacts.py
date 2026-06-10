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


def _parse_contact_id(value: Any) -> str:
    v = str(value or "").strip()
    if not v:
        raise ValidationError("Missing --contact-id")
    return v


def cmd_contacts_list(args: Any, ctx: dict[str, Any]) -> int:
    _require_api_key(ctx)
    api = _api(ctx)
    res = api.call(command="contact_list")
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="contact_list", params={}, response=res.response)) if out_path else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "contact_list",
        "out_path": export_written,
        "dynadot": {
            "command": "contact_list",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("contacts.list", {"out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_contacts_get(args: Any, ctx: dict[str, Any]) -> int:
    contact_id = _parse_contact_id(getattr(args, "contact_id", None))

    _require_api_key(ctx)
    api = _api(ctx)
    params: dict[str, Any] = {"contact_id": contact_id}
    res = api.call(command="get_contact", params=params)
    out_path = str(getattr(args, "out", "") or "").strip() or None
    export_written = (
        write_json_file(out_path, _export_obj(ctx, command="get_contact", params=dict(params), response=res.response))
        if out_path
        else None
    )

    out = {
        "ok": True,
        "dry_run": True,
        "command": "get_contact",
        "contact_id": contact_id,
        "out_path": export_written,
        "dynadot": {
            "command": "get_contact",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("contacts.get", {"contact_id": contact_id, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_contacts(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    contacts = subparsers.add_parser("contacts", help="Contact reads (read-only)")
    contacts_sub = contacts.add_subparsers(dest="contacts_cmd", required=True, parser_class=parser_class)

    list_p = contacts_sub.add_parser("list", help="List contacts (read-only)")
    list_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    list_p.set_defaults(func=cmd_contacts_list, write_capable=False)

    get_p = contacts_sub.add_parser("get", help="Get a contact by id (read-only)")
    get_p.add_argument("--contact-id", dest="contact_id", required=True, help="Contact id")
    get_p.add_argument("--out", default=None, help="Write full JSON export to a file")
    get_p.set_defaults(func=cmd_contacts_get, write_capable=False)

