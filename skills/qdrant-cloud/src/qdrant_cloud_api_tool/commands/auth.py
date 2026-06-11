from __future__ import annotations

from typing import Any

from ..cloud_http import QdrantCloudHttpClient
from ..errors import SafetyError, ValidationError
from ..operations_v1 import find_operation_by_rpc

_AUTH_CHECK_RPC = "qdrant.cloud.account.v1.AccountService.ListAccounts"


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    live = bool(ctx.get("live"))

    out: dict[str, Any] = {
        "ok": True,
        "live": live,
        "base_url": cfg.base_url,
        "api_key_present": bool(cfg.api_key),
        "checked": "offline" if not live else "live",
        "notes": None,
    }

    if not live:
        out["notes"] = "Offline OK. Re-run with --live to validate credentials against the API."
        ctx["audit"].write("auth.check.offline", {"base_url": cfg.base_url})
        ctx["out"].emit(out)
        return 0

    if not cfg.api_key:
        raise ValidationError("Missing QDRANT_CLOUD_API_KEY")

    op = find_operation_by_rpc(_AUTH_CHECK_RPC)
    if op.http_verb.upper() != "GET":
        raise SafetyError(f"Internal error: auth check RPC must be GET, got {op.http_verb}")

    client = QdrantCloudHttpClient(
        base_url=cfg.base_url,
        api_key=cfg.api_key,
        timeout_s=float(ctx["timeout_s"] or cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    result = client.request_json(live=True, method=op.http_verb, path=op.http_path)
    out.update(
        {
            "ok": bool(result.ok),
            "http": {"url": result.url, "status": result.status},
            "response": result.response_json,
            "response_text": result.response_text,
            "error": result.error,
        }
    )
    ctx["audit"].write("auth.check.live", {"base_url": cfg.base_url, "ok": bool(out["ok"])})
    ctx["out"].emit(out)
    return 0 if bool(out["ok"]) else 1

