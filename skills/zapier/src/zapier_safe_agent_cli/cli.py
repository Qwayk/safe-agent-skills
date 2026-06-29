from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .config import Config, load_config
from .errors import NotSupportedError, SafetyError, ToolError, ValidationError
from .json_files import read_json_file, write_json_file
from .http import HttpClient
from .operations import ApiOperation, by_group, load_operations
from .output import Output
from .project_config import load_project_config
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


_TOOL_NAME = "qwayk-zapier-safe-agent-cli"

_REDACTED_BODY_JSON = "<redacted-body-json>"
_REDACTED_BODY_FILE = "<redacted-body-file>"


@dataclass(frozen=True)
class _ApiBaseUrls:
    partner: str
    ai_actions: str
    trigger_inbox: str

    @classmethod
    def from_config(cls, cfg: Config) -> "_ApiBaseUrls":
        return cls(partner=cfg.base_url, ai_actions=cfg.ai_actions_base_url, trigger_inbox=cfg.trigger_inbox_base_url)


def _safe_redact(obj):
    if isinstance(obj, dict):
        out: dict[str, object] = {}
        for key, value in obj.items():
            k = str(key).lower()
            if k in {"authorization", "token", "access_token", "jwt", "client_secret", "password"} or k.endswith("_token") or k.endswith("_secret"):
                out[key] = "***REDACTED***"
            else:
                out[key] = _safe_redact(value)
        return out
    if isinstance(obj, list):
        return [_safe_redact(v) for v in obj]
    return obj


def _redact_command(argv: list[str]) -> str:
    parts: list[str] = [_TOOL_NAME]
    i = 0
    while i < len(argv):
        arg = str(argv[i])

        if arg == "--body-json":
            parts.append("--body-json")
            parts.append(_REDACTED_BODY_JSON)
            i += 1
            if i < len(argv):
                i += 1
            continue

        if arg == "--body-file":
            parts.append("--body-file")
            parts.append(_REDACTED_BODY_FILE)
            i += 1
            if i < len(argv):
                i += 1
            continue

        if arg.startswith("--body-json="):
            parts.append(f"--body-json={_REDACTED_BODY_JSON}")
            i += 1
            continue

        if arg.startswith("--body-file="):
            parts.append(f"--body-file={_REDACTED_BODY_FILE}")
            i += 1
            continue

        parts.append(arg)
        i += 1

    return " ".join(parts)


class _ToolArgumentParser(argparse.ArgumentParser):
    """Keep parse errors in JSON output mode."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    mode = str(argv[idx + 1]).strip()
    return mode if mode in {"json", "text"} else "json"


def _normalize_param_name(name: str) -> str:
    return name.replace("_", "-")


def _restore_param_name(name: str) -> str:
    return name.replace("-", "_")


def _to_snake_case(value: str) -> str:
    s = re.sub(r"[-\s]+", "_", value.strip())
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def _to_operation_command(group: str, command: str) -> str:
    return command


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _hash_obj(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _command_signature(group: str, op: ApiOperation) -> str:
    return f"{group} {op.command}"


def get_registered_operation_commands() -> list[str]:
    return sorted(_command_signature(op.group, op) for op in load_operations())


def _base_urls(cfg: Config) -> _ApiBaseUrls:
    return _ApiBaseUrls.from_config(cfg)


def _get_operation_base_url(cfg: Config, op: ApiOperation) -> str:
    base_urls = _base_urls(cfg)
    if op.base_url_ref == "ai-actions":
        return base_urls.ai_actions
    if op.base_url_ref == "trigger-inbox":
        return base_urls.trigger_inbox
    return base_urls.partner


def _auth_headers(cfg: Config) -> tuple[str, dict[str, str]]:
    if cfg.access_token:
        return f"Bearer {cfg.access_token}", {
            "Authorization": f"Bearer {cfg.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    if cfg.jwt:
        headers = {
            "Authorization": f"Bearer {cfg.jwt}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if cfg.client_id:
            headers["X-Client-Id"] = cfg.client_id
        if cfg.client_secret:
            headers["X-Client-Secret"] = cfg.client_secret
        return f"Bearer {cfg.jwt}", headers

    if cfg.client_id and cfg.client_secret:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Client-Id": cfg.client_id,
            "X-Client-Secret": cfg.client_secret,
        }
        return "", headers

    raise ValidationError("Missing authentication credentials: set one of ZAPIER_ACCESS_TOKEN, ZAPIER_JWT, or ZAPIER_CLIENT_ID+ZAPIER_CLIENT_SECRET")


def _build_url(op: ApiOperation, args: argparse.Namespace, cfg: Config) -> str:
    url = _get_operation_base_url(cfg, op)
    path = op.path
    for p in op.path_params:
        arg_name = _to_snake_case(p)
        param_name = arg_name
        if not hasattr(args, param_name):
            normalized = _normalize_param_name(arg_name)
            if hasattr(args, normalized):
                param_name = normalized
            elif hasattr(args, p):
                param_name = p
            else:
                param_name = _restore_param_name(normalized)
        value = str(getattr(args, param_name, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing required path parameter: {param_name}")
        path = path.replace("{" + p + "}", urllib.parse.quote(value, safe=""))

    return f"{url.rstrip('/')}{path}"


def _collect_path_params(op: ApiOperation, args: argparse.Namespace) -> dict[str, str]:
    path_params: dict[str, str] = {}
    for p in op.path_params:
        arg_name = _to_snake_case(p)
        param_name = arg_name
        if not hasattr(args, param_name):
            normalized = _normalize_param_name(arg_name)
            if hasattr(args, normalized):
                param_name = normalized
            elif hasattr(args, p):
                param_name = p
            else:
                param_name = _restore_param_name(normalized)
        value = str(getattr(args, param_name, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing required path parameter: {param_name}")
        path_params[p] = value

    return path_params


def _collect_request_fields(
    *,
    op: ApiOperation,
    cfg: Config,
    args: argparse.Namespace,
) -> tuple[str, dict[str, str], dict[str, object] | list[object] | None, dict[str, str]]:
    path_params = _collect_path_params(op, args)
    query = _collect_query_args(op, args)
    body = _collect_body_input(args)
    url = _build_url(op, args, cfg)
    return url, path_params, body, query


def _coerce_str_dict(value: object | None) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in value.items():
        out[str(key)] = str(value)
    return out


def _plan_mismatch_reasons(
    *,
    plan_in: dict,
    op: ApiOperation,
    cfg: Config,
    path: str,
    path_params: dict[str, str],
    query: dict[str, str],
    body: object | None,
    risk: str,
) -> list[str]:
    mismatches: list[str] = []

    if str(plan_in.get("operation_id") or "") != str(op.operation_id):
        mismatches.append("operation_id")
    if str(plan_in.get("operation") or "") != str(op.command):
        mismatches.append("operation")
    if str(plan_in.get("method") or "").upper() != op.method.upper():
        mismatches.append("method")
    if str(plan_in.get("path") or "") != path:
        mismatches.append("path")

    expected_base_url = _get_operation_base_url(cfg, op)
    if str(plan_in.get("base_url") or "") != expected_base_url:
        mismatches.append("base_url")

    if _coerce_str_dict(plan_in.get("path_params")) != _coerce_str_dict(path_params):
        mismatches.append("path_params")
    if _coerce_str_dict(plan_in.get("query")) != _coerce_str_dict(query):
        mismatches.append("query")

    plan_body_present = bool(plan_in.get("body_present"))
    if body is not None:
        if not plan_body_present:
            mismatches.append("body_present")
        if str(plan_in.get("body_sha256") or "") != _hash_obj(body):
            mismatches.append("body_sha256")
    else:
        if plan_body_present:
            mismatches.append("body_present")
            if plan_in.get("body_sha256") not in (None, ""):
                mismatches.append("body_sha256")

    if str(plan_in.get("risk_level") or "") != risk:
        mismatches.append("risk_level")

    if str(plan_in.get("env_fingerprint") or "") != cfg.auth_fingerprint():
        mismatches.append("env_fingerprint")

    return mismatches


def _collect_query_args(op: ApiOperation, args: argparse.Namespace) -> dict[str, str]:
    query: dict[str, str] = {}
    for item in op.required_query_params:
        key = _to_snake_case(item)
        value = str(getattr(args, key, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing required query parameter: {_normalize_param_name(item)}")
        query[item] = value
    return query


def _collect_body_input(args: argparse.Namespace) -> dict[str, object] | list[object] | None:
    body_file = getattr(args, "body_file", None)
    body_json = getattr(args, "body_json", None)

    if body_file and body_json:
        raise ValidationError("Use only one of --body-file or --body-json")
    if body_file:
        obj = read_json_file(body_file)
        if not isinstance(obj, (dict, list)):
            raise ValidationError("--body-file must contain a JSON object or array")
        return obj
    if body_json:
        try:
            obj = json.loads(body_json)
        except Exception:
            raise ValidationError("--body-json must be valid JSON") from None
        if not isinstance(obj, (dict, list)):
            raise ValidationError("--body-json must be a JSON object or array")
        return obj
    return None


def _validate_env_auth(cfg: Config) -> None:
    # Require any supported auth shape.
    if not (cfg.access_token or cfg.jwt or (cfg.client_id and cfg.client_secret)):
        raise ValidationError("Missing auth credentials: provide ZAPIER_ACCESS_TOKEN, or ZAPIER_JWT, or both ZAPIER_CLIENT_ID and ZAPIER_CLIENT_SECRET")


def _build_plan(*, cfg: Config, command: str, op: ApiOperation, path_params: dict[str, str], query: dict[str, str], body: object | None, risk: str) -> dict[str, object]:
    return {
        "tool": _TOOL_NAME,
        "version": __version__,
        "generated_at_utc": _now_iso(),
        "env_fingerprint": cfg.auth_fingerprint(),
        "command": command,
        "operation_id": op.operation_id,
        "operation": op.command,
        "method": op.method,
        "path": op.path,
        "base_url": _get_operation_base_url(cfg, op),
        "base_url_ref": op.base_url_ref,
        "risk_level": risk,
        "risk_reasons": ["write_or_sensitive_operation"] if risk == "high" else [],
        "path_params": {k: str(v) for k, v in path_params.items()},
        "query": {k: str(v) for k, v in query.items()},
        "body_present": body is not None,
        "body_sha256": _hash_obj(body) if body is not None else None,
        "plan_instructions": [
            "Run with --apply and --plan-in after reviewing this plan first.",
            "For high-risk operations include --yes or --ack-no-snapshot/--ack-irreversible.",
        ],
    }


def _run_operation(args: argparse.Namespace, ctx: dict) -> int:
    args = args
    cfg: Config = ctx["cfg"]
    out = ctx["out"]
    _validate_env_auth(cfg)

    op: ApiOperation = ctx["operation"]
    command = ctx["command_str"]
    apply = bool(args.apply)
    high_risk = op.is_high_risk

    url, path_params, body, query = _collect_request_fields(op=op, cfg=cfg, args=args)

    if not op.request_body and body is not None:
        raise ValidationError(f"Operation {op.command} does not accept a request body")

    risk_level = "high" if op.is_high_risk else "medium"

    if apply and bool(getattr(args, "plan_in", None)):
        plan_in = read_json_file(args.plan_in)
        if not isinstance(plan_in, dict):
            raise ValidationError("--plan-in must point to a JSON object")
        mismatches = _plan_mismatch_reasons(
            plan_in=plan_in,
            op=op,
            cfg=cfg,
            path=op.path,
            path_params=path_params,
            query=query,
            body=body,
            risk=risk_level,
        )
        if mismatches:
            out.emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "refused": True,
                    "reasons": [f"Reviewed plan does not match this command: {', '.join(sorted(set(mismatches)))}"],
                    "refusal_type": "SafetyError",
                    "command": command,
                }
            )
            if "audit" in ctx:
                ctx["audit"].write("operation.apply", {"operation": op.command, "status": "plan-refused", "mismatches": mismatches})
            return 0

    # Read operations may run directly.
    if not op.is_write:
        headers = _auth_headers(cfg)[1]
        http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent=ctx["user_agent"])
        response = http.request(op.method, url, headers=headers, params=query)
        payload = response.json()
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "command": command,
                "operation": op.command,
                "method": op.method,
                "path": op.path,
                "status": response.status,
                "response": _safe_redact(payload),
                "query": query,
            }
        )
        return 0

    plan = _build_plan(cfg=cfg, command=command, op=op, path_params=path_params, query=query, body=body, risk=risk_level)

    if not apply:
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        default_plan_path = None
        artifacts_dir = ctx.get("artifacts_dir")
        if isinstance(artifacts_dir, Path):
            default_plan_path_obj = artifacts_dir / "plan.json"
            default_plan_path = str(default_plan_path_obj)
            if plan_path != default_plan_path:
                write_json_file(default_plan_path, plan)
        out.emit(
            {
                "ok": True,
                "dry_run": True,
                "command": command,
                "operation": op.command,
                "status": "planned",
                "risk_level": plan["risk_level"],
                "artifacts_dir": str(ctx.get("artifacts_dir")) if ctx.get("artifacts_dir") else None,
                "runs_index": str(ctx.get("runs_index_path")) if ctx.get("runs_index_path") else None,
                "plan_out": default_plan_path or plan_path,
                "plan": plan,
            }
        )
        if "audit" in ctx:
            ctx["audit"].write("operation.plan", {"operation": op.command, "path": op.path, "plan": _safe_redact(plan)})
        return 0

    if high_risk and not args.plan_in:
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": ["High-risk operations require --plan-in plus plan review"],
                "refusal_type": "SafetyError",
                "command": command,
            }
        )
        return 0

    if high_risk and not (args.yes or args.ack_irreversible or args.ack_no_snapshot):
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": ["High-risk operation requires --yes or --ack-irreversible/--ack-no-snapshot"],
                "refusal_type": "SafetyError",
                "command": command,
            }
        )
        return 0

    if op.request_body and body is None:
        raise ValidationError(f"Missing request body for {op.command}; use --body-json or --body-file")

    headers = _auth_headers(cfg)[1]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent=ctx["user_agent"])
    response = http.request(op.method, url, headers=headers, params=query, json_body=body)

    response_payload: object | None
    try:
        response_payload = response.json()
    except Exception:
        response_payload = response.text()

    receipt = {
        "tool": _TOOL_NAME,
        "version": __version__,
        "applied_at_utc": _now_iso(),
        "env_fingerprint": cfg.auth_fingerprint(),
        "command": command,
        "operation": op.command,
        "operation_id": op.operation_id,
        "method": op.method,
        "base_url": _get_operation_base_url(cfg, op),
        "path": op.path,
        "status": response.status,
        "plan": _safe_redact(plan),
        "response": _safe_redact(response_payload),
        "query": query,
        "path_params": path_params,
        "verification": {
            "type": "response_code",
            "status": response.status,
            "verified_at": _now_iso(),
        },
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    default_receipt_path = None
    artifacts_dir = ctx.get("artifacts_dir")
    if isinstance(artifacts_dir, Path):
        default_receipt = artifacts_dir / "receipt.json"
        default_receipt_path = str(default_receipt)
        if receipt_path != default_receipt_path:
            write_json_file(default_receipt_path, receipt)

    out.emit(
        {
            "ok": True,
            "dry_run": False,
            "command": command,
            "operation": op.command,
            "status": response.status,
            "receipt_out": default_receipt_path or receipt_path,
            "artifacts_dir": str(ctx.get("artifacts_dir")) if ctx.get("artifacts_dir") else None,
            "runs_index": str(ctx.get("runs_index_path")) if ctx.get("runs_index_path") else None,
            "receipt": _safe_redact(receipt),
        }
    )
    if "audit" in ctx:
        ctx["audit"].write("operation.apply", {"operation": op.command, "status": response.status})
    return 0


def _cmd_auth_check(args: argparse.Namespace, ctx: dict) -> int:
    cfg = ctx["cfg"]
    out = ctx["out"]
    try:
        _validate_env_auth(cfg)
    except ToolError as e:
        out.emit(
            {
                "ok": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "command": "auth check",
            }
        )
        return 1

    op_name = "profiles-me-list"
    matching: ApiOperation | None = None
    for op in load_operations():
        if op.command == op_name:
            matching = op
            break
    if matching is None:
        raise NotSupportedError("Auth check operation not found in operation table")

    query: dict[str, str] = {}
    body = None
    url = _build_url(matching, args, cfg)
    headers = _auth_headers(cfg)[1]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent=ctx["user_agent"])
    response = http.request("GET", url, headers=headers, params=query)
    payload = response.json()
    out.emit(
        {
            "ok": True,
            "command": f"{_TOOL_NAME} auth check",
            "status": response.status,
            "operation": op_name,
            "auth": {
                "credential_fingerprint": cfg.auth_fingerprint(),
                "base_url": cfg.base_url,
                "ai_actions_base_url": cfg.ai_actions_base_url,
                "trigger_inbox_base_url": cfg.trigger_inbox_base_url,
            },
            "result": _safe_redact(payload),
        }
    )
    return 0


def _cmd_onboarding(args: argparse.Namespace, ctx: dict) -> int:
    env_file = str(getattr(args, "env_file", ".env"))
    out = ctx["out"]
    env_path = Path(env_file)
    wrote = False
    if not getattr(args, "no_write_env", False) and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
            wrote = True

    env_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    env_map = {line.split("=", 1)[0].strip(): line for line in env_lines if "=" in line}
    missing = []
    for key in ("ZAPIER_ACCESS_TOKEN", "ZAPIER_TIMEOUT_S"):
        if not env_map.get(key):
            missing.append(key)

    out.emit(
        {
            "ok": True,
            "onboarding": {
                "env_file": env_file,
                "env_created": wrote,
                "missing": missing,
                "next_command": f"{_TOOL_NAME} --output json auth check",
                "steps": [
                    "Copy .env.example to .env",
                    "Fill required keys (or leave ACCESS_TOKEN empty if using OAuth token flow)",
                    "Run `qwayk-zapier-safe-agent-cli --output json auth check`",
                ],
            },
        }
    )
    return 0


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    rows = list_runs(runs_index, limit=int(getattr(args, "limit", 20) or 20))
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict) -> int:
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
    artifacts = row.get("artifacts_dir")
    if isinstance(artifacts, str):
        summary_path = Path(artifacts) / "summary.md"
        if summary_path.exists():
            summary = summary_path.read_text(encoding="utf-8")
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _error_payload(*, message: object, error_type: str, command: str | None = None) -> dict[str, object]:
    text = str(message or "").strip()
    # Do not leak provider response bodies that might include private payload details.
    text = text.split("\n", 1)[0]
    text = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1***REDACTED***", text)
    text = re.sub(r"(?i)(token|access_token|jwt|client_secret|password)([=:]\s*)[^\s,;]+", r"\1\2***REDACTED***", text)
    text = re.sub(r"(?i)(\"(?:token|access_token|jwt|client_secret|password)\"\s*:\s*\")[^\"]+\"", r"\1***REDACTED***\"", text)
    payload: dict[str, object] = {
        "ok": False,
        "error": text or "Operation failed",
        "error_type": error_type,
    }
    if command:
        payload["command"] = command
    return payload


def _register_operation_subcommands(subparsers: argparse._SubParsersAction, *, write_capable: bool, defaults: dict[str, object]) -> None:
    ops = by_group()
    for group in sorted(ops):
        group_parser = subparsers.add_parser(group, help=f"Zapier {group} operations")
        group_sub = group_parser.add_subparsers(dest="operation_name", required=True, parser_class=_ToolArgumentParser)
        for op in ops[group]:
            action = op.command
            op_parser = group_sub.add_parser(action, help=(op.summary[:90] if op.summary else op.command))
            for p in sorted(op.path_params):
                arg = _normalize_param_name(p)
                op_parser.add_argument(f"--{arg}", required=True, help=f"Path parameter: {p}")
            for q in sorted(op.required_query_params):
                arg = _normalize_param_name(q)
                op_parser.add_argument(f"--{arg}", required=True, help=f"Required query parameter: {q}")
            if op.request_body:
                op_parser.add_argument("--body-json", default=None, help="Request body as JSON")
                op_parser.add_argument("--body-file", default=None, help="Path to JSON request body")
            op_parser.set_defaults(
                func=_run_operation,
                operation=op,
                write_capable=bool(op.is_write or defaults.get("write_capable", False)),
            )


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog=_TOOL_NAME)
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON")
    p.add_argument("--project-dir", default=None, help="Optional project directory")
    p.add_argument("--env-file", default=".env", help="Optional env file path")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging")
    p.add_argument("--debug", action="store_true", help="Show tracebacks")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format")
    p.add_argument("--log-file", default=None, help="Optional audit log path")
    p.add_argument("--apply", action="store_true", help="Apply a planned change")
    p.add_argument("--yes", action="store_true", help="Generic consent for high-risk operations")
    p.add_argument("--ack-irreversible", action="store_true", help="Explicit irreversible operation acknowledgement")
    p.add_argument("--ack-no-snapshot", action="store_true", help="Acknowledge no-snapshot operation")
    p.add_argument("--plan-out", default=None, help="Write dry-run plan to file")
    p.add_argument("--plan-in", default=None, help="Apply from plan file")
    p.add_argument("--receipt-out", default=None, help="Write apply receipt to file")
    p.add_argument("--run-id", default=None, help="Run id for local history")
    p.add_argument("--artifacts-dir", default=None, help="Override artifacts directory")
    p.add_argument("--no-artifacts", action="store_true", help="Disable local run artifacts")

    sub = p.add_subparsers(dest="root_cmd", required=False, parser_class=_ToolArgumentParser)

    onboarding = sub.add_parser("onboarding", help="Create local env file and show first setup steps")
    onboarding.add_argument("--no-write-env", action="store_true")
    onboarding.set_defaults(func=_cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Auth checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Check auth and token validity")
    auth_check.set_defaults(func=_cmd_auth_check, write_capable=False)

    runs = sub.add_parser("runs", help="Read local run index and summaries")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20)
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run")
    runs_show.add_argument("--run-id", required=True)
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    _register_operation_subcommands(sub, write_capable=True, defaults={})
    return p


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str,
    env_fingerprint: str | None,
    output_obj: dict | None,
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
            "ts": _now_iso(),
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


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    audit = CompositeAuditLogger([])  # temp; replaced after parse
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit:
        return 0

    command_str = _redact_command(argv)

    if bool(args.version):
        out.emit({"ok": True, "tool": _TOOL_NAME, "version": __version__})
        return 0

    if not getattr(args, "root_cmd", None):
        out.emit({"ok": False, "error": "Missing command. Use --help to see available commands.", "error_type": "ValidationError"})
        return 1

    cfg: Config | None = None
    apply = bool(args.apply)
    write_capable = bool(getattr(args, "write_capable", False))

    run_ctx: RunContext = init_run_context(
        env_file=str(args.env_file),
        enabled=write_capable,
        run_id=str(args.run_id) if args.run_id else None,
        artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
        no_artifacts=bool(args.no_artifacts),
    )

    run_audit_log = str(run_ctx.audit_log_path) if run_ctx.audit_log_path else None
    global_audit_log = str(args.log_file) if args.log_file else None

    loggers = []
    if run_audit_log:
        loggers.append(AuditLogger(path=run_audit_log, enabled=True))
    if global_audit_log:
        loggers.append(AuditLogger(path=global_audit_log, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    runs_index_path = runs_index_path_for_env_file(str(args.env_file))

    try:
        project_cfg, config_dir = load_project_config(str(getattr(args, "config", None) or "" ) or None)
        project_dir_arg = str(getattr(args, "project_dir", "") or "").strip()
        project_dir = Path(project_dir_arg) if project_dir_arg else (Path(config_dir) if config_dir else Path("."))

        if str(getattr(args, "root_cmd", "")) in {"runs", "onboarding", "auth"}:
            if str(args.root_cmd) in {"auth"}:
                cfg = load_config(str(args.env_file))
                timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
            else:
                timeout_s = float(args.timeout_s) if args.timeout_s is not None else 30

            ctx = {
                "cfg": cfg,
                "timeout_s": timeout_s,
                "verbose": bool(args.verbose),
                "out": out,
                "audit": audit,
                "tool": _TOOL_NAME,
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_irreversible": bool(args.ack_irreversible),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
                "user_agent": f"{_TOOL_NAME}/{__version__}",
            }
            try:
                return int(args.func(args, ctx))
            finally:
                audit.close()

        # Operational commands (generated operations)
        cfg = load_config(str(args.env_file))
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s

        if run_ctx.enabled and run_ctx.artifacts_dir and not args.apply and not args.plan_out:
            args.plan_out = str(run_ctx.artifacts_dir / "plan.json")
        if run_ctx.enabled and run_ctx.artifacts_dir and args.apply and not args.receipt_out:
            args.receipt_out = str(run_ctx.artifacts_dir / "receipt.json")

        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": _TOOL_NAME,
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "user_agent": f"{_TOOL_NAME}/{__version__}",
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_irreversible": bool(args.ack_irreversible),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": runs_index_path,
            "operation": args.operation,
        }

        audit.bind_context(
            {
                "tool": _TOOL_NAME,
                "version": __version__,
                "command": ctx["command_str"],
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.auth_fingerprint(),
                "run_id": run_ctx.run_id,
            }
        )

        rc = int(args.func(args, ctx))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL_NAME,
            version=__version__,
            command=ctx["command_str"],
            env_fingerprint=cfg.auth_fingerprint(),
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log or global_audit_log,
            audit_log_global_path=global_audit_log,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return rc
    except (ValidationError, SafetyError, NotSupportedError, RuntimeError) as e:
        out.emit(_error_payload(message=e, error_type=type(e).__name__, command=command_str))
        return 1
    except Exception as e:  # pragma: no cover - defensive fallback
        if bool(getattr(args, "debug", False)):
            raise
        out.emit(_error_payload(message=e, error_type=type(e).__name__, command=command_str))
        return 1
    finally:
        audit.close()


__all__ = [
    "build_parser",
    "main",
    "get_registered_operation_commands",
]
