from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..instagram_client import InstagramAPIClient
from ..oauth_tokens import get_token_status, redact_token_dict, token_path_for_env_file, write_token_payload
from .write_utils import run_write_command


def _client(ctx: dict[str, Any]) -> InstagramAPIClient:
    return InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_auth_check(args: object, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    result = client.get_me()
    out = {
        "ok": True,
        "auth": "ok",
        "method": "auth.check",
        "result": result,
        "base_url": ctx["cfg"].base_url,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_login_url(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    scope = str(getattr(args, "scope", "") or "").strip() or None
    state = str(getattr(args, "state", "") or "").strip() or None
    url = client.build_login_url(scope=scope, state=state, response_type="code")
    out = {"ok": True, "command": "auth.login_url", "login_url": url}
    ctx["audit"].write("auth.login_url", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    src = Path(args.file)

    def execute() -> dict[str, Any]:
        src_data = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(src_data, dict):
            raise ValidationError("Token file must be a JSON object")
        dest = token_path_for_env_file(ctx["env_file"])
        st = write_token_payload(payload=src_data, dest_file=dest)
        return {"stored_to": st.path, "token_status": st.__dict__}

    out = run_write_command(
        ctx=ctx,
        command="auth token set",
        selector={"kind": "auth.token.set", "file": str(src)},
        proposed_changes=[{"action": "store_token_from_file", "source": str(src)}],
        execute=execute,
    )
    out["command"] = "auth.token_set"
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {
        "ok": True,
        "env_token_present": bool(ctx["cfg"].token),
        "token_status": st.__dict__,
    }
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_code_exchange(args, ctx) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    if not code:
        raise ValidationError("Missing --code")

    client = _client(ctx)

    def execute() -> dict[str, Any]:
        payload = client.exchange_auth_code(code=code)
        if not isinstance(payload, dict):
            raise ValidationError("Auth code exchange returned unexpected payload")
        dest = token_path_for_env_file(ctx["env_file"])
        write_token_payload(payload=payload, dest_file=dest)
        return redact_token_dict(payload)

    out = run_write_command(
        ctx=ctx,
        command="auth code exchange",
        selector={"kind": "auth.code.exchange"},
        proposed_changes=[{"action": "exchange_auth_code", "fields": ["access_token", "user_id", "expires_in"]}],
        execute=execute,
    )
    out["command"] = "auth.code_exchange"
    ctx["audit"].write("auth.code_exchange", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_exchange_long(args, ctx) -> int:
    token_hint = str(getattr(args, "short_token", "") or "").strip()

    client = InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        token=token_hint or None,
    )

    def execute() -> dict[str, Any]:
        payload = client.exchange_short_lived_to_long()
        if not isinstance(payload, dict):
            raise ValidationError("Token exchange response has unexpected payload")
        dest = token_path_for_env_file(ctx["env_file"])
        write_token_payload(payload=payload, dest_file=dest)
        return redact_token_dict(payload)

    out = run_write_command(
        ctx=ctx,
        command="auth token exchange-long",
        selector={"kind": "auth.token.exchange_long"},
        proposed_changes=[{"action": "exchange_short_lived_token"}],
        execute=execute,
    )
    out["command"] = "auth.token_exchange_long"
    ctx["audit"].write("auth.token_exchange_long", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_refresh(args, ctx) -> int:
    token_hint = str(getattr(args, "long_token", "") or "").strip()

    client = InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        token=token_hint or None,
    )

    def execute() -> dict[str, Any]:
        payload = client.refresh_long_lived_token()
        if not isinstance(payload, dict):
            raise ValidationError("Token refresh response has unexpected payload")
        dest = token_path_for_env_file(ctx["env_file"])
        write_token_payload(payload=payload, dest_file=dest)
        return redact_token_dict(payload)

    out = run_write_command(
        ctx=ctx,
        command="auth token refresh",
        selector={"kind": "auth.token.refresh"},
        proposed_changes=[{"action": "refresh_long_lived_token"}],
        execute=execute,
    )
    out["command"] = "auth.token_refresh"
    ctx["audit"].write("auth.token_refresh", out)
    ctx["out"].emit(out)
    return 0
