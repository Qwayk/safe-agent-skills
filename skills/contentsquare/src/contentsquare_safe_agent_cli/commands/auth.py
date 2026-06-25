from __future__ import annotations

from ..contentsquare_client import ContentsquareClient
from ..errors import ValidationError


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    scope = getattr(args, "scope", None) or "data-export"
    if "enrichment" in str(scope).split() and str(scope).strip() != "enrichment":
        raise ValidationError("Contentsquare enrichment OAuth scope cannot be combined with other scopes")
    token = ContentsquareClient(
        cfg=cfg,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        oauth_project_id=ctx.get("oauth_project_id"),
    ).token(scope=scope)
    out = {
        "ok": True,
        "auth_base_url": cfg.auth_base_url,
        "api_base_url": cfg.api_base_url or token.endpoint,
        "token_obtained": True,
        "token_expires_in_seconds": token.expires_in,
        "scope": token.scope,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_me(args, ctx) -> int:
    _ = args
    payload = ContentsquareClient(
        cfg=ctx["cfg"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        oauth_project_id=ctx.get("oauth_project_id"),
    ).me()
    out = {"ok": True, "credential": payload}
    ctx["audit"].write("auth.me", out)
    ctx["out"].emit(out)
    return 0
