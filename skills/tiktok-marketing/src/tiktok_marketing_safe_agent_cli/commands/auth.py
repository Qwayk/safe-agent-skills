from __future__ import annotations

from pathlib import Path

from ..api_dispatch import (
    build_api_call_plan,
    load_operations_from_pinned_snapshot,
    operations_by_command,
)
from ..errors import ToolError, ValidationError
from ..http import HttpClient
from ..oauth_tokens import get_token_status, token_path_for_env_file, read_token_json, write_token_from_file


def _resolve_access_token(cfg, env_file: str) -> tuple[str | None, str | None]:
    env_token = str(cfg.token or "").strip()
    if env_token:
        return env_token, "env"

    token_path = token_path_for_env_file(env_file)
    token_data = read_token_json(token_path) if token_path.exists() else None
    if isinstance(token_data, dict):
        access_token = str(token_data.get("access_token") or token_data.get("token") or "").strip()
        if access_token:
            return access_token, "token_file"
    return None, None


def _operation_lookup(op_name: str):
    op = operations_by_command(load_operations_from_pinned_snapshot()).get(op_name)
    if not op:
        raise ValidationError(f"Missing operation in pinned manifest: {op_name}")
    return op


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out: dict[str, object] = {
        "ok": True,
        "base_url": cfg.base_url,
        "app_id_present": bool(cfg.app_id),
        "app_secret_present": bool(cfg.app_secret),
        "env_access_token_present": bool(cfg.token),
        "oauth_token": {"exists": tok_status.exists, "path": tok_status.path},
        "live_checked": False,
    }

    access_token, token_source = _resolve_access_token(cfg, str(ctx["env_file"]))
    out["token_source"] = token_source

    if not access_token:
        raise ValidationError("Missing access token. Set TIKTOK_MARKETING_ACCESS_TOKEN or store token.json in .state")

    if not cfg.app_id or not cfg.app_secret:
        raise ValidationError("Missing TIKTOK_MARKETING_APP_ID or TIKTOK_MARKETING_APP_SECRET")

    op = _operation_lookup("oauth2-advertiser-get")
    plan = build_api_call_plan(
        tool="tiktok-marketing-api-tool",
        tool_version="0.1.0",
        env_fingerprint=str(cfg.base_url),
        op=op,
        base_url=str(cfg.base_url),
        path_json=None,
        query_json=None,
        body_json=None,
        path_pairs=None,
        query_pairs=[f"app_id={cfg.app_id}", f"secret={cfg.app_secret}"],
        body_pairs=None,
        file_pairs=None,
        query_defaults={"app_id": str(cfg.app_id or ""), "secret": str(cfg.app_secret or ""), "access_token": str(access_token)},
        header_defaults={"access_token": str(access_token)},
    )

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"tiktok-marketing-api-tool/{ctx.get('tool_version') or '0.1.0'}",
    )
    response = client.request(
        method=plan["operation"]["method"],
        url=plan["operation"]["url"],
        headers={"Accept": "application/json", "Access-Token": str(access_token)},
        params=plan["inputs"].get("query") or {},
    )
    payload = response.json()
    if isinstance(payload, dict):
        code = payload.get("code")
        if code is not None and str(code).strip() not in {"", "0"}:
            message = payload.get("message") or payload.get("msg") or "TikTok API returned an error"
            raise ToolError(f"TikTok API returned code {code}: {message}")

    advertiser_count = None
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            advertisers = data.get("list")
            if isinstance(advertisers, list):
                advertiser_count = len(advertisers)

    out["live_checked"] = True
    out["live_status_code"] = response.status
    out["token_source"] = token_source
    out["auth_endpoint"] = "oauth2-advertiser-get"
    out["advertiser_count"] = advertiser_count
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
