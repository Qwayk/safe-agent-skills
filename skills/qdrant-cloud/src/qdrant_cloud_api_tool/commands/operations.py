from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import shlex
import time
from typing import Any

from ..cloud_http import QdrantCloudHttpClient
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..operations_v1 import Operation, find_operation_by_rpc, find_verification_read_op
from ..redaction import redact_any


_BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Qdrant Cloud write has no saved before-state snapshot or provider backup. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)

_PROVIDER_BACKUP_RESTORE_METHODS = {
    "CreateBackup",
    "RestoreBackup",
    "CreateClusterFromBackup",
}
_RESTORE_BACKUP_RPC = "qdrant.cloud.cluster.backup.v1.BackupService.RestoreBackup"
_PRICE_QUOTE_RPCS = {
    "qdrant.cloud.booking.v1.BookingService.GetQuote",
    "qdrant.cloud.booking.v1.BookingService.GetBackupQuote",
}
_POTENTIALLY_PAID_RPCS = {
    _RESTORE_BACKUP_RPC,
    "qdrant.cloud.cluster.backup.v1.BackupService.CreateBackup",
    "qdrant.cloud.cluster.backup.v1.BackupService.CreateBackupSchedule",
    "qdrant.cloud.cluster.backup.v1.BackupService.UpdateBackupSchedule",
    "qdrant.cloud.cluster.v1.ClusterService.CreateCluster",
    "qdrant.cloud.cluster.v1.ClusterService.CreateClusterFromBackup",
    "qdrant.cloud.cluster.v1.ClusterService.UnsuspendCluster",
    "qdrant.cloud.cluster.v1.ClusterService.UpdateCluster",
    "qdrant.cloud.serverless.collection.v1.CollectionService.CreateCollection",
    "qdrant.cloud.serverless.collection.v1.CollectionService.UpgradeCollection",
}


def _utc(ts: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts or time.time()))


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _json_sha256(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj)).hexdigest()


def _sign_plan(plan: dict[str, Any], api_key: str) -> str:
    return hmac.new(api_key.encode("utf-8"), _canonical_json(plan), hashlib.sha256).hexdigest()


def is_read_operation(verb: str, rpc: str) -> bool:
    return verb.upper() == "GET" or rpc in _PRICE_QUOTE_RPCS


@dataclasses.dataclass(frozen=True)
class OperationRisk:
    level: str
    reasons: list[str]
    requires_apply: bool
    requires_yes: bool
    requires_ack_irreversible: bool
    requires_ack_spend_money: bool
    requires_plan_in: bool


def _is_provider_backup_restore_family(*, op: Operation) -> bool:
    if op.method in _PROVIDER_BACKUP_RESTORE_METHODS:
        return True
    return False


def _operation_recovery_contract(*, op: Operation) -> dict[str, str]:
    if _is_provider_backup_restore_family(op=op):
        return {
            "contract": "provider-backup-restore",
            "details": "Recovery is explicit at provider level through backup/restore commands (for example, create-backup, restore-backup, create-cluster-from-backup). This is not an automatic rollback for other writes.",
        }
    return {
        "contract": "no-recovery",
        "details": "No automatic rollback is guaranteed for this operation. If you need recovery, run provider-native backup/restore commands as a separate workflow.",
    }


def _operation_before_state_contract(*, op: Operation, risk: OperationRisk) -> dict[str, Any]:
    if not risk.requires_apply:
        return {
            "required": False,
            "supported": False,
            "status": "not-required",
            "notes": "Read-like operations do not need before-state capture.",
        }
    if _is_provider_backup_restore_family(op=op):
        return {
            "required": False,
            "supported": True,
            "status": "provider-backup-restore-family",
            "notes": "This operation is part of Qdrant Cloud provider backup/restore. It is allowed live after the normal gates, but it is not automatic rollback for unrelated writes.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "notes": (
            "No useful before-state snapshot or provider backup is captured for this ordinary Qdrant Cloud write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _operation_verification_plan(*, op: Operation, risk: OperationRisk) -> Any:
    if op.rpc == _RESTORE_BACKUP_RPC:
        return {"type": "restore_history", "notes": "Check for a new restore entry for this backup in the account."}
    if risk.requires_apply and not _is_provider_backup_restore_family(op=op):
        return {
            "type": "best_effort_after_apply",
            "requires_no_snapshot_approval": True,
            "notes": "Apply can run after explicit no-snapshot approval, then records HTTP result and best-effort read-back when a matching GET exists.",
        }
    return [
        "Best-effort: capture HTTP status + response body.",
        "For writes: if a GET operation exists with the same path template, run it as a read-back check.",
    ]


def classify_operation_risk(*, verb: str, path: str, rpc: str, domain: str) -> OperationRisk:
    v = verb.strip().upper()
    d = domain.strip().lower()
    p = path.strip().lower()

    is_delete = v == "DELETE"
    can_charge = (
        rpc in _POTENTIALLY_PAID_RPCS
        or "payment" in d or "billing" in d or "payment" in p or "billing" in p
    )

    if is_read_operation(v, rpc):
        return OperationRisk(
            level="low",
            reasons=["reads account data or returns a price estimate"],
            requires_apply=False,
            requires_yes=False,
            requires_ack_irreversible=False,
            requires_ack_spend_money=False,
            requires_plan_in=False,
        )

    reasons = ["changes Qdrant Cloud"]
    irreversible = is_delete or rpc == _RESTORE_BACKUP_RPC
    if is_delete:
        reasons.append("deletes a resource")
    if rpc == _RESTORE_BACKUP_RPC:
        reasons.append("restores over the existing cluster, replacing newer data and settings")
    if can_charge:
        reasons.append("can change what you pay")

    high_risk = irreversible or can_charge
    return OperationRisk(
        level="high" if high_risk else "medium",
        reasons=reasons,
        requires_apply=True,
        requires_yes=high_risk,
        requires_ack_irreversible=irreversible,
        requires_ack_spend_money=can_charge,
        requires_plan_in=True,
    )


def _load_request_obj(args: Any) -> dict[str, Any]:
    req_file = str(getattr(args, "request_json", "") or "").strip()
    if not req_file:
        return {}
    obj = read_json_file(req_file)
    if not isinstance(obj, dict):
        raise ValidationError("--request-json must be a JSON object")
    return obj


def _load_path_params(args: Any, op: Operation) -> dict[str, str]:
    out: dict[str, str] = {}
    for template_name, arg_name in op.path_params:
        v = str(getattr(args, arg_name, "") or "").strip()
        if not v:
            raise ValidationError(f"Missing --{arg_name.replace('_', '-')}")
        out[template_name] = v
    return out


def _build_plan(
    *, op: Operation, path_params: dict[str, str], request_obj: dict[str, Any],
    risk: OperationRisk, ctx: dict[str, Any],
) -> dict[str, Any]:
    recovery = _operation_recovery_contract(op=op)
    cfg = ctx["cfg"]
    plan = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "generated_at_utc": _utc(),
        "env_fingerprint": ctx["cfg"].env_fingerprint,
        "command": ctx.get("command_str"),
        "operation": {
            "rpc": op.rpc,
            "domain": op.domain,
            "http_verb": op.http_verb,
            "http_path": op.http_path,
            "path_params": path_params,
        },
        "risk_level": risk.level,
        "risk_reasons": list(risk.reasons),
        "safety": {
            "requires_live": True,
            "requires_apply": risk.requires_apply,
            "requires_yes": risk.requires_yes,
            "requires_ack_irreversible": risk.requires_ack_irreversible,
            "requires_ack_spend_money": risk.requires_ack_spend_money,
            "requires_plan_in": risk.requires_plan_in,
            "before_state": _operation_before_state_contract(op=op, risk=risk),
            "recovery": recovery,
        },
        "request_sha256": _json_sha256(request_obj),
        "request": redact_any(request_obj),
        "verification_plan": _operation_verification_plan(op=op, risk=risk),
    }
    if risk.requires_apply:
        if cfg.api_key:
            plan["review_signature"] = _sign_plan(plan, cfg.api_key)
        else:
            plan["review_note"] = "Set the API key and make a new plan before approving this write."
    return plan


def _enforce_plan_drift(
    *, plan_obj: dict[str, Any], op: Operation, path_params: dict[str, str],
    request_obj: dict[str, Any], ctx: dict[str, Any],
) -> None:
    cfg = ctx["cfg"]
    signature = plan_obj.pop("review_signature", None)
    if not isinstance(signature, str) or not signature.isascii():
        raise SafetyError("This plan does not have a review signature. Generate and review a new plan with the API key set.")
    if not cfg.api_key or not hmac.compare_digest(signature, _sign_plan(plan_obj, cfg.api_key)):
        raise SafetyError("The API key or saved plan changed. Generate and review a new plan.")
    if plan_obj.get("env_fingerprint") != cfg.env_fingerprint:
        raise SafetyError("The Qdrant API address changed. Review a new plan.")
    if plan_obj.get("operation") != {
        "rpc": op.rpc, "domain": op.domain, "http_verb": op.http_verb,
        "http_path": op.http_path, "path_params": path_params,
    }:
        raise SafetyError("The operation or target changed. Review a new plan.")
    if plan_obj.get("request_sha256") != _json_sha256(request_obj):
        raise SafetyError("The request changed. Review a new plan.")


def cmd_qdrant_cloud_operation(args: Any, ctx: dict[str, Any]) -> int:
    rpc = str(getattr(args, "rpc", "") or "").strip()
    if not rpc:
        raise ValidationError("Internal error: missing rpc")

    op = find_operation_by_rpc(rpc)
    request_obj = _load_request_obj(args)
    path_params = _load_path_params(args, op)

    risk = classify_operation_risk(verb=op.http_verb, path=op.http_path, rpc=op.rpc, domain=op.domain)
    is_get = op.http_verb.upper() == "GET"
    live = bool(ctx.get("live"))
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack_irreversible = bool(ctx.get("ack_irreversible"))
    ack_spend_money = bool(ctx.get("ack_spend_money"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None

    client = QdrantCloudHttpClient(
        base_url=ctx["cfg"].base_url,
        api_key=ctx["cfg"].api_key,
        timeout_s=float(ctx["timeout_s"] or ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )

    # Live read path
    if (not risk.requires_apply) and live:
        result = client.request_json(
            live=True,
            method=op.http_verb,
            path=op.http_path,
            path_params=path_params,
            query_params=(request_obj or None) if is_get else None,
            json_body=None if is_get else (request_obj or None),
        )
        out = {
            "ok": bool(result.ok),
            "dry_run": False,
            "read": True,
            "operation": {
                "rpc": op.rpc,
                "domain": op.domain,
                "http_verb": op.http_verb,
                "http_path": op.http_path,
                "path_params": path_params,
            },
            "http": {"url": result.url, "status": result.status},
            "response": result.response_json,
            "response_text": result.response_text,
            "error": result.error,
            "verification": {"ok": bool(result.ok), "details": "HTTP status check (no provider-specific read-back)."},
        }
        ctx["audit"].write("qdrant_cloud.operation.read", {"rpc": op.rpc, "ok": bool(out["ok"])})
        ctx["out"].emit(out)
        return 0

    if not apply:
        plan = _build_plan(op=op, path_params=path_params, request_obj=request_obj, risk=risk, ctx=ctx)
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("qdrant_cloud.operation.plan", {"rpc": op.rpc, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    # Apply gates
    if risk.requires_yes and not yes:
        raise SafetyError(f"{op.rpc} requires --yes")
    if risk.requires_ack_irreversible and not ack_irreversible:
        raise SafetyError(f"{op.rpc} requires --ack-irreversible")
    if risk.requires_ack_spend_money and not ack_spend_money:
        raise SafetyError(f"{op.rpc} requires --ack-spend-money")
    if risk.requires_plan_in and not plan_in:
        raise SafetyError(f"{op.rpc} requires --plan-in (apply from a reviewed plan file)")

    if not live:
        raise SafetyError("Refusing to make network requests without --live")

    if risk.requires_plan_in and plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("--plan-in must be a JSON object plan")
        _enforce_plan_drift(plan_obj=plan_obj, op=op, path_params=path_params, request_obj=request_obj, ctx=ctx)

    if risk.requires_apply and not _is_provider_backup_restore_family(op=op) and not bool(ctx.get("ack_no_snapshot")):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [_BEFORE_STATE_REFUSAL_REASON],
            "refusal_type": "SafetyError",
            "operation": {"rpc": op.rpc, "domain": op.domain, "http_verb": op.http_verb, "http_path": op.http_path},
            "plan_out": None,
        }
        ctx["audit"].write("qdrant_cloud.operation.refused", {"rpc": op.rpc, "reason": _BEFORE_STATE_REFUSAL_REASON})
        ctx["out"].emit(out)
        return 0

    # Execute
    result = client.request_json(
        live=live,
        method=op.http_verb,
        path=op.http_path,
        path_params=path_params,
        query_params=(request_obj or None) if is_get else None,
        json_body=None if is_get else (request_obj or None),
    )

    # Best-effort verification
    verification: dict[str, Any] = {"ok": None, "details": "not attempted"}
    if op.rpc == _RESTORE_BACKUP_RPC:
        verification = {
            "ok": None,
            "details": "Check restore history for a new entry for this backup before reporting completion or trying again.",
            "backup_id": path_params["backup_id"],
            "command": shlex.join([
                "qdrant-cloud-api-tool", "--env-file", ctx["env_file"], "--output", "json", "--live",
                "cluster-backup-v1", "list-backup-restores", "--account-id", path_params["account_id"],
            ]),
        }
    elif not result.ok:
        verification = {
            "ok": None,
            "details": "Check the affected resource before trying this write again.",
        }
    elif op.http_verb.upper() == "DELETE":
        verification = {"ok": None, "details": "Not implemented for DELETE in v0.1.0 (provider-specific semantics)."}
    else:
        read_op = find_verification_read_op(op)
        if read_op:
            read_result = client.request_json(
                live=live,
                method=read_op.http_verb,
                path=read_op.http_path,
                path_params=path_params,
                query_params=None,
            )
            verification = {
                "ok": bool(read_result.ok),
                "details": "GET read-back on same path template",
                "read_back": {"rpc": read_op.rpc, "http": {"url": read_result.url, "status": read_result.status}},
            }
        else:
            verification = {
                "ok": None,
                "details": "No deterministic GET read-back found for this path template in the official inventory.",
            }

    receipt = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "applied_at_utc": _utc(),
        "env_fingerprint": ctx["cfg"].env_fingerprint,
        "command": ctx.get("command_str"),
        "operation": {
            "rpc": op.rpc,
            "domain": op.domain,
            "http_verb": op.http_verb,
            "http_path": op.http_path,
            "path_params": path_params,
        },
        "risk_level": risk.level,
        "risk_reasons": list(risk.reasons),
        "safety": {
            "before_state": _operation_before_state_contract(op=op, risk=risk),
            "recovery": _operation_recovery_contract(op=op),
            "no_snapshot_approval": {
                "approved": bool(risk.requires_apply and not _is_provider_backup_restore_family(op=op)),
                "flag": "--ack-no-snapshot" if risk.requires_apply and not _is_provider_backup_restore_family(op=op) else None,
            },
        },
        "ok": bool(result.ok),
        "http": {"url": result.url, "status": result.status},
        "response": result.response_json,
        "response_text": result.response_text,
        "error": result.error,
        "verification": verification,
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, redact_any(receipt)) if receipt_out else None
    out = {"ok": bool(result.ok), "dry_run": False, "receipt": redact_any(receipt), "receipt_out": receipt_path}
    ctx["audit"].write("qdrant_cloud.operation.apply", {"rpc": op.rpc, "ok": bool(out["ok"]), "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0 if bool(out["ok"]) else 1
