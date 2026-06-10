from __future__ import annotations

from pathlib import Path

from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def cmd_auth_check(args, ctx) -> int:
    # Keep this command read-only and safe: it should only validate local configuration.
    # This tool's live Stripe API calls are intentionally gated elsewhere.
    _ = args
    cfg = ctx["cfg"]

    api_key = str(getattr(cfg, "api_key", "") or "")
    key_present = bool(api_key)
    key_type = "unknown"
    mode = "unknown"
    if api_key.startswith("sk_"):
        key_type = "secret"
    elif api_key.startswith("rk_"):
        key_type = "restricted"
    if "_test_" in api_key:
        mode = "test"
    elif "_live_" in api_key:
        mode = "live"

    # OAuth token helpers are optional, but Stripe API auth uses API keys.
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    out = {
        "ok": True,
        "stripe_api_key_present": key_present,
        "stripe_api_key_type": key_type,
        "stripe_api_key_mode": mode,
        "stripe_version_override": getattr(cfg, "stripe_version", None),
        "stripe_account_allowlist_configured": bool(getattr(cfg, "stripe_account_allowlist", ())),
        "stripe_account_allowlist_count": len(getattr(cfg, "stripe_account_allowlist", ()) or ()),
        "oauth_token": {"exists": status.exists, "path": status.path},
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
