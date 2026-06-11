from __future__ import annotations

from .meals import fetch_categories


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    categories = fetch_categories(ctx)
    out = {
        "ok": True,
        "command": "auth.check",
        "connection": {
            "status": "ok",
            "probe": "categories.php",
            "category_count": len(categories),
        },
        "api": {
            "base_url": cfg.base_url,
            "key_mode": "default_public_key" if cfg.api_key == "1" else "custom_key",
            "key_source": cfg.api_key_source,
            "timeout_s": cfg.timeout_s,
        },
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
