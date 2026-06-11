from __future__ import annotations

import json
from typing import Any

from ..api_dispatch import (
    build_api_call_plan,
    join_base_url_and_path,
    load_operations_from_pinned_snapshot,
    operations_by_id,
)
from ..errors import SafetyError, ValidationError
from ..http import HttpClient, redact_url
from ..oauth_tokens import read_token_json, token_path_for_env_file


def _load_user_access_token(env_file: str) -> str | None:
    tok_path = token_path_for_env_file(env_file)
    data = read_token_json(tok_path)
    if not data:
        return None
    tok = data.get("access_token")
    if isinstance(tok, str) and tok.strip():
        return tok.strip()
    return None


def cmd_users_resolve(args: Any, ctx: dict[str, Any]) -> int:
    username = str(getattr(args, "username", "") or "").strip()
    if not username:
        raise ValidationError("Missing --username")

    include_receives_dm = bool(getattr(args, "include_receives_your_dm", False))
    user_fields = ["id", "name", "username"]
    if include_receives_dm:
        user_fields.append("receives_your_dm")

    ops = load_operations_from_pinned_snapshot()
    op = operations_by_id(ops).get("getUsersByUsername")
    if not op:
        raise RuntimeError("Pinned OpenAPI snapshot missing operationId getUsersByUsername")

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "x-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx["cfg"].base_url),
        op=op,
        base_url=str(ctx["cfg"].base_url),
        env_file=str(ctx["env_file"]),
        env_bearer_token=ctx["cfg"].token,
        auth="auto",
        path_json=json.dumps({"username": username}),
        query_json=json.dumps({"user.fields": ",".join(user_fields)}),
        body_json=None,
        path_pairs=None,
        query_pairs=None,
        file_pairs=None,
    )

    if not bool(ctx.get("live")):
        out = {"ok": True, "dry_run": True, "plan": plan}
        ctx["audit"].write("users.resolve.plan", {"username": username})
        ctx["out"].emit(out)
        return 0

    auth_raw = plan.get("auth")
    auth_obj: dict[str, Any] = auth_raw if isinstance(auth_raw, dict) else {}
    auth_mode = str(auth_obj.get("mode") or "").strip()
    if auth_mode == "bearer":
        token = ctx["cfg"].token
    elif auth_mode == "oauth2":
        token = _load_user_access_token(str(ctx["env_file"]))
    elif auth_mode == "none":
        token = None
    else:
        token = None

    if auth_mode in {"bearer", "oauth2"} and not token:
        raise SafetyError("Refused: missing token for selected auth mode")
    if auth_mode == "unsupported":
        raise SafetyError("Refused: this operation requires an unsupported auth mode (UserToken)")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    operation_raw = plan.get("operation")
    op_obj: dict[str, Any] = operation_raw if isinstance(operation_raw, dict) else {}
    filled_path = str(op_obj.get("path_filled") or "").strip()
    url = join_base_url_and_path(str(ctx["cfg"].base_url), filled_path)
    inputs_raw = plan.get("inputs")
    inputs: dict[str, Any] = inputs_raw if isinstance(inputs_raw, dict) else {}
    query = inputs.get("query")
    if not isinstance(query, dict):
        query = {}

    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    resp = client.request("GET", url, headers=headers or None, params=query or None, retries=0)
    body_text = resp.text()
    body_json = None
    try:
        body_json = json.loads(body_text)
    except Exception:
        body_json = None

    out = {
        "ok": True,
        "dry_run": False,
        "request": {"method": "GET", "url": redact_url(resp.url)},
        "response": {"status": resp.status, "body_json": body_json, "body_text": None if body_json is not None else body_text},
    }
    ctx["audit"].write("users.resolve.live", {"username": username, "status": resp.status})
    ctx["out"].emit(out)
    return 0
