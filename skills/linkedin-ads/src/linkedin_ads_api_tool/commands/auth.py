from __future__ import annotations

from pathlib import Path

from ..errors import ValidationError
from ..http import HttpClient, build_linkedin_headers
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file
from ..operation_catalog import ADS_ACCOUNT_USERS


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError(
            "Missing LinkedIn token. Set LINKEDIN_ADS_TOKEN/LINKEDIN_ADS_ACCESS_TOKEN or run onboarding/auth token set first."
        )

    url = f"{cfg.base_url.rstrip('/')}/adAccountUsers"
    headers = build_linkedin_headers(
        token=cfg.token,
        linkedin_version=cfg.linkedin_version,
        restli_protocol_version=cfg.restli_protocol_version,
    )
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="linkedin-ads-safe-cli/0.1.0")
    response = client.request("GET", url, headers=headers, params={"q": "authenticatedUser"})
    try:
        payload = response.json()
    except Exception:
        payload = {"_raw": response.text()}

    count = None
    if isinstance(payload, dict) and isinstance(payload.get("elements"), list):
        count = len(payload["elements"])
    elif isinstance(payload, list):
        count = len(payload)

    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "token_present": bool(cfg.token),
        "auth_check": {
            "doc_url": ADS_ACCOUNT_USERS,
            "method": "GET",
            "query": "authenticatedUser",
            "status": response.status,
            "authenticated_users_count": count,
        },
        "response": payload,
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
