from __future__ import annotations

from ..errors import ValidationError
from .read_api import extract_list, read_request, redact_error, require_read_context


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = require_read_context(ctx["out"], ctx.get("cfg"))
    if cfg is None:
        return 1

    if not cfg.advertiser_id:
        out = {
            "ok": False,
            "blocked": True,
            "setup_needed": True,
            "error": "Missing AWIN_ADVERTISER_ID",
            "error_type": "SetupNeeded",
            "next_step": "Set AWIN_ADVERTISER_ID in .env and run auth check again",
        }
        ctx["out"].emit(out)
        return 1

    http = ctx["http_client"]
    token = cfg.token
    endpoint = f"advertisers/{cfg.advertiser_id}/publishers"
    try:
        resp = read_request(http=http, base_url=cfg.base_url, token=token, endpoint=endpoint)
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), token)
        raise ValidationError(f"Auth check request failed: {message}") from exc

    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Auth check response was not JSON: {exc}") from exc

    publishers = extract_list(payload, keys=("publishers", "items", "data"))

    out = {
        "ok": True,
        "auth_check": {
            "endpoint": endpoint,
            "method": "GET",
            "auth_header": "Bearer",
            "auth_query": ["accessToken"],
        },
        "publisher_count": len(publishers),
        "status": resp.status,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
