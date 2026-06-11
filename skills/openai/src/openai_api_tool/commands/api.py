from __future__ import annotations

import hashlib
import json
import re
import secrets
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from ..api_dispatch import build_api_call_plan, load_operations_from_pinned_snapshot, operations_by_command
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file

SPEND_PATH_KEYWORDS = (
    "chat",
    "responses",
    "moderations",
    "completions",
    "embeddings",
    "images",
    "audio",
    "videos",
    "fine_tuning",
    "batches",
    "assistants",
    "realtime",
    "evals",
    "vector_stores",
)

SPEND_TAG_KEYWORDS = (
    "chat",
    "responses",
    "moderations",
    "moderation",
    "completions",
    "embeddings",
    "images",
    "audio",
    "videos",
    "fine-tuning",
    "batch",
    "batches",
    "assistants",
    "realtime",
    "evals",
    "vector stores",
)


def _classify_operation(op: Any) -> dict[str, Any]:
    method = str(op.method or "").upper()
    path_lower = str(op.path or "").lower()
    tags_lower = {str(tag or "").lower() for tag in op.tags}
    is_read = method in {"GET", "HEAD"}
    is_write = not is_read
    spend_money = any(keyword in path_lower for keyword in SPEND_PATH_KEYWORDS) or any(
        keyword in tag for keyword in SPEND_TAG_KEYWORDS for tag in tags_lower
    )
    irreversible = method == "DELETE"
    gates = {
        "apply": is_write,
        "live": is_write,
        "plan_in": spend_money or irreversible,
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


def _compute_plan_hash(plan: dict[str, Any]) -> str:
    plan_copy = {k: v for k, v in plan.items() if k != "plan_hash"}
    serialized = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _build_no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "No built-in rollback, snapshots, or provider restore are available in this CLI. "
            "If rollback is needed, run a separate explicit restore action through API calls."
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
    path.write_bytes(data)
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
            preview = _truncate_preview(response.body.decode("utf-8", errors="replace"))
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


def _validate_plan_for_apply(plan: dict[str, Any], plan_in: dict[str, Any], base: str) -> None:
    plan_op = plan.get("operation") or {}
    in_op = plan_in.get("operation") or {}
    sanitized_plan = _sanitize_plan_for_output(plan)
    sanitized_plan_in = _sanitize_plan_for_output(plan_in)
    if str(plan_in.get("env_fingerprint") or "") != str(base):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")

    if str(in_op.get("operation_command") or "") != str(plan_op.get("operation_command") or ""):
        raise SafetyError("Refused: plan command mismatch")
    if str(in_op.get("method") or "") != str(plan_op.get("method") or ""):
        raise SafetyError("Refused: plan method mismatch")
    if str(in_op.get("path_template") or "") != str(plan_op.get("path_template") or ""):
        raise SafetyError("Refused: plan path mismatch")

    if sanitized_plan_in.get("inputs") != sanitized_plan.get("inputs"):
        raise SafetyError("Refused: plan inputs differ from current values")

    plan_hash = str(plan.get("plan_hash") or "")
    plan_in_hash = str(plan_in.get("plan_hash") or "")
    if plan_hash and plan_in_hash and plan_hash != plan_in_hash:
        raise SafetyError("Refused: plan hash changed since plan creation")


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    tag = str(getattr(args, "tag", "") or "").strip()
    ops = load_operations_from_pinned_snapshot()
    out_ops: list[dict[str, Any]] = []
    for op in ops:
        if tag and tag not in op.tags:
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
    payload = {"ok": True, "ops": out_ops_sorted, "count": len(out_ops_sorted)}
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
    plan_hash = _compute_plan_hash(plan)
    plan["plan_hash"] = plan_hash

    sanitized_plan = _sanitize_plan_for_output(plan)
    plan_out = ctx.get("plan_out")
    plan_path = None
    if plan_out:
        plan_path = write_json_file(plan_out, sanitized_plan)

    missing_required = plan.get("requirements", {}).get("missing_required") or []

    ctx["audit"].write(
        "api.call.plan",
        {
            "operation_command": op_cmd,
            "method": op.method,
            "plan_out": plan_path,
            "plan_hash": plan_hash,
            "classification": classification,
        },
    )

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

    streaming = _is_streaming_plan(plan)
    plan_in_path = ctx.get("plan_in")
    if plan_in_path:
        plan_in_obj = read_json_file(plan_in_path)
        if not isinstance(plan_in_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_for_apply(plan, plan_in_obj, str(ctx["cfg"].base_url))

    if apply and classification["is_write"] and not bool(ctx.get("ack_no_snapshot")):
        return _emit_before_state_refusal(ctx, op_cmd, sanitized_plan, plan_path)

    run_read_live = classification["is_read"] and live
    if not apply and not run_read_live:
        payload = {"ok": True, "dry_run": True, "plan": sanitized_plan, "plan_out": plan_path}
        ctx["out"].emit(payload)
        return 0

    stream_to: Path | None = None
    if streaming:
        art_dir = _artifact_dir_path(ctx)
        if not art_dir:
            raise SafetyError("Refused: streaming responses require an artifacts directory")
        stream_to = art_dir / _artifact_filename(op_cmd, plan_hash, "stream.bin")
        stream_to.parent.mkdir(parents=True, exist_ok=True)

    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise SafetyError("Refused: missing OPENAI_API_KEY for live calls")

    headers: dict[str, str] = {
        "authorization": f"Bearer {cfg.api_key}",
        "content-type": "application/json",
        "accept": "application/json",
    }
    if cfg.organization_id:
        headers["openai-organization"] = cfg.organization_id
    if cfg.project_id:
        headers["openai-project"] = cfg.project_id
    if op.beta_header:
        headers["OpenAI-Beta"] = op.beta_header
    files = plan["inputs"]["files"] or {}
    body_inputs = plan["inputs"]["body"] or {}
    request_kwargs: dict[str, Any] = {
        "method": plan["operation"]["method"],
        "url": plan["operation"]["url"],
        "headers": headers,
        "params": plan["inputs"]["query"],
        "json_body": body_inputs,
    }

    receipt_out = ctx.get("receipt_out")

    with ExitStack() as stack:
        file_objs: dict[str, Any] = {}
        for field, path in files.items():
            if path:
                fh = stack.enter_context(open(path, "rb"))
                file_objs[field] = (path, fh)
        if file_objs:
            request_kwargs["files"] = file_objs
            request_kwargs["json_body"] = None
            headers.pop("content-type", None)
            multipart_body: dict[str, Any] = {}
            for key, value in body_inputs.items():
                if value is None:
                    continue
                multipart_body[key] = _serialize_multipart_value(value)
            if multipart_body:
                request_kwargs["data"] = multipart_body

        client = HttpClient(
            timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
            verbose=bool(ctx.get("verbose")),
            user_agent=f"openai-api-tool/{ctx.get('tool_version') or '0.1.0'}",
        )

        response = client.request(
            **request_kwargs,
            stream_to=stream_to,
            stream_stop_token=STREAM_STOP_TOKEN if streaming else None,
            max_stream_bytes=STREAM_MAX_BYTES if streaming else None,
        )

    response_summary = {
        "status": response.status,
        "url": response.url,
        "headers": _sanitize_headers(response.headers),
        "body": _build_response_body_summary(response, ctx, plan_hash, op_cmd),
    }

    verification = {"status": "skipped", "details": "No verification target"}
    if classification["is_write"]:
        verify_url = plan["operation"]["url"]
        try:
            verify_resp = client.request(
                method="GET",
                url=verify_url,
                headers=headers,
                params=plan["inputs"]["query"],
                json_body=None,
            )
            verification = {
                "status": "passed",
                "details": f"GET {verify_url} -> {verify_resp.status}",
            }
        except Exception as exc:  # noqa: BLE001
            status_code = _extract_http_status_code(exc)
            if classification.get("irreversible") and status_code in {404, 410}:
                verification = {
                    "status": "passed",
                    "details": f"GET {verify_url} -> resource gone (HTTP {status_code})",
                }
            else:
                verification = {"status": "failed", "details": str(exc)}

    receipt = {
        "plan_hash": plan_hash,
        "operation": plan["operation"],
        "classification": classification,
        **({"recovery": write_recovery} if write_recovery is not None else {}),
        **(
            {
                "before_state": plan.get("before_state"),
                "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
            }
            if classification["is_write"]
            else {}
        ),
        "request": {
            "method": plan["operation"]["method"],
            "url": plan["operation"]["url"],
            "query": plan["inputs"]["query"],
            "body": plan["inputs"]["body"],
            "files": list(plan["inputs"]["files"].keys()),
        },
        "response": response_summary,
        "verification": verification,
    }

    sanitized_receipt = _sanitize_receipt_for_output(receipt)
    if receipt_out:
        write_json_file(receipt_out, sanitized_receipt)

    ctx["audit"].write(
        "api.call.apply",
        {
            "operation_command": op_cmd,
            "method": op.method,
            "plan_hash": plan_hash,
            "response_status": response.status,
            "refused": False,
        },
    )

    payload = {
        "ok": True,
        "dry_run": False,
        "plan": sanitized_plan,
        "receipt": sanitized_receipt,
        "receipt_out": receipt_out,
    }
    ctx["out"].emit(payload)
    return 0
