from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..json_files import write_json_file
from ..oauth_tokens import get_token_status, read_token_json, token_path_for_env_file
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    ensure_blocked_apply_contract,
    recovery_contract,
    refusal_output,
)


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    live = bool(getattr(args, "live", False))
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    note = None

    # Keep this command read-only and safe by default: it should only validate local configuration.
    # If `--live` is requested, it may run a minimal network call in real use (tests do not use this).
    if live:
        note = "Live check not implemented in this tool build (use `api <resource.method>` for a real request)."

    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "api_key_present": bool(cfg.api_key),
        "oauth_client_secrets_file": cfg.oauth_client_secrets_file,
        "oauth_scopes": list(cfg.oauth_scopes),
        "oauth_token": {"exists": status.exists, "path": status.path},
        "note": note,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def _build_auth_write_plan(
    *,
    ctx: dict[str, Any],
    command: str,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    provider_write: dict[str, Any] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "youtube-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command_id": command,
        "command": str(ctx.get("command_str") or command),
        "selector": selector,
        "risk_level": "high",
        "risk_reasons": ["local-auth-state-write"],
        "preconditions": ["before-state for the local auth state exists before any write"],
        "baseline": {"env_fingerprint": ctx["cfg"].base_url},
        "proposed_changes": proposed_changes,
        "before_state": blocked_before_state(
            action=command,
            proposed_changes=proposed_changes,
            provider_write=provider_write,
            local_state=local_state,
        ),
        "verification_plan": before_state_refusal_verification_plan(),
        "recovery": recovery_contract(),
        "dry_run": True,
    }


def _emit_auth_write_plan_or_refusal(*, ctx: dict[str, Any], plan: dict[str, Any], command: str) -> int:
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path, "command": command}
        ctx["audit"].write(f"{command}.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = ensure_blocked_apply_contract(
        plan,
        action=command,
        proposed_changes=plan.get("proposed_changes") if isinstance(plan.get("proposed_changes"), list) else [],
        local_state=plan.get("before_state", {}).get("local_state") if isinstance(plan.get("before_state"), dict) else None,
    )
    out = refusal_output(plan=plan)
    out["command"] = command
    ctx["audit"].write(f"{command}.refused", {"reasons": out["reasons"]})
    ctx["out"].emit(out)
    return 0


def cmd_auth_login(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    client_secrets_file = str(getattr(args, "client_secrets_file", "") or "").strip() or (
        cfg.oauth_client_secrets_file or ""
    )
    if not client_secrets_file:
        raise ValidationError(
            "Missing OAuth client secrets file (set YOUTUBE_OAUTH_CLIENT_SECRETS_FILE or pass --client-secrets-file)"
        )
    p = Path(client_secrets_file)
    if not p.exists():
        raise ValidationError(f"OAuth client secrets file not found: {p}")

    scopes_raw = str(getattr(args, "scopes", "") or "").strip()
    scopes = list(cfg.oauth_scopes)
    if scopes_raw:
        scopes = [s for s in (x.strip() for x in scopes_raw.replace(",", " ").split()) if s]
    if not scopes:
        raise ValidationError("OAuth scopes list must not be empty")

    dest = token_path_for_env_file(ctx["env_file"])
    plan = _build_auth_write_plan(
        ctx=ctx,
        command="auth.login",
        selector={"kind": "auth.login", "target": ".state/token.json"},
        proposed_changes=[
            {
                "action": "run_google_oauth_flow",
                "client_secrets_file": str(p),
                "scopes": scopes,
                "console": bool(getattr(args, "console", False)),
            }
        ],
        provider_write={"service": "Google OAuth", "action": "oauth_login_flow"},
        local_state={"kind": "oauth_token_store", "path": str(dest), "writes_token_file": True},
    )
    return _emit_auth_write_plan_or_refusal(ctx=ctx, plan=plan, command="auth.login")


def cmd_auth_token_set(args: Any, ctx: dict[str, Any]) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    plan = _build_auth_write_plan(
        ctx=ctx,
        command="auth.token_set",
        selector={"kind": "auth.token", "target": ".state/token.json"},
        proposed_changes=[{"action": "store_token_file", "source_file": str(Path(args.file)), "dest_file": str(dest)}],
        local_state={"kind": "oauth_token_store", "path": str(dest), "writes_token_file": True},
    )
    return _emit_auth_write_plan_or_refusal(ctx=ctx, plan=plan, command="auth.token_set")


def cmd_auth_token_status(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_show_safe(args: Any, ctx: dict[str, Any]) -> int:
    """
    Debug helper: show a redacted view of the token file (never includes token values).
    """
    _ = args
    p = token_path_for_env_file(ctx["env_file"])
    data = read_token_json(p)
    out: dict[str, Any] = {"ok": True, "exists": bool(data is not None), "path": str(p), "token": None}
    if isinstance(data, dict):
        safe: dict[str, Any] = {}
        for k, v in data.items():
            lk = str(k).lower()
            if lk in {"access_token", "refresh_token", "id_token", "client_secret", "token"} or lk.endswith("_token"):
                safe[k] = "***REDACTED***"
            else:
                safe[k] = v
        out["token"] = safe
    ctx["audit"].write("auth.token_show_safe", {"exists": out["exists"], "path": out["path"]})
    ctx["out"].emit(out)
    return 0
