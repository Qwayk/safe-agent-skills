from __future__ import annotations

from ..errors import ToolError
from ..paypal_auth import resolve_access_token


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    try:
        token_result = resolve_access_token(
            cfg=cfg,
            verbose=bool(ctx.get("verbose")),
            timeout_s=float(ctx["timeout_s"]) if ctx.get("timeout_s") else None,
        )
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError("PayPal auth check failed.") from exc
    scopes = token_result.scope.split() if token_result.scope else []
    out = {
        "ok": True,
        "environment": cfg.environment,
        "base_url": cfg.base_url,
        "token_source": token_result.source,
        "token_type": token_result.token_type,
        "expires_in": token_result.expires_in,
        "scope_count": len(scopes),
        "scopes": scopes,
        "app_id": token_result.app_id,
        "partner_attribution_id_configured": bool(cfg.partner_attribution_id),
        "auth_assertion_configured": bool(cfg.auth_assertion),
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
