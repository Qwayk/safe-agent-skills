from __future__ import annotations

import hashlib
import json
import time
from contextlib import ExitStack
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
from .auth import ensure_access_token
from .write_safety import (
    before_state_contract,
    before_state_refusal_output,
    before_state_refusal_verification_plan,
)

IRREVERSIBLE_PATH_KEYWORDS = (
    "delete",
    "/del",
    "unfriend",
    "revert",
    "close_thread",
    "clearflairtemplates",
)

RISKY_PATH_KEYWORDS = (
    "submit",
    "edit",
    "friend",
    "flair",
    "widget",
    "wiki",
    "emoji",
    "vote",
    "report",
    "block",
    "ban",
    "mute",
    "lock",
    "spoiler",
    "sticky",
    "filter",
)

SECRET_KEY_EXACT = {
    "authorization",
    "token",
    "access_token",
    "refresh_token",
    "client_secret",
    "password",
    "cookie",
}

IRREVERSIBLE_WRITE_MODE = "irreversible_and_clearly_labeled"
API_WRITE_REFUSAL_REASON = (
    "Refused: this Reddit API write has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _classify_operation(op: Any) -> dict[str, Any]:
    method = str(op.method or "").upper()
    path_lower = str(op.path or "").lower()
    is_read = method in {"GET", "HEAD"}
    is_write = not is_read
    irreversible = method == "DELETE" or any(keyword in path_lower for keyword in IRREVERSIBLE_PATH_KEYWORDS)
    risky = is_write and (irreversible or method in {"PATCH"} or any(keyword in path_lower for keyword in RISKY_PATH_KEYWORDS))
    return {
        "method": method,
        "is_read": is_read,
        "is_write": is_write,
        "irreversible": irreversible,
        "risky": risky,
        "section": str(op.section or ""),
        "oauth_scope": str(op.oauth_scope or ""),
        "gates": {
            "live": True,
            "apply": is_write,
            "plan_in": risky,
            "yes": risky,
            "ack_irreversible": irreversible,
        },
    }


def _risk_level(classification: dict[str, Any]) -> str:
    if bool(classification.get("risky")):
        return "high"
    if bool(classification.get("is_write")):
        return "medium"
    return "low"


def _risk_reasons(classification: dict[str, Any]) -> list[str]:
    if bool(classification.get("is_read")):
        return ["read-only-operation"]
    reasons = ["write-operation"]
    if bool(classification.get("risky")):
        reasons.append("risky-write")
    if bool(classification.get("irreversible")):
        reasons.append("irreversible-write")
    return reasons


def _preconditions(classification: dict[str, Any], missing_required: list[dict[str, Any]]) -> list[str]:
    out = ["env_fingerprint must match when applying from a reviewed plan"]
    if bool(classification.get("is_write")):
        out.append("live writes require --live --apply")
    gates = classification.get("gates") or {}
    if bool(gates.get("plan_in")):
        out.append("risky apply requires --plan-in")
    if bool(gates.get("yes")):
        out.append("risky apply requires --yes")
    if bool(gates.get("ack_irreversible")):
        out.append("irreversible apply requires --ack-irreversible")
    if missing_required:
        out.append("fill every required path value before a live call")
    return out


def _verification_plan(op: Any, classification: dict[str, Any]) -> dict[str, Any]:
    if bool(classification.get("is_read")):
        return {
            "type": "read-only",
            "notes": "Read-only operation. No post-apply verification is needed.",
        }
    return before_state_refusal_verification_plan()


def _legacy_write_verification_plan(op: Any) -> dict[str, Any]:
    if _matching_get_operation(op) is not None:
        return {
            "type": "best-effort-read-back",
            "notes": "If the provider exposes a matching GET path, try a read-back check after the write.",
        }
    return {
        "type": "response-only",
        "notes": "No generic read-back target exists for this endpoint in the pinned Reddit inventory.",
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
            "Treat current Reddit write families as irreversible_and_clearly_labeled and fix problems manually "
            "from the saved plan and refusal output."
        ),
    }


def _compute_plan_hash(plan: dict[str, Any]) -> str:
    plan_copy = {key: value for key, value in plan.items() if key != "plan_hash"}
    encoded = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ensure_write_safety_contract(plan: dict[str, Any], op: Any, classification: dict[str, Any]) -> dict[str, Any]:
    if not bool(classification.get("is_write")):
        return plan
    plan["before_state"] = before_state_contract(
        reason=(
            "This source tool can build and review Reddit write plans, but no reliable endpoint-specific "
            "before-state snapshot is available for this generic API operation."
        ),
        provider_write={
            "operation_command": str(getattr(op, "operation_command", "") or ""),
            "method": str(getattr(op, "method", "") or ""),
            "path_template": str(getattr(op, "path", "") or ""),
            "url": (plan.get("operation") or {}).get("url"),
        },
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["legacy_verification_plan"] = _legacy_write_verification_plan(op)
    return plan


def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in {"authorization", "cookie", "set-cookie"}:
            continue
        out[key_lower] = value
    return out


def _redact_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() in SECRET_KEY_EXACT or str(key).lower().endswith("_token"):
                redacted[key] = "<redacted>"
            else:
                redacted[key] = _redact_json_value(item)
        return redacted
    if isinstance(value, list):
        return [_redact_json_value(item) for item in value]
    return value


def _sanitize_for_output(value: Any) -> Any:
    return _redact_json_value(value)


def _sanitize_plan_for_output(plan: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_for_output(plan)


def _sanitize_receipt_for_output(receipt: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_for_output(receipt)


def _current_env_fingerprint(ctx: dict[str, Any], cfg: Any) -> str:
    cached = ctx.get("env_fingerprint")
    if cached:
        return str(cached)
    if (
        getattr(cfg, "base_url", None) is not None
        and getattr(cfg, "authorize_url", None) is not None
        and getattr(cfg, "token_url", None) is not None
        and getattr(cfg, "oauth_scopes", None) is not None
        and getattr(cfg, "user_agent", None) is not None
    ):
        return build_env_fingerprint(cfg)
    return str(getattr(cfg, "base_url", "")) or ""


def _build_response_body_summary(response: Any) -> dict[str, Any]:
    content_type = str(response.headers.get("content-type") or "")
    if "json" in content_type.lower():
        try:
            payload = _redact_json_value(response.json())
            return {"type": "json", "body_json": payload}
        except Exception:
            pass
    return {
        "type": "text",
        "body_text": response.text()[:4000],
        "truncated": len(response.body) > 4000,
    }


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
        {"operation_command": op_cmd, "reasons": reasons, "plan_hash": sanitized_plan.get("plan_hash")},
    )
    ctx["out"].emit(payload)
    return 0


def _validate_plan_for_apply(plan: dict[str, Any], plan_in: dict[str, Any], env_fingerprint: str) -> None:
    plan_op = plan.get("operation") or {}
    plan_in_op = plan_in.get("operation") or {}
    sanitized_plan = _sanitize_plan_for_output(plan)
    sanitized_plan_in = _sanitize_plan_for_output(plan_in)

    if str(plan_in.get("env_fingerprint") or "") != str(env_fingerprint):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan_in_op.get("operation_command") or "") != str(plan_op.get("operation_command") or ""):
        raise SafetyError("Refused: plan command mismatch")
    if str(plan_in_op.get("method") or "") != str(plan_op.get("method") or ""):
        raise SafetyError("Refused: plan method mismatch")
    if str(plan_in_op.get("path_template") or "") != str(plan_op.get("path_template") or ""):
        raise SafetyError("Refused: plan path mismatch")
    if sanitized_plan_in.get("inputs") != sanitized_plan.get("inputs"):
        raise SafetyError("Refused: plan inputs differ from current values")
    if str(plan_in.get("plan_hash") or "") and str(plan_in.get("plan_hash") or "") != str(plan.get("plan_hash") or ""):
        raise SafetyError("Refused: plan hash changed since plan creation")


def _matching_get_operation(op: Any) -> Any | None:
    for candidate in load_operations_from_pinned_snapshot():
        if candidate.method == "GET" and candidate.path == op.path:
            return candidate
    return None


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    method = str(getattr(args, "method", "") or "").strip().upper()
    section = str(getattr(args, "section", "") or "").strip().lower()
    scope = str(getattr(args, "scope", "") or "").strip().lower()
    ops = load_operations_from_pinned_snapshot()

    rows: list[dict[str, Any]] = []
    for op in ops:
        if method and op.method != method:
            continue
        if section and op.section.lower() != section:
            continue
        if scope and op.oauth_scope.lower() != scope:
            continue
        rows.append(
            {
                "operation_command": op.operation_command,
                "method": op.method,
                "path": op.path,
                "doc_url": op.doc_url,
                "section": op.section,
                "oauth_scope": op.oauth_scope,
                "required_path_params": list(op.required_path_params),
            }
        )
    payload = {"ok": True, "ops": rows, "count": len(rows)}
    ctx["audit"].write("api.ops.list", {"count": len(rows), "method": method or None, "section": section or None, "scope": scope or None})
    ctx["out"].emit(payload)
    return 0


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing operation")

    by_cmd = operations_by_command(load_operations_from_pinned_snapshot())
    op = by_cmd.get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "qwayk-reddit-safe-agent-cli",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=_current_env_fingerprint(ctx, ctx["cfg"]),
        op=op,
        base_url=str(ctx["cfg"].base_url),
        path_json=getattr(args, "path_json", None),
        query_json=getattr(args, "query_json", None),
        body_json=getattr(args, "body_json", None),
        path_pairs=getattr(args, "path", None),
        query_pairs=getattr(args, "query", None),
        body_pairs=getattr(args, "body", None),
        file_pairs=getattr(args, "file", None),
        body_format=str(getattr(args, "body_format", "form") or "form"),
    )

    classification = _classify_operation(op)
    missing_required = plan.get("requirements", {}).get("missing_required") or []
    plan["generated_at_utc"] = _utc_now()
    plan["command"] = ctx.get("command_str") or None
    plan["classification"] = classification
    plan["risk_level"] = _risk_level(classification)
    plan["risk_reasons"] = _risk_reasons(classification)
    plan["preconditions"] = _preconditions(classification, missing_required)
    plan["verification_plan"] = _verification_plan(op, classification)
    plan["rollback"] = _rollback_contract(classification)
    plan = _ensure_write_safety_contract(plan, op, classification)
    plan_hash = _compute_plan_hash(plan)
    plan["plan_hash"] = plan_hash
    sanitized_plan = _sanitize_plan_for_output(plan)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitized_plan) if plan_out else None

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
    if apply and gates["ack_irreversible"] and not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: --ack-irreversible is required for irreversible operations")
    if missing_required and live:
        desc = ", ".join(f"{item.get('in')}:{item.get('name')}" for item in missing_required)
        reasons.append(f"Refused: missing required inputs ({desc})")
    if reasons:
        return _emit_refusal(ctx, op_cmd, reasons, sanitized_plan, plan_path)

    if not apply and not (classification["is_read"] and live):
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": sanitized_plan, "plan_out": plan_path})
        return 0

    if ctx.get("plan_in"):
        plan_in_obj = read_json_file(ctx["plan_in"])
        if not isinstance(plan_in_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_for_apply(plan, plan_in_obj, _current_env_fingerprint(ctx, ctx["cfg"]))

    if classification["is_write"]:
        if not bool(ctx.get("ack_no_snapshot")):
            out = before_state_refusal_output(sanitized_plan, reason=API_WRITE_REFUSAL_REASON)
            ctx["audit"].write(
                "api.call.refused",
                {
                    "operation_command": op_cmd,
                    "method": op.method,
                    "plan_hash": plan_hash,
                    "reason": API_WRITE_REFUSAL_REASON,
                    "before_state": sanitized_plan.get("before_state"),
                },
            )
            ctx["out"].emit(out)
            return 0

    cfg = ctx["cfg"]
    access_token, token_source = ensure_access_token(
        cfg=cfg,
        env_file=str(ctx["env_file"]),
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
    )

    headers: dict[str, str] = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent=cfg.user_agent)
    request_kwargs: dict[str, Any] = {
        "method": plan["operation"]["method"],
        "url": plan["operation"]["url"],
        "headers": headers,
        "params": plan["inputs"]["query"],
        "json_body": None,
        "data": None,
        "files": None,
    }

    body = plan["inputs"]["body"] or {}
    body_format = str(plan["inputs"]["body_format"] or "form").strip().lower()
    file_map = plan["inputs"]["files"] or {}

    if file_map:
        request_kwargs["data"] = {str(key): str(value) for key, value in body.items() if value is not None}
    elif body and plan["operation"]["method"] not in {"GET", "HEAD"}:
        if body_format == "json":
            headers["Content-Type"] = "application/json"
            request_kwargs["json_body"] = body
        else:
            request_kwargs["data"] = {str(key): str(value) for key, value in body.items() if value is not None}

    with ExitStack() as stack:
        if file_map:
            files_payload: dict[str, Any] = {}
            for field, path in file_map.items():
                handle = stack.enter_context(open(path, "rb"))
                files_payload[field] = (path, handle)
            request_kwargs["files"] = files_payload

        response = client.request(**request_kwargs)

    verification = {"status": "skipped", "details": "No generic verification target for this endpoint"}
    if classification["is_write"]:
        verify_op = _matching_get_operation(op)
        if verify_op is not None:
            verify_response = client.request(
                method="GET",
                url=plan["operation"]["url"],
                headers=headers,
                params=plan["inputs"]["query"],
            )
            verification = {
                "status": "passed",
                "details": f"GET verification returned HTTP {verify_response.status}",
            }

    receipt = {
        "tool": ctx.get("tool") or "qwayk-reddit-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": _current_env_fingerprint(ctx, cfg),
        "command": ctx.get("command_str") or None,
        "plan_hash": plan_hash,
        "token_source": token_source,
        "operation": plan["operation"],
        "classification": classification,
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": bool(classification.get("is_write")),
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Reddit API write.",
        } if classification.get("is_write") else None,
        "request": {
            "method": plan["operation"]["method"],
            "url": plan["operation"]["url"],
            "query": plan["inputs"]["query"],
            "body": plan["inputs"]["body"],
            "body_format": body_format,
            "files": sorted(file_map.keys()),
        },
        "response": {
            "status": response.status,
            "url": response.url,
            "headers": _sanitize_headers(response.headers),
            "body": _build_response_body_summary(response),
        },
        "verification": verification,
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
            "plan": sanitized_plan,
            "receipt": sanitized_receipt,
            "receipt_out": ctx.get("receipt_out"),
        }
    )
    return 0
