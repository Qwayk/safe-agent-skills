from __future__ import annotations

from ..errors import ValidationError
from ..api_runner import execute_call, build_headers, redact_headers


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.token:
        out = {
            "ok": False,
            "base_url": cfg.base_url,
            "error": "Missing CALLRAIL_API_TOKEN",
            "error_type": ValidationError.__name__,
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 1

    url = f"{cfg.base_url}/v3/a.json"
    request_meta = {
        "method": "GET",
        "url": url,
        "headers": redact_headers(build_headers(cfg.token, cfg.request_from)),
    }
    try:
        request_meta, response_meta = execute_call(
            cfg=cfg,
            method="GET",
            url=url,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx["verbose"]),
            user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
            payload=None,
        )
    except Exception as e:  # noqa: BLE001
        out = {
            "ok": False,
            "base_url": cfg.base_url,
            "request": request_meta,
            "error": str(e),
            "error_type": type(e).__name__,
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 1

    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_token_present": bool(cfg.token),
        "request": request_meta,
        "response": response_meta,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
