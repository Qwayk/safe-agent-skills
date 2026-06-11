from __future__ import annotations

import re
import time
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..redaction import redact_any
from ..soap_client import MsAdsSoapClient


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def pascal_to_kebab(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.replace("_", "-").lower()


def _json_sha256(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _before_state_for_risk(risk: "Risk") -> dict[str, Any]:
    if not risk.requires_apply:
        return {
            "required": False,
            "supported": False,
            "statement": "Read-like operation. No before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "statement": (
            "This Microsoft Ads operation has no reliable generic before-state snapshot. "
            "Apply may continue only after explicit no-snapshot approval."
        ),
    }


def _verification_plan_for_risk(risk: "Risk") -> list[str]:
    if not risk.requires_apply:
        return [
            "Best-effort: capture HTTP status + response body (truncated).",
            "Provider-specific read-back verification is not implemented in v0.1.0.",
        ]
    return [
        "Best-effort: capture HTTP status + response body (truncated).",
        "Provider-specific read-back verification is not implemented in v0.1.0.",
        "Receipt must record explicit no-snapshot approval for write operations.",
    ]


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise SafetyError(
        "Refused: this Microsoft Ads write has no reliable generic before-state snapshot. "
        "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
    )


@dataclass(frozen=True)
class Risk:
    level: str  # low | medium | high | irreversible
    reasons: list[str]
    requires_apply: bool
    requires_yes: bool
    requires_ack_irreversible: bool
    requires_plan_in: bool


def classify_operation_risk(*, service: str, operation: str) -> Risk:
    # Safe defaults: unknown is gated as high-risk write.
    # The full provider schema is large; this heuristic is intentionally conservative.
    op = operation
    lop = op.lower()

    read_prefixes = ("get", "list", "search", "query", "download", "retrieve", "poll")
    if lop.startswith(read_prefixes):
        return Risk(
            level="low",
            reasons=["Read-like operation name"],
            requires_apply=False,
            requires_yes=False,
            requires_ack_irreversible=False,
            requires_plan_in=False,
        )

    if "delete" in lop or lop.startswith("remove"):
        return Risk(
            level="irreversible",
            reasons=["Delete/remove-like operation name"],
            requires_apply=True,
            requires_yes=True,
            requires_ack_irreversible=True,
            requires_plan_in=True,
        )

    spend_keywords = ("budget", "bid", "billing", "payment", "invoice", "credit", "fund", "coupon")
    if any(k in lop for k in spend_keywords):
        return Risk(
            level="high",
            reasons=["Spend/billing-impacting operation (conservative heuristic)"],
            requires_apply=True,
            requires_yes=True,
            requires_ack_irreversible=False,
            requires_plan_in=True,
        )

    # Default: treat all non-read ops as writes, but allow apply without plan-in unless classified high/irreversible.
    return Risk(
        level="medium",
        reasons=["Non-read operation name (conservative heuristic)"],
        requires_apply=True,
        requires_yes=False,
        requires_ack_irreversible=False,
        requires_plan_in=False,
    )


def _load_request_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("--request-json must be a JSON object")
    return obj


def cmd_msads_operation(args: Any, ctx: dict) -> int:
    service = str(getattr(args, "service", "") or "").strip()
    operation = str(getattr(args, "operation", "") or "").strip()
    if not service or not operation:
        raise ValidationError("Internal error: missing service/operation bindings")

    cfg = ctx["cfg"]
    live = bool(ctx.get("live"))
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack_irreversible = bool(ctx.get("ack_irreversible"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    plan_out = str(ctx.get("plan_out") or "").strip() or None
    receipt_out = str(ctx.get("receipt_out") or "").strip() or None

    request_obj = _load_request_json(getattr(args, "request_json", None))
    risk = classify_operation_risk(service=service, operation=operation)

    client = MsAdsSoapClient(
        env_file=str(ctx["env_file"]),
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"msads-api-tool/{ctx['tool_version']}",
        endpoints=cfg.endpoints,
        developer_token=cfg.developer_token,
        customer_id=cfg.customer_id,
        customer_account_id=cfg.customer_account_id,
    )

    base_plan = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "generated_at_utc": _utc(time.time()),
        "env_fingerprint": cfg.env_fingerprint,
        "command": ctx["command_str"],
        "risk_level": risk.level,
        "risk_reasons": risk.reasons,
        "safety": {
            "requires_live": True,
            "requires_apply": risk.requires_apply,
            "requires_yes": risk.requires_yes,
            "requires_ack_irreversible": risk.requires_ack_irreversible,
            "requires_plan_in": risk.requires_plan_in,
        },
        "operation": {
            "service": service,
            "operation": operation,
            "operation_kebab": pascal_to_kebab(operation),
        },
        "request_sha256": _json_sha256(request_obj),
        "request": redact_any(request_obj),
        "api_plan": client.build_plan(service=service, operation=operation, request_obj=request_obj, live=live),
        "verification_plan": _verification_plan_for_risk(risk),
        "before_state": _before_state_for_risk(risk),
        "rollback": {
            "supported": False,
            "mode": "irreversible_and_clearly_labeled",
            "notes": "No built-in rollback, snapshots, or provider restore are available in this runtime. Treat write families as irreversible_and_clearly_labeled.",
        },
    }

    # Live reads: allow execution without --apply for read-like operations.
    if (not risk.requires_apply) and live:
        result = client.call(service=service, operation=operation, request_obj=request_obj)
        fault_detected = False
        if isinstance(result.response_text, str) and result.response_text:
            fault_detected = "<fault" in result.response_text.lower()
        verification_ok = bool(result.ok) and (not fault_detected)
        out = {
            "ok": bool(result.ok) and verification_ok,
            "dry_run": False,
            "read": True,
            "operation": base_plan["operation"],
            "http": {
                "url": result.url,
                "status": result.status,
                "started_at_utc": result.started_at_utc,
                "finished_at_utc": result.finished_at_utc,
            },
            "response_text": result.response_text,
            "error": result.error,
            "verification": {
                "ok": verification_ok,
                "details": "HTTP status + SOAP Fault tag scan (no read-back verification in v0.1.0).",
            },
        }
        ctx["audit"].write(
            "msads.operation.read",
            {"service": service, "operation": operation, "ok": bool(out["ok"])},
        )
        ctx["out"].emit(out)
        return 0

    if not apply:
        plan_path = write_json_file(plan_out, base_plan) if plan_out else None
        out = {"ok": True, "dry_run": True, "plan": base_plan, "plan_out": plan_path}
        ctx["audit"].write("msads.operation.plan", {"service": service, "operation": operation, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    # Apply path
    if risk.requires_yes and not yes:
        raise SafetyError(f"{service}:{operation} requires --yes")
    if risk.requires_ack_irreversible and not ack_irreversible:
        raise SafetyError(f"{service}:{operation} requires --ack-irreversible")
    if risk.requires_plan_in and not plan_in:
        raise SafetyError(f"{service}:{operation} requires --plan-in (apply from a reviewed plan file)")
    if not live:
        raise SafetyError("Refusing to make network requests without --live")

    # If applying from a plan file, use it as the source of truth for service/operation/request.
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("--plan-in must be a JSON object plan")
        env_fp_in = str(plan_obj.get("env_fingerprint") or "").strip()
        if not env_fp_in:
            raise SafetyError("Plan missing env_fingerprint; refuse to apply")
        if env_fp_in != cfg.env_fingerprint:
            raise SafetyError(f"Plan env_fingerprint mismatch: plan={env_fp_in} cli={cfg.env_fingerprint}")

        op_obj = plan_obj.get("operation") if isinstance(plan_obj.get("operation"), dict) else {}
        svc_in = str(op_obj.get("service") or "").strip()
        op_in = str(op_obj.get("operation") or "").strip()
        if svc_in and svc_in != service:
            raise SafetyError(f"Plan service mismatch: plan={svc_in} cli={service}")
        if op_in and op_in != operation:
            raise SafetyError(f"Plan operation mismatch: plan={op_in} cli={operation}")
        req_sha_in = str(plan_obj.get("request_sha256") or "").strip()
        if not req_sha_in:
            raise SafetyError("Plan missing request_sha256; refuse to apply")
        req_sha_now = _json_sha256(request_obj)
        if req_sha_in != req_sha_now:
            raise SafetyError("Plan request mismatch (request_sha256 differs); refuse to apply")

    _require_no_snapshot_approval(ctx)

    result = client.call(service=service, operation=operation, request_obj=request_obj)
    fault_detected = False
    if isinstance(result.response_text, str) and result.response_text:
        fault_detected = "<fault" in result.response_text.lower()
    verification_ok = bool(result.ok) and (not fault_detected)
    receipt = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "applied_at_utc": _utc(time.time()),
        "env_fingerprint": cfg.env_fingerprint,
        "command": ctx["command_str"],
        "operation": {"service": service, "operation": operation},
        "risk_level": risk.level,
        "before_state": base_plan["before_state"],
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable generic before-state snapshot is available for this Microsoft Ads SOAP operation.",
        },
        "ok": bool(result.ok),
        "changed": None,
        "http": {
            "url": result.url,
            "status": result.status,
            "started_at_utc": result.started_at_utc,
            "finished_at_utc": result.finished_at_utc,
        },
        "response_text": result.response_text,
        "error": result.error,
        "verification": {
            "ok": verification_ok,
            "details": "HTTP status + SOAP Fault tag scan (no read-back verification in v0.1.0).",
        },
        "rollback": {
            "supported": False,
            "mode": "irreversible_and_clearly_labeled",
            "notes": "No built-in rollback, snapshots, or provider restore are available in this runtime. This write action is irreversible_and_clearly_labeled.",
        },
    }

    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": bool(result.ok), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "msads.operation.apply",
        {"service": service, "operation": operation, "receipt_out": receipt_path, "ok": bool(result.ok)},
    )
    ctx["out"].emit(out)
    return 0
