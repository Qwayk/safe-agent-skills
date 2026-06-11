from __future__ import annotations

from ..client import WooCommerceClient


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = WooCommerceClient(
        cfg=cfg,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        user_agent=f'{ctx["tool"]}/{ctx["tool_version"]}',
    )
    envelope = client.request_json(
        "GET",
        "/orders",
        params={"per_page": 1},
        auth_required=True,
    )
    payload = envelope.payload if isinstance(envelope.payload, list) else []
    out = {
        "ok": True,
        "store_url": cfg.store_url,
        "api_base_url": cfg.api_base_url,
        "auth_mode": "query_string" if cfg.query_string_auth else "basic",
        "verify_ssl": cfg.verify_ssl,
        "orders_preview_count": len(payload),
        "orders_total_header": envelope.response.headers.get("x-wp-total"),
        "orders_total_pages_header": envelope.response.headers.get("x-wp-totalpages"),
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
