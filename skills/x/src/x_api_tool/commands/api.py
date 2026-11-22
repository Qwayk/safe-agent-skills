from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..api_dispatch import (
    build_api_call_plan,
    join_base_url_and_path,
    load_operations_from_pinned_snapshot,
    operations_by_id,
    validate_plan_for_apply,
)
from ..errors import SafetyError, ValidationError
from ..http import HttpClient, redact_url
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import read_token_json, token_path_for_env_file
from .write_safety import check_review, ensure_blocked_apply_contract, mark_reviewed, read_account, refusal_output


_POST_CHANGES = {"createPosts", "deletePosts"}
_MESSAGE_SENDS = {
    "createDirectMessagesByConversationId",
    "createDirectMessagesByParticipantId",
    "createDirectMessagesConversation",
    "sendChatMessage",
}


def _check_created_post(
    response: dict[str, Any], *, ctx: dict[str, Any], headers: dict[str, str], account: dict[str, str]
) -> dict[str, Any]:
    body = response.get("body_json")
    data = body.get("data") if isinstance(body, dict) else None
    post_id = str(data.get("id") or "") if isinstance(data, dict) else ""
    result: dict[str, Any] = {"supported": True, "ok": False, "post_id": post_id or None}
    if not post_id.isascii() or not post_id.isdigit():
        return {**result, "notes": "X did not confirm the post ID. Check X before trying again."}
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    try:
        readback = client.request(
            "GET", ctx["cfg"].base_url.rstrip("/") + f"/tweets/{post_id}",
            headers=headers, params={"tweet.fields": "author_id"}, retries=0,
        ).json()
        confirmed = readback.get("data") if isinstance(readback, dict) else None
    except (RuntimeError, ValueError):
        confirmed = None
    if not isinstance(confirmed, dict) or str(confirmed.get("id")) != post_id or str(confirmed.get("author_id")) != account["id"]:
        return {**result, "notes": "X returned a post ID, but read-back did not confirm it. Check X before trying again."}
    return {**result, "ok": True}

def _load_user_access_token(env_file: str) -> str | None:
    tok_path = token_path_for_env_file(env_file)
    data = read_token_json(tok_path)
    if not data:
        return None
    tok = data.get("access_token")
    if isinstance(tok, str) and tok.strip():
        return tok.strip()
    return None


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    tag = str(getattr(args, "tag", "") or "").strip()
    scheme = str(getattr(args, "security_scheme", "") or "").strip()
    ops = load_operations_from_pinned_snapshot()
    out_ops = []
    for op in ops:
        if tag and tag not in op.tags:
            continue
        if scheme:
            allowed = set()
            for alt in op.security:
                for req in alt:
                    allowed.add(req.scheme)
            if scheme not in allowed:
                continue
        out_ops.append(
            {
                "operation_id": op.operation_id,
                "method": op.method,
                "path": op.path,
                "tags": list(op.tags),
                "security": op.security_repr(),
            }
        )
    out_ops_sorted = sorted(out_ops, key=lambda o: (o["operation_id"], o["method"], o["path"]))
    payload = {"ok": True, "ops": out_ops_sorted, "count": len(out_ops_sorted)}
    ctx["audit"].write("api.ops.list", {"count": len(out_ops_sorted), "tag": tag or None, "scheme": scheme or None})
    ctx["out"].emit(payload)
    return 0


def _execute_live_http(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    query: dict[str, Any],
    body: dict[str, Any] | None,
    files: dict[str, str],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")

    req_headers = dict(headers)
    if body is not None and not files:
        req_headers.setdefault("Content-Type", "application/json")

    requests_files = None
    data = None
    if files:
        requests_files = {}
        for field, path in files.items():
            p = Path(path)
            if not p.exists() or not p.is_file():
                raise ValidationError(f"File not found: {path}")
            requests_files[field] = p.open("rb")
        data = {}
        if body:
            for k, v in body.items():
                data[str(k)] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)

    try:
        if requests_files:
            # Use requests directly for multipart (HttpClient currently only supports json/data).
            import requests  # local import

            with requests.Session() as s:
                s.headers["User-Agent"] = "x-api-tool"
                resp = s.request(
                    method=method,
                    url=url,
                    headers=req_headers,
                    params=query or None,
                    data=data,
                    files=requests_files,
                    timeout=float(ctx["timeout_s"]),
                )
                status = resp.status_code
                body_bytes = resp.content
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                resp_url = resp.url
        else:
            r = client.request(
                method=method,
                url=url,
                headers=req_headers or None,
                params=query or None,
                json_body=body,
                data=None,
                retries=0,
            )
            status = r.status
            body_bytes = r.body
            resp_headers = r.headers
            resp_url = r.url
    finally:
        if requests_files:
            for f in requests_files.values():
                try:
                    f.close()
                except Exception:
                    pass

    body_text = body_bytes.decode("utf-8", errors="replace")
    body_json = None
    try:
        body_json = json.loads(body_text)
    except Exception:
        body_json = None

    return {
        "status": status,
        "url": resp_url,
        "headers": resp_headers,
        "body_json": body_json,
        "body_text": None if body_json is not None else body_text,
    }


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    op_id = str(getattr(args, "op", "") or "").strip()
    if not op_id:
        raise ValidationError("Missing operation")

    ops = load_operations_from_pinned_snapshot()
    by_id = operations_by_id(ops)
    op = by_id.get(op_id)
    if not op:
        raise ValidationError(f"Unknown operationId: {op_id}")

    auth = str(getattr(args, "auth", "auto") or "auto").strip()

    post_change = op_id in _POST_CHANGES
    plan_in = ctx.get("plan_in")
    if post_change and plan_in and (
        auth != "auto" or any(
            getattr(args, field, None) for field in ("path_json", "query_json", "body_json", "path", "query", "file")
        )
    ):
        raise SafetyError("Use only the saved plan for the post. Save a new preview if the request changes.")
    if ctx.get("apply") and op_id in _MESSAGE_SENDS:
        raise SafetyError("Use dm send or dm bulk-send to review recipients, consent and opt-outs before sending.")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        validate_plan_for_apply(plan_obj, op_id=op_id, ctx_base_url=str(ctx["cfg"].base_url))
        plan = plan_obj
    else:
        plan = build_api_call_plan(
            tool=ctx.get("tool") or "x-api-tool",
            tool_version=ctx.get("tool_version") or "",
            env_fingerprint=str(ctx["cfg"].base_url),
            op=op,
            base_url=str(ctx["cfg"].base_url),
            env_file=str(ctx["env_file"]),
            env_bearer_token=ctx["cfg"].token,
            auth=auth,
            path_json=getattr(args, "path_json", None),
            query_json=getattr(args, "query_json", None),
            body_json=getattr(args, "body_json", None),
            path_pairs=getattr(args, "path", None),
            query_pairs=getattr(args, "query", None),
            file_pairs=getattr(args, "file", None),
        )

    plan_out = ctx.get("plan_out")
    if post_change and plan_out and ctx.get("live") and not ctx.get("apply"):
        token = _load_user_access_token(str(ctx["env_file"]))
        if not token or plan.get("auth", {}).get("mode") != "oauth2":
            raise SafetyError("Use a user token to save a connected post plan.")
        mark_reviewed(plan, read_account(ctx, token))
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    operation_raw = plan.get("operation")
    plan_operation: dict[str, Any] = operation_raw if isinstance(operation_raw, dict) else {}
    method = str(plan_operation.get("method") or "").upper()
    if method != op.method.upper():
        raise ValidationError("The plan method does not match the X command.")

    # Default is plan-only.
    will_execute = False
    if method in {"GET", "HEAD"}:
        will_execute = bool(ctx.get("live"))
        if not will_execute:
            out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
            ctx["audit"].write("api.call.plan", {"operation_id": op_id, "method": method, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0
    else:
        if not bool(ctx.get("apply")):
            out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
            ctx["audit"].write("api.call.plan", {"operation_id": op_id, "method": method, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0
        if not bool(ctx.get("yes")):
            raise SafetyError("Refused: non-GET operations require --apply --yes")
        if method == "DELETE" and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: DELETE requires --ack-irreversible")
        plan = ensure_blocked_apply_contract(
            plan,
            action=f"api.{op_id}",
            provider_write={
                "service": "X API",
                "operation_id": op_id,
                "method": method,
                "path": str(plan_operation.get("path_template") or ""),
            },
            requires_ack_irreversible=method == "DELETE",
        )
        if not bool(ctx.get("ack_no_snapshot")):
            out = refusal_output(plan=plan)
            ctx["audit"].write("api.call.refused", {"operation_id": op_id, "method": method, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0
        will_execute = True

    account = None
    reviewed_token = None
    if post_change and ctx.get("apply"):
        if not plan_in:
            raise SafetyError("Apply this post change with --plan-in and the saved connected preview.")
        token = _load_user_access_token(str(ctx["env_file"]))
        if not token or plan.get("auth", {}).get("mode") != "oauth2":
            raise SafetyError("Use the reviewed user account for this post change.")
        account = check_review(plan, ctx, token)
        reviewed_token = token

    # Prepare live request from plan.
    op_obj = plan_operation
    # plan stores redacted url; rebuild the real url from cfg + filled path.
    path_filled = str(op_obj.get("path_filled") or "").strip()
    if not path_filled:
        raise ValidationError("Plan missing operation.path_filled")
    real_url = join_base_url_and_path(str(ctx["cfg"].base_url), path_filled)

    inputs_raw = plan.get("inputs")
    inputs: dict[str, Any] = inputs_raw if isinstance(inputs_raw, dict) else {}
    query_inputs_raw = inputs.get("query")
    query_inputs: dict[str, Any] = query_inputs_raw if isinstance(query_inputs_raw, dict) else {}
    body_inputs_raw = inputs.get("body")
    body_inputs = body_inputs_raw if isinstance(body_inputs_raw, dict) else None
    file_inputs_raw = inputs.get("files")
    file_inputs = file_inputs_raw if isinstance(file_inputs_raw, dict) else {}

    # Auth selection (do not store secrets in outputs).
    auth_raw = plan.get("auth")
    auth_obj: dict[str, Any] = auth_raw if isinstance(auth_raw, dict) else {}
    auth_mode = str(auth_obj.get("mode") or "").strip()
    if auth_mode == "none":
        token = None
    elif auth_mode == "bearer":
        token = ctx["cfg"].token
    elif auth_mode == "oauth2":
        token = reviewed_token or _load_user_access_token(str(ctx["env_file"]))
    else:
        token = None

    if auth_mode in {"bearer", "oauth2"} and not token:
        raise SafetyError("Refused: missing token for requested/selected auth mode")
    if auth_mode == "unsupported":
        raise SafetyError("Refused: this operation requires an unsupported auth mode (UserToken)")

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if not will_execute:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("api.call.plan", {"operation_id": op_id, "method": method, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    try:
        resp = _execute_live_http(
            method=method,
            url=real_url,
            headers=headers,
            query=query_inputs,
            body=body_inputs,
            files={str(k): str(v) for k, v in file_inputs.items()},
            ctx=ctx,
        )
    except RuntimeError as error:
        if op_id == "createPosts" and str(error).startswith(("HTTP 5", "Request failed")):
            raise RuntimeError("X did not confirm the create request. Check the account before retrying.") from error
        raise

    verification: dict[str, Any] = {"supported": False, "ok": None, "notes": "Automatic read-back verification is not implemented for this operation."}
    if op_id == "createPosts" and account is not None:
        verification = _check_created_post(resp, ctx=ctx, headers=headers, account=account)
    ok = 200 <= int(resp["status"]) < 300 and verification["ok"] is not False

    receipt = {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_operation": {"operation_id": op_id, "method": method, "url": redact_url(resp.get("url") or real_url)},
        "changed": None,
        "before_state": plan.get("before_state") if method not in {"GET", "HEAD"} else None,
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this X write.",
        } if method not in {"GET", "HEAD"} else None,
        "verification": verification,
        "account": account,
        "http": {"status": resp.get("status"), "headers": resp.get("headers")},
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {
        "ok": ok,
        "dry_run": False,
        "plan_out": plan_path,
        "receipt_out": receipt_path,
        "receipt": receipt,
        "response": {
            "status": resp.get("status"),
            "url": redact_url(resp.get("url") or real_url),
            "body_json": resp.get("body_json"),
            "body_text": resp.get("body_text"),
        },
    }
    ctx["audit"].write(
        "api.call.apply",
        {"operation_id": op_id, "method": method, "status": resp.get("status"), "plan_out": plan_path, "receipt_out": receipt_path},
    )
    ctx["out"].emit(out)
    return 0 if ok else 1
