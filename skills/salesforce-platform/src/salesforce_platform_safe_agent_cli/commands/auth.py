from __future__ import annotations

from pathlib import Path

from ..config import load_config
from ..http import HttpClient
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def cmd_auth_check(args, ctx) -> int:
    cfg = load_config(ctx["env_file"])
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    if not cfg.instance_url:
        ctx["out"].emit(
            {
                "ok": False,
                "error": "Missing SALESFORCE_INSTANCE_URL",
                "error_type": "ValidationError",
            }
        )
        return 1
    if not cfg.token:
        ctx["out"].emit(
            {
                "ok": False,
                "error": "Missing Salesforce access token. Set SALESFORCE_ACCESS_TOKEN or use auth token set.",
                "error_type": "ValidationError",
                "instance_url": cfg.instance_url,
                "oauth_token": {"exists": status.exists, "path": status.path},
            }
        )
        return 1

    client = HttpClient(
        timeout_s=float(getattr(args, "timeout_s", None) or cfg.timeout_s),
        verbose=bool(getattr(args, "verbose", False)),
        user_agent="qwayk-salesforce-platform-safe-agent-cli/safe-apis",
    )
    resp = client.request(
        "GET",
        cfg.instance_url.rstrip("/") + f"/services/data/v{cfg.api_version}/limits/",
        headers={
            "Authorization": f"Bearer {cfg.token}",
            "Accept": "application/json",
        },
    )
    limits = resp.json()
    out = {
        "ok": True,
        "instance_url": cfg.instance_url,
        "api_version": cfg.api_version,
        "token_source": cfg.token_source,
        "oauth_token": {"exists": status.exists, "path": status.path},
        "sforce_limit_info": resp.headers.get("sforce-limit-info"),
        "sample_limits": {
            name: limits.get(name)
            for name in ["DailyApiRequests", "DailyBulkApiBatches", "DailyBulkV2QueryJobs"]
            if isinstance(limits, dict) and name in limits
        },
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
