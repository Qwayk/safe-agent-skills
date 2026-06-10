from __future__ import annotations

import argparse
from typing import Any, Type

from ..dynadot_api import DynadotApi
from ..errors import ValidationError
from ..http import HttpClient


def _api(ctx: dict[str, Any]) -> DynadotApi:
    api = ctx.get("api")
    if isinstance(api, DynadotApi):
        return api
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]), user_agent="dynadot-api-tool")
    return DynadotApi(base_url=cfg.base_url, api_key=cfg.api_key, http=http)


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise ValidationError("Missing DYNADOT_API_KEY")

    api = _api(ctx)
    res = api.call(command="is_processing")
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_api_key_present": True,
        "dynadot": {
            "command": "is_processing",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def register_auth(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    auth = subparsers.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=parser_class)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=cmd_auth_check, write_capable=False)
