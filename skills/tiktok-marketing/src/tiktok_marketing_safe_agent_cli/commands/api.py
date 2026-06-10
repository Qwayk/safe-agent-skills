from __future__ import annotations

import hashlib
import json
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from ..api_dispatch import (
    build_api_call_plan,
    load_operations_from_pinned_snapshot,
    operations_by_command,
)
from ..errors import SafetyError, ToolError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from .auth import _resolve_access_token
from .write_safety import (
    before_state_contract,
    before_state_refusal_output,
    before_state_refusal_verification_plan,
)

REDACTED = "***REDACTED***"
IRREVERSIBLE_WRITE_MODE = "irreversible_and_clearly_labeled"
API_WRITE_REFUSAL_REASON = (
    "Refused: this TikTok Marketing API write has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _classify_operation(op: Any) -> dict[str, Any]:
    method = str(op.method or "").upper()
    is_read = method in {"GET", "HEAD"}
    is_write = not is_read
    return {
        "method": method,
        "is_read": is_read,
        "is_write": is_write,
        "gates": {
            "live": True,
            "apply": is_write,
            "plan_in": is_write,
            "yes": is_write,
            "ack_irreversible": is_write,
        },
    }


def _risk_level(classification: dict[str, Any]) -> str:
    if bool(classification.get("is_write")):
        return "high"
    return "low"


def _risk_reasons(classification: dict[str, Any]) -> list[str]:
    if bool(classification.get("is_read")):
        return ["read-only-operation"]
    return ["write-operation", "irreversible-write", "no-snapshot-approval-required"]


def _preconditions(classification: dict[str, Any], missing_required: list[dict[str, Any]]) -> list[str]:
    out = ["env_fingerprint must match when applying from a reviewed plan"]
    if bool(classification.get("is_write")):
        out.extend(
            [
                "live writes require --live --apply",
                "live writes require --plan-in",
                "live writes require --yes",
                "live writes require --ack-irreversible",
            ]
        )
    if missing_required:
        out.append("fill every required input before a live call")
    return out


def _verification_plan(classification: dict[str, Any]) -> dict[str, Any]:
    if bool(classification.get("is_read")):
        return {
            "type": "provider-response-only",
            "notes": "Read execution is accepted only from the live provider response in this build.",
        }
    return before_state_refusal_verification_plan()


def _legacy_write_verification_plan() -> dict[str, Any]:
    return {
        "type": "provider-response-only",
        "notes": "Write execution is accepted only from the HTTP result plus provider JSON response. No read-back is attempted in this build.",
    }


def _rollback_contract(classification: dict[str, Any]) -> dict[str, Any]:
    if not bool(classification.get("is_write")):
        return {
            "supported": False,
            "notes": "No changes in dry-run or read-only output.",
        }
    return {
        "supported": False,
        "mode": IRREVERSIBLE_WRITE_MODE,
        "automatic_rollback": False,
        "requires_ack_irreversible": bool((classification.get("gates") or {}).get("ack_irreversible")),
        "notes": (
            "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
            "Treat current TikTok Marketing write families as irreversible_and_clearly_labeled and use the saved "
            "plan and refusal output for manual follow-up only."
        ),
    }


def _compute_plan_hash(plan: dict[str, Any]) -> str:
    plan_copy = {k: v for k, v in plan.items() if k != "plan_hash"}
    encoded = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ensure_write_safety_contract(plan: dict[str, Any], op: Any, classification: dict[str, Any]) -> dict[str, Any]:
    if not bool(classification.get("is_write")):
        return plan
    plan["before_state"] = before_state_contract(
        reason=(
            "This source tool can build and review TikTok Marketing write plans, but no reliable "
            "operation-specific before-state snapshot is available for this generic API operation."
        ),
        provider_write={
            "operation_command": str(getattr(op, "operation_command", "") or ""),
            "method": str(getattr(op, "method", "") or ""),
            "path_template": str(getattr(op, "path", "") or ""),
            "url": (plan.get("operation") or {}).get("url"),
            "family": str(getattr(op, "family", "") or ""),
            "body_mode": str(getattr(op, "body_mode", "") or ""),
        },
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["legacy_verification_plan"] = _legacy_write_verification_plan()
    plan["rollback"] = _rollback_contract(classification)
    return plan


def _is_secret_key(key: str) -> bool:
    lower = str(key or "").lower()
    if lower in {"access-token", "access_token", "authorization", "secret", "app_secret", "client_secret"}:
        return True
    return lower.endswith("_token") or lower.endswith("_secret")


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: (REDACTED if _is_secret_key(k) else _redact_value(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def _sanitize_plan_for_output(plan: dict[str, Any]) -> dict[str, Any]:
    return _redact_value(plan)


def _sanitize_receipt_for_output(receipt: dict[str, Any]) -> dict[str, Any]:
    return _redact_value(receipt)


def _sanitize_headers(headers: dict[str, str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in (headers or {}).items():
        key_lower = str(key).lower()
        if key_lower in {"access-token", "authorization", "x-access-token", "token", "cookie"}:
            continue
        out[str(key)] = value
    return out


def _provider_error_message(body_preview: dict[str, Any]) -> str | None:
    if body_preview.get("type") != "json":
        return None
    payload = body_preview.get("body")
    if not isinstance(payload, dict):
        return None
    code = payload.get("code")
    if code is None or str(code).strip() in {"", "0"}:
        return None
    message = payload.get("message") or payload.get("msg") or "TikTok API returned an error"
    return f"TikTok API returned code {code}: {message}"


def _read_body_preview(response: Any) -> dict[str, Any]:
    headers = response.headers
    body_bytes = response.body
    content_type = str(headers.get("content-type") or "")
    if body_bytes is None:
        return {"type": "empty"}
    if "json" in content_type.lower():
        try:
            payload = response.json()
            return {"type": "json", "body": _redact_value(payload)}
        except Exception:
            pass
    text = body_bytes.decode("utf-8", errors="replace")
    return {"type": "text", "text": text[:4096], "truncated": len(text) > 4096}


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


def _validate_plan_for_apply(
    *,
    op_cmd: str,
    op_method: str,
    op_path_template: str,
    plan_in: dict[str, Any],
    base_fingerprint: str,
) -> None:
    in_op = plan_in.get("operation") or {}
    if str(plan_in.get("env_fingerprint") or "") != str(base_fingerprint):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(in_op.get("operation_command") or "") != str(op_cmd):
        raise SafetyError("Refused: plan command mismatch")
    if str(in_op.get("method") or "") != str(op_method):
        raise SafetyError("Refused: plan method mismatch")
    if str(in_op.get("path_template") or "") != str(op_path_template):
        raise SafetyError("Refused: plan path mismatch")


def _serialize_multipart_value(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return str(value)


def _serialize_form(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(k): _serialize_multipart_value(v) for k, v in value.items() if v is not None}


def _restore_redacted_value(value: Any, replacement: str | None) -> Any:
    if value == REDACTED and replacement:
        return replacement
    return value


def _restore_redacted_mapping(values: dict[str, Any], replacements: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in values.items():
        out[key] = _restore_redacted_tree(value, replacements, key_name=str(key))
    return out


def _restore_redacted_tree(value: Any, replacements: dict[str, str], *, key_name: str | None = None) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for child_key, child_value in value.items():
            out[str(child_key)] = _restore_redacted_tree(
                child_value,
                replacements,
                key_name=str(child_key),
            )
        return out
    if isinstance(value, list):
        return [_restore_redacted_tree(item, replacements) for item in value]
    replacement = replacements.get(str(key_name or "").lower())
    return _restore_redacted_value(value, replacement)


def _contains_redacted_value(value: Any) -> bool:
    if value == REDACTED:
        return True
    if isinstance(value, dict):
        return any(_contains_redacted_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_redacted_value(item) for item in value)
    return False


def _needs_access_token(op: Any) -> bool:
    if any(str(source).strip() == "access_token" for source in op.header_param_sources.values()):
        return True
    return any(str(name).lower() == "access-token" for name in op.required_header_params)


def cmd_api_ops_list(args, ctx) -> int:
    method = str(getattr(args, "method", "") or "").strip().upper()
    family = str(getattr(args, "family", "") or "").strip()
    ops = load_operations_from_pinned_snapshot()
    rows: list[dict[str, Any]] = []
    for op in ops:
        if method and op.method.upper() != method:
            continue
        if family and str(op.family or "").strip() != family:
            continue
        rows.append(
            {
                "operation_command": op.operation_command,
                "method": op.method,
                "path": op.path,
                "doc_url": op.doc_url,
                "family": op.family,
                "body_mode": op.body_mode,
                "required_query_params": list(op.required_query_params),
                "required_header_params": list(op.required_header_params),
                "required_request_body": bool(op.required_request_body),
                "tags": list(op.tags),
                "query_param_sources": dict(op.query_param_sources),
                "header_param_sources": dict(op.header_param_sources),
            }
        )
    ops_sorted = sorted(rows, key=lambda item: (item["operation_command"], item["method"]))
    payload = {"ok": True, "count": len(ops_sorted), "ops": ops_sorted}
    ctx["audit"].write(
        "api.ops.list",
        {"count": len(ops_sorted), "method": method or None, "family": family or None},
    )
    ctx["out"].emit(payload)
    return 0


def cmd_api_ops_show(args, ctx) -> int:
    operation_command = str(getattr(args, "operation_command", "") or "").strip()
    if not operation_command:
        raise ValidationError("Missing operation command")
    ops = load_operations_from_pinned_snapshot()
    by_cmd = operations_by_command(ops)
    op = by_cmd.get(operation_command)
    if not op:
        raise ValidationError(f"Unknown operation command: {operation_command}")
    payload = {
        "ok": True,
        "operation": {
            "operation_command": op.operation_command,
            "method": op.method,
            "path": op.path,
            "doc_url": op.doc_url,
            "family": op.family,
            "body_mode": op.body_mode,
            "tags": list(op.tags),
            "content_types": list(op.content_types),
            "collection_formats": list(op.collection_formats),
            "required_path_params": list(op.required_path_params),
            "required_query_params": list(op.required_query_params),
            "required_header_params": list(op.required_header_params),
            "query_param_sources": dict(op.query_param_sources),
            "header_param_sources": dict(op.header_param_sources),
            "file_param_names": list(op.file_param_names),
            "form_field_names": list(op.form_field_names),
            "required_request_body": bool(op.required_request_body),
            "source": op.source,
            "source_files": list(op.source_files),
            "summary": op.summary,
        },
    }
    ctx["audit"].write("api.ops.show", {"operation_command": operation_command})
    ctx["out"].emit(payload)
    return 0


def cmd_api_call(args, ctx) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing operation")

    ops = load_operations_from_pinned_snapshot()
    by_cmd = operations_by_command(ops)
    op = by_cmd.get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")

    cfg = ctx["cfg"]
    access_token, token_source = _resolve_access_token(cfg, str(ctx["env_file"]))
    query_defaults = {
        "app_id": str(cfg.app_id or "").strip(),
        "secret": str(cfg.app_secret or "").strip(),
        "advertiser_id": "",
        "access_token": str(access_token or "").strip(),
    }
    header_defaults = {"access_token": str(access_token or "").strip()}

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "tiktok-marketing-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(cfg.base_url),
        op=op,
        base_url=str(cfg.base_url),
        path_json=getattr(args, "path_json", None),
        query_json=getattr(args, "query_json", None),
        body_json=getattr(args, "body_json", None),
        path_pairs=getattr(args, "path", None),
        query_pairs=getattr(args, "query", None),
        body_pairs=getattr(args, "body", None),
        file_pairs=getattr(args, "file", None),
        query_defaults=query_defaults,
        header_defaults=header_defaults,
    )

    classification = _classify_operation(op)
    missing_required = plan.get("requirements", {}).get("missing_required") or []
    plan["generated_at_utc"] = _utc_now()
    plan["classification"] = classification
    plan["risk_level"] = _risk_level(classification)
    plan["risk_reasons"] = _risk_reasons(classification)
    plan["preconditions"] = _preconditions(classification, missing_required)
    plan["verification_plan"] = _verification_plan(classification)
    plan["rollback"] = _rollback_contract(classification)
    plan = _ensure_write_safety_contract(plan, op, classification)
    plan_hash = _compute_plan_hash(plan)
    plan["plan_hash"] = plan_hash
    sanitized_plan = _sanitize_plan_for_output(plan)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitized_plan) if plan_out else None

    apply = bool(ctx.get("apply"))
    live = bool(ctx.get("live"))
    plan_in_obj: dict[str, Any] | None = None

    if apply and ctx.get("plan_in"):
        plan_in_loaded = read_json_file(ctx["plan_in"])
        if not isinstance(plan_in_loaded, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_for_apply(
            op_cmd=op.operation_command,
            op_method=op.method,
            op_path_template=op.path,
            plan_in=plan_in_loaded,
            base_fingerprint=str(cfg.base_url),
        )
        plan_in_obj = plan_in_loaded

    execution_plan = plan_in_obj or plan
    execution_plan = _ensure_write_safety_contract(execution_plan, op, classification)
    sanitized_execution_plan = _sanitize_plan_for_output(execution_plan)
    execution_missing_required = execution_plan.get("requirements", {}).get("missing_required") or []
    current_missing_required = plan.get("requirements", {}).get("missing_required") or []

    reasons: list[str] = []
    if classification["is_write"]:
        if apply and not live:
            reasons.append("Refused: --live is required for apply")
        if apply and not bool(ctx.get("yes")):
            reasons.append("Refused: --yes is required for POST/PUT/PATCH/DELETE operations")
        if apply and not bool(ctx.get("plan_in")):
            reasons.append("Refused: --plan-in is required for POST/PUT/PATCH/DELETE operations")
        if apply and not bool(ctx.get("ack_irreversible")):
            reasons.append("Refused: --ack-irreversible is required for write operations in this runtime")
        if apply and bool(execution_missing_required):
            missing_desc = ", ".join(
                f"{item.get('in')}:{item.get('name')}" for item in execution_missing_required
            )
            reasons.append(f"Refused: missing required inputs ({missing_desc})")
    else:
        if apply and not live:
            reasons.append("Refused: --live is required for --apply")
        if live and bool(current_missing_required):
            missing_desc = ", ".join(
                f"{item.get('in')}:{item.get('name')}" for item in current_missing_required
            )
            reasons.append(f"Refused: missing required inputs ({missing_desc})")

    if reasons:
        return _emit_refusal(ctx, op_cmd, reasons, sanitized_plan, plan_path)

    should_execute = (classification["is_read"] and live) or (classification["is_write"] and apply)

    if not should_execute:
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": sanitized_plan, "plan_out": plan_path})
        return 0

    if classification["is_write"]:
        if not bool(ctx.get("ack_no_snapshot")):
            out = before_state_refusal_output(sanitized_execution_plan, reason=API_WRITE_REFUSAL_REASON)
            ctx["audit"].write(
                "api.call.refused",
                {
                    "operation_command": op_cmd,
                    "method": op.method,
                    "plan_hash": sanitized_execution_plan.get("plan_hash") or plan_hash,
                    "reason": API_WRITE_REFUSAL_REASON,
                    "before_state": sanitized_execution_plan.get("before_state"),
                },
            )
            ctx["out"].emit(out)
            return 0

    if _needs_access_token(op) and not access_token:
        raise SafetyError("Missing access token (TIKTOK_MARKETING_ACCESS_TOKEN or .state/token.json)")

    secret_value = str(cfg.app_secret or "").strip()
    defaults_map = {
        "access-token": str(access_token or "").strip(),
        "access_token": str(access_token or "").strip(),
        "app_id": str(cfg.app_id or "").strip(),
        "app_secret": secret_value,
        "client_secret": secret_value,
        "secret": secret_value,
    }
    query_values = _restore_redacted_mapping(dict(execution_plan.get("inputs", {}).get("query") or {}), defaults_map)
    body_inputs = _restore_redacted_tree(execution_plan.get("inputs", {}).get("body"), defaults_map)
    files = dict(execution_plan.get("inputs", {}).get("files") or {})
    body_mode = str(execution_plan.get("operation", {}).get("body_mode") or "").strip().lower() or "none"
    if _contains_redacted_value(query_values) or _contains_redacted_value(body_inputs):
        raise SafetyError("Refused: plan still contains redacted secret values that are missing in the current environment")

    request_headers: dict[str, str] = {"Accept": "application/json"}
    for header_name, source in op.header_param_sources.items():
        replacement = defaults_map.get(str(source).lower())
        if replacement:
            request_headers[header_name] = replacement

    request_kwargs: dict[str, Any] = {
        "method": execution_plan["operation"]["method"],
        "url": execution_plan["operation"]["url"],
        "headers": request_headers,
        "params": query_values,
        "json_body": None,
        "data": None,
        "files": None,
    }

    with ExitStack() as stack:
        if files:
            request_kwargs["files"] = {}
            for field, file_path in files.items():
                fh = stack.enter_context(open(file_path, "rb"))
                request_kwargs["files"][field] = (Path(file_path).name, fh)
            request_kwargs["json_body"] = None
            request_kwargs["data"] = _serialize_form(body_inputs)
        elif body_inputs is not None:
            if body_mode == "json":
                request_kwargs["json_body"] = body_inputs
            else:
                request_kwargs["data"] = _serialize_form(body_inputs)

        client = HttpClient(
            timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
            verbose=bool(ctx.get("verbose")),
            user_agent=f"tiktok-marketing-api-tool/{ctx.get('tool_version') or '0.1.0'}",
        )
        response = client.request(**request_kwargs)

    response_summary = {
        "status": response.status,
        "url": response.url,
        "headers": _sanitize_headers(response.headers),
        "body": _read_body_preview(response),
    }
    provider_error = _provider_error_message(response_summary["body"])
    if provider_error:
        raise ToolError(provider_error)

    receipt = {
        "tool": ctx.get("tool") or "tiktok-marketing-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": str(cfg.base_url),
        "command": ctx.get("command_str") or None,
        "plan_hash": str(execution_plan.get("plan_hash") or plan_hash),
        "token_source": token_source,
        "operation": execution_plan["operation"],
        "classification": classification,
        "before_state": execution_plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": bool(classification.get("is_write")),
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this TikTok Marketing API write.",
        } if classification.get("is_write") else None,
        "request": {
            "method": execution_plan["operation"]["method"],
            "url": execution_plan["operation"]["url"],
            "query": query_values,
            "headers": sorted(list(request_kwargs["headers"].keys())),
            "body": body_inputs,
            "files": sorted(files.keys()) if isinstance(files, dict) else [],
            "body_mode": body_mode,
        },
        "response": response_summary,
        "verification": {
            "status": "provider-response-only",
            "details": "Verified by HTTP success and provider JSON response only. No read-back was attempted.",
        },
        "rollback_plan": _rollback_contract(classification),
    }
    sanitized_receipt = _sanitize_receipt_for_output(receipt)
    if ctx.get("receipt_out"):
        write_json_file(ctx["receipt_out"], sanitized_receipt)

    ctx["audit"].write(
        "api.call.apply",
        {
            "operation_command": op_cmd,
            "method": op.method,
            "plan_hash": plan_hash,
            "response_status": response.status,
        },
    )

    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "plan": sanitized_execution_plan,
            "receipt": sanitized_receipt,
            "receipt_out": ctx.get("receipt_out"),
        }
    )
    return 0
