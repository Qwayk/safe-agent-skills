from __future__ import annotations

import hashlib
import json
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from ..api_dispatch import (
    build_api_call_plan,
    load_operations_from_pinned_snapshot,
    operations_by_command,
)
from ..config import build_env_fingerprint
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file


HIGH_IMPACT_PATH_KEYWORDS = (
    "delete",
    "bulk",
    "send",
    "cancel",
    "suppress",
    "unsubscribe",
    "request_profile_deletion",
    "relationship",
    "relationships",
    "remove",
)

SECRET_KEYS = {
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "cookie",
    "token",
    "secret",
}


def _classify_operation(op: Any) -> dict[str, Any]:
    method = str(op.method or "").upper()
    path_lower = str(op.path or "").lower()
    command = str(op.operation_command or "").lower()
    tags = {str(tag or "").lower() for tag in getattr(op, "tags", ())}
    is_read = method in {"GET", "HEAD"}
    is_write = not is_read
    high_impact = is_write and (
        method == "DELETE"
        or any(keyword in path_lower for keyword in HIGH_IMPACT_PATH_KEYWORDS)
        or any(keyword in command for keyword in HIGH_IMPACT_PATH_KEYWORDS)
        or any(keyword in tag for tag in tags for keyword in ("delete", "bulk", "send"))
        or any(keyword in path_lower for keyword in ("suppress", "unsubscribe"))
    )
    return {
        "method": method,
        "is_read": is_read,
        "is_write": is_write,
        "high_impact": high_impact,
        "gates": {
            "live": True,
            "apply": is_write,
            "plan_in": high_impact,
            "yes": high_impact,
        },
    }


def _compute_plan_hash(plan: dict[str, Any]) -> str:
    plan_copy = dict(plan)
    plan_copy.pop("plan_hash", None)
    plan_copy.pop("no_recovery", None)
    serialized = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _build_no_recovery_info() -> dict[str, Any]:
    return {
        "automatic_rollback_available": False,
        "snapshots_created": False,
        "provider_backups": [],
        "note": "No automatic rollback is available. No snapshots or provider backups are created.",
    }


def _build_before_state_info(*, is_write: bool) -> dict[str, Any]:
    if not is_write:
        return {
            "required": False,
            "supported": False,
            "statement": "Read operation; no before-state capture required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "statement": (
            "No useful before-state snapshot is captured for this Klaviyo write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _write_refusal_message() -> str:
    return (
        "Refused: this Klaviyo write has no saved before-state snapshot. "
        "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
    )


def _is_secret_key(key: str) -> bool:
    lower = str(key or "").lower()
    if not lower:
        return False
    if lower in SECRET_KEYS:
        return True
    if lower.endswith("_token") or lower.endswith("_secret") or lower.startswith("secret_") or lower.startswith("key_"):
        return True
    return False


def _redact_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            out[key] = "<redacted>" if _is_secret_key(key) else _redact_json_value(item)
        return out
    if isinstance(value, list):
        return [_redact_json_value(item) for item in value]
    return value


def _sanitize_for_output(value: Any) -> Any:
    return _redact_json_value(value)


def _build_body_summary(response: Any) -> dict[str, Any]:
    body_bytes = bytes(response.body)
    content_type = str(response.headers.get("content-type", "")).lower()
    if "json" in content_type:
        try:
            return {
                "type": "json",
                "body_json": _sanitize_for_output(response.json()),
            }
        except Exception:
            pass
    text = body_bytes.decode("utf-8", errors="replace")
    truncated = len(body_bytes) > 4000
    return {"type": "text", "text": text[:4000], "truncated": truncated}


def _emit_refusal(
    ctx: dict[str, Any],
    op_cmd: str,
    reasons: list[str],
    sanitized_plan: dict[str, Any],
    plan_path: str | None,
) -> int:
    out = {
        "ok": True,
        "dry_run": True,
        "plan": sanitized_plan,
        "plan_out": plan_path,
        "refused": True,
        "refusal_type": "SafetyError",
        "reasons": reasons,
    }
    ctx["audit"].write("api.call.refused", {"operation_command": op_cmd, "reasons": reasons})
    ctx["out"].emit(out)
    return 0


def _validate_plan_for_apply(plan: dict[str, Any], plan_in: dict[str, Any], env_fingerprint: str) -> None:
    if not isinstance(plan_in, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan_in.get("env_fingerprint") or "") != str(env_fingerprint):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan_in.get("plan_hash") or "") != str(plan.get("plan_hash") or ""):
        raise SafetyError("Refused: plan hash changed since plan creation")
    if str(plan_in.get("operation", {}).get("operation_command") or "") != str(
        plan.get("operation", {}).get("operation_command") or ""
    ):
        raise SafetyError("Refused: plan command mismatch")
    if _sanitize_for_output(plan_in.get("inputs", {})) != _sanitize_for_output(plan.get("inputs", {})):
        raise SafetyError("Refused: plan inputs changed since plan creation")


def _sanitize_headers(headers: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in headers.items():
        lk = str(key).lower()
        if lk in SECRET_KEYS:
            continue
        out[lk] = value
    return out


def cmd_api_ops_show(args: Any, ctx: dict[str, Any]) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing --op")

    ops = operations_by_command(load_operations_from_pinned_snapshot())
    op = ops.get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")

    payload = {
        "ok": True,
        "operation": {
            "operation_command": op.operation_command,
            "method": op.method,
            "path": op.path,
            "doc_url": op.doc_url,
            "tags": list(op.tags),
            "subtag": op.subtag,
            "required_path_params": list(op.required_path_params),
            "required_request_body": bool(op.required_request_body),
            "requires_company_id": bool(op.requires_company_id),
            "content_types": list(op.content_types),
            "has_multipart_request": bool(op.has_multipart_request),
            "operation_aliases": list(op.operation_aliases),
        },
    }
    ctx["audit"].write("api.ops.show", {"operation_command": op_cmd})
    ctx["out"].emit(payload)
    return 0


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    method = str(getattr(args, "method", "") or "").strip().upper()
    tag = str(getattr(args, "tag", "") or "").strip().lower()
    ops = load_operations_from_pinned_snapshot()
    out_ops: list[dict[str, Any]] = []
    for op in ops:
        if method and op.method != method:
            continue
        tags_lower = {t.lower() for t in op.tags}
        if tag and tag not in tags_lower:
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
                "requires_company_id": bool(op.requires_company_id),
                "content_types": list(op.content_types),
                "has_multipart_request": bool(op.has_multipart_request),
            }
        )
    out_ops = sorted(out_ops, key=lambda item: (item["operation_command"], item["method"], item["path"]))
    payload = {"ok": True, "ops": out_ops, "count": len(out_ops)}
    ctx["audit"].write("api.ops.list", {"count": len(out_ops), "method": method or None, "tag": tag or None})
    ctx["out"].emit(payload)
    return 0


def _to_headers(cfg: Any, op: Any) -> dict[str, str]:
    headers = {
        "accept": "application/vnd.api+json",
    }
    if cfg.api_revision:
        headers["revision"] = str(cfg.api_revision)
    if str(getattr(op, "path", "") or "").startswith("/client/"):
        return headers
    if not cfg.api_key:
        raise SafetyError("Missing KLAVIYO_API_KEY for live calls")
    headers["authorization"] = f"Klaviyo-API-Key {cfg.api_key}"
    return headers


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing operation")

    op_map = operations_by_command(load_operations_from_pinned_snapshot())
    op = op_map.get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")

    cfg = ctx["cfg"]
    query_pairs = list(getattr(args, "query", None) or [])
    if op.requires_company_id and cfg.company_id and not any(
        str(pair).split("=", 1)[0].strip() == "company_id" for pair in query_pairs if "=" in str(pair)
    ):
        query_pairs = [*query_pairs, f"company_id={cfg.company_id}"]
    plan = build_api_call_plan(
        tool=ctx.get("tool") or "klaviyo-safe-agent-cli",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=build_env_fingerprint(cfg),
        op=op,
        base_url=str(cfg.base_url),
        path_json=getattr(args, "path_json", None),
        query_json=getattr(args, "query_json", None),
        body_json=getattr(args, "body_json", None),
        path_pairs=getattr(args, "path", None),
        query_pairs=query_pairs,
        file_pairs=getattr(args, "file", None),
    )

    classification = _classify_operation(op)
    plan["classification"] = classification
    plan["before_state"] = _build_before_state_info(is_write=bool(classification["is_write"]))
    plan["no_recovery"] = _build_no_recovery_info()

    plan_hash = _compute_plan_hash(plan)
    plan["plan_hash"] = plan_hash

    sanitized_plan = _sanitize_for_output(plan)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitized_plan) if plan_out else None

    ctx["audit"].write(
        "api.call.plan",
        {"operation_command": op_cmd, "method": op.method, "plan_hash": plan_hash},
    )

    missing_required = plan.get("requirements", {}).get("missing_required") or []
    apply = bool(ctx.get("apply"))
    live = bool(ctx.get("live"))
    gates = classification["gates"]
    reasons: list[str] = []

    if live and op.requires_company_id and not plan["inputs"]["query"].get("company_id"):
        reasons.append("Refused: company_id is required for /client/* operations")
    if apply and not live:
        reasons.append("Refused: --live is required for real HTTP calls")
    if gates["plan_in"] and apply and not ctx.get("plan_in"):
        reasons.append("Refused: --plan-in is required for high-impact operations")
    if apply and gates["yes"] and not bool(ctx.get("yes")):
        reasons.append("Refused: --yes is required for high-impact operations")
    if (live or apply) and missing_required:
        missing_desc = ", ".join(f"{item.get('in')}:{item.get('name')}" for item in missing_required)
        reasons.append(f"Refused: missing required inputs ({missing_desc})")
    if reasons:
        return _emit_refusal(ctx, op_cmd, reasons, sanitized_plan, plan_path)

    is_read = bool(classification["is_read"])
    plan_out_obj = sanitized_plan

    if not apply and not (is_read and live):
        payload = {"ok": True, "dry_run": True, "plan": plan_out_obj, "plan_out": plan_path}
        ctx["out"].emit(payload)
        return 0

    plan_in = ctx.get("plan_in")
    if apply and gates["plan_in"]:
        plan_in_obj = read_json_file(plan_in)
        _validate_plan_for_apply(plan, plan_in_obj, build_env_fingerprint(cfg))

    if apply and bool(classification["is_write"]) and not bool(ctx.get("ack_no_snapshot")):
        return _emit_refusal(ctx, op_cmd, [_write_refusal_message()], sanitized_plan, plan_path)

    headers = _to_headers(cfg, op)
    content_types = list(op.content_types)
    if content_types:
        headers["content-type"] = content_types[0]
    if op.has_multipart_request or bool(plan["inputs"]["files"]):
        headers.pop("content-type", None)

    files = plan["inputs"]["files"]
    body_obj = plan["inputs"]["body"] or None

    request_kwargs: dict[str, Any] = {
        "method": plan["operation"]["method"],
        "url": plan["operation"]["url"],
        "headers": headers,
        "params": plan["inputs"]["query"],
        "json_body": None,
        "data": None,
        "files": None,
    }
    if files:
        request_kwargs["data"] = body_obj or {}
    else:
        request_kwargs["json_body"] = body_obj

    receipt_out = ctx.get("receipt_out")
    client = HttpClient(timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s), verbose=bool(ctx.get("verbose")), user_agent=f"klaviyo-safe-agent-cli/{ctx.get('tool_version') or '0.1.0'}")

    with ExitStack() as stack:
        file_objs: dict[str, Any] = {}
        if files:
            for field, file_path in files.items():
                p = Path(file_path)
                if not p.exists():
                    raise ValidationError(f"File not found: {file_path}")
                handle = stack.enter_context(open(p, "rb"))
                file_objs[field] = (p.name, handle)
            request_kwargs["files"] = file_objs

        try:
            response = client.request(**request_kwargs)
        except RuntimeError as exc:
            out = {
                "ok": False,
                "dry_run": False,
                "refused": True,
                "refusal_type": "HttpError",
                "reasons": [str(exc).splitlines()[0] if str(exc) else "HTTP error"],
                "error_type": "HttpError",
            }
            ctx["audit"].write("api.call.http_error", {"operation_command": op_cmd})
            ctx["out"].emit(out)
            return 0

    response_summary = {
        "status": response.status,
        "url": response.url,
        "headers": _sanitize_headers(response.headers),
        "body": _build_body_summary(response),
    }
    receipt = {
        "plan_hash": plan_hash,
        "operation": plan["operation"],
        "classification": classification,
        "backups": [],
        "rollback_plan": None,
        "no_recovery": _build_no_recovery_info(),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": bool(apply and classification["is_write"]), "flag": "--ack-no-snapshot"},
        "request": {
            "method": request_kwargs["method"],
            "url": request_kwargs["url"],
            "query": request_kwargs["params"],
            "body": request_kwargs.get("json_body") or None,
            "files": list(plan["inputs"]["files"].keys()) if plan["inputs"]["files"] else [],
        },
        "response": response_summary,
        "verification": {"status": "not run", "details": "No automatic verification in this slice"},
    }
    sanitized_receipt = _sanitize_for_output(receipt)

    if receipt_out:
        write_json_file(receipt_out, sanitized_receipt)

    ctx["audit"].write(
        "api.call.apply",
        {
            "operation_command": op_cmd,
            "plan_hash": plan_hash,
            "response_status": response.status,
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
