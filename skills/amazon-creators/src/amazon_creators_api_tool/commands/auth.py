from __future__ import annotations

from pathlib import Path

from ..errors import SafetyError
from ..json_files import write_json_file
from ..oauth_tokens import (
    authorization_header,
    get_token_status,
    load_cached_token,
    redact_token_dict,
    token_path_for_env_file,
)
from .write_safety import build_local_write_plan, ensure_blocked_apply_contract, refusal_output


def cmd_auth_check(args, ctx) -> int:
    # Validate the loaded configuration and the cached token metadata without making a catalog request.
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    authorization_header(ctx["cfg"], ctx["env_file"])
    token_sample = redact_token_dict(load_cached_token(tok_path) or {})
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "credential_version": cfg.credential_version,
        "locale": cfg.locale,
        "oauth_token": {"status": status.__dict__, "sample": token_sample},
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    src = Path(args.file)
    if not src.exists():
        raise SafetyError(f"Refused: token input file not found: {src}")
    plan = build_local_write_plan(
        ctx=ctx,
        command_id="auth.token_set",
        selector={"kind": "oauth_token_cache", "target": ".state/token.json"},
        proposed_changes=[{"action": "store_token_file", "source_file": str(src), "dest_file": str(dest)}],
        risk_reasons=["local-token-cache-write"],
        local_state={"kind": "oauth_token_cache", "path": str(dest), "writes_token_file": True},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path, "command": "auth.token_set"}
        ctx["audit"].write("auth.token_set.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0
    plan = ensure_blocked_apply_contract(
        plan,
        action="auth.token_set",
        local_state={"kind": "oauth_token_cache", "path": str(dest), "writes_token_file": True},
    )
    out = refusal_output(plan=plan)
    out["command"] = "auth.token_set"
    ctx["audit"].write("auth.token_set.refused", {"reasons": out["reasons"]})
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_fetch(args, ctx) -> int:
    cfg = ctx["cfg"]
    force = bool(getattr(args, "force", False))
    dest = token_path_for_env_file(ctx["env_file"])
    plan = build_local_write_plan(
        ctx=ctx,
        command_id="auth.token_fetch",
        selector={"kind": "oauth_token_cache", "target": ".state/token.json"},
        proposed_changes=[
            {
                "action": "fetch_and_cache_token",
                "credential_version": cfg.credential_version,
                "locale": cfg.locale,
                "force": force,
                "dest_file": str(dest),
            }
        ],
        risk_reasons=["oauth-token-endpoint-request", "local-token-cache-write"],
        local_state={
            "kind": "oauth_token_cache",
            "path": str(dest),
            "writes_token_file": True,
            "uses_token_endpoint": True,
        },
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path, "command": "auth.token_fetch"}
        ctx["audit"].write("auth.token_fetch.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0
    plan = ensure_blocked_apply_contract(
        plan,
        action="auth.token_fetch",
        local_state={
            "kind": "oauth_token_cache",
            "path": str(dest),
            "writes_token_file": True,
            "uses_token_endpoint": True,
        },
    )
    out = refusal_output(plan=plan)
    out["command"] = "auth.token_fetch"
    ctx["audit"].write("auth.token_fetch.refused", {"reasons": out["reasons"]})
    ctx["out"].emit(out)
    return 0
