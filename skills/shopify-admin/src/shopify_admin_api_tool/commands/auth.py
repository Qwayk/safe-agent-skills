from __future__ import annotations

from ..errors import ValidationError
from ..shopify_graphql import ShopifyAdminGraphQLClient

def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    if cfg is None:
        raise ValidationError("Missing config")

    client = ShopifyAdminGraphQLClient(
        shop_domain=cfg.shop_domain,
        admin_access_token=cfg.admin_access_token,
        api_version=cfg.api_version,
        timeout_s=ctx["timeout_s"],
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx.get('tool')}/{ctx.get('tool_version')}",
    )

    # Minimal, read-only call. Avoid returning shop name (not needed for auth check).
    resp = client.execute(
        query="query { shop { id } }",
        variables={},
    )

    out = {
        "ok": True,
        "shop_domain": cfg.shop_domain,
        "api_version": cfg.api_version,
        "endpoint": client.endpoint_url,
        "token_present": bool(cfg.admin_access_token),
        "graphql": {
            "http_status": resp.http_status,
            "has_errors": bool(resp.errors),
            "shop_id_present": bool(((resp.data or {}).get("shop") or {}).get("id")),
        },
    }

    ctx["audit"].write("auth.check", {"ok": True, "graphql": {"http_status": resp.http_status}})
    ctx["out"].emit(out)
    return 0
