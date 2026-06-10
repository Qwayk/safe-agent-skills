from __future__ import annotations

from pathlib import Path

from ..errors import SafetyError, ToolError
from ..oauth_tokens import get_token_status, read_token_json, token_path_for_env_file, write_token_from_file
from ..http import HttpClient


def _resolve_access_token(cfg, env_file: str) -> str | None:
    if getattr(cfg, "token", None):
        return str(cfg.token).strip() or None

    token_path = token_path_for_env_file(env_file)
    data = read_token_json(token_path)
    if not data:
        return None
    token = data.get("access_token")
    return str(token).strip() if isinstance(token, str) and token.strip() else None


def _redact_auth_request_error(exc: Exception) -> str:
    message = str(exc)
    if "401" in message or "403" in message:
        return "authentication failed or missing required scopes"
    if "timeout" in message.lower():
        return "authentication check failed due to timeout"
    return "authentication check failed"


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    token = _resolve_access_token(cfg, ctx["env_file"])
    if not token:
        raise SafetyError("Missing token. Set HUBSPOT_ACCESS_TOKEN or run auth token set --file token.json")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "qwayk-hubspot-safe-agent-cli/auth-check",
    }

    transport = HttpClient(timeout_s=ctx["timeout_s"], verbose=bool(ctx.get("verbose")), user_agent="qwayk-hubspot-safe-agent-cli/auth-check")
    url = cfg.base_url.rstrip("/") + "/crm/owners/2026-03"
    try:
        response = transport.request("GET", url, headers=headers, params={"limit": 1})
        status = response.status
        payload = response.json() if response.body else None
    except Exception as e:  # noqa: BLE001
        safe_error = _redact_auth_request_error(e)
        raise ToolError(f"HubSpot auth check failed: {safe_error}") from None

    if payload is None:
        payload = {"sample": "ok"}

    out = {
        "ok": True,
        "scope": "read-check",
        "base_url": cfg.base_url,
        "status": status,
        "env_token_present": bool(cfg.token),
        "sample_owner_id": (
            ((payload.get("results") or [None])[0] or {}).get("id")
            if isinstance(payload, dict)
            else None
        ),
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
