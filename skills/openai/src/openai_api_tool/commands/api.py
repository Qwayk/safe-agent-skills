from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..api_dispatch import (
    build_api_call_plan,
    is_retired,
    join_base_url_and_path,
    load_operations_from_pinned_snapshot,
    operations_by_command,
)
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from .auth import _build_auth_headers

# These POST operations start metered work or can add billed storage.
_PAID_POSTS = {
    "Compactconversation",
    "CreateContainer",
    "CreateContainerFile",
    "CreateVideoEdit",
    "CreateVideoExtend",
    "CreateVideoRemix",
    "accept-realtime-call",
    "create-realtime-call",
    "createBatch",
    "createChatCompletion",
    "createCompletion",
    "createEmbedding",
    "createEvalRun",
    "createFineTuningJob",
    "createImage",
    "createImageEdit",
    "createImageVariation",
    "createResponse",
    "createSpeech",
    "createTranscription",
    "createTranslation",
    "createVectorStore",
    "createVectorStoreFile",
    "createVectorStoreFileBatch",
    "createVideo",
    "resumeFineTuningJob",
    "runGrader",
}

_CREATE_READBACKS = {
    "CreateContainer": "/containers/{id}",
    "createBatch": "/batches/{id}",
    "createConversation": "/conversations/{id}",
    "createFile": "/files/{id}",
    "createFineTuningJob": "/fine_tuning/jobs/{id}",
    "createResponse": "/responses/{id}",
    "createVectorStore": "/vector_stores/{id}",
    "createVideo": "/videos/{id}",
}


def _classify_operation(op: Any) -> dict[str, Any]:
    method = str(op.method or "").upper()
    is_read = method in {"GET", "HEAD"}
    is_write = not is_read
    spend_money = method == "POST" and op.operation_command in _PAID_POSTS
    irreversible = method == "DELETE"
    gates = {
        "apply": is_write,
        "live": is_write,
        "plan_in": is_write,
        "yes": spend_money or irreversible,
        "ack_spend_money": spend_money,
        "ack_irreversible": irreversible,
    }
    return {
        "method": method,
        "is_read": is_read,
        "is_write": is_write,
        "spend_money": spend_money,
        "irreversible": irreversible,
        "tags": sorted(op.tags),
        "gates": gates,
    }


def _compute_plan_hash(plan: dict[str, Any], key: str | None = None) -> str:
    plan_copy = {k: v for k, v in plan.items() if k != "plan_hash"}
    serialized = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    data = serialized.encode("utf-8")
    if key is not None:
        return hmac.new(key.encode("utf-8"), data, "sha256").hexdigest()
    return hashlib.sha256(data).hexdigest()


def _build_no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "No built-in rollback, snapshots, or provider restore are available in this CLI. "
            "Check the affected resource before deciding whether a separate fix is possible."
        ),
    }


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this OpenAI write has no saved before-state snapshot. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


def _build_before_state_contract(*, operation: str | None = None, target: str | None = None) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "operation": operation,
        "target": target,
        "saved_path": None,
        "provider_backup_id": None,
        "reason": (
            "No useful before-state snapshot is captured for this OpenAI write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _build_before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "type": "best_effort_after_apply",
        "status": "requires-no-snapshot-approval",
        "requires_no_snapshot_approval": True,
        "notes": (
            "Apply can run after explicit no-snapshot approval, then records provider response "
            "and best-effort read-back when available."
        ),
    }


def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if "authorization" in key_lower:
            continue
        if key_lower in {"set-cookie", "cookie"}:
            continue
        out[key_lower] = value
    return out


_HTTP_STATUS_PATTERN = re.compile(r"HTTP (\d{3})")


def _extract_http_status_code(exc: Exception) -> int | None:
    match = _HTTP_STATUS_PATTERN.search(str(exc))
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _truncate_body(text: str, limit: int = 512) -> str:
    trimmed = text.strip()
    if len(trimmed) <= limit:
        return trimmed
    return trimmed[:limit] + "..."


SECRET_VALUE_PREFIXES = ("sk-", "pk-", "rtok-", "tok_")
SECRET_KEY_EXACT = {
    "authorization",
    "api_key",
    "token",
    "access_token",
    "refresh_token",
    "client_secret",
    "client_key",
    "secret",
    "password",
    "credential",
    "credentials",
    "private_key",
}
SECRET_KEY_SUFFIXES = ("_secret", "_key", "_token")
SECRET_KEY_PREFIXES = ("secret_", "key_")
SAFE_TOKEN_KEYS = {
    "max_tokens",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "token_count",
    "token_usage",
    "logit_bias",
}
STREAM_STOP_TOKEN = b"[DONE]"
STREAM_MAX_BYTES = 5 * 1024 * 1024
JSON_PREVIEW_LIMIT = 1024


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _is_streaming_plan(plan: dict[str, Any]) -> bool:
    body = plan.get("inputs", {}).get("body") or {}
    query = plan.get("inputs", {}).get("query") or {}
    stream_body = _truthy(body.get("stream")) if isinstance(body, dict) else False
    stream_query = _truthy(query.get("stream")) if isinstance(query, dict) else False
    return stream_body or stream_query


def _artifact_dir_path(ctx: dict[str, Any]) -> Path | None:
    art = ctx.get("artifacts_dir")
    if art is None:
        return None
    if isinstance(art, Path):
        return art
    if isinstance(art, str):
        return Path(art)
    return None


def _sanitize_command_name(op_cmd: str) -> str:
    sanitized = []
    for ch in str(op_cmd or ""):
        if ch.isalnum() or ch in {"_", "-", "."}:
            sanitized.append(ch)
        else:
            sanitized.append("_")
    return "".join(sanitized)


def _artifact_filename(op_cmd: str, plan_hash: str, suffix: str) -> str:
    base = _sanitize_command_name(op_cmd)
    short_hash = (plan_hash or "")[:8] or secrets.token_hex(4)
    return f"{base}_{short_hash}_{suffix}"


def _is_secret_key(key: str) -> bool:
    lower = str(key or "").lower()
    if not lower:
        return False
    if lower in SAFE_TOKEN_KEYS:
        return False
    if lower in SECRET_KEY_EXACT:
        return True
    if any(lower.endswith(suffix) for suffix in SECRET_KEY_SUFFIXES):
        return True
    if any(lower.startswith(prefix) for prefix in SECRET_KEY_PREFIXES):
        return True
    return False


def _redact_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: "<redacted>" if _is_secret_key(k) else _redact_json_value(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_redact_json_value(item) for item in value]
    if isinstance(value, str):
        lower = value.lower()
        if any(lower.startswith(prefix) for prefix in SECRET_VALUE_PREFIXES):
            return "<redacted>"
    return value


def _sanitize_for_output(value: Any) -> Any:
    return _redact_json_value(value)


def _sanitize_plan_for_output(plan: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_for_output(plan)


def _sanitize_receipt_for_output(receipt: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_for_output(receipt)


def _truncate_preview(text: str) -> str:
    return _truncate_body(text, limit=JSON_PREVIEW_LIMIT)


def _save_binary_artifact(
    data: bytes,
    content_type: str | None,
    ctx: dict[str, Any],
    op_cmd: str,
    plan_hash: str,
    suffix: str,
) -> dict[str, Any]:
    art_dir = _artifact_dir_path(ctx)
    if not art_dir:
        raise SafetyError("Refused: binary responses require an artifacts directory")
    filename = _artifact_filename(op_cmd, plan_hash, suffix)
    path = art_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    sha = hashlib.sha256(data).hexdigest()
    return {
        "path": str(path),
        "sha256": sha,
        "byte_count": len(data),
        "content_type": content_type or "application/octet-stream",
    }


def _build_response_body_summary(
    response: Any,
    ctx: dict[str, Any],
    plan_hash: str,
    op_cmd: str,
) -> dict[str, Any]:
    headers = response.headers
    content_type = headers.get("content-type", "")
    if response.artifact_path:
        artifact = {
            "path": response.artifact_path,
            "sha256": response.artifact_sha256,
            "byte_count": response.artifact_byte_count,
            "content_type": response.artifact_content_type or content_type or "application/octet-stream",
            "truncated": bool(response.artifact_truncated),
        }
        return {"type": "binary", "artifact": artifact, "streamed": True}
    if not response.body:
        return {"type": "empty", "size_bytes": 0}
    if "json" in str(content_type).lower():
        try:
            payload = response.json()
        except Exception:
            payload = None
        preview = "<empty>"
        if payload is not None:
            sanitized = _redact_json_value(payload)
            preview = _truncate_preview(json.dumps(sanitized, ensure_ascii=False))
        else:
            preview = "<invalid JSON>"
        return {"type": "json", "preview": preview, "size_bytes": len(response.body)}
    artifact = _save_binary_artifact(
        response.body,
        content_type,
        ctx,
        op_cmd,
        plan_hash,
        "response.bin",
    )
    return {"type": "binary", "artifact": artifact, "streamed": False}


def _serialize_multipart_value(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _emit_refusal(
    ctx: dict[str, Any],
    op_cmd: str,
    reasons: list[str],
    sanitized_plan: dict[str, Any],
    plan_path: str | None,
) -> int:
    payload = {
        "ok": True,
        "dry_run": True,
        "plan": sanitized_plan,
        "plan_out": plan_path,
        "refused": True,
        "reasons": reasons,
        "refusal_type": "SafetyError",
    }
    ctx["audit"].write(
        "api.call.refused",
        {
            "operation_command": op_cmd,
            "reasons": reasons,
            "plan_hash": sanitized_plan.get("plan_hash"),
        },
    )
    ctx["out"].emit(payload)
    return 0


def _emit_before_state_refusal(
    ctx: dict[str, Any],
    op_cmd: str,
    sanitized_plan: dict[str, Any],
    plan_path: str | None,
) -> int:
    payload = {
        "ok": True,
        "dry_run": False,
        "plan": sanitized_plan,
        "plan_out": plan_path,
        "refused": True,
        "reasons": [BEFORE_STATE_REFUSAL_REASON],
        "refusal_type": "SafetyError",
        "verification_plan": _build_before_state_refusal_verification_plan(),
    }
    ctx["audit"].write(
        "api.call.refused",
        {
            "operation_command": op_cmd,
            "reasons": payload["reasons"],
            "plan_hash": sanitized_plan.get("plan_hash"),
            "before_state": (sanitized_plan.get("before_state") or {}),
        },
    )
    ctx["out"].emit(payload)
    return 0


def _settings_root(ctx: dict[str, Any]) -> Path:
    return Path(ctx["env_file"]).resolve().parent


def _check_output_path(path: str | None, args: Any, ctx: dict[str, Any], plan: dict[str, Any]) -> None:
    if not path:
        return
    output = Path(path).resolve()
    protected = [ctx["env_file"], ctx.get("plan_in")]
    protected.extend(plan["inputs"]["files"].values())
    protected.extend(
        value for name in ("path_json", "query_json", "body_json")
        if (value := getattr(args, name, None)) and not value.lstrip().startswith("{")
    )
    protected_paths = [Path(value).resolve() for value in protected if value]
    receipt_dir = (_settings_root(ctx) / ".state" / "receipts").resolve()
    if output.is_relative_to(receipt_dir) or any(
        output == item or (output.exists() and item.exists() and output.samefile(item))
        for item in protected_paths
    ):
        raise SafetyError("Choose a separate output path from the settings, inputs and saved approvals")


def _prepare_uploads(
    plan: dict[str, Any], stack: ExitStack, *, send: bool,
) -> dict[str, Any]:
    hashes = {}
    uploads = {}
    for field, path in plan["inputs"]["files"].items():
        with Path(path).open("rb") as original:
            if send:
                # Send the same bytes that were checked, even if the original file changes.
                opened = stack.enter_context(tempfile.TemporaryFile())
                shutil.copyfileobj(original, opened)
                opened.seek(0)
                hashes[field] = hashlib.file_digest(opened, "sha256").hexdigest()
                opened.seek(0)
                uploads[field] = (Path(path).name, opened)
            else:
                hashes[field] = hashlib.file_digest(original, "sha256").hexdigest()
    if hashes:
        plan["file_sha256"] = hashes
    return uploads


def _finish_plan(
    plan: dict[str, Any], saved: dict[str, Any] | None, ctx: dict[str, Any],
) -> None:
    write = plan["classification"]["is_write"]
    cfg = ctx["cfg"]
    key = cfg.api_key if write else None
    if write:
        if saved is not None:
            nonce = saved.get("approval_id")
            if not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{32}", nonce) or not key:
                raise SafetyError("Prepare a new plan with the configured API key before applying")
        else:
            nonce = secrets.token_hex(16)
        plan["approval_id"] = nonce
        plan["account_bound"] = bool(key)
        plan["account"] = {"organization": cfg.organization_id, "project": cfg.project_id}
    # The approval only applies where its single-use receipt will be saved.
    to_sign = {**plan, "settings_folder": str(_settings_root(ctx))} if write else plan
    plan["plan_hash"] = _compute_plan_hash(to_sign, key)
    if saved is not None and saved != _sanitize_plan_for_output(plan):
        raise SafetyError("The approved plan does not match this account, settings folder or inputs")


def _resource_result(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _verify_result(
    op: Any, response: Any, request: dict[str, Any], ops: list[Any], client: HttpClient, cfg: Any,
) -> dict[str, Any]:
    result = _resource_result(response)
    resource_id = result.get("id")
    if not isinstance(resource_id, str) or not resource_id:
        return {"status": "response_only", "details": "No resource ID to check separately"}
    details = {"resource_id": resource_id, "resource_status": result.get("status")}
    path = _CREATE_READBACKS.get(op.operation_command)
    expected_absent = op.method == "DELETE" and result.get("deleted") is True
    if expected_absent and any(item.method == "GET" and item.path == op.path for item in ops):
        if resource_id not in request["inputs"]["path"].values():
            return {**details, "status": "needs_check", "details": "The reply named a different resource"}
        url = request["operation"]["url"]
    elif path and not (
        op.operation_command == "createResponse" and (request["inputs"]["body"] or {}).get("store") is False
    ):
        url = join_base_url_and_path(cfg.base_url, path.format(id=quote(resource_id, safe="")))
    else:
        return {**details, "status": "response_only"}
    try:
        read = client.request(method="GET", url=url, headers=_build_auth_headers(cfg))
    except RuntimeError as exc:
        if expected_absent and _extract_http_status_code(exc) in {404, 410}:
            return {**details, "status": "passed", "details": "The deleted resource is no longer available"}
        return {**details, "status": "needs_check", "details": "Could not read the specific resource back"}
    if not expected_absent and _resource_result(read).get("id") == resource_id:
        return {**details, "status": "passed", "details": "Read back the same resource ID"}
    return {**details, "status": "needs_check", "details": "The read did not confirm the change"}


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    tag = str(getattr(args, "tag", "") or "").strip()
    ops = load_operations_from_pinned_snapshot()
    out_ops: list[dict[str, Any]] = []
    for op in ops:
        if is_retired(op) or (tag and tag not in op.tags):
            continue
        out_ops.append(
            {
                "operation_command": op.operation_command,
                "method": op.method,
                "path": op.path,
                "doc_url": op.doc_url,
                "tags": list(op.tags),
                "required_path_params": list(op.required_path_params),
                "required_request_body": bool(op.required_request_body),
                "beta_header": op.beta_header,
            }
        )
    out_ops_sorted = sorted(out_ops, key=lambda o: (o["operation_command"], o["method"], o["path"]))
    payload = {"ok": True, "ops": out_ops_sorted, "count": len(out_ops_sorted), "retired_count": sum(map(is_retired, ops))}
    ctx["audit"].write("api.ops.list", {"count": len(out_ops_sorted), "tag": tag or None})
    ctx["out"].emit(payload)
    return 0


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing operation")

    ops = load_operations_from_pinned_snapshot()
    by_cmd = operations_by_command(ops)
    op = by_cmd.get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")
    if is_retired(op):
        ctx["out"].emit({
            "ok": False,
            "error_type": "RetiredOperation",
            "error": "OpenAI retired the Assistants API. Use Responses or Conversations.",
            "migration": "https://developers.openai.com/api/docs/assistants/migration",
        })
        return 1

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "openai-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx["cfg"].base_url),
        op=op,
        base_url=str(ctx["cfg"].base_url),
        path_json=getattr(args, "path_json", None),
        query_json=getattr(args, "query_json", None),
        body_json=getattr(args, "body_json", None),
        path_pairs=getattr(args, "path", None),
        query_pairs=getattr(args, "query", None),
        file_pairs=getattr(args, "file", None),
    )

    classification = _classify_operation(op)
    plan["classification"] = classification
    write_recovery = _build_no_recovery_contract() if classification["is_write"] else None
    if write_recovery is not None:
        plan["recovery"] = write_recovery
        plan["before_state"] = _build_before_state_contract(
            operation=op_cmd,
            target=plan.get("operation", {}).get("url"),
        )
        plan["verification_plan"] = _build_before_state_refusal_verification_plan()
        plan["post_apply_verification_plan"] = {
            "type": "read-back",
            "notes": (
                "After explicit no-snapshot approval, apply the write and verify with "
                "a read-back or documented idempotence check when available."
            ),
        }
    plan_path = None
    plan_out = ctx.get("plan_out")
    receipt_out = ctx.get("receipt_out")
    _check_output_path(plan_out, args, ctx, plan)
    _check_output_path(receipt_out, args, ctx, plan)
    if plan_out and receipt_out and Path(plan_out).resolve() == Path(receipt_out).resolve():
        raise SafetyError("Use separate files for the plan and receipt")
    sanitized_plan = _sanitize_plan_for_output(plan)

    missing_required = plan.get("requirements", {}).get("missing_required") or []

    apply = bool(ctx.get("apply"))
    live = bool(ctx.get("live"))
    gates = classification["gates"]
    reasons: list[str] = []

    if apply and not live:
        reasons.append("Refused: --live is required for apply")
    if apply and gates["plan_in"] and not ctx.get("plan_in"):
        reasons.append("Refused: this operation requires --plan-in for apply")
    if apply and gates["yes"] and not bool(ctx.get("yes")):
        reasons.append("Refused: --yes is required for risky operations")
    if apply and gates["ack_spend_money"] and not bool(ctx.get("ack_spend_money")):
        reasons.append("Refused: --ack-spend-money is required for spend-money operations")
    if apply and gates["ack_irreversible"] and not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: --ack-irreversible is required for irreversible operations")

    if missing_required and (live or apply):
        missing_desc = ", ".join(
            f"{item.get('in') or 'input'}:{item.get('name') or 'unknown'}" for item in missing_required
        )
        reasons.append(f"Refused: missing required inputs ({missing_desc})")
    if reasons:
        return _emit_refusal(ctx, op_cmd, reasons, sanitized_plan, plan_path)

    saved = read_json_file(ctx["plan_in"]) if ctx.get("plan_in") else None
    if ctx.get("plan_in") and not isinstance(saved, dict):
        raise ValidationError("Plan file must be a JSON object")

    if apply and classification["is_write"] and not bool(ctx.get("ack_no_snapshot")):
        return _emit_before_state_refusal(ctx, op_cmd, sanitized_plan, plan_path)

    live_read = classification["is_read"] and live
    with ExitStack() as stack:
        uploads = _prepare_uploads(plan, stack, send=apply or live_read)
        _finish_plan(plan, saved, ctx)
        sanitized_plan = _sanitize_plan_for_output(plan)
        if plan_out:
            plan_path = write_json_file(plan_out, sanitized_plan)
        ctx["audit"].write("api.call.plan", {
            "operation_command": op_cmd, "plan_hash": plan["plan_hash"],
            "classification": classification, "plan_out": plan_path,
        })
        if not apply and not live_read:
            ctx["out"].emit({"ok": True, "dry_run": True, "plan": sanitized_plan, "plan_out": plan_path})
            return 0
        return _send_api_call(op, ops, plan, sanitized_plan, ctx, uploads)


def _send_api_call(
    op: Any, ops: list[Any], plan: dict[str, Any], sanitized_plan: dict[str, Any],
    ctx: dict[str, Any], uploads: dict[str, Any],
) -> int:
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise SafetyError("Refused: missing OPENAI_API_KEY for live calls")
    headers = _build_auth_headers(cfg)
    if op.beta_header:
        headers["OpenAI-Beta"] = op.beta_header
    body = plan["inputs"]["body"]
    request_kwargs: dict[str, Any] = {
        "method": op.method,
        "url": plan["operation"]["url"],
        "headers": headers,
        "params": plan["inputs"]["query"],
        "json_body": body,
    }
    if uploads:
        request_kwargs["files"] = uploads
        request_kwargs["json_body"] = None
        headers.pop("content-type", None)
        request_kwargs["data"] = {
            key: _serialize_multipart_value(value) for key, value in (body or {}).items() if value is not None
        }
    plan_hash = plan["plan_hash"]
    streaming = _is_streaming_plan(plan)
    stream_to: Path | None = None
    if streaming:
        art_dir = _artifact_dir_path(ctx)
        if not art_dir:
            raise SafetyError("Refused: streaming responses require an artifacts directory")
        stream_to = art_dir / _artifact_filename(op.operation_command, plan_hash, "stream.bin")
        stream_to.parent.mkdir(parents=True, exist_ok=True)

    classification = plan["classification"]
    write = classification["is_write"]
    canonical_receipt = _settings_root(ctx) / ".state" / "receipts" / f"{plan_hash}.json" if write else None
    receipt_out = ctx.get("receipt_out")
    receipt = {
        "plan_hash": plan_hash,
        "operation": plan["operation"],
        "classification": classification,
        "request": {
            "method": op.method,
            "url": plan["operation"]["url"],
            "query": plan["inputs"]["query"],
            "body": body,
            "files": list(uploads),
        },
        "verification": {"status": "pending"},
    }
    if canonical_receipt:
        receipt.update(
            status="pending",
            recovery=plan["recovery"],
            before_state=plan["before_state"],
            no_snapshot_approval={"approved": True, "flag": "--ack-no-snapshot"},
        )
        _reserve_approval(canonical_receipt, receipt, receipt_out)

    client = HttpClient(
        timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"openai-api-tool/{ctx.get('tool_version') or '0.1.0'}",
    )
    try:
        response = client.request(
            **request_kwargs,
            stream_to=stream_to,
            stream_stop_token=STREAM_STOP_TOKEN if streaming else None,
            max_stream_bytes=STREAM_MAX_BYTES if streaming else None,
        )
    except (RuntimeError, OSError) as exc:
        if not canonical_receipt:
            raise
        receipt.update(
            status="needs_check",
            verification={"status": "needs_check", "http_status": _extract_http_status_code(exc)},
        )
        return _save_api_result(receipt, sanitized_plan, canonical_receipt, receipt_out, ctx, ok=False)

    receipt.update(
        status="response_received",
        response={
            "status": response.status, "url": response.url,
            "headers": _sanitize_headers(response.headers),
        },
        verification={"status": "read" if not write else "response_only"},
    )
    try:
        receipt["response"]["body"] = _build_response_body_summary(response, ctx, plan_hash, op.operation_command)
    except (SafetyError, OSError):
        # Preserve the HTTP outcome even if a local artifact could not be saved.
        receipt["response"]["body"] = {"type": "unavailable", "size_bytes": len(response.body)}
        return _save_api_result(receipt, sanitized_plan, canonical_receipt, receipt_out, ctx, ok=False)
    if canonical_receipt:
        # Save the provider reply before doing any optional follow-up read.
        try:
            write_json_file(canonical_receipt, _sanitize_receipt_for_output(receipt))
        except OSError:
            return _save_api_result(receipt, sanitized_plan, canonical_receipt, receipt_out, ctx, ok=False)
        receipt["verification"] = _verify_result(op, response, plan, ops, client, cfg)
    return _save_api_result(receipt, sanitized_plan, canonical_receipt, receipt_out, ctx, ok=True)


def _reserve_approval(path: Path, receipt: dict[str, Any], copy: str | None) -> None:
    if path.exists():
        raise SafetyError(f"This approval was already used. Check the saved receipt at {path}")
    if copy and Path(copy).exists():
        raise SafetyError("Choose a new filename for the receipt copy")
    try:
        write_json_file(path, _sanitize_receipt_for_output(receipt), exclusive=True)
    except OSError as exc:
        if isinstance(exc, FileExistsError) and path.exists():
            raise SafetyError(f"This approval was already used. Check the saved receipt at {path}") from exc
        raise SafetyError("Could not save the receipt before sending. No request was sent.") from exc


def _save_api_result(
    receipt: dict[str, Any], plan: dict[str, Any], canonical: Path | None,
    copy: str | None, ctx: dict[str, Any], *, ok: bool,
) -> int:
    safe = _sanitize_receipt_for_output(receipt)
    receipt_path = str(canonical) if canonical else copy
    error = None
    try:
        if canonical:
            write_json_file(canonical, safe)
        if copy:
            write_json_file(copy, safe, exclusive=canonical is not None)
    except OSError:
        ok = False
        error = "Could not finish saving the receipt. Check the saved result before sending anything again."
    if not ok and not error:
        error = (
            "OpenAI did not confirm the result. Check the account before sending again."
            if receipt["status"] == "needs_check"
            else "OpenAI replied, but the tool could not save or read the full result."
        )
    ctx["audit"].write("api.call.apply", {
        "operation_command": plan["operation"]["operation_command"],
        "plan_hash": plan["plan_hash"],
        "status": receipt["status"],
    })
    payload = {"ok": ok, "dry_run": False, "plan": plan, "receipt": safe, "receipt_out": receipt_path}
    if error:
        payload["error"] = error
    ctx["out"].emit(payload)
    return 0 if ok else 1
