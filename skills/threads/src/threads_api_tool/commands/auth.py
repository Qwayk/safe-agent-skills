from __future__ import annotations

from typing import Any

from ..commands.common import run_write_command
from ..errors import ValidationError
from ..oauth_tokens import redact_token_dict, token_path_for_env_file, write_token_payload
from ..threads_client import ThreadsAPIClient


def _client(ctx: dict[str, Any]) -> ThreadsAPIClient:
    return ThreadsAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_auth_check(args: object, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    result = client.get_me(fields="id,username")
    out = {
        "ok": True,
        "command": "auth.check",
        "result": result,
        "method": "auth.check",
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_authorize_url(args, ctx) -> int:
    _ = ctx
    scope = str(getattr(args, "scope", "") or "").strip() or None
    state = str(getattr(args, "state", "") or "").strip() or None
    client = _client(ctx)
    out = {
        "ok": True,
        "command": "auth.authorize_url",
        "authorize_url": client.build_authorize_url(scope=scope, state=state, response_type="code"),
    }
    ctx["audit"].write("auth.authorize_url", out)
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
        command="auth.code_exchange",
        selector={"kind": "auth.code_exchange", "code": "***REDACTED***"},
        proposed_changes=[{"action": "exchange_auth_code", "code": "***REDACTED***"}],
        execute=execute,
    )
    out["command"] = "auth.code_exchange"
    ctx["audit"].write("auth.code_exchange", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    token_status = ctx["cfg"].token is not None
    default_user_id = str(getattr(ctx["cfg"], "default_user_id", "") or "").strip() or None
    from ..oauth_tokens import get_token_status

    status = get_token_status(token_path_for_env_file(ctx["env_file"]))

    out = {
        "ok": True,
        "command": "auth.token_status",
        "env_token_present": token_status,
        "default_user_id": default_user_id,
        "token_store": {
            "exists": status.exists,
            "path": status.path,
            "updated_at_utc": status.updated_at_utc,
            "fields": status.fields,
            "has_refresh_token": status.has_refresh_token,
            "expires_at_utc": status.expires_at_utc,
        },
    }
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_exchange_long(args, ctx) -> int:
    short_token = str(getattr(args, "short_token", "") or "").strip() or None

    client = _client(ctx)

    def execute() -> dict[str, Any]:
        payload = client.exchange_short_lived_token(short_token=short_token)
        if not isinstance(payload, dict):
            raise ValidationError("Token exchange response has unexpected payload")
        dest = token_path_for_env_file(ctx["env_file"])
        write_token_payload(payload=payload, dest_file=dest)
        return redact_token_dict(payload)

    out = run_write_command(
        ctx=ctx,
        command="auth.token_exchange_long",
        selector={"kind": "auth.exchange_long", "source": "short_token" if short_token else "env"},
        proposed_changes=[{"action": "exchange_short_lived_token"}],
        execute=execute,
    )
    out["command"] = "auth.token_exchange_long"
    ctx["audit"].write("auth.token_exchange_long", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_refresh(args, ctx) -> int:
    long_token = str(getattr(args, "long_token", "") or "").strip() or None

    client = _client(ctx)

    def execute() -> dict[str, Any]:
        payload = client.refresh_long_lived_token(long_token=long_token)
        if not isinstance(payload, dict):
            raise ValidationError("Token refresh response has unexpected payload")
        dest = token_path_for_env_file(ctx["env_file"])
        write_token_payload(payload=payload, dest_file=dest)
        return redact_token_dict(payload)

    out = run_write_command(
        ctx=ctx,
        command="auth.token_refresh",
        selector={"kind": "auth.refresh", "source": "long_token" if long_token else "env"},
        proposed_changes=[{"action": "refresh_long_lived_token"}],
        execute=execute,
    )
    out["command"] = "auth.token_refresh"
    ctx["audit"].write("auth.token_refresh", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_app_token_generate(args, ctx: object) -> int:
    _ = args
    client = _client(ctx)
    payload = client.generate_app_access_token()
    if not isinstance(payload, dict):
        raise ValidationError("App token response has unexpected payload")

    out = {
        "ok": True,
        "command": "auth.app_token_generate",
        "result": redact_token_dict(payload),
    }
    ctx["audit"].write("auth.app_token_generate", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_debug_token(args, ctx) -> int:
    input_token = str(getattr(args, "input_token", "") or "").strip() or None
    client = _client(ctx)
    payload = client.debug_token(input_token=input_token)
    if not isinstance(payload, dict):
        raise ValidationError("Debug token response has unexpected payload")
    out = {
        "ok": True,
        "command": "auth.debug_token",
        "result": redact_token_dict(payload),
    }
    ctx["audit"].write("auth.debug_token", out)
    ctx["out"].emit(out)
    return 0
