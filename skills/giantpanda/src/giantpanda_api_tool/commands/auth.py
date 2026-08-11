from __future__ import annotations

from .. import config as config_mod


def cmd_auth_check(args, ctx) -> int:
    _ = args
    token = ctx["cfg"].token
    token_present = bool(token and not config_mod.is_placeholder_token(token))
    out = ctx["out"]
    out.emit(
        {
            "ok": True,
            "auth": {
                "ready": token_present,
                "token_present": token_present,
            },
        },
    )
    return 0
