from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient, build_linkedin_headers
from ..json_files import read_json_file, write_json_file
from ..operation_catalog import OperationSpec, OPERATIONS_BY_FAMILY, READ, RISKY

_PATH_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")
IRREVERSIBLE_WRITE_MODE = "irreversible_and_clearly_labeled"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _to_arg_name(path_key: str) -> str:
    return path_key.replace("_", "-")


def _extract_placeholders(template: str) -> list[str]:
    return list(dict.fromkeys(_PATH_PLACEHOLDER_RE.findall(template)))


def _split_path_query(template: str) -> tuple[str, dict[str, str]]:
    if "?" not in template:
        return template, {}
    path_part, raw_query = template.split("?", 1)
    query: dict[str, str] = {}
    if raw_query:
        for part in raw_query.split("&"):
            if not part or "=" not in part:
                continue
            k, v = part.split("=", 1)
            query[k] = v
    return path_part, query


def _format_value(value: str, values: dict[str, str]) -> str:
    if "{" not in value:
        return value
    try:
        return value.format(**values)
    except KeyError as exc:
        raise ValidationError(f"Missing value for placeholder in fixed query: {exc.args[0]}") from None


def _parse_params(raw: list[str] | None) -> dict[str, str]:
    params: dict[str, str] = {}
    if not raw:
        return params
    for item in raw:
        if "=" not in item:
            raise ValidationError(f"Invalid --param value: {item}. Use key=value")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"Invalid --param value: {item}. Empty key")
        params[key] = value
    return params


def _parse_body(*, body_json: str | None, body_file: str | None) -> Any:
    if body_json and body_file:
        raise ValidationError("Use only one of --body-json or --body-file")

    if body_json is not None:
        try:
            return json.loads(body_json)
        except Exception as exc:
            raise ValidationError(f"Invalid JSON in --body-json: {type(exc).__name__}: {exc}") from None

    if body_file is not None:
        obj = read_json_file(body_file)
        if obj is None:
            return None
        return obj

    return None


def _request_signature(
    *,
    spec: OperationSpec,
    resolved_path: str,
    query: dict[str, str],
    body: Any,
    env_fingerprint: str,
) -> str:
    return _hash(
        {
            "method": spec.method,
            "resolved_path": resolved_path,
            "query": query,
            "body": body,
            "env_fingerprint": env_fingerprint,
        }
    )


def _rollback_contract(spec: OperationSpec) -> dict[str, Any]:
    return {
        "mode": IRREVERSIBLE_WRITE_MODE,
        "supported": False,
        "requires_ack_irreversible": True,
        "notes": (
            "This runtime does not capture before-state snapshots or provider backups. "
            "Treat every live LinkedIn write as irreversible here."
        ),
    }


def _before_state_contract(spec: OperationSpec) -> dict[str, Any]:
    if spec.safety == READ:
        return {
            "required": False,
            "supported": False,
            "statement": "Read operation. No before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "statement": (
            "This LinkedIn Ads operation has no reliable before-state snapshot in this runtime. "
            "Apply may continue only after explicit no-snapshot approval."
        ),
    }


def _verification_plan(spec: OperationSpec) -> dict[str, Any]:
    if spec.safety == READ:
        return {
            "type": "api_call",
            "checks": [
                "HTTP status code is 2xx",
                "Response parses as JSON or returns text",
            ],
        }
    return {
        "type": "best_effort_after_apply",
        "checks": [
            "Apply gates pass only with the required flags and matching plan.",
            "HTTP status code is recorded in the receipt.",
            "Receipt records explicit no-snapshot approval.",
        ],
    }


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise SafetyError(
        "Refused: this LinkedIn Ads write has no reliable before-state snapshot in this runtime. "
        "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
    )


def _build_plan(
    *,
    family: str,
    spec: OperationSpec,
    path_template: str,
    resolved_path: str,
    path_values: dict[str, str],
    query: dict[str, str],
    body: Any,
    tool: str,
    version: str,
    command: str,
    env_fingerprint: str,
) -> dict[str, Any]:
    signature = _request_signature(
        spec=spec,
        resolved_path=resolved_path,
        query=query,
        body=body,
        env_fingerprint=env_fingerprint,
    )
    request = {
        "method": spec.method,
        "path_template": path_template,
        "resolved_path": resolved_path,
        "path_values": path_values,
        "query": query,
        "body": body,
    }
    preconditions = [
        "env_fingerprint must match plan",
        "resolved request must match signature",
    ]
    if spec.safety != READ:
        preconditions.append("live apply requires --ack-irreversible")
    if spec.safety == RISKY:
        preconditions.append("high-risk apply also requires --yes and matching --plan-in")
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "operation": {
            "family": family,
            "command": spec.command,
            "method": spec.method,
            "path_template": path_template,
            "safety": spec.safety,
            "status": spec.status,
            "doc_url": spec.doc_url,
        },
        "risk_level": "high" if spec.safety == RISKY else "medium" if spec.safety != READ else "low",
        "risk_reasons": list(spec.gate_tags),
        "preconditions": preconditions,
        "baseline": {
            "env_fingerprint": env_fingerprint,
            "family": family,
            "command": spec.command,
            "method": spec.method,
            "path_template": path_template,
            "resolved_path": resolved_path,
            "query": query,
            "body_sha256": _hash({"body": body}) if body is not None else None,
        },
        "request_signature": signature,
        "proposed_changes": [
            {
                "type": "api_request",
                "operation": f"{spec.method} {path_template}",
            }
        ],
        "verification_plan": _verification_plan(spec),
        "before_state": _before_state_contract(spec),
        "rollback": _rollback_contract(spec),
        "request": request,
        "plan_fingerprint": signature,
    }


def _validate_plan_in(
    *,
    plan: dict[str, Any],
    family: str,
    spec: OperationSpec,
    path_template: str,
    resolved_path: str,
    query: dict[str, str],
    body: Any,
    env_fingerprint: str,
) -> None:
    op = plan.get("operation")
    if not isinstance(op, dict):
        raise ValidationError("Plan file missing operation section")
    if op.get("family") != family or op.get("command") != spec.command:
        raise SafetyError("Refused: plan belongs to a different operation")
    if op.get("method") != spec.method or op.get("path_template") != path_template:
        raise SafetyError("Refused: plan operation does not match this command")

    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan file missing baseline section")
    if str(baseline.get("env_fingerprint") or "") != str(env_fingerprint):
        raise SafetyError("Refused: plan env fingerprint does not match current environment")

    expected = _request_signature(
        spec=spec,
        resolved_path=resolved_path,
        query=query,
        body=body,
        env_fingerprint=env_fingerprint,
    )
    if str(plan.get("request_signature") or "") != expected:
        raise SafetyError("Refused: plan signature changed since the plan was generated")


def _read_response(resp_obj: Any) -> Any:
    try:
        return resp_obj.json()
    except Exception:
        return {"_raw": resp_obj.text()}


def _build_receipt(
    *,
    tool: str,
    version: str,
    command: str,
    env_fingerprint: str,
    family: str,
    spec: OperationSpec,
    resolved_path: str,
    query: dict[str, str],
    body: Any,
    status: int,
    response_body: Any,
) -> dict[str, Any]:
    return {
        "tool": tool,
        "version": version,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "operation": {
            "family": family,
            "command": spec.command,
            "method": spec.method,
            "path": resolved_path,
        },
        "before_state": _before_state_contract(spec),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this LinkedIn Ads operation.",
        },
        "request": {
            "method": spec.method,
            "resolved_path": resolved_path,
            "query": query,
            "body_present": body is not None,
        },
        "response": {
            "status": status,
            "body": response_body,
        },
        "changed": status < 300,
        "verification": {
            "ok": status < 300,
            "details": {
                "status": status,
            },
        },
        "rollback_plan": _rollback_contract(spec),
    }


def _add_operation_args(parser: argparse.ArgumentParser, spec: OperationSpec) -> None:
    placeholders = _extract_placeholders(spec.path)
    for placeholder in sorted(set(placeholders)):
        parser.add_argument(
            f"--{_to_arg_name(placeholder)}",
            required=True,
            help=f"Required path/query value from {spec.path}",
        )

    if spec.method.upper() != "GET":
        parser.add_argument("--body-file", default=None, help="Path to JSON body file")
        parser.add_argument("--body-json", default=None, help='JSON body text')

    parser.add_argument(
        "--param",
        action="append",
        default=None,
        help="Repeat as key=value for extra query parameters",
    )


def _path_arg_values(*, args: argparse.Namespace, placeholders: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for name in placeholders:
        attr = name.replace("-", "_")
        raw = getattr(args, attr, None)
        if raw is None or str(raw).strip() == "":
            raise ValidationError(f"Missing required parameter --{_to_arg_name(name)}")
        values[name] = str(raw).strip()
    return values


def _run_operation(*, family: str, spec: OperationSpec, args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    placeholders = _extract_placeholders(spec.path)
    path_values = _path_arg_values(args=args, placeholders=placeholders)

    path_part, fixed_query = _split_path_query(spec.path)
    path_filled = path_part.format(**path_values)
    query: dict[str, str] = {k: _format_value(v, path_values) for k, v in fixed_query.items()}
    query.update(_parse_params(getattr(args, "param", None)))

    body = _parse_body(
        body_json=getattr(args, "body_json", None),
        body_file=getattr(args, "body_file", None),
    )

    if spec.method.upper() == "GET" and body is not None:
        raise ValidationError("GET operations do not accept --body-file or --body-json")

    apply = bool(ctx.get("apply"))
    is_high_risk = spec.safety == RISKY
    resolved_url = cfg.base_url.rstrip("/") + path_filled
    env_fingerprint = cfg.env_fingerprint
    requires_network = spec.safety == READ or apply

    if spec.safety != READ and not apply:
        plan = _build_plan(
            family=family,
            spec=spec,
            path_template=spec.path,
            resolved_path=resolved_url,
            path_values=path_values,
            query=dict(query),
            body=body,
            tool=str(ctx.get("tool", "linkedin-ads-api-tool")),
            version=str(ctx.get("tool_version", "0.0.0")),
            command=str(ctx.get("command_str", "")),
            env_fingerprint=env_fingerprint,
        )
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        out = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
        }
        ctx["audit"].write("operation.plan", {"family": family, "command": spec.command, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if is_high_risk:
        if not apply:
            raise SafetyError("Refused: high-risk operations require --apply")
        if not bool(ctx.get("yes")):
            raise SafetyError("Refused: high-risk operations require --yes")
        plan_in_path = str(ctx.get("plan_in") or "").strip()
        if not plan_in_path:
            raise SafetyError("Refused: high-risk operations require --plan-in")
        plan_obj = read_json_file(plan_in_path)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_in(
            plan=plan_obj,
            family=family,
            spec=spec,
            path_template=spec.path,
            resolved_path=resolved_url,
            query=dict(query),
            body=body,
            env_fingerprint=env_fingerprint,
        )
    if spec.safety != READ and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: live LinkedIn writes require --ack-irreversible")

    if spec.safety != READ:
        _require_no_snapshot_approval(ctx)

    if requires_network and not getattr(cfg, "token", None):
        raise ValidationError(
            "Missing LinkedIn token. Set LINKEDIN_ADS_TOKEN/LINKEDIN_ADS_ACCESS_TOKEN "
            "or run onboarding/auth token set first."
        )

    headers = build_linkedin_headers(
        token=cfg.token,
        linkedin_version=cfg.linkedin_version,
        restli_protocol_version=cfg.restli_protocol_version,
    )
    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent="linkedin-ads-safe-cli/0.1.0",
    )

    response = client.request(
        spec.method,
        resolved_url,
        headers=headers,
        params=query,
        json_body=body,
    )
    response_body = _read_response(response)

    if spec.safety == READ:
        out = {
            "ok": True,
            "dry_run": False,
            "operation": {
                "family": family,
                "command": spec.command,
                "method": spec.method,
                "path": path_filled,
            },
            "http_status": response.status,
            "response": response_body,
        }
        ctx["audit"].write("operation.read", {"family": family, "command": spec.command, "http_status": response.status})
        ctx["out"].emit(out)
        return 0

    receipt = _build_receipt(
        tool=str(ctx.get("tool", "linkedin-ads-api-tool")),
        version=str(ctx.get("tool_version", "0.0.0")),
        command=str(ctx.get("command_str", "")),
        env_fingerprint=env_fingerprint,
        family=family,
        spec=spec,
        resolved_path=path_filled,
        query=dict(query),
        body=body,
        status=response.status,
        response_body=response_body,
    )
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": True,
        "dry_run": False,
        "status": response.status,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    ctx["audit"].write("operation.apply", {"family": family, "command": spec.command, "http_status": response.status})
    ctx["out"].emit(out)
    return 0


def register_operation_families(
    parser: argparse._SubParsersAction,
    *,
    parser_class: type[argparse.ArgumentParser],
) -> None:
    for family, operations in OPERATIONS_BY_FAMILY.items():
        family_parser = parser.add_parser(family, help=f"LinkedIn Ads API family: {family}")
        op_subparsers = family_parser.add_subparsers(dest="operation", required=True, parser_class=parser_class)
        for spec in operations:
            op = op_subparsers.add_parser(spec.command, help=spec.note)
            _add_operation_args(op, spec)
            op.set_defaults(
                func=_make_operation_handler(family=family, spec=spec),
                write_capable=(spec.safety != READ),
            )


def _make_operation_handler(*, family: str, spec: OperationSpec):
    def _handler(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
        return _run_operation(family=family, spec=spec, args=args, ctx=ctx)

    _handler.__name__ = f"handle_{family.replace('-', '_')}_{spec.command.replace('-', '_')}"
    return _handler
