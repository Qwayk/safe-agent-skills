from __future__ import annotations

from ..skimlinks import PRODUCT_SCOPE, SHARED_SCOPE, SkimlinksClient, make_http_client


def _safe_error_text(exc: Exception, cfg) -> str:
    text = str(exc)
    for value in (
        cfg.client_id,
        cfg.client_secret,
        cfg.product_client_id,
        cfg.product_client_secret,
    ):
        if value:
            text = text.replace(value, "<redacted>")
    return text


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = SkimlinksClient(cfg=cfg, http=make_http_client(ctx))
    scope = str(getattr(args, "scope", SHARED_SCOPE) or SHARED_SCOPE)
    scopes = [SHARED_SCOPE, PRODUCT_SCOPE] if scope == "all" else [scope]

    checks = []
    ok = True
    for item in scopes:
        try:
            checks.append(client.auth_check(scope=item))
        except Exception as exc:  # noqa: BLE001
            ok = False
            checks.append(
                {
                    "ok": False,
                    "scope": item,
                    "error": _safe_error_text(exc, cfg),
                    "error_type": type(exc).__name__,
                    "token_received": False,
                }
            )

    out = {
        "ok": ok,
        "checks": checks,
        "auth_url": cfg.auth_url,
        "publisher_id_configured": bool(cfg.publisher_id),
        "product_credentials_configured": bool(
            cfg.product_client_id and cfg.product_client_secret
        ),
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0 if ok else 1
