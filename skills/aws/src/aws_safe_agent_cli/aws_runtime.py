from __future__ import annotations

import argparse
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import boto3
import botocore

from . import __version__
from .allowlists import AllowLists
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import inventory as inventory_cmd
from .commands import onboarding as onboarding_cmd
from .config import Config, load_config
from .errors import SafetyError, ToolError, ValidationError
from .generated_registry import GeneratedRegistry, load_generated_registry
from .json_files import read_json_file, write_json_file
from .output import Output
from .project_config import load_project_config
from .model_loader import load_operation_model
from .redaction import REDACTED, redact_obj, redact_text
from .runs import (
    RunContext,
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
)
from .sts_identity import fetch_caller_identity
from .validation import load_input_json, validate_operation_input


_READ_PREFIXES = (
    "batchget",
    "check",
    "describe",
    "get",
    "list",
    "lookup",
    "preview",
    "search",
    "validate",
)

_NO_SNAPSHOT_PREFIXES = (
    "cancel",
    "disable",
    "detach",
    "revoke",
    "stop",
)

_IRREVERSIBLE_PREFIXES = (
    "delete",
    "remove",
    "terminate",
)

_WRITE_PREFIXES = (
    "accept",
    "add",
    "associate",
    "attach",
    "begin",
    "build",
    "copy",
    "create",
    "enable",
    "import",
    "install",
    "modify",
    "patch",
    "post",
    "publish",
    "put",
    "register",
    "reject",
    "restore",
    "resume",
    "run",
    "send",
    "set",
    "start",
    "submit",
    "update",
)

_SECURITY_IDENTITY_SERVICES = {
    "account",
    "acm",
    "acm-pca",
    "cognito-idp",
    "cloudtrail",
    "iam",
    "identitystore",
    "kms",
    "organizations",
    "rolesanywhere",
    "secretsmanager",
    "sso-admin",
    "sts",
    "verifiedpermissions",
}

_SECRET_BEARING_SERVICES = {
    "acm",
    "acm-pca",
    "cloudhsm",
    "cloudhsmv2",
    "kms",
    "payment-cryptography",
    "payment-cryptography-data",
    "secretsmanager",
    "ssm",
}

_SPEND_QUOTA_SERVICES = {
    "apprunner",
    "athena",
    "autoscaling",
    "batch",
    "bedrock",
    "budgets",
    "cloudformation",
    "dynamodb",
    "ec2",
    "ecs",
    "eks",
    "elasticache",
    "elasticbeanstalk",
    "emr",
    "fsx",
    "glue",
    "lambda",
    "lightsail",
    "opensearch",
    "rds",
    "redshift",
    "sagemaker",
    "service-quotas",
    "workspaces",
}

_MESSAGING_SERVICES = {
    "chime-sdk-messaging",
    "connectcampaigns",
    "connectcampaignsv2",
    "mailmanager",
    "pinpoint",
    "pinpoint-email",
    "pinpoint-sms-voice",
    "pinpoint-sms-voice-v2",
    "ses",
    "sesv2",
    "sns",
    "socialmessaging",
    "sqs",
}

_PUBLIC_EXPOSURE_SERVICES = {
    "apigateway",
    "apigatewayv2",
    "cloudfront",
    "ec2",
    "elb",
    "elbv2",
    "globalaccelerator",
    "route53",
    "route53domains",
    "route53resolver",
    "s3",
    "s3control",
    "waf",
    "waf-regional",
    "wafv2",
}

_DATA_MOVEMENT_SERVICES = {
    "backup",
    "dataexchange",
    "datasync",
    "dms",
    "ebs",
    "firehose",
    "glacier",
    "kinesis",
    "migrationhuborchestrator",
    "mgn",
    "s3",
    "s3control",
    "snowball",
    "storagegateway",
    "transfer",
}

_SECURITY_OPERATION_TOKENS = (
    "accesskey",
    "account",
    "admin",
    "authorization",
    "certificate",
    "credential",
    "group",
    "identity",
    "key",
    "login",
    "permission",
    "policy",
    "role",
    "user",
    "delegatedadmin",
)

_SECRET_OPERATION_TOKENS = (
    "credential",
    "keypair",
    "password",
    "privatekey",
    "secret",
    "token",
)

_SPEND_OPERATION_TOKENS = (
    "allocate",
    "capacity",
    "cluster",
    "domain",
    "instance",
    "job",
    "purchase",
    "reserve",
    "run",
    "start",
)

_MESSAGING_OPERATION_TOKENS = (
    "campaign",
    "email",
    "message",
    "publish",
    "send",
    "sms",
)

_PUBLIC_EXPOSURE_OPERATION_TOKENS = (
    "acl",
    "cors",
    "distribution",
    "domain",
    "hostedzone",
    "internetgateway",
    "permission",
    "policy",
    "public",
    "route",
)

_DATA_MOVEMENT_OPERATION_TOKENS = (
    "copy",
    "download",
    "export",
    "import",
    "migration",
    "putobject",
    "replicate",
    "restore",
    "starttaskexecution",
    "transfer",
    "upload",
)


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _operation_snake_name(operation_name: str) -> str:
    out = []
    for idx, ch in enumerate(operation_name):
        if ch.isupper() and idx:
            prev = operation_name[idx - 1]
            if prev.islower() or (prev.isupper() and idx + 1 < len(operation_name) and operation_name[idx + 1].islower()):
                out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _has_any_token(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def _operation_policy(service_name: str, operation_name: str) -> dict[str, Any]:
    service = service_name.lower()
    lower = operation_name.lower()
    if lower.startswith(_READ_PREFIXES):
        mode = "read"
    elif lower.startswith(_IRREVERSIBLE_PREFIXES):
        mode = "irreversible"
    elif lower.startswith(_NO_SNAPSHOT_PREFIXES):
        mode = "high_no_snapshot"
    elif lower.startswith(_WRITE_PREFIXES):
        mode = "remote_write"
    else:
        mode = "unknown_mutating"
    is_write = mode != "read"
    categories: set[str] = set()
    reasons: list[str] = []

    if service in _SECURITY_IDENTITY_SERVICES or _has_any_token(lower, _SECURITY_OPERATION_TOKENS):
        categories.add("security_identity")
        reasons.append("can affect AWS identity, access, permissions, or trust")
    if service in _SECRET_BEARING_SERVICES or _has_any_token(lower, _SECRET_OPERATION_TOKENS):
        categories.add("secret")
        reasons.append("can expose or change credentials, keys, certificates, or secret material")
    if is_write and (service in _SPEND_QUOTA_SERVICES or _has_any_token(lower, _SPEND_OPERATION_TOKENS)):
        categories.add("spend_quota")
        reasons.append("can create, start, reserve, or change billable capacity or service quota state")
    if is_write and (service in _MESSAGING_SERVICES or _has_any_token(lower, _MESSAGING_OPERATION_TOKENS)):
        categories.add("messaging")
        reasons.append("can send, publish, queue, or trigger customer-visible messages")
    if is_write and (service in _PUBLIC_EXPOSURE_SERVICES or _has_any_token(lower, _PUBLIC_EXPOSURE_OPERATION_TOKENS)):
        categories.add("public_exposure")
        reasons.append("can affect public access, routing, network exposure, or resource policy")
    if is_write and (service in _DATA_MOVEMENT_SERVICES or _has_any_token(lower, _DATA_MOVEMENT_OPERATION_TOKENS)):
        categories.add("data_movement")
        reasons.append("can move, copy, import, export, restore, or replicate data")
    if is_write:
        categories.add("no_snapshot")
        reasons.append("the generic AWS model path does not have operation-specific before-state capture")
    if mode == "irreversible":
        categories.add("irreversible")
        reasons.append("delete/remove/terminate style action can be hard or impossible to undo")
    if mode == "unknown_mutating":
        categories.add("unknown_mutating")
        reasons.append("operation name is not safely classed as a read or known write family")

    high_risk = bool(categories - {"no_snapshot"})
    return {
        "mode": mode,
        "risk_categories": sorted(categories),
        "risk_reasons": reasons,
        "high_risk": high_risk,
        "sensitive_service": service in _SECRET_BEARING_SERVICES or service in {"sts", "iam", "kms", "secretsmanager"},
        "is_read": mode == "read",
        "is_write": is_write,
        "requires_plan": is_write,
        "requires_ack_no_snapshot": is_write and ("no_snapshot" in categories or high_risk),
        "requires_ack_irreversible": "irreversible" in categories,
    }


def _response_needs_output_file(response: Any) -> bool:
    if isinstance(response, (bytes, bytearray)):
        return True
    if hasattr(response, "read"):
        return True
    if isinstance(response, dict):
        for value in response.values():
            if _response_needs_output_file(value):
                return True
    if isinstance(response, list):
        for value in response:
            if _response_needs_output_file(value):
                return True
    return False


def _shape_has_blob(shape: Any) -> bool:
    if shape is None:
        return False
    if getattr(shape, "type_name", None) == "blob":
        return True
    members = getattr(shape, "members", None)
    if isinstance(members, dict):
        for member in members.values():
            if _shape_has_blob(member):
                return True
    member_shapes = getattr(shape, "member", None)
    if member_shapes is not None and _shape_has_blob(member_shapes):
        return True
    return False


def _write_binary_output(path: str, response: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = None
    if hasattr(response, "read"):
        payload = response.read()
    elif isinstance(response, (bytes, bytearray)):
        payload = bytes(response)
    elif isinstance(response, dict):
        for value in response.values():
            if hasattr(value, "read"):
                payload = value.read()
                break
            if isinstance(value, (bytes, bytearray)):
                payload = bytes(value)
                break
    if payload is None:
        raise ValidationError("Could not find binary output to write")
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if not isinstance(payload, (bytes, bytearray)):
        raise ValidationError("Binary output must be bytes")
    p.write_bytes(bytes(payload))


def _sanitize_command(argv: list[str]) -> str:
    parts: list[str] = []
    skip_next = False
    for item in argv:
        if skip_next:
            parts.append(REDACTED)
            skip_next = False
            continue
        if item == "--input-json":
            parts.append(item)
            skip_next = True
            continue
        if item.startswith("--input-json="):
            parts.append("--input-json=" + REDACTED)
            continue
        parts.append(item)
    return "qwayk-aws-safe-agent-cli " + " ".join(parts)


def _build_version_payload(registry: GeneratedRegistry) -> dict[str, Any]:
    return {
        "ok": True,
        "tool": "qwayk-aws-safe-agent-cli",
        "version": __version__,
        "boto3_version": boto3.__version__,
        "botocore_version": botocore.__version__,
        "inventory_counts": registry.summary_payload(),
    }


def _add_service_command_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    parser.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    parser.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    parser.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    parser.add_argument("--ack-no-snapshot", action="store_true", help="Extra acknowledgement for no-snapshot actions")
    parser.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    parser.add_argument("--input-json", default=None, help="Operation input as JSON text or a JSON file path")
    parser.add_argument("--output-file", default=None, help="Write binary or secret payloads to this path")


def _build_parser() -> argparse.ArgumentParser:
    registry = load_generated_registry()
    p = _ToolArgumentParser(prog="qwayk-aws-safe-agent-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    _add_service_command_flags(p)
    p.add_argument("--run-id", default=None, help="Optional run id (for run history/audit)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing local run artifacts")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    inventory = sub.add_parser("inventory", help="Pinned inventory information (local)")
    inventory_sub = inventory.add_subparsers(dest="inventory_cmd", required=True, parser_class=_ToolArgumentParser)
    inventory_summary = inventory_sub.add_parser("summary", help="Show inventory counts and source metadata")
    inventory_summary.set_defaults(func=inventory_cmd.cmd_inventory_summary, write_capable=False)

    for service_name in registry.service_names():
        service_index = registry.get_service(service_name)
        service_parser = sub.add_parser(service_name, help=f"AWS {service_name} operations")
        _add_service_command_flags(service_parser)
        service_parser.add_argument(
            "operation",
            choices=service_index.operation_kebabs,
            help="Generated operation name",
        )
        service_parser.set_defaults(func=cmd_generated_operation, write_capable=False)

    return p


@lru_cache(maxsize=1)
def build_parser() -> argparse.ArgumentParser:
    return _build_parser()


def _cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary = None
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = Path(ad) / "summary.md"
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str | None,
    env_fingerprint: str | None,
    output_obj: dict[str, Any] | None,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
    apply: bool | None,
    yes: bool | None,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return

    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    plan_path = str(plan_file) if plan_file.exists() else None
    receipt_path = str(receipt_file) if receipt_file.exists() else None
    command = redact_text(command or "")

    summary_lines = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=plan_path,
        receipt_path=receipt_path,
        audit_log_path=audit_log_path,
        audit_log_global_path=audit_log_global_path,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary_lines)

    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": tool,
            "version": version,
            "command": command,
            "env_fingerprint": env_fingerprint,
            "dry_run": bool(output_obj.get("dry_run")) if isinstance(output_obj, dict) else None,
            "apply": apply,
            "yes": yes,
            "ok": bool(output_obj.get("ok")) if isinstance(output_obj, dict) else None,
            "refused": bool(output_obj.get("refused")) if isinstance(output_obj, dict) else False,
            "plan_path": plan_path,
            "receipt_path": receipt_path,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )


def _build_service_plan(
    *,
    cfg: Config,
    service_name: str,
    operation_name: str,
    operation_kebab: str,
    input_obj: dict[str, Any],
    policy: dict[str, Any],
    identity: dict[str, str] | None,
) -> dict[str, Any]:
    return redact_obj(
        {
            "tool": "qwayk-aws-safe-agent-cli",
            "version": __version__,
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "service": service_name,
            "operation": operation_kebab,
            "botocore_operation": operation_name,
            "region": cfg.region_name,
            "profile": cfg.profile_name,
            "allowlists": {
                "allowed_accounts": list(cfg.allowed_accounts),
                "allowed_regions": list(cfg.allowed_regions),
            },
            "risk": policy,
            "input": input_obj,
            "identity": identity,
        }
    )


def _validate_plan_for_apply(
    *,
    plan: dict[str, Any],
    cfg: Config,
    service_name: str,
    operation_kebab: str,
    input_obj: dict[str, Any],
) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("service") or "") != service_name:
        raise SafetyError("Refused: plan service does not match the current command")
    if str(plan.get("operation") or "") != operation_kebab:
        raise SafetyError("Refused: plan operation does not match the current command")
    if str(plan.get("region") or "") != cfg.region_name:
        raise SafetyError("Refused: plan region does not match the current environment")
    planned_input = plan.get("input") or {}
    if redact_obj(planned_input) != redact_obj(input_obj):
        raise SafetyError("Refused: plan input does not match the current input")


def _apply_output_file_if_needed(response: Any, output_file: str | None) -> tuple[Any, str | None]:
    if output_file and _response_needs_output_file(response):
        _write_binary_output(output_file, response)
        return {"output_file": output_file, "binary_output_written": True}, output_file
    return response, None


def _http_status_from_response(response_summary: Any) -> int | None:
    if not isinstance(response_summary, dict):
        return None
    metadata = response_summary.get("ResponseMetadata")
    if not isinstance(metadata, dict):
        return None
    status = metadata.get("HTTPStatusCode")
    if isinstance(status, int):
        return status
    try:
        return int(str(status))
    except Exception:
        return None


def _build_apply_verification(
    *,
    service_name: str,
    operation_kebab: str,
    plan: dict[str, Any],
    response_summary: Any,
    policy: dict[str, Any],
) -> dict[str, Any]:
    http_status = _http_status_from_response(response_summary)
    checks: list[dict[str, Any]] = [
        {
            "name": "aws_call_completed_without_exception",
            "ok": True,
            "checked": "The boto3 call returned control to the CLI without raising an exception.",
        },
        {
            "name": "reviewed_plan_matched_command",
            "ok": True,
            "checked": "The saved plan matched service, operation, region, and input before apply.",
        },
        {
            "name": "response_captured_and_redacted",
            "ok": True,
            "checked": "The AWS response was captured for the receipt after redaction.",
        },
    ]
    if http_status is None:
        checks.append(
            {
                "name": "response_metadata_http_status",
                "ok": None,
                "checked": "No HTTP status was available in ResponseMetadata.",
            }
        )
    else:
        checks.append(
            {
                "name": "response_metadata_http_status",
                "ok": 200 <= http_status < 400,
                "checked": f"ResponseMetadata.HTTPStatusCode was {http_status}.",
                "value": http_status,
            }
        )

    read_back = {
        "attempted": False,
        "reason": "No generic safe read-back can be inferred for every pinned Botocore operation.",
    }
    status = "verified" if read_back.get("attempted") and http_status is not None and 200 <= http_status < 400 else "limited"
    return redact_obj(
        {
            "ran": True,
            "status": status,
            "service": service_name,
            "operation": operation_kebab,
            "checked_plan_service": plan.get("service"),
            "checked_plan_operation": plan.get("operation"),
            "checks": checks,
            "read_back": read_back,
            "limits": [
                "This verification confirms the reviewed plan matched and the AWS SDK call returned a captured response.",
                "It does not claim resource state was read back unless an operation-specific read-back check is added later.",
                "AWS eventual consistency can delay visible state after a successful write.",
            ],
            "risk_categories": policy.get("risk_categories", []),
        }
    )


def cmd_generated_operation(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    registry: GeneratedRegistry = ctx["registry"]
    service_name = str(getattr(args, "cmd", "") or "").strip()
    operation_kebab = str(getattr(args, "operation", "") or "").strip()
    operation = registry.get_operation(service_name, operation_kebab)
    cfg: Config = ctx["cfg"]
    policy = _operation_policy(service_name, operation.operation_name)

    input_obj = validate_operation_input(
        service_name=service_name,
        operation_name=operation.operation_name,
        input_obj=load_input_json(getattr(args, "input_json", None)),
    )
    operation_model = load_operation_model(service_name, operation.operation_name)

    plan_out = ctx.get("plan_out")
    receipt_out = ctx.get("receipt_out")
    output_file = str(getattr(args, "output_file", None) or "")
    output_file = output_file or None
    if policy["is_write"] and not bool(getattr(args, "apply", False)):
        plan = _build_service_plan(
            cfg=cfg,
            service_name=service_name,
            operation_name=operation.operation_name,
            operation_kebab=operation_kebab,
            input_obj=input_obj,
            policy=policy,
            identity=None,
        )
        if plan_out:
            write_json_file(plan_out, plan)
        out = {
            "ok": True,
            "dry_run": True,
            "service": service_name,
            "operation": operation_kebab,
            "plan": plan,
            "plan_out": plan_out,
            "risk": policy["mode"],
        }
        ctx["audit"].write("aws.plan", out)
        ctx["out"].emit(out)
        return 0

    if policy["is_write"]:
        if not bool(getattr(args, "apply", False)):
            raise SafetyError("Refused: write operations require --apply or a dry-run plan")
        if not str(getattr(args, "plan_in", "") or "").strip():
            raise SafetyError("Refused: live writes require --plan-in and --yes")
        if not bool(getattr(args, "yes", False)):
            raise SafetyError("Refused: live writes require --plan-in and --yes")
        if policy["requires_ack_no_snapshot"] and not bool(getattr(args, "ack_no_snapshot", False)):
            raise SafetyError("Refused: this write requires --ack-no-snapshot")
        if policy["requires_ack_irreversible"] and not bool(getattr(args, "ack_irreversible", False)):
            raise SafetyError("Refused: this write requires --ack-irreversible")
        plan = read_json_file(str(getattr(args, "plan_in")))
        _validate_plan_for_apply(
            plan=plan,
            cfg=cfg,
            service_name=service_name,
            operation_kebab=operation_kebab,
            input_obj=input_obj,
        )

    if (_shape_has_blob(operation_model.output_shape) or bool(getattr(operation_model, "has_streaming_output", False))) and not output_file:
        raise SafetyError("Refused: this operation returns binary data and requires --output-file")

    identity_obj: dict[str, str] | None = None
    if not (service_name == "sts" and operation.operation_name == "GetCallerIdentity"):
        identity = fetch_caller_identity(cfg)
        identity_obj = {
            "account": identity.account,
            "arn": identity.arn,
            "user_id": identity.user_id,
        }
        allowlists = AllowLists(accounts=cfg.allowed_accounts, regions=cfg.allowed_regions)
        reasons = allowlists.check(account_id=identity.account, region_name=cfg.region_name)
        if reasons:
            raise SafetyError("; ".join(reasons))

    from .sts_identity import make_sts_client

    if service_name == "sts":
        boto_client = make_sts_client(cfg)
    else:
        import boto3 as _boto3
        from botocore.config import Config as BotoConfig

        session_kwargs: dict[str, str] = {"region_name": cfg.region_name}
        if cfg.profile_name:
            session_kwargs["profile_name"] = cfg.profile_name
        session = _boto3.Session(**session_kwargs)
        boto_client = session.client(
            service_name,
            region_name=cfg.region_name,
            config=BotoConfig(connect_timeout=cfg.timeout_s, read_timeout=cfg.timeout_s, retries={"max_attempts": 0}),
        )

    method_name = _operation_snake_name(operation.operation_name)
    method = getattr(boto_client, method_name)
    response = method(**input_obj)

    response_summary: Any = redact_obj(response)
    if _response_needs_output_file(response):
        if not output_file:
            raise SafetyError("Refused: this operation returns binary data and requires --output-file")
        _write_binary_output(output_file, response)
        response_summary = {"binary_output_written": True, "output_file": output_file}

    if policy["is_write"]:
        verification = _build_apply_verification(
            service_name=service_name,
            operation_kebab=operation_kebab,
            plan=plan,
            response_summary=response_summary,
            policy=policy,
        )
        receipt = redact_obj(
            {
                "ok": True,
                "applied": True,
                "tool": "qwayk-aws-safe-agent-cli",
                "version": __version__,
                "service": service_name,
                "operation": operation_kebab,
                "region": cfg.region_name,
                "identity": identity_obj,
                "input": input_obj,
                "response": response_summary,
                "verification": verification,
            }
        )
        if receipt_out:
            write_json_file(receipt_out, receipt)
        output_payload = {
            "ok": True,
            "applied": True,
            "service": service_name,
            "operation": operation_kebab,
            "receipt": receipt,
            "receipt_out": receipt_out,
            "response": response_summary,
        }
    else:
        output_payload = {
            "ok": True,
            "service": service_name,
            "operation": operation_kebab,
            "response": response_summary,
        }

    if output_file and response_summary.get("binary_output_written"):
        output_payload["output_file"] = output_file

    ctx["audit"].write("aws.execute", output_payload)
    ctx["out"].emit(redact_obj(output_payload))
    return 0


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    registry = load_generated_registry()
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": redact_text(str(e)), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    _ensure_arg_defaults(args)

    if bool(getattr(args, "version", False)):
        payload = _build_version_payload(registry)
        if args.output == "json":
            out.emit(payload)
        else:
            print(
                f"qwayk-aws-safe-agent-cli {__version__} "
                f"(boto3 {boto3.__version__}, botocore {botocore.__version__})"
            )
        return 0

    cmd = str(getattr(args, "cmd", "") or "")
    if not cmd:
        out.emit({"ok": False, "error": "Missing command. Use --help to see available commands.", "error_type": "ValidationError"})
        return 1

    command_str = _sanitize_command(argv)
    project_cfg, config_dir = load_project_config(str(getattr(args, "config", None) or "") or None)
    project_dir_arg = str(getattr(args, "project_dir", "") or "").strip()
    project_dir = Path(project_dir_arg) if project_dir_arg else (Path(config_dir) if config_dir else Path("."))

    needs_config = cmd not in {"runs", "onboarding", "inventory"}
    cfg = load_config(args.env_file) if needs_config else None

    write_capable = bool(getattr(args, "write_capable", False))
    if cmd in registry.services:
        op_policy = _operation_policy(cmd, registry.get_operation(cmd, str(getattr(args, "operation", ""))).operation_name)
        write_capable = op_policy["is_write"]

    run_ctx: RunContext = init_run_context(
        env_file=str(args.env_file),
        enabled=write_capable,
        run_id=str(args.run_id) if args.run_id else None,
        artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
        no_artifacts=bool(args.no_artifacts),
    )
    run_audit_log_path = str(run_ctx.audit_log_path) if (run_ctx.enabled and run_ctx.audit_log_path) else None
    global_audit_log_path = str(args.log_file) if args.log_file else None
    runs_index_path = runs_index_path_for_env_file(str(args.env_file))
    if cmd == "runs":
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    loggers: list[AuditLogger] = []
    if run_audit_log_path:
        loggers.append(AuditLogger(path=run_audit_log_path, enabled=True))
    if global_audit_log_path:
        loggers.append(AuditLogger(path=global_audit_log_path, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    try:
        command_str = _sanitize_command(argv)
        audit.bind_context(
            {
                "tool": "qwayk-aws-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.region_name if cfg else None,
                "run_id": run_ctx.run_id,
            }
        )

        if cmd in {"runs", "onboarding", "inventory"}:
            ctx = {
                "cfg": cfg,
                "out": out,
                "audit": audit,
                "tool": "qwayk-aws-safe-agent-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": None if cfg is None else cfg.timeout_s,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "ack_irreversible": bool(args.ack_irreversible),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
                "registry": registry,
            }
            rc = int(args.func(args, ctx))
            return rc

        if cfg is None:
            cfg = load_config(args.env_file)

        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "qwayk-aws-safe-agent-cli",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "ack_irreversible": bool(args.ack_irreversible),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
            "registry": registry,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "qwayk-aws-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.region_name,
                "run_id": run_ctx.run_id,
            }
        )

        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-aws-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.region_name,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )

        return rc
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except SafetyError as e:
        audit.write("refused", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [redact_text(str(e))], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-aws-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.region_name if cfg else None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        message = redact_text(str(e))
        audit.write("error", {"error": message, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": message, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-aws-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.region_name if cfg else None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        message = redact_text(str(e))
        audit.write("error", {"error": message, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": message, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-aws-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.region_name if cfg else None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    finally:
        audit.close()


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    mode = str(argv[idx + 1] or "").strip()
    return mode if mode in {"json", "text"} else "json"


def _ensure_arg_defaults(args: argparse.Namespace) -> None:
    defaults = {
        "apply": False,
        "yes": False,
        "plan_out": None,
        "plan_in": None,
        "receipt_out": None,
        "ack_no_snapshot": False,
        "ack_irreversible": False,
        "input_json": None,
        "output_file": None,
        "timeout_s": None,
        "verbose": False,
        "debug": False,
        "run_id": None,
        "artifacts_dir": None,
        "no_artifacts": False,
        "log_file": None,
        "config": None,
        "project_dir": None,
        "env_file": ".env",
        "output": "json",
    }
    for key, default in defaults.items():
        if not hasattr(args, key):
            setattr(args, key, default)
