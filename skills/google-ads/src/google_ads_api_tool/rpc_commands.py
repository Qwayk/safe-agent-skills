from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from google.api_core import exceptions as gexc

from .errors import SafetyError, ValidationError
from .google_ads_client import SUPPORTED_API_VERSION, build_google_ads_client, protobuf_to_dict
from .json_files import read_json_file, write_json_file
from .protobuf_json import parse_request_json
from .rpc_v22_registry import RPC_METHODS_V22, RpcMethodSpec


_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_INT_STRING_RE = re.compile(r"^-?\d+$")
_FLOAT_STRING_RE = re.compile(r"^-?\d+\.\d+$")

_CAMPAIGN_CRITERION_AD_SCHEDULE_REMOVE_FIELDS: list[str] = [
    "campaign",
    "criterion_id",
    "type",
    "status",
    "negative",
    "bid_modifier",
    "ad_schedule.day_of_week",
    "ad_schedule.start_hour",
    "ad_schedule.start_minute",
    "ad_schedule.end_hour",
    "ad_schedule.end_minute",
]


def _camel_to_kebab(name: str) -> str:
    parts = _CAMEL_BOUNDARY_RE.split(name.strip())
    return "-".join(p.lower() for p in parts if p)


def _method_is_mutate(spec: RpcMethodSpec) -> bool:
    # Backwards-compatible helper used by earlier tooling; kept for readability.
    return spec.method.startswith("Mutate")


_READ_VERBS: set[str] = {
    "Get",
    "List",
    "Search",
    "Suggest",
    "Generate",
    "Validate",
    "Retrieve",
}

_WRITE_VERBS: set[str] = {
    "Add",
    "Append",
    "Apply",
    "Cancel",
    "Configure",
    "Create",
    "Dismiss",
    "Enable",
    "End",
    "Graduate",
    "Move",
    "Mutate",
    "Promote",
    "Provide",
    "Regenerate",
    "Remove",
    "Run",
    "Schedule",
    "Start",
    "Update",
    "Upload",
}


def _method_is_write(spec: RpcMethodSpec) -> bool:
    verb = _CAMEL_BOUNDARY_RE.split(spec.method.strip())[0]
    if verb in _READ_VERBS:
        return False
    if verb in _WRITE_VERBS:
        return True
    # Fail closed: treat unknown verbs as writes so safety gates cannot be bypassed.
    return True


def register_v22_rpc_commands(sub: argparse._SubParsersAction) -> None:
    """
    Register explicit per-RPC-method commands for Google Ads API v22.

    Command shape:
      google-ads-api-tool <service-kebab> <method-kebab> --in request.json
    """
    by_service: dict[str, list[RpcMethodSpec]] = {}
    for spec in RPC_METHODS_V22:
        by_service.setdefault(spec.service, []).append(spec)

    for service_name in sorted(by_service.keys()):
        service_cmd = _camel_to_kebab(service_name)
        service_p = sub.add_parser(service_cmd, help=f"{service_name} RPC methods (v22)")
        service_sub = service_p.add_subparsers(
            dest=f"{service_cmd}_cmd", required=True, parser_class=type(service_p)
        )

        for spec in sorted(by_service[service_name], key=lambda s: s.method):
            is_write = _method_is_write(spec)
            method_cmd = _camel_to_kebab(spec.method)
            mp = service_sub.add_parser(method_cmd, help=f"{service_name}.{spec.method} (v22)")
            mp.add_argument("--in", dest="in_path", required=True, help="JSON request file for this RPC method")
            if is_write:
                mp.add_argument(
                    "--customer-id",
                    dest="customer_id_override",
                    default=None,
                    help="Safety override for write calls (digits only; used for allowlist gating)",
                )
            mp.set_defaults(func=cmd_rpc_method, rpc_method_spec=spec, write_capable=is_write)


def cmd_rpc_method(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    spec: RpcMethodSpec = getattr(args, "rpc_method_spec", None)
    if not isinstance(spec, RpcMethodSpec):
        raise ValidationError("Internal error: missing rpc_method_spec")

    in_path = str(getattr(args, "in_path", "") or "").strip()
    if not in_path:
        raise ValidationError("Missing --in PATH")
    req_obj = read_json_file(Path(in_path))

    customer_id_override = getattr(args, "customer_id_override", None)
    msg = parse_request_json(
        service=spec.service,
        request_type=spec.request_type,
        obj=req_obj,
        customer_id_override=str(customer_id_override) if customer_id_override else None,
    )

    apply = bool(ctx.get("apply"))
    out = ctx["out"]

    is_write = _method_is_write(spec)
    if is_write:
        return _cmd_write(
            spec=spec,
            request_msg=msg,
            in_path=in_path,
            ctx=ctx,
            customer_id_override=str(customer_id_override) if customer_id_override else None,
        )

    # Read methods (no --apply gate; always safe as external reads).
    if apply:
        # Keep Standard v2 semantics: `--apply` is for writes; for read-only RPCs it is ignored.
        apply = False

    client = build_google_ads_client(ctx["cfg"])
    svc = client.get_service(spec.service, version=SUPPORTED_API_VERSION)
    fn = getattr(svc, spec.python_method, None)
    if not callable(fn):
        raise ValidationError(f"Service method not found: {spec.service}.{spec.python_method}")

    timeout_s = float(ctx.get("timeout_s") or 30)

    if spec.call_type == "unary_stream":
        max_messages = 100
        stream = _call_with_retries(lambda: fn(request=msg, timeout=timeout_s), ctx=ctx)
        messages: list[dict[str, Any]] = []
        truncated = False
        for i, resp in enumerate(stream):
            if i >= max_messages:
                truncated = True
                break
            messages.append(protobuf_to_dict(resp))
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "rpc": asdict(spec),
                "input_path": str(Path(in_path)),
                "stream": True,
                "stream_max_messages": max_messages,
                "truncated": truncated,
                "count": len(messages),
                "responses": messages,
            }
        )
        return 0

    resp = _call_with_retries(lambda: fn(request=msg, timeout=timeout_s), ctx=ctx)
    out.emit(
        {
            "ok": True,
            "dry_run": False,
            "rpc": asdict(spec),
            "input_path": str(Path(in_path)),
            "response": protobuf_to_dict(resp),
        }
    )
    return 0


def _call_with_retries(fn: Callable[[], Any], *, ctx: dict[str, Any]) -> Any:
    cfg = ctx["cfg"]
    max_attempts = int(getattr(cfg, "retry_max_attempts", 3) or 3)
    base_delay_s = float(getattr(cfg, "retry_base_delay_s", 1.0) or 1.0)
    max_attempts = max(1, min(max_attempts, 10))
    base_delay_s = max(0.0, min(base_delay_s, 10.0))

    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except gexc.ServiceUnavailable as e:
            last = e
        except gexc.DeadlineExceeded as e:
            last = e
        except gexc.InternalServerError as e:
            last = e

        if attempt >= max_attempts:
            break
        time.sleep(base_delay_s * (2 ** (attempt - 1)))
    if last:
        raise last
    return fn()


def _plan_fingerprint(core: dict[str, Any]) -> str:
    payload = json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _payload_digest(obj: Any) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _request_summary(request_obj: dict[str, Any]) -> dict[str, Any]:
    keys = sorted([k for k in request_obj.keys() if isinstance(k, str)])
    ops = None
    for field_name in ("operations", "mutate_operations"):
        maybe_ops = request_obj.get(field_name)
        if isinstance(maybe_ops, list):
            ops = maybe_ops
            break
    op_actions: dict[str, int] = {}
    op_count = None
    if isinstance(ops, list):
        op_count = len(ops)
        for op in ops:
            if isinstance(op, dict):
                for k in op.keys():
                    if isinstance(k, str) and k:
                        op_actions[k] = int(op_actions.get(k, 0)) + 1
    return {
        "top_level_keys": keys,
        "operations_count": op_count,
        "operation_action_counts": {k: op_actions[k] for k in sorted(op_actions.keys())},
    }


def _plain_english_write_summary(
    *,
    spec: RpcMethodSpec,
    operations_count: int,
    risk_level: str,
    risk_reasons: list[str],
    irreversible: bool,
    request_summary: dict[str, Any],
    verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    action_counts = request_summary.get("operation_action_counts") if isinstance(request_summary, dict) else {}
    action_parts: list[str] = []
    if isinstance(action_counts, dict):
        for key in sorted(action_counts.keys()):
            count = int(action_counts.get(key) or 0)
            label = str(key).replace("_operation", "").replace("_", " ").strip()
            if count > 0:
                action_parts.append(f"{count} {label}")
    headline = f"{operations_count} Google Ads change"
    if operations_count != 1:
        headline += "s"
    headline += f" for {spec.service}.{spec.method}"
    if irreversible:
        headline += ", including remove work"

    details = []
    if action_parts:
        details.append("Operations: " + ", ".join(action_parts))
    if risk_reasons:
        details.append(f"Risk: {risk_level} because " + "; ".join(risk_reasons))
    else:
        details.append(f"Risk: {risk_level}")
    if isinstance(verification, dict):
        if verification.get("attempted"):
            details.append(
                "Verification: "
                f"{int(verification.get('verified_resources') or 0)} resources, "
                f"{int(verification.get('verified_fields') or 0)} fields checked"
            )
        elif verification.get("reason"):
            details.append(f"Verification: not completed ({verification.get('reason')})")
    return {
        "headline": headline,
        "details": details,
    }


def _request_operations_from_message(request_msg: Any) -> list[Any]:
    for field_name in ("operations", "mutate_operations"):
        if not hasattr(request_msg, field_name):
            continue
        try:
            return list(getattr(request_msg, field_name))
        except Exception:
            continue
    return []


def _unwrap_operation_dict(op: Any) -> dict[str, Any] | None:
    if not isinstance(op, dict):
        return None
    if any(key in op for key in ("create", "update", "remove", "update_mask")):
        return op
    for value in op.values():
        if isinstance(value, dict) and any(key in value for key in ("create", "update", "remove", "update_mask")):
            return value
    return None


def _request_operation_dicts(request_obj: Any) -> list[dict[str, Any]]:
    if not isinstance(request_obj, dict):
        return []
    for field_name in ("operations", "mutate_operations"):
        maybe_ops = request_obj.get(field_name)
        if not isinstance(maybe_ops, list):
            continue
        out: list[dict[str, Any]] = []
        for op in maybe_ops:
            unwrapped = _unwrap_operation_dict(op)
            if isinstance(unwrapped, dict):
                out.append(unwrapped)
        return out
    return []


def _write_plan_and_receipt_artifacts(*, ctx: dict[str, Any], plan: dict[str, Any] | None, receipt: dict[str, Any] | None) -> None:
    artifacts_dir = ctx.get("artifacts_dir")
    if artifacts_dir:
        ad = Path(artifacts_dir)
        if plan is not None:
            write_json_file(ad / "plan.json", plan)
        if receipt is not None:
            write_json_file(ad / "receipt.json", receipt)


def _artifact_before_dir(ctx: dict[str, Any]) -> Path:
    artifacts_dir = ctx.get("artifacts_dir")
    if not artifacts_dir:
        raise SafetyError(
            "Live writes require local run artifacts so before-state can be saved. "
            "Remove --no-artifacts or pass --artifacts-dir."
        )
    before_dir = Path(artifacts_dir) / "before"
    before_dir.mkdir(parents=True, exist_ok=True)
    return before_dir


def _before_state_targets(*, spec: RpcMethodSpec, request_obj: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(request_obj, dict):
        raise SafetyError("request payload could not be inspected safely")

    targets: list[dict[str, Any]] = []
    blockers: list[str] = []
    ops = _request_operation_dicts(request_obj)
    if not ops:
        raise SafetyError("no inspectable update operations were found")

    for index, op in enumerate(ops, start=1):
        if "create" in op:
            blockers.append(f"operation {index} is a create")
            continue
        if "remove" in op:
            remove_target = _remove_before_state_target(spec=spec, operation_index=index, op=op)
            if remove_target is None:
                blockers.append(f"operation {index} is an unsupported remove")
                continue
            targets.append(remove_target)
            continue
        update_obj = op.get("update")
        if not isinstance(update_obj, dict):
            blockers.append(f"operation {index} has no inspectable update payload")
            continue
        resource_name = str(update_obj.get("resource_name") or "").strip()
        if not resource_name:
            blockers.append(f"operation {index} update has no resource_name")
            continue
        field_paths = _parse_update_mask_paths(op.get("update_mask"))
        if not field_paths:
            blockers.append(f"operation {index} update has no readable update_mask")
            continue
        tables = _resource_tables_for_verification(spec=spec, resource_name=resource_name)
        if not tables:
            blockers.append(f"operation {index} target table could not be inferred")
            continue
        targets.append(
            {
                "operation_index": index,
                "resource_name": resource_name,
                "field_paths": field_paths,
                "tables": tables,
            }
        )

    if blockers:
        joined = "; ".join(blockers)
        raise SafetyError(joined)
    return targets


def _planned_before_state_status(*, spec: RpcMethodSpec, request_obj: dict[str, Any] | None) -> dict[str, Any]:
    try:
        targets = _before_state_targets(spec=spec, request_obj=request_obj)
    except SafetyError as e:
        return {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "reason": str(e),
            "approval_required": "--ack-no-snapshot",
        }
    return {
        "required": True,
        "supported": True,
        "status": "will_capture_on_apply",
        "target_count": len(targets),
        "reason": "A live before-state snapshot will be saved immediately before the approved Google Ads write.",
    }


def _no_snapshot_before_state(*, reason: str) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "reason": reason,
    }


def _remove_before_state_target(
    *,
    spec: RpcMethodSpec,
    operation_index: int,
    op: dict[str, Any],
) -> dict[str, Any] | None:
    resource_name = str(op.get("remove") or "").strip()
    if not resource_name:
        return None
    table = _resource_table_from_resource_name(resource_name)
    if (
        spec.service == "CampaignCriterionService"
        and spec.method == "MutateCampaignCriteria"
        and table == "campaign_criterion"
    ):
        return {
            "operation_index": operation_index,
            "resource_name": resource_name,
            "field_paths": list(_CAMPAIGN_CRITERION_AD_SCHEDULE_REMOVE_FIELDS),
            "tables": ["campaign_criterion"],
            "operation_type": "remove",
            "remove_kind": "campaign_criterion_ad_schedule",
        }
    return None


def _write_before_state_file(
    *,
    ctx: dict[str, Any],
    index: int,
    spec: RpcMethodSpec,
    resource_name: str,
    table: str,
    fields: list[str],
    query: str,
    rows: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", resource_name.strip("/").replace("/", "__"))[:140]
    path = _artifact_before_dir(ctx) / f"{index:02d}_{safe_name or 'resource'}.json"
    payload = {
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rpc": {"service": spec.service, "method": spec.method},
        "resource_name": resource_name,
        "table": table,
        "fields": fields,
        "query": query,
        "rows": rows,
        "row_count": len(rows),
    }
    if metadata:
        payload["metadata"] = metadata
    write_json_file(path, payload)
    out = {
        "path": str(path),
        "captured_at_utc": payload["captured_at_utc"],
        "resource_name": resource_name,
        "table": table,
        "fields": fields,
        "row_count": len(rows),
    }
    if metadata:
        out["metadata"] = metadata
    return out


def _validate_campaign_criterion_ad_schedule_row(row_dicts: list[dict[str, Any]], *, resource_name: str) -> None:
    if not row_dicts:
        raise SafetyError(f"Could not capture before-state for {resource_name}: target was not found.")
    row = row_dicts[0]
    criterion = row.get("campaign_criterion") if isinstance(row, dict) else None
    if not isinstance(criterion, dict):
        raise SafetyError(
            f"Could not capture before-state for {resource_name}: campaign_criterion row was not readable."
        )
    criterion_type = str(criterion.get("type") or criterion.get("type_") or "").strip().upper()
    ad_schedule = criterion.get("ad_schedule")
    if criterion_type and criterion_type != "AD_SCHEDULE":
        raise SafetyError(
            f"Refusing remove for {resource_name}: readable CampaignCriterion is {criterion_type}, not AD_SCHEDULE."
        )
    if not isinstance(ad_schedule, dict) or not ad_schedule:
        raise SafetyError(
            f"Refusing remove for {resource_name}: readable CampaignCriterion has no ad_schedule before-state."
        )


def _restore_recipes_from_before_state(saved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = []
    for item in saved:
        metadata = item.get("metadata")
        if not isinstance(metadata, dict):
            continue
        if metadata.get("remove_kind") != "campaign_criterion_ad_schedule":
            continue
        recipes.append(
            {
                "type": "campaign_criterion_ad_schedule_add_back",
                "source_before_state_path": item.get("path"),
                "resource_name_removed": item.get("resource_name"),
                "table": item.get("table"),
                "manual_recipe": [
                    "Open the before-state JSON file.",
                    "Read rows[0].campaign_criterion.campaign and rows[0].campaign_criterion.ad_schedule.",
                    "Create a CampaignCriterionOperation with create.campaign set to the saved campaign and create.ad_schedule set to the saved ad_schedule.",
                    "Run the normal dry-run, approval, apply, and verification flow before adding it back.",
                ],
            }
        )
    return recipes


def _capture_before_state_before_write(
    *,
    client: Any,
    customer_id: str,
    request_obj: dict[str, Any] | None,
    spec: RpcMethodSpec,
    timeout_s: float,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    targets = _before_state_targets(spec=spec, request_obj=request_obj)
    try:
        gas = client.get_service("GoogleAdsService", version=SUPPORTED_API_VERSION)
    except Exception as e:  # noqa: BLE001
        raise SafetyError(f"Could not load GoogleAdsService for before-state capture: {type(e).__name__}: {e}") from None

    saved: list[dict[str, Any]] = []
    for target in targets:
        rn = str(target["resource_name"])
        field_paths = [str(path) for path in target.get("field_paths", []) if str(path).strip()]
        tables = [str(table) for table in target.get("tables", []) if str(table).strip()]
        query_error: str | None = None
        for table in tables:
            fields = [f"{table}.resource_name"]
            for field_path in field_paths:
                field = f"{table}.{field_path}"
                if field not in fields:
                    fields.append(field)
            escaped = rn.replace("'", "\\'")
            query = (
                f"SELECT {', '.join(fields)} FROM {table} "
                f"WHERE {table}.resource_name = '{escaped}' LIMIT 1"
            )
            try:
                req_mod = __import__(
                    "google.ads.googleads.v22.services.types.google_ads_service",
                    fromlist=["SearchGoogleAdsRequest"],
                )
                SearchReq = getattr(req_mod, "SearchGoogleAdsRequest")
                req = SearchReq(customer_id=customer_id, query=query)
                rows = _call_with_retries(lambda: gas.search(request=req, timeout=timeout_s), ctx=ctx)
                row_dicts = [row if isinstance(row, dict) else protobuf_to_dict(row) for row in rows]
            except Exception as e:  # noqa: BLE001
                query_error = f"{type(e).__name__}: {e}"
                continue
            if not row_dicts:
                query_error = "target was not found by before-state GAQL query"
                continue
            target_metadata = {
                key: target[key]
                for key in ("operation_type", "remove_kind")
                if key in target
            }
            if target.get("remove_kind") == "campaign_criterion_ad_schedule":
                _validate_campaign_criterion_ad_schedule_row(row_dicts, resource_name=rn)
            saved.append(
                _write_before_state_file(
                    ctx=ctx,
                    index=len(saved) + 1,
                    spec=spec,
                    resource_name=rn,
                    table=table,
                    fields=fields,
                    query=query,
                    rows=row_dicts,
                    metadata=target_metadata or None,
                )
            )
            query_error = None
            break
        if query_error:
            raise SafetyError(f"Could not capture before-state for {rn}: {query_error}")

    return {"saved": saved, "restore_recipes": _restore_recipes_from_before_state(saved)}


def _cmd_write(
    *,
    spec: RpcMethodSpec,
    request_msg: Any,
    in_path: str,
    ctx: dict[str, Any],
    customer_id_override: str | None,
) -> int:
    cfg = ctx["cfg"]
    apply = bool(ctx.get("apply"))
    out = ctx["out"]
    include_rpc_payload = bool(ctx.get("include_rpc_payload"))
    ack_sensitive_payload = bool(ctx.get("ack_sensitive_payload"))
    if include_rpc_payload and not ack_sensitive_payload:
        raise SafetyError("Refusing to include raw RPC payloads without --ack-sensitive-payload.")

    # Structural info (no secrets).
    customer_id = str(getattr(request_msg, "customer_id", "") or "").strip()
    override_digits = "".join(ch for ch in (customer_id_override or "") if ch.isdigit())
    customer_for_gating = customer_id or override_digits or ""

    operations = _request_operations_from_message(request_msg)
    request_obj = protobuf_to_dict(request_msg)

    operations_count = len(operations) if operations else 1
    max_ops_req = int(getattr(cfg, "max_mutate_operations_per_request", 100) or 100)
    max_ops_run = int(getattr(cfg, "max_mutate_operations_per_run", 1000) or 1000)
    if operations_count > max_ops_req:
        raise SafetyError(f"Too many operations in one request: {operations_count} > {max_ops_req}")
    if operations_count > max_ops_run:
        raise SafetyError(f"Too many operations in one run: {operations_count} > {max_ops_run}")

    irreversible = any(_operation_is_remove(op) for op in operations)
    risk_level, risk_reasons = _classify_mutate_risk(
        spec=spec,
        irreversible=irreversible,
        request_obj=request_obj if isinstance(request_obj, dict) else None,
    )
    request_digest = _payload_digest(request_obj)
    req_summary = _request_summary(request_obj) if isinstance(request_obj, dict) else {"top_level_keys": []}

    plan_core = {
        "tool": "google-ads-api-tool",
        "api_version": SUPPORTED_API_VERSION,
        "kind": "google_ads_rpc_plan",
        "rpc": {"service": spec.service, "method": spec.method},
        "customer_id": customer_for_gating or None,
        "operations_count": operations_count,
        "irreversible": irreversible,
        "risk": {"level": risk_level, "reasons": risk_reasons},
        "request_digest": request_digest,
        "request_summary": req_summary,
        "plain_english_summary": _plain_english_write_summary(
            spec=spec,
            operations_count=operations_count,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
            irreversible=irreversible,
            request_summary=req_summary,
        ),
    }
    fingerprint = _plan_fingerprint(plan_core)
    plan = dict(plan_core)
    plan["plan_fingerprint"] = fingerprint
    plan["before_state"] = _planned_before_state_status(
        spec=spec,
        request_obj=request_obj if isinstance(request_obj, dict) else None,
    )
    if not bool(plan["before_state"].get("supported", True)):
        plan["notes"] = [
            "No saved before-state snapshot is available for this Google Ads write shape. Apply requires explicit --ack-no-snapshot approval.",
        ]
    if include_rpc_payload:
        plan["request"] = request_obj

    if not apply:
        plan_out = ctx.get("plan_out")
        if plan_out:
            write_json_file(Path(str(plan_out)), plan)
        _write_plan_and_receipt_artifacts(ctx=ctx, plan=plan, receipt=None)
        out.emit({"ok": True, "dry_run": True, "rpc": asdict(spec), "input_path": str(Path(in_path)), "plan": plan})
        return 0

    # Apply safety gates.
    if bool(getattr(cfg, "external_writes_disabled", False)):
        raise SafetyError("External writes are disabled by configuration (kill switch enabled).")
    if not customer_for_gating:
        raise SafetyError("Write methods require a customer id for allowlist gating (use --customer-id).")

    allowlist = set(getattr(cfg, "write_customer_id_allowlist", set()) or set())
    if customer_for_gating not in allowlist:
        raise SafetyError(f"Customer id is not allowlisted for writes: {customer_for_gating}")

    if irreversible and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("This plan includes remove operations; pass --ack-irreversible to proceed.")

    spend_impacting = any("spend-impacting" in r for r in risk_reasons)
    if spend_impacting and not bool(ctx.get("ack_spend")):
        raise SafetyError("This write is budget/billing/spend-impacting; pass --ack-spend to proceed.")

    high_risk = risk_level in {"high", "irreversible"}
    batch = operations_count > 1
    if (high_risk or batch or irreversible) and not bool(ctx.get("yes")):
        raise SafetyError("Missing --yes for risky/batch write operation.")

    plan_in_path = ctx.get("plan_in")
    if high_risk and not plan_in_path:
        raise SafetyError("High-risk write requires --plan-in (deterministic apply from reviewed plan).")
    if plan_in_path:
        planned = read_json_file(Path(str(plan_in_path)))
        if not isinstance(planned, dict):
            raise SafetyError("--plan-in must be a JSON object.")
        expected_fp = str(planned.get("plan_fingerprint") or "").strip()
        if not expected_fp or expected_fp != fingerprint:
            raise SafetyError("Plan drift detected: --plan-in fingerprint does not match computed plan.")

    # Save before-state when possible; otherwise continue only with explicit no-snapshot approval.
    _artifact_before_dir(ctx)
    before_state_probe = plan.get("before_state") if isinstance(plan.get("before_state"), dict) else {}
    no_snapshot_reason = str(before_state_probe.get("reason") or "").strip()
    if not bool(before_state_probe.get("supported", True)) and not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused: this Google Ads write has no saved before-state snapshot. Review the dry-run plan and pass "
            f"--ack-no-snapshot only when the approved change should continue without an automatic restore point. {no_snapshot_reason}".strip()
        )

    client = build_google_ads_client(cfg)
    if bool(before_state_probe.get("supported", True)):
        before_state = _capture_before_state_before_write(
            client=client,
            customer_id=customer_for_gating,
            request_obj=request_obj if isinstance(request_obj, dict) else None,
            spec=spec,
            timeout_s=float(ctx.get("timeout_s") or 30),
            ctx=ctx,
        )
    else:
        before_state = _no_snapshot_before_state(reason=no_snapshot_reason or "No supported before-state target was found.")
    plan["before_state"] = before_state

    svc = client.get_service(spec.service, version=SUPPORTED_API_VERSION)
    fn = getattr(svc, spec.python_method, None)
    if not callable(fn):
        raise ValidationError(f"Service method not found: {spec.service}.{spec.python_method}")

    timeout_s = float(ctx.get("timeout_s") or 30)
    resp = _call_with_retries(lambda: fn(request=request_msg, timeout=timeout_s), ctx=ctx)
    resp_dict = protobuf_to_dict(resp)
    response_digest = _payload_digest(resp_dict)
    resp_summary = {
        "resource_names": sorted(set(_extract_resource_names(resp_dict)))[:20],
    }

    verification = _best_effort_verify_after_write(
        client=client,
        customer_id=customer_for_gating,
        request_obj=request_obj,
        response_obj=resp_dict,
        spec=spec,
        timeout_s=timeout_s,
        ctx=ctx,
    )

    receipt = {
        "tool": "google-ads-api-tool",
        "api_version": SUPPORTED_API_VERSION,
        "kind": "google_ads_rpc_receipt",
        "rpc": {"service": spec.service, "method": spec.method},
        "input_path": str(Path(in_path)),
        "plan_fingerprint": fingerprint,
        "customer_id": customer_for_gating,
        "operations_count": operations_count,
        "irreversible": irreversible,
        "risk": {"level": risk_level, "reasons": risk_reasons},
        "before_state": before_state,
        "restore_recipes": before_state.get("restore_recipes") if isinstance(before_state, dict) else [],
        "verification": verification,
        "response_digest": response_digest,
        "response_summary": resp_summary,
        "plain_english_summary": _plain_english_write_summary(
            spec=spec,
            operations_count=operations_count,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
            irreversible=irreversible,
            request_summary=req_summary,
            verification=verification,
        ),
    }
    if isinstance(before_state, dict) and not bool(before_state.get("supported", True)):
        receipt["no_snapshot_approval"] = {
            "approved": bool(ctx.get("ack_no_snapshot")),
            "reason": "No saved before-state snapshot was available for this Google Ads write.",
        }
    if include_rpc_payload:
        receipt["response"] = resp_dict

    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        write_json_file(Path(str(receipt_out)), receipt)
    _write_plan_and_receipt_artifacts(ctx=ctx, plan=plan, receipt=receipt)
    out.emit({"ok": True, "dry_run": False, "rpc": asdict(spec), "before_state": before_state, "receipt": receipt})
    return 0


def _operation_is_remove(op: Any) -> bool:
    if hasattr(op, "remove"):
        try:
            if str(getattr(op, "remove") or "").strip():
                return True
        except Exception:
            pass
    pb = getattr(op, "_pb", None)
    if pb is None:
        return False
    try:
        for oneof in pb.DESCRIPTOR.oneofs:  # type: ignore[attr-defined]
            which = pb.WhichOneof(oneof.name)
            if not which:
                continue
            if which == "remove":
                return True
            nested = getattr(op, which, None)
            if nested is not None and nested is not op and _operation_is_remove(nested):
                return True
    except Exception:
        return False
    return False


def _risk_text_from_request_obj(request_obj: dict[str, Any] | None) -> str:
    if not isinstance(request_obj, dict):
        return ""

    parts: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(key, str) and key.strip():
                    parts.append(key.strip())
                if key == "resource_name" and isinstance(item, str) and item.strip():
                    parts.append(item.strip())
                visit(item)
            return
        if isinstance(value, list):
            for item in value:
                visit(item)

    visit(request_obj)
    return " ".join(parts)


def _classify_mutate_risk(
    *,
    spec: RpcMethodSpec,
    irreversible: bool,
    request_obj: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    tokens = f"{spec.service} {spec.method} {spec.request_type} {_risk_text_from_request_obj(request_obj)}".lower()
    reasons: list[str] = []
    level = "medium"
    if irreversible:
        level = "irreversible"
        reasons.append("includes remove operations")
    # Spend-impacting heuristics.
    spend_keywords = (
        "budget",
        "billing",
        "invoice",
        "payments",
        "accountbudget",
        "campaignbudget",
        "account_budget",
        "campaign_budget",
    )
    if any(k in tokens for k in spend_keywords):
        level = "high" if level != "irreversible" else level
        reasons.append("budget/billing/spend-impacting keywords detected")
    if not reasons:
        reasons.append("write method")
    return level, reasons


def _extract_resource_names(obj: Any) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "resource_name" and isinstance(v, str) and v.strip():
                out.append(v.strip())
            out.extend(_extract_resource_names(v))
    elif isinstance(obj, list):
        for it in obj:
            out.extend(_extract_resource_names(it))
    return out


def _resource_table_from_resource_name(resource_name: str) -> str | None:
    """
    Heuristic mapping from resource name path segment to GAQL resource table.

    Example: customers/123/campaignBudgets/456 -> campaign_budget
    """
    s = (resource_name or "").strip()
    parts = [p for p in s.split("/") if p]
    if len(parts) < 3 or parts[0] != "customers":
        return None
    return _identifier_to_table_name(parts[2])


_WRITE_VERB_PREFIXES: tuple[str, ...] = (
    "Mutate",
    "Create",
    "Append",
    "Apply",
    "Cancel",
    "Configure",
    "Dismiss",
    "Enable",
    "End",
    "Graduate",
    "Move",
    "Promote",
    "Provide",
    "Regenerate",
    "Remove",
    "Run",
    "Schedule",
    "Start",
    "Update",
    "Upload",
)


def _identifier_to_table_name(identifier: str) -> str | None:
    """Convert API identifiers into a GAQL table name candidate."""

    s = (identifier or "").strip()
    if not s:
        return None

    # Strip common RPC naming wrappers.
    for prefix in _WRITE_VERB_PREFIXES:
        if s.startswith(prefix) and len(s) > len(prefix):
            s = s[len(prefix) :]
            break

    if s.endswith("Service"):
        s = s[: -len("Service")]

    if s.endswith("Criteria") and len(s) > len("Criteria"):
        s = f"{s[:-len('Criteria')]}Criterion"

    table = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
    if not table:
        return None

    # Lower camel collection fragments usually need simple singularization.
    if table.endswith("_views"):
        table = f"{table[:-1]}"
    if table.endswith("ies") and len(table) > 3:
        table = f"{table[:-3]}y"
    elif table.endswith("s") and len(table) > 1:
        table = table[:-1]
    return table


def _snake_case_identifier(identifier: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", str(identifier or "").strip()).lower()


def _normalize_field_path(path: str) -> str:
    parts = [p.strip() for p in str(path or "").split(".") if p.strip()]
    return ".".join(_snake_case_identifier(part) for part in parts)


def _resource_tables_for_verification(*, spec: RpcMethodSpec, resource_name: str) -> list[str]:
    tables: list[str] = []
    for source in (spec.method, spec.service):
        candidate = _identifier_to_table_name(source)
        if candidate:
            tables.append(candidate)

    table = _resource_table_from_resource_name(resource_name)
    if table:
        tables.append(table)

    seen: set[str] = set()
    deduped: list[str] = []
    for table_name in tables:
        if table_name in seen:
            continue
        seen.add(table_name)
        deduped.append(table_name)
    return deduped


def _extract_request_remove_resource_names(request_obj: Any) -> set[str]:
    removes: set[str] = set()
    for op in _request_operation_dicts(request_obj):
        rm = op.get("remove")
        if isinstance(rm, str):
            rm = rm.strip()
            if rm:
                removes.add(rm)
    return removes


def _parse_update_mask_paths(update_mask_obj: Any) -> list[str]:
    raw_paths: list[str] = []
    if isinstance(update_mask_obj, str):
        raw_paths = [p.strip() for p in update_mask_obj.split(",") if p.strip()]
    elif isinstance(update_mask_obj, dict):
        maybe_paths = update_mask_obj.get("paths")
        if isinstance(maybe_paths, list):
            raw_paths = [str(p).strip() for p in maybe_paths if str(p).strip()]
    elif isinstance(update_mask_obj, list):
        raw_paths = [str(p).strip() for p in update_mask_obj if str(p).strip()]
    return [_normalize_field_path(path) for path in raw_paths if path]


def _value_at_path(obj: Any, path: str) -> tuple[bool, Any]:
    current = obj
    for part in [p for p in str(path or "").split(".") if p]:
        if isinstance(current, dict):
            if part not in current:
                return False, None
            current = current[part]
            continue
        if isinstance(current, list):
            try:
                idx = int(part)
            except Exception:
                return False, None
            if idx < 0 or idx >= len(current):
                return False, None
            current = current[idx]
            continue
        return False, None
    return True, current


def _normalize_compare_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize_compare_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_compare_value(v) for v in value]
    if isinstance(value, str):
        s = value.strip()
        if _INT_STRING_RE.fullmatch(s):
            try:
                return int(s)
            except Exception:
                return value
        if _FLOAT_STRING_RE.fullmatch(s):
            try:
                return float(s)
            except Exception:
                return value
        return value
    return value


def _default_value_for(expected: Any) -> Any:
    if isinstance(expected, bool):
        return False
    if isinstance(expected, int):
        return 0
    if isinstance(expected, float):
        return 0.0
    if isinstance(expected, str):
        return ""
    if isinstance(expected, list):
        return []
    if isinstance(expected, dict):
        return {}
    return None


def _is_default_like(value: Any) -> bool:
    return _normalize_compare_value(value) == _normalize_compare_value(_default_value_for(value))


def _extract_request_update_expectations(
    request_obj: dict[str, Any] | None,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    expectations: dict[str, dict[str, Any]] = {}
    skipped: list[dict[str, Any]] = []
    for op in _request_operation_dicts(request_obj):
        update_obj = op.get("update")
        if not isinstance(update_obj, dict):
            continue
        resource_name = str(update_obj.get("resource_name") or "").strip()
        if not resource_name:
            continue

        field_expectations = expectations.setdefault(resource_name, {})
        for field_path in _parse_update_mask_paths(op.get("update_mask")):
            found, expected = _value_at_path(update_obj, field_path)
            if not found:
                skipped.append(
                    {
                        "resource_name": resource_name,
                        "field_path": field_path,
                        "reason": "Field from update_mask was not present in update payload",
                    }
                )
                continue
            field_expectations[field_path] = expected
    return expectations, skipped


def _verification_targets(
    *,
    request_obj: dict[str, Any] | None,
    response_obj: dict[str, Any],
    update_expectations: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    response_names = sorted(set(_extract_resource_names(response_obj)))
    request_names = _extract_request_remove_resource_names(request_obj)
    expected_updates = update_expectations or {}

    names_set: set[str] = set(response_names)
    names_set.update(request_names)
    names_set.update(expected_updates.keys())

    targets: list[dict[str, Any]] = []
    for rn in sorted(names_set):
        should_exist = rn not in request_names
        targets.append(
            {
                "resource_name": rn,
                "should_exist": should_exist,
                "field_expectations": expected_updates.get(rn, {}) if should_exist else {},
            }
        )
    return targets


def _lookup_row_value(row_obj: dict[str, Any], *, table: str, field_path: str, expected: Any) -> tuple[bool, Any]:
    found, value = _value_at_path(row_obj, f"{table}.{field_path}")
    if found:
        return True, value
    found, value = _value_at_path(row_obj, field_path)
    if found:
        return True, value
    if _is_default_like(expected):
        return True, _default_value_for(expected)
    return False, None


def _best_effort_verify_after_write(
    *,
    client: Any,
    customer_id: str,
    request_obj: dict[str, Any] | None,
    response_obj: dict[str, Any],
    spec: RpcMethodSpec,
    timeout_s: float,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    update_expectations, skipped_fields = _extract_request_update_expectations(request_obj)
    targets = _verification_targets(
        request_obj=request_obj,
        response_obj=response_obj,
        update_expectations=update_expectations,
    )
    if not targets:
        return {
            "attempted": True,
            "type": "gaql_readback",
            "ok": True,
            "fully_verified": True,
            "resource_names": [],
            "verified_resources": 0,
            "verified_fields": 0,
            "skipped_fields": skipped_fields,
        }

    max_verify = 20
    targets = targets[:max_verify]

    try:
        gas = client.get_service("GoogleAdsService", version=SUPPORTED_API_VERSION)
    except Exception:
        return {
            "attempted": False,
            "type": "gaql_readback",
            "ok": False,
            "fully_verified": False,
            "reason": "Failed to load GoogleAdsService for read-back verification.",
            "resource_names": [target["resource_name"] for target in targets],
            "verified_fields": 0,
            "skipped_fields": skipped_fields,
        }

    verified = 0
    verified_fields = 0
    failures: list[dict[str, Any]] = []
    for target in targets:
        rn = str(target.get("resource_name") or "").strip()
        should_exist = bool(target.get("should_exist"))
        field_expectations = target.get("field_expectations")
        if not isinstance(field_expectations, dict):
            field_expectations = {}
        tables = _resource_tables_for_verification(spec=spec, resource_name=rn)
        if not tables:
            failures.append(
                {
                    "resource_name": rn,
                    "expected": "present" if should_exist else "absent",
                    "reason": "Could not infer GAQL table for resource name",
                }
            )
            continue

        rows_by_table: list[bool] = []
        query_succeeded = False
        query_error: str | None = None
        row_for_compare: dict[str, Any] | None = None
        selected_table: str | None = None
        for table in tables:
            escaped = rn.replace("'", "\\'")
            select_fields = [f"{table}.resource_name"]
            for field_path in sorted(field_expectations.keys()):
                select_field = f"{table}.{field_path}"
                if select_field not in select_fields:
                    select_fields.append(select_field)
            query = (
                f"SELECT {', '.join(select_fields)} FROM {table} "
                f"WHERE {table}.resource_name = '{escaped}' LIMIT 1"
            )
            try:
                req_mod = __import__(
                    "google.ads.googleads.v22.services.types.google_ads_service",
                    fromlist=["SearchGoogleAdsRequest"],
                )
                SearchReq = getattr(req_mod, "SearchGoogleAdsRequest")
                req = SearchReq(customer_id=customer_id, query=query)
                rows = _call_with_retries(
                    lambda: gas.search(request=req, timeout=timeout_s),
                    ctx=ctx,
                )
                query_succeeded = True
                has_row = False
                for row in rows:
                    has_row = True
                    row_for_compare = row if isinstance(row, dict) else protobuf_to_dict(row)
                    selected_table = table
                    break
                rows_by_table.append(has_row)
                if should_exist and has_row:
                    break
                if not should_exist and has_row:
                    break
            except Exception as e:  # noqa: BLE001
                query_error = f"{type(e).__name__}: {e}"

        if should_exist:
            if any(rows_by_table):
                field_failures: list[dict[str, Any]] = []
                if row_for_compare is None:
                    field_failures.append(
                        {
                            "resource_name": rn,
                            "expected": "present",
                            "reason": "Resource was found but no readable row payload was available",
                        }
                    )
                else:
                    for field_path, expected in sorted(field_expectations.items()):
                        found, actual = _lookup_row_value(
                            row_for_compare,
                            table=selected_table or tables[0],
                            field_path=field_path,
                            expected=expected,
                        )
                        if not found:
                            skipped_fields.append(
                                {
                                    "resource_name": rn,
                                    "field_path": field_path,
                                    "reason": "Field was not returned by GAQL read-back",
                                }
                            )
                            continue
                        if _normalize_compare_value(actual) != _normalize_compare_value(expected):
                            field_failures.append(
                                {
                                    "resource_name": rn,
                                    "field_path": field_path,
                                    "expected_value": expected,
                                    "actual_value": actual,
                                    "reason": "Field value did not match requested update",
                                }
                            )
                        else:
                            verified_fields += 1
                if field_failures:
                    failures.extend(field_failures)
                else:
                    verified += 1
            elif not query_succeeded and query_error is not None:
                failures.append(
                    {
                        "resource_name": rn,
                        "expected": "present",
                        "reason": query_error,
                    }
                )
            else:
                failures.append(
                    {
                        "resource_name": rn,
                        "expected": "present",
                        "reason": "Not found via GAQL read-back",
                    }
                )
        else:
            if any(rows_by_table):
                failures.append(
                    {
                        "resource_name": rn,
                        "expected": "absent",
                        "reason": "Resource still present via GAQL read-back",
                    }
                )
            elif not query_succeeded and query_error is not None:
                failures.append(
                    {
                        "resource_name": rn,
                        "expected": "absent",
                        "reason": "No successful GAQL query for resource after remove action",
                        "detail": query_error,
                    }
                )
            else:
                verified += 1

    ok = len(failures) == 0
    return {
        "attempted": True,
        "type": "gaql_readback",
        "ok": ok,
        "fully_verified": ok and not skipped_fields,
        "resource_names": [target["resource_name"] for target in targets],
        "verified_resources": verified,
        "verified_fields": verified_fields,
        "skipped_fields": skipped_fields,
        "failed_resources": failures,
    }
