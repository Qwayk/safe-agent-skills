from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def cmd_account_campaign_mappings_get(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    client = _client(ctx)
    res = client.get(f"/account-campaign-mappings/{email}")
    out = {"ok": True, "account_campaign_mapping": res.data}
    ctx["audit"].write("account_campaign_mappings.get", {"ok": True})
    ctx["out"].emit(out)
    return 0

