from __future__ import annotations

from ..http import HttpClient
from ..wp_api import WordPressApi


def cmd_auth_check(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    me = api.users_me()
    ctx["audit"].write("auth.check", {"user_id": me.get("id"), "name": me.get("name")})
    ctx["out"].emit({"ok": True, "me": {"id": me.get("id"), "name": me.get("name")}})
    return 0

