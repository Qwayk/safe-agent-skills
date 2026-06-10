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
from ..http import HttpClient
from ..http import redact_url
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import token_path_for_env_file, read_token_json
from .write_safety import ensure_blocked_apply_contract, refusal_output


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

    plan_in = ctx.get("plan_in")
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
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    method = str(plan.get("operation", {}).get("method") or "").upper()
    if not method:
        raise ValidationError("Plan missing operation.method")

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
                "path": str(plan.get("operation", {}).get("path_template") or ""),
            },
            requires_ack_irreversible=method == "DELETE",
        )
        if not bool(ctx.get("ack_no_snapshot")):
            out = refusal_output(plan=plan)
            ctx["audit"].write("api.call.refused", {"operation_id": op_id, "method": method, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0
        will_execute = True

    # Prepare live request from plan.
    op_obj = plan.get("operation") if isinstance(plan.get("operation"), dict) else {}
    url = str(op_obj.get("url") or "").strip()
    # plan stores redacted url; rebuild the real url from cfg + filled path.
    path_filled = str(op_obj.get("path_filled") or "").strip()
    if not path_filled:
        raise ValidationError("Plan missing operation.path_filled")
    real_url = join_base_url_and_path(str(ctx["cfg"].base_url), path_filled)

    inputs = plan.get("inputs") if isinstance(plan.get("inputs"), dict) else {}
    path_inputs = inputs.get("path") if isinstance(inputs.get("path"), dict) else {}
    query_inputs = inputs.get("query") if isinstance(inputs.get("query"), dict) else {}
    body_inputs = inputs.get("body") if isinstance(inputs.get("body"), dict) else None
    file_inputs = inputs.get("files") if isinstance(inputs.get("files"), dict) else {}

    # Auth selection (do not store secrets in outputs).
    auth_obj = plan.get("auth") if isinstance(plan.get("auth"), dict) else {}
    auth_mode = str(auth_obj.get("mode") or "").strip()
    if auth_mode == "none":
        token = None
    elif auth_mode == "bearer":
        token = ctx["cfg"].token
    elif auth_mode == "oauth2":
        token = _load_user_access_token(str(ctx["env_file"]))
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

    resp = _execute_live_http(
        method=method,
        url=real_url,
        headers=headers,
        query=query_inputs,
        body=body_inputs,
        files={str(k): str(v) for k, v in file_inputs.items()},
        ctx=ctx,
    )

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
        "verification": {"supported": False, "ok": None, "notes": "Automatic read-back verification is not implemented for this operation."},
        "http": {"status": resp.get("status"), "headers": resp.get("headers")},
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {
        "ok": True,
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
    return 0
