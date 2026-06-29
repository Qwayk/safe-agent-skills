from __future__ import annotations

from ..config import credential_fingerprint
from ..errors import ValidationError
from ..http import HttpClient
from ..sanitize import redact_value


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise ValidationError("Missing N8N_API_KEY")
    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"n8n-safe-agent-cli/{ctx.get('tool_version')}",
    )
    response = client.request(
        "GET",
        cfg.base_url.rstrip("/") + "/workflows",
        headers={"Accept": "application/json", "X-N8N-API-KEY": cfg.api_key},
        params={"limit": "1"},
        retries=1,
    )
    try:
        body = response.json()
    except Exception:
        body = {"text": response.text()}
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "credential_fingerprint": credential_fingerprint(cfg.api_key),
        "sample_request": {"method": "GET", "path": "/workflows", "query": {"limit": "1"}},
        "response": {"status": response.status, "body": redact_value(body)},
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
