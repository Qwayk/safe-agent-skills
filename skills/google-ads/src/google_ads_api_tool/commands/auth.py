from __future__ import annotations

from typing import Any

from ..google_ads_client import build_google_ads_client, parse_customer_id_from_resource_name


def _mask(value: str, *, keep_prefix: int = 2, keep_suffix: int = 4) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    if len(s) <= keep_prefix + keep_suffix:
        return "***"
    return f"{s[:keep_prefix]}***{s[-keep_suffix:]}"


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = build_google_ads_client(cfg)

    customer_service = client.get_service("CustomerService")
    resp = customer_service.list_accessible_customers()

    resource_names = list(getattr(resp, "resource_names", []) or [])
    customer_ids: list[str] = []
    for rn in resource_names:
        cid = parse_customer_id_from_resource_name(str(rn))
        if cid:
            customer_ids.append(cid)

    out = {
        "ok": True,
        "tool": ctx.get("tool") or "google-ads-api-tool",
        "version": ctx.get("tool_version"),
        "authenticated": True,
        "customer_count": len(customer_ids),
        "customer_ids": customer_ids,
        "resource_names": resource_names,
        "auth": {
            "developer_token_masked": _mask(cfg.developer_token),
            "client_id_masked": _mask(cfg.client_id),
            "login_customer_id": cfg.login_customer_id,
        },
        "warnings": [],
    }
    ctx["audit"].write("auth.check", {"ok": True, "customer_count": len(customer_ids)})
    ctx["out"].emit(out)
    return 0

