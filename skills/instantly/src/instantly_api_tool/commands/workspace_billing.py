from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def cmd_workspace_billing_plan_details(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/workspace-billing/plan-details")
    ctx["audit"].write("workspace_billing.plan_details", {"ok": True})
    ctx["out"].emit({"ok": True, "plan_details": res.data})
    return 0


def cmd_workspace_billing_subscription_details(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/workspace-billing/subscription-details")
    ctx["audit"].write("workspace_billing.subscription_details", {"ok": True})
    ctx["out"].emit({"ok": True, "subscription_details": res.data})
    return 0

