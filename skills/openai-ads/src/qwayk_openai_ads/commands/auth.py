from __future__ import annotations

from ..config import credential_fingerprint
from ..http import HttpClient
from ..sanitize import redact_url, redact_value


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.api_key:
        out = {
            "ok": False,
            "base_url": cfg.base_url,
            "api_key_present": False,
            "error": "Missing OPENAI_ADS_API_KEY",
            "error_type": "ValidationError",
        }
        ctx["audit"].write("auth.check.missing", out)
        ctx["out"].emit(out)
        return 1

    response = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"openai-ads-safe-agent-cli/{ctx.get('tool_version')}",
    ).request(
        "GET",
        cfg.base_url.rstrip("/") + "/ad_account",
        headers={"Accept": "application/json", "Authorization": f"Bearer {cfg.api_key}"},
        retries=1,
        url_sanitizer=redact_url,
    )
    try:
        body = response.json()
    except Exception:
        body = {"text": response.text()}
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "api_key_present": True,
        "credential_fingerprint": credential_fingerprint(cfg.api_key),
        "safe_read": "GET /ad_account",
        "response": {"status": response.status, "url": redact_url(response.url), "body": redact_value(body)},
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
