from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..official import OperationDef, load_official_manifest
from ..redaction import redact_for_artifacts
from ..shopify_graphql import ShopifyAdminGraphQLClient


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _env_fingerprint(*, shop_domain: str, api_version: str) -> str:
    return f"{shop_domain}|{api_version}"


def _stable_json_hash(obj: Any) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _classify_mutation_risk(op_name: str) -> tuple[str, list[str]]:
    name = str(op_name or "")
    reasons: list[str] = []

    irreversible_markers = (
        "Delete",
        "Destroy",
        "Remove",
        "Purge",
        "Uninstall",
        "Cancel",
        "Close",
        "Deactivate",
        "Revoke",
    )
    high_markers = (
        "Bulk",
        "Batch",
        "Import",
        "Export",
        "Send",
        "Publish",
        "Enable",
        "Disable",
        "Start",
        "Run",
        "Execute",
        "Subscription",
        "Purchase",
        "UsageRecord",
        "Charge",
        "Payment",
        "Refund",
        "Capture",
        "Void",
        "Fulfill",
        "Fulfillment",
    )

    if any(m in name for m in irreversible_markers):
        reasons.append("name_contains_irreversible_marker")
        return "irreversible", reasons
    if any(m in name for m in high_markers):
        reasons.append("name_contains_high_risk_marker")
        return "high", reasons
    return "normal", ["default_normal_write"]


def _load_vars(vars_path: str | None) -> dict[str, Any]:
    if not vars_path:
        return {}
    obj = read_json_file(vars_path)
    if not isinstance(obj, dict):
        raise ValidationError("--vars JSON must be an object/dict")
    return obj


def _load_return_shape(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Return shape file not found: {p}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        raise ValidationError("Return shape file is empty")
    lowered = text.lower()
    if any(tok in lowered for tok in ("mutation", "query", "subscription", "fragment")):
        raise ValidationError("Return shape must be a selection set only (no query/mutation/fragment)")
    if not text.startswith("{") or not text.endswith("}"):
        raise ValidationError("Return shape must start with '{' and end with '}'")
    return text


def _default_selection_set(op: OperationDef) -> str:
    if op.return_doc_kind in {"scalars", "enums"}:
        return ""
    return "{ __typename }"


def _build_graphql_document(
    *,
    op: OperationDef,
    variables: dict[str, Any],
    selection_set: str,
) -> tuple[str, dict[str, Any]]:
    known_args = {a.name: a for a in op.args}
    unexpected = sorted([k for k in variables.keys() if k not in known_args])
    if unexpected:
        raise ValidationError(f"Unexpected variables for {op.kind}:{op.name}: {', '.join(unexpected)}")

    for a in op.args:
        if a.required and a.name not in variables:
            raise ValidationError(f"Missing required variable: {a.name}")

    used_args = [known_args[k] for k in variables.keys()]
    if used_args:
        var_defs = ", ".join([f"${a.name}: {a.gql_type}" for a in used_args])
        call_args = ", ".join([f"{a.name}: ${a.name}" for a in used_args])
        head = f"{op.kind} {op.name}({var_defs}) {{\n  {op.name}({call_args})"
    else:
        head = f"{op.kind} {op.name} {{\n  {op.name}"

    if selection_set:
        doc = head + f" {selection_set}\n}}\n"
    else:
        doc = head + "\n}\n"
    return doc, variables


def _validate_version_pin(*, cfg_api_version: str, manifest_api_version: str, allow_mismatch: bool) -> None:
    if cfg_api_version == manifest_api_version:
        return
    if allow_mismatch:
        return
    raise SafetyError(
        "Refused: SHOPIFY_ADMIN_API_VERSION does not match the pinned tool version "
        f"({cfg_api_version} != {manifest_api_version}). "
        "Re-run with --allow-version-mismatch if you accept reduced coverage guarantees."
    )


def cmd_execute_operation(args: Any, ctx: dict[str, Any]) -> int:
    op_kind = str(getattr(args, "op_kind", "") or "").strip()
    op_kebab = str(getattr(args, "op_kebab", "") or "").strip()
    vars_path = str(getattr(args, "vars", "") or "").strip() or None
    return_shape_file = str(getattr(args, "return_shape_file", "") or "").strip() or None
    ack_unsafe_return_shape = bool(getattr(args, "ack_unsafe_return_shape", False))
    allow_version_mismatch = bool(getattr(args, "allow_version_mismatch", False))

    manifest = load_official_manifest()
    op = manifest.find(op_kind, kebab=op_kebab)
    if not op:
        raise ValidationError(f"Unknown operation: {op_kind} {op_kebab}")

    cfg = ctx["cfg"]
    _validate_version_pin(
        cfg_api_version=str(cfg.api_version),
        manifest_api_version=str(manifest.api_version),
        allow_mismatch=allow_version_mismatch,
    )

    variables = _load_vars(vars_path)

    if return_shape_file:
        if not ack_unsafe_return_shape:
            raise SafetyError("Refused: --return-shape-file requires --ack-unsafe-return-shape")
        selection_set = _load_return_shape(return_shape_file)
    else:
        selection_set = _default_selection_set(op)

    gql_doc, gql_vars = _build_graphql_document(op=op, variables=variables, selection_set=selection_set)

    if op.kind == "query":
        client = ShopifyAdminGraphQLClient(
            shop_domain=cfg.shop_domain,
            admin_access_token=cfg.admin_access_token,
            api_version=cfg.api_version,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx.get("verbose")),
            user_agent=f"{ctx.get('tool')}/{ctx.get('tool_version')}",
        )
        resp = client.execute(query=gql_doc, variables=gql_vars)
        out = {
            "ok": True,
            "kind": op.kind,
            "operation": op.name,
            "api_version": cfg.api_version,
            "http_status": resp.http_status,
            "has_graphql_errors": bool(resp.errors),
            "data": resp.data,
            "errors": resp.errors,
        }
        ctx["audit"].write(
            "graphql.query",
            {"ok": True, "operation": op.name, "http_status": resp.http_status, "has_graphql_errors": bool(resp.errors)},
        )
        ctx["out"].emit(out)
        return 0

    risk_level, risk_reasons = _classify_mutation_risk(op.name)
    required_flags: list[str] = ["--apply"]
    if risk_level in {"high", "irreversible"}:
        required_flags.extend(["--yes", "--plan-in"])
    if risk_level == "irreversible":
        required_flags.append("--ack-irreversible")

    plan = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": _env_fingerprint(shop_domain=cfg.shop_domain, api_version=cfg.api_version),
        "command": ctx.get("command_str"),
        "selector": {"kind": "shopify_admin_graphql", "operation_kind": op.kind, "operation": op.name},
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "required_flags": required_flags,
        "baseline": {
            "shop_domain": cfg.shop_domain,
            "api_version": cfg.api_version,
            "operation_kind": op.kind,
            "operation": op.name,
            "vars_hash_sha256": _stable_json_hash(gql_vars),
            "selection_hash_sha256": _stable_json_hash(selection_set),
        },
        "request": {
            "graphql": {
                "document": gql_doc,
                "variables_redacted": redact_for_artifacts(gql_vars),
                "selection_set": selection_set,
                "return_gql_type": op.return_gql_type,
            }
        },
        "verification_plan": {
            "type": "graphql",
            "requires_no_snapshot_approval": True,
            "notes": "Apply can run after explicit no-snapshot approval, then records the Shopify GraphQL response.",
        },
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "notes": (
                "No useful before-state snapshot is captured for this Shopify Admin mutation. "
                "The mutation may still run after the reviewed plan and explicit no-snapshot approval."
            ),
        },
        "rollback": {
            "supported": False,
            "notes": "This tool does not create backups or restore points and does not auto-rollback.",
        },
    }

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj

    plan_out = ctx.get("plan_out")
    if plan_out:
        plan_path = write_json_file(plan_out, plan)
    else:
        plan_path = None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(
            "graphql.mutation.plan",
            {"operation": op.name, "risk_level": risk_level, "plan_out": plan_path},
        )
        ctx["out"].emit(out)
        return 0

    if risk_level in {"high", "irreversible"} and not plan_in:
        raise SafetyError("Refused: high-risk mutations require --plan-in")
    if risk_level in {"high", "irreversible"} and not bool(ctx.get("yes")):
        raise SafetyError("Refused: high-risk mutations require --yes")
    if risk_level == "irreversible" and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: irreversible mutations require --ack-irreversible")

    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline")
    if str(baseline.get("shop_domain") or "") != str(cfg.shop_domain):
        raise SafetyError("Refused: plan shop_domain does not match current config")
    if str(baseline.get("api_version") or "") != str(cfg.api_version):
        raise SafetyError("Refused: plan api_version does not match current config")
    if str(baseline.get("operation_kind") or "") != op.kind or str(baseline.get("operation") or "") != op.name:
        raise SafetyError("Refused: plan operation does not match current command")
    if str(baseline.get("vars_hash_sha256") or "") != _stable_json_hash(gql_vars):
        raise SafetyError("Refused: plan variables hash does not match current variables")
    if str(baseline.get("selection_hash_sha256") or "") != _stable_json_hash(selection_set):
        raise SafetyError("Refused: plan selection set hash does not match current selection")

    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused: this Shopify mutation has no saved before-state snapshot. "
            "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
        )

    client = ShopifyAdminGraphQLClient(
        shop_domain=cfg.shop_domain,
        admin_access_token=cfg.admin_access_token,
        api_version=cfg.api_version,
        timeout_s=ctx["timeout_s"],
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx.get('tool')}/{ctx.get('tool_version')}",
    )
    resp = client.execute(query=gql_doc, variables=gql_vars)
    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "operation": {"kind": op.kind, "name": op.name},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "rollback": plan.get("rollback"),
        "http_status": resp.http_status,
        "has_graphql_errors": bool(resp.errors),
        "data": resp.data,
        "errors": resp.errors,
        "verification": {
            "type": "provider_response",
            "ok": bool(resp.http_status and int(resp.http_status) < 400 and not resp.errors),
        },
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "plan": plan, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "graphql.mutation.apply",
        {
            "operation": op.name,
            "http_status": resp.http_status,
            "has_graphql_errors": bool(resp.errors),
            "receipt_out": receipt_path,
            "no_snapshot_approval": True,
        },
    )
    ctx["out"].emit(out)
    return 0
