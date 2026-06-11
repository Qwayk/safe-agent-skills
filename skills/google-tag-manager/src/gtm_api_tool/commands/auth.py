from __future__ import annotations

from typing import Any

from ..auth import auth_summary
from ..errors import ToolError
from ..gtm_api import GtmApi


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    api = GtmApi(
        cfg=cfg,
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
        timeout_s=ctx.get("timeout_s"),
    )

    # Read-only smoke request (no side effects).
    # Discovery: tagmanager.accounts.list -> GET tagmanager/v2/accounts
    out: dict[str, Any] = {
        "ok": True,
        "auth": auth_summary(cfg),
        "request": {
            "method_id": "tagmanager.accounts.list",
            "http_method": "GET",
            "path": "tagmanager/v2/accounts",
        },
        "response": None,
    }

    try:
        resp = api.request(
            http_method="GET",
            path="tagmanager/v2/accounts",
            query=None,
            body=None,
            retries=cfg.read_retries,
        )
        out["response"] = {"ok": resp.status < 400, "status": resp.status, "url": resp.url, "body": resp.body_json}
    except ToolError:
        raise
    except Exception as e:  # noqa: BLE001
        out["ok"] = False
        out["response"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    ctx["audit"].write("auth.check", {"ok": out["ok"], "mode": cfg.auth_mode})
    ctx["out"].emit(out)
    return 0 if out.get("ok") else 1
