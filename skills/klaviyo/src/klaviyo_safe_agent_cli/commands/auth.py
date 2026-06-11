from __future__ import annotations

from typing import Any

from ..api_dispatch import join_base_url_and_path
from ..config import build_env_fingerprint
from ..http import HttpClient


def _redact_message(message: str, *, api_key: str | None, company_id: str | None) -> str:
    text = str(message or "")
    if not text:
        return text
    for value in (api_key, company_id):
        if value:
            text = text.replace(str(value), "***REDACTED***")
    return text


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    live_allowed = bool(ctx.get("live"))
    out: dict[str, Any] = {
        "ok": True,
        "base_url": cfg.base_url,
        "api_key_present": bool(cfg.api_key),
        "company_id_present": bool(cfg.company_id),
        "live_allowed": live_allowed,
        "live_checked": False,
    }
    out["env_fingerprint"] = build_env_fingerprint(cfg)
    if not live_allowed:
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    if not cfg.api_key:
        out.update(
            {
                "ok": False,
                "error_type": "ValidationError",
                "error": "Missing KLAVIYO_API_KEY for live auth checks",
                "live_checked": True,
                "live_ok": False,
            }
        )
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    headers = {
        "authorization": f"Klaviyo-API-Key {cfg.api_key}",
        "accept": "application/vnd.api+json",
        "revision": str(cfg.api_revision),
    }
    client = HttpClient(
        timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"klaviyo-safe-agent-cli/{ctx.get('tool_version') or '0.1.0'}",
    )
    url = join_base_url_and_path(str(cfg.base_url), "/api/accounts")
    try:
        response = client.request(
            method="GET",
            url=url,
            headers=headers,
            params={"fields[account]": "public_api_key"},
            json_body=None,
        )
    except RuntimeError as exc:
        status = None
        message = _redact_message(str(exc).splitlines()[0], api_key=cfg.api_key, company_id=cfg.company_id)
        first = str(exc).strip().splitlines()[0] if str(exc).strip() else ""
        if first.startswith("HTTP "):
            parts = first.split()
            if len(parts) > 1:
                try:
                    status = int(parts[1])
                except ValueError:
                    status = None

        out.update(
            {
                "ok": False,
                "live_checked": True,
                "live_status_code": status,
                "live_ok": False,
                "error_type": "HttpError",
                "error": message or "HTTP error",
            }
        )
        if cfg.company_id:
            out["env_company_id_present"] = True
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    out["live_checked"] = True
    out["live_status_code"] = response.status
    out["live_ok"] = response.status < 400
    if response.status < 400 and cfg.company_id is None:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                if isinstance(payload.get("data"), list):
                    first = payload["data"][0] if payload["data"] else None
                    if isinstance(first, dict):
                        attributes = first.get("attributes") or {}
                        if isinstance(attributes, dict) and attributes.get("public_api_key"):
                            out["derived_company_id"] = str(attributes["public_api_key"])
        except Exception:
            pass

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
