from __future__ import annotations

from typing import Any

from .. import __version__
from ..api_dispatch import join_base_url_and_path
from ..http import HttpClient


def _build_auth_headers(cfg: Any) -> dict[str, str]:
    headers: dict[str, str] = {
        "authorization": f"Bearer {cfg.api_key}",
        "content-type": "application/json",
        "accept": "application/json",
    }
    if cfg.organization_id:
        headers["openai-organization"] = cfg.organization_id
    if cfg.project_id:
        headers["openai-project"] = cfg.project_id
    return headers


def _parse_http_error(exc: RuntimeError) -> tuple[int | None, str | None]:
    text = str(exc).strip()
    if not text:
        return None, None
    lines = text.splitlines()
    first_line = lines[0]
    parts = first_line.split()
    status: int | None = None
    if len(parts) >= 2 and parts[0] == "HTTP":
        try:
            status = int(parts[1])
        except ValueError:
            status = None
    details = "\n".join(lines[1:]) if len(lines) > 1 else None
    return status, details


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    """Report config state and optionally do a live auth check."""
    _ = args
    cfg = ctx["cfg"]
    live_allowed = bool(ctx.get("live"))
    out: dict[str, Any] = {
        "ok": True,
        "base_url": cfg.base_url,
        "api_key_present": bool(cfg.api_key),
        "organization_id_present": bool(cfg.organization_id),
        "project_id_present": bool(cfg.project_id),
        "live_allowed": live_allowed,
        "live_checked": False,
    }

    if not live_allowed:
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    if not cfg.api_key:
        out.update(
            {
                "ok": False,
                "error_type": "ValidationError",
                "error": "Missing OPENAI_API_KEY for live auth checks",
            }
        )
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    headers = _build_auth_headers(cfg)
    client = HttpClient(
        timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"openai-api-tool/{ctx.get('tool_version') or __version__}",
    )
    url = join_base_url_and_path(cfg.base_url, "/models")
    try:
        response = client.request(method="GET", url=url, headers=headers, params=None, json_body=None)
        out.update(
            {
                "live_checked": True,
                "live_status_code": response.status,
                "live_ok": response.status < 400,
            }
        )
    except RuntimeError as exc:
        status_code, details = _parse_http_error(exc)
        out.update(
            {
                "ok": False,
                "live_checked": True,
                "live_status_code": status_code,
                "live_ok": False,
                "error_type": "HttpError",
                "error": str(exc).splitlines()[0] if str(exc) else "HTTP error",
            }
        )
        if details:
            out["error_details"] = details

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
