from __future__ import annotations

from ..config import normalize_ad_account_id
from ..errors import ValidationError


def cmd_auth_check(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    cfg = ctx.get("cfg")
    client = ctx.get("graph")

    if not cfg or not client:
        raise RuntimeError("Internal error: missing cfg/client")

    if not cfg.access_token:
        raise ValidationError("Missing META_ADS_ACCESS_TOKEN (run `meta-ads-api-tool onboarding`)")

    ad_account_id = normalize_ad_account_id(getattr(args, "ad_account_id", None) or cfg.ad_account_id)

    # Prefer an account-scoped call when an ad account id is available, since Marketing tokens
    # can be system-user tokens where `/me` isn't always as helpful.
    if ad_account_id:
        payload = client.get_ad_account(ad_account_id, params={"fields": "id,account_id,name,account_status,currency,timezone_name"})
        out_obj = {"ok": True, "auth_check": {"mode": "ad_account", "ad_account_id": ad_account_id, "response": payload}}
        audit.write("auth.check", {"mode": "ad_account", "ad_account_id": ad_account_id, "ok": True})
        out.emit(out_obj)
        return 0

    payload = client.get("me", params={"fields": "id,name"})
    out_obj = {"ok": True, "auth_check": {"mode": "me", "response": payload}}
    audit.write("auth.check", {"mode": "me", "ok": True})
    out.emit(out_obj)
    return 0

