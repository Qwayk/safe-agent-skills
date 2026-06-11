from __future__ import annotations

from ..http import HttpClient
from ..wp_api import WordPressApi


def cmd_settings_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    settings = api.settings(context=str(getattr(args, "context", "view") or "view"))
    ctx["out"].emit({"ok": True, "settings": settings})
    return 0

