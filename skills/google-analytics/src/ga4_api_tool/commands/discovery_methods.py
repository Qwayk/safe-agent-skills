from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from dataclasses import dataclass
from typing import Any

from ..errors import SafetyError, ValidationError
from ..ga4_api import Ga4ApiClient
from ..json_files import read_json_file, write_json_file
from ..method_inventory import SnapshotSpec, methods_for_snapshot, snapshots, to_kebab
from ..plan import PreparedRequest, build_no_recovery_contract, build_plan, env_fingerprint, request_fingerprint, validate_plan_for_apply
from ..redaction import sanitize


_BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this GA4 write has no saved before-state snapshot. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


@dataclass(frozen=True)
class OperationKey:
    service: str
    version: str
    method_id: str


def _safe_flag_name(param_name: str) -> str | None:
    # Argparse flags must be reasonable; skip any weird discovery params.
    if not param_name:
        return None
    if any(ch in param_name for ch in ("$", ".", ":")):
        return None
    # Convert camelCase to kebab-case, but keep underscores as dashes too.
    out: list[str] = []
    for ch in param_name:
        if ch == "_":
            out.append("-")
            continue
        if ch.isupper():
            out.append("-")
            out.append(ch.lower())
            continue
        out.append(ch)
    flag = "".join(out).strip("-")
    if not flag:
        return None
    return f"--{flag}"

_PATH_VAR_RE = re.compile(r"{([^}]+)}")


def _build_path_from_args(path_template: str, args: argparse.Namespace) -> str:
    path = path_template
    for raw in _PATH_VAR_RE.findall(path_template):
        is_reserved = raw.startswith("+")
        name = raw.lstrip("+")
        value = getattr(args, name, None)
        if value is None or str(value).strip() == "":
            raise ValidationError(f"Missing required path parameter: {name}")
        quoted = urllib.parse.quote(str(value), safe="/" if is_reserved else "")
        path = path.replace("{" + raw + "}", quoted)
    return path


def _parse_body(args: argparse.Namespace) -> dict[str, Any] | None:
    body_json = getattr(args, "body_json", None)
    body_file = getattr(args, "body_file", None)
    if body_json and body_file:
        raise ValidationError("Use only one of: --body-json or --body-file")
    if body_file:
        obj = read_json_file(body_file)
        if not isinstance(obj, dict):
            raise ValidationError("Request body must be a JSON object")
        return obj
    if body_json:
        try:
            obj = json.loads(str(body_json))
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Invalid --body-json: {type(e).__name__}: {e}") from None
        if not isinstance(obj, dict):
            raise ValidationError("Request body must be a JSON object")
        return obj
    return None


def _system_query_from_args(args: argparse.Namespace) -> dict[str, Any]:
    q: dict[str, Any] = {}
    fields = getattr(args, "fields", None)
    quota_user = getattr(args, "quota_user", None)
    if fields:
        q["fields"] = fields
    if quota_user:
        q["quotaUser"] = quota_user
    return q


def _risk_level_for_method(*, snapshot: SnapshotSpec, method_id: str, http_method: str, method_name: str) -> tuple[str, list[str]]:
    hm = http_method.upper()

    if hm == "GET":
        return "low", ["http:get"]
    if hm == "DELETE":
        return "irreversible", ["http:delete"]

    # Read-like POSTs (explicit allowlist)
    if snapshot.service_token == "data":
        if method_name in {
            "runReport",
            "runPivotReport",
            "runRealtimeReport",
            "batchRunReports",
            "batchRunPivotReports",
            "checkCompatibility",
            "runFunnelReport",
            "query",  # audienceExports.query
        }:
            return "low", ["read_like_post:data_reports"]
    if snapshot.service_token == "admin":
        if method_name in {"runAccessReport", "searchChangeHistoryEvents"}:
            return "low", ["read_like_post:admin_reports"]

    # High-risk: batch writes and permission-ish surfaces
    if method_name.lower().startswith("batch") and method_name not in {"batchRunReports", "batchRunPivotReports"}:
        return "high", ["batch_write"]
    if ".accessBindings." in method_id:
        return "high", ["access_control_change"]
    if method_name in {"provisionAccountTicket"}:
        return "high", ["account_provisioning"]

    # Default write level
    if hm in {"POST", "PUT", "PATCH"}:
        return "medium", [f"http:{hm.lower()}"]

    return "medium", [f"http:{hm.lower()}"]


def classify_risk(*, snapshot: SnapshotSpec, method_id: str, http_method: str, method_name: str) -> dict[str, Any]:
    level, reasons = _risk_level_for_method(
        snapshot=snapshot, method_id=method_id, http_method=http_method, method_name=method_name
    )
    return {"level": level, "reasons": reasons}


def _enforce_apply_gates(*, risk: dict[str, Any], ctx: dict[str, Any]) -> None:
    level = str(risk.get("level") or "")
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack = bool(ctx.get("ack_irreversible"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None

    if not apply:
        return

    if level in {"low", "medium"}:
        return

    if level == "high":
        if not yes:
            raise SafetyError("Refused: high-risk operation requires --yes")
        if not plan_in:
            raise SafetyError("Refused: high-risk operation requires --plan-in (reviewed plan)")
        return

    if level == "irreversible":
        if not yes:
            raise SafetyError("Refused: irreversible operation requires --yes")
        if not ack:
            raise SafetyError("Refused: irreversible operation requires --ack-irreversible")
        if not plan_in:
            raise SafetyError("Refused: irreversible operation requires --plan-in (reviewed plan)")
        return

    # Safe default: unknown risk requires maximum gating.
    raise SafetyError("Refused: unknown risk level; cannot apply safely")


def cmd_discovery_method(args: argparse.Namespace, ctx: dict) -> int:
    op: OperationKey | None = getattr(args, "ga4_operation_key", None)
    snap: SnapshotSpec | None = getattr(args, "ga4_snapshot_spec", None)
    method = getattr(args, "ga4_method_spec", None)
    if not op or not snap or not method:
        ctx["out"].emit({"ok": False, "error": "Missing discovery command metadata", "error_type": "InternalError"})
        return 1

    cfg = ctx["cfg"]
    env_fp = env_fingerprint(cfg)

    # Build request components
    path = _build_path_from_args(method.path, args)
    query: dict[str, Any] = {}
    for p in method.parameters:
        val = getattr(args, p.name, None)
        if val is None:
            continue
        if p.location == "query":
            query[p.name] = val
    query.update(_system_query_from_args(args))
    body = _parse_body(args) if method.has_request_body else None

    base_url = cfg.admin_base_url if op.service == "admin" else cfg.data_base_url
    full_url = base_url.rstrip("/") + "/" + path.lstrip("/")

    req = PreparedRequest(method=method.http_method.upper(), url=full_url, query=query, body=body)
    req_fp = request_fingerprint(req)
    operation_obj = {"service": op.service, "version": op.version, "method_id": op.method_id}
    risk = classify_risk(
        snapshot=snap,
        method_id=op.method_id,
        http_method=method.http_method,
        method_name=method.method_name,
    )

    level = str(risk.get("level") or "")
    is_write_like = level != "low"

    # Read-like operations execute by default. Write-like operations are dry-run by default.
    if not is_write_like:
        client = ctx.get("api_client")
        if client is None:
            client = Ga4ApiClient(
                cfg=cfg,
                timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
                verbose=bool(ctx.get("verbose")),
                user_agent=f"ga4-api-tool/{ctx.get('tool_version') or '0.0.0'}",
            )
        res = client.request(
            service=op.service,
            method=req.method,
            path=path,
            query=query,
            body=body,
            retries=2,
        )
        out = sanitize(
            {
                "ok": bool(res.status and int(res.status) < 400),
                "dry_run": False,
                "operation": operation_obj,
                "risk": risk,
                "request": {"method": req.method, "url": res.url, "query": query, "body": body},
                "response": {"status": res.status, "url": res.url, "json": res.json, "text": res.text},
            }
        )
        ctx["audit"].write("ga4.read", {"operation": operation_obj, "risk": risk, "status": res.status})
        ctx["out"].emit(out)
        return 0 if out.get("ok") else 1

    # Apply gates (before reading plan-in; failures must not hit network).
    _enforce_apply_gates(risk=risk, ctx=ctx)

    apply = bool(ctx.get("apply"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    if apply and plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        validate_plan_for_apply(
            plan_obj,
            expected_env_fingerprint=env_fp,
            expected_request_fingerprint=req_fp,
            expected_operation=operation_obj,
        )
    plan = build_plan(ctx=ctx, operation=operation_obj, risk=risk, req=req, env_fp=env_fp, req_fp=req_fp)
    if is_write_like:
        plan["recovery"] = build_no_recovery_contract()

    if apply and not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(_BEFORE_STATE_REFUSAL_REASON)

    plan_path = write_json_file(str(ctx.get("plan_out") or ""), plan) if ctx.get("plan_out") else None

    if not apply:
        ctx["audit"].write("ga4.plan", {"operation": operation_obj, "risk": risk, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = ctx.get("api_client")
    if client is None:
        client = Ga4ApiClient(
            cfg=cfg,
            timeout_s=float(ctx.get("timeout_s") or cfg.timeout_s),
            verbose=bool(ctx.get("verbose")),
            user_agent=f"ga4-api-tool/{ctx.get('tool_version') or '0.0.0'}",
        )
    res = client.request(
        service=op.service,
        method=req.method,
        path=path,
        query=query,
        body=body,
        retries=2,
    )
    receipt = sanitize(
        {
            "tool": ctx.get("tool") or "ga4-api-tool",
            "version": ctx.get("tool_version") or None,
            "operation": operation_obj,
            "risk": risk,
            "request": {"method": req.method, "url": res.url, "query": query, "body": body},
            "before_state": plan.get("before_state"),
            "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
            "recovery": plan.get("recovery"),
            "response": {"status": res.status, "url": res.url, "json": res.json, "text": res.text},
            "verification": {"type": "provider_response", "ok": bool(res.status and int(res.status) < 400)},
        }
    )
    receipt_path = write_json_file(str(ctx.get("receipt_out") or ""), receipt) if ctx.get("receipt_out") else None
    out = {"ok": bool(res.status and int(res.status) < 400), "dry_run": False, "plan": plan, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("ga4.apply", {"operation": operation_obj, "risk": risk, "status": res.status, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0 if out.get("ok") else 1


def register_discovery_commands(sub: argparse._SubParsersAction) -> None:
    """
    Register explicit CLI commands for every method in the vendored discovery snapshots.

    Shape:
      ga4-api-tool admin v1alpha <resource chain> <method>
      ga4-api-tool data v1beta <resource chain> <method>
      ga4-api-tool data v1alpha <resource chain> <method>
    """

    service_parsers: dict[str, argparse.ArgumentParser] = {}
    version_parsers: dict[tuple[str, str], argparse.ArgumentParser] = {}
    chain_parsers: dict[tuple[str, str, tuple[str, ...]], argparse.ArgumentParser] = {}

    def get_service_parser(service: str) -> argparse.ArgumentParser:
        if service not in service_parsers:
            p = sub.add_parser(service, help=f"{service} API commands (from discovery)")
            service_parsers[service] = p
            version_sub = p.add_subparsers(dest=f"{service}_version", required=True, parser_class=type(p))
            p.set_defaults(_ga4_version_subparsers=version_sub)
        return service_parsers[service]

    def get_version_parser(service: str, version: str) -> argparse.ArgumentParser:
        key = (service, version)
        if key in version_parsers:
            return version_parsers[key]
        sp = get_service_parser(service)
        version_sub: argparse._SubParsersAction = getattr(sp, "_defaults", {}).get("_ga4_version_subparsers")  # type: ignore[assignment]
        p = version_sub.add_parser(version, help=f"{service} {version} (vendored discovery)")  # type: ignore[arg-type]
        version_parsers[key] = p
        next_sub = p.add_subparsers(dest=f"{service}_{version}_resource", required=True, parser_class=type(p))
        p.set_defaults(_ga4_resource_subparsers=next_sub)
        return p

    def get_chain_parser(service: str, version: str, chain: tuple[str, ...]) -> argparse.ArgumentParser:
        key = (service, version, chain)
        if key in chain_parsers:
            return chain_parsers[key]

        # Build incremental chain: (a) then (a,b) then (a,b,c) ...
        vparser = get_version_parser(service, version)
        current = vparser
        for i in range(len(chain)):
            partial = chain[: i + 1]
            partial_key = (service, version, partial)
            if partial_key in chain_parsers:
                current = chain_parsers[partial_key]
                continue

            subparsers: argparse._SubParsersAction = getattr(current, "_defaults", {}).get("_ga4_resource_subparsers")  # type: ignore[assignment]
            p = subparsers.add_parser(partial[-1], help=f"Resource: {' '.join(partial)}")  # type: ignore[arg-type]
            next_sub = p.add_subparsers(dest=f"{service}_{version}_{'_'.join(partial)}", required=True, parser_class=type(p))
            p.set_defaults(_ga4_resource_subparsers=next_sub)
            chain_parsers[partial_key] = p
            current = p

        return chain_parsers[key]

    for snap in snapshots():
        for m in methods_for_snapshot(snap):
            op_key = OperationKey(
                service=snap.service_token,
                version=snap.version_token,
                method_id=m.method_id,
            )

            chain_tokens = tuple(to_kebab(x) for x in m.resource_chain)
            method_token = to_kebab(m.method_name)
            parent = get_chain_parser(snap.service_token, snap.version_token, chain_tokens)
            subparsers: argparse._SubParsersAction = getattr(parent, "_defaults", {}).get("_ga4_resource_subparsers")  # type: ignore[assignment]
            method_parser = subparsers.add_parser(method_token, help=f"{m.http_method} {m.path}")  # type: ignore[arg-type]

            # Discovery parameters
            for p in m.parameters:
                flag = _safe_flag_name(p.name)
                if not flag:
                    continue
                kwargs: dict = {"required": bool(p.required and p.location == "path")}
                if p.repeated:
                    kwargs["action"] = "append"
                method_parser.add_argument(flag, dest=p.name, **kwargs)

            if m.has_request_body:
                g = method_parser.add_mutually_exclusive_group(required=False)
                g.add_argument("--body-json", default=None, help="Request body as JSON string")
                g.add_argument("--body-file", default=None, help="Request body JSON file path")

            method_parser.set_defaults(
                func=cmd_discovery_method,
                write_capable=(classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name).get("level") != "low"),
                ga4_operation_key=op_key,
                ga4_snapshot_spec=snap,
                ga4_method_spec=m,
            )
