from __future__ import annotations

import base64
from typing import Any
from pathlib import Path

from ..errors import SafetyError
from ..http import HttpClient
from ..redaction import redact_headers, redact_obj
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def _build_headers_for_live(cfg) -> dict[str, str]:
    if getattr(cfg, "oauth_access_token", None):
        return {"Authorization": f"Bearer {cfg.oauth_access_token}"}
    if getattr(cfg, "email", None) and getattr(cfg, "api_token", None):
        raw = f"{cfg.email}/token:{cfg.api_token}".encode("utf-8")
        b64 = base64.b64encode(raw).decode("ascii")
        return {"Authorization": f"Basic {b64}"}
    raise SafetyError("Missing Zendesk credentials: set ZENDESK_EMAIL + ZENDESK_API_TOKEN or ZENDESK_OAUTH_ACCESS_TOKEN")


def _extract_rate_limit_headers(headers: dict[str, str]) -> dict[str, str]:
    keep: dict[str, str] = {}
    for k, v in (headers or {}).items():
        lk = str(k).lower().strip()
        if lk in {"retry-after"} or "rate" in lk or "ratelimit" in lk:
            keep[lk] = v
    return keep


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    out: dict[str, Any] = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_api_token_present": bool(cfg.api_token),
        "env_email_present": bool(cfg.email),
        "env_oauth_access_token_present": bool(cfg.oauth_access_token),
        "oauth_token": {"exists": status.exists, "path": status.path},
        "live_supported": True,
    }

    if bool(getattr(args, "live", False)):
        headers = _build_headers_for_live(cfg)
        url = str(cfg.base_url).rstrip("/") + "/api/v2/account/settings.json"
        client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="zendesk-api-tool")
        resp = client.request(method="GET", url=url, headers=headers, retries=2)
        resp_json: Any = None
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = {"raw_text": resp.text()}
        out["live"] = {
            "status": resp.status,
            "url": resp.url,
            "rate_limit": _extract_rate_limit_headers(resp.headers),
            "headers": redact_headers(resp.headers),
            "json": redact_obj(resp_json),
        }

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
