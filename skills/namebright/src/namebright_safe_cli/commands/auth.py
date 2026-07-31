from __future__ import annotations

from typing import Any

from ..client import NameBrightClient


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    _ = args
    timeout_s = float(ctx.get("timeout_s", 30.0) or 30.0)
    client_factory = ctx.get("client_factory")
    if not callable(client_factory):
        client_factory = NameBrightClient

    client = client_factory(
        cfg=cfg,
        timeout_s=timeout_s,
        verbose=bool(ctx.get("verbose", False)),
        user_agent=ctx.get("tool", "namebright-safe-cli"),
    )
    token_payload = client.request_token_status() if hasattr(client, "request_token_status") else {}
    token_status: Any = {}
    if isinstance(token_payload, dict):
        maybe = token_payload.get("token_status")
        if isinstance(maybe, dict):
            token_status = maybe
    out = {
        "ok": True,
        "token_status": token_status,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
