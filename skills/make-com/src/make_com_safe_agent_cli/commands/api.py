from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path
from typing import Any

from ..config import credential_fingerprint
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..inventory import find_operation, load_inventory, operation_is_write, operations_by_family
from ..json_files import read_json_file, write_json_file
from ..sanitize import redact_url, redact_value
NO_SNAPSHOT_NOTE = (
    "Make does not document a guaranteed safe before-state read for this operation in the "
    "pinned inventory. Applying it requires explicit no-snapshot approval."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _redact(value: Any) -> Any:
    return redact_value(value)


def _parse_pairs(pairs: list[str] | None, *, label: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in pairs or []:
        if "=" not in raw:
            raise ValidationError(f"{label} values must use name=value")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"{label} name cannot be empty")
        parsed[key] = value
    return parsed


def _load_body(args: Any) -> Any:
    body_json = str(getattr(args, "body_json", "") or "").strip()
    body_file = str(getattr(args, "body_file", "") or "").strip()
    if body_json and body_file:
        raise ValidationError("Use either --body-json or --body-file, not both")
    if body_file:
        return read_json_file(body_file)
    if body_json:
        try:
            return json.loads(body_json)
        except json.JSONDecodeError as e:
            raise ValidationError(f"--body-json is not valid JSON: {e.msg}") from None
    return None


def _stable_sha256(value: Any) -> str | None:
    if value is None:
        return None
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _target_fingerprints(*, path_params: dict[str, str], query: dict[str, str]) -> dict[str, str | None]:
    return {
        "path_params_sha256": _stable_sha256(path_params),
        "query_sha256": _stable_sha256(query),
    }


def _validate_required(op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> None:
    missing: list[str] = []
    for param in op.get("parameters") or []:
        if not isinstance(param, dict) or not bool(param.get("required")):
            continue
        name = str(param.get("name") or "")
        location = str(param.get("in") or "")
        if location == "path" and name not in path_params:
            missing.append(f"path:{name}")
        if location == "query" and name not in query:
            missing.append(f"query:{name}")
    if bool(op.get("request_body_required")) and body is None:
        missing.append("body")
    if missing:
        raise ValidationError("Missing required input: " + ", ".join(missing))


def _build_url(base_url: str, path_template: str, path_params: dict[str, str]) -> str:
    path = path_template
    for key, value in path_params.items():
        path = path.replace("{" + key + "}", str(value))
    if "{" in path or "}" in path:
        raise ValidationError(f"Missing path parameter for {path_template}")
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def _headers(ctx: dict[str, Any]) -> dict[str, str]:
    cfg = ctx["cfg"]
    headers = {"Accept": "application/json"}
    if cfg.token:
        headers["Authorization"] = f"Token {cfg.token}"
    return headers


def _request(ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> dict[str, Any]:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing MAKE_API_TOKEN")
    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"make-com-safe/{ctx.get('tool_version')}",
    )
    response = client.request(
        str(op["method"]).upper(),
        _build_url(cfg.base_url, str(op["path"]), path_params),
        headers=_headers(ctx),
        params=query or None,
        json_body=body if isinstance(body, dict) else None,
        data=body if body is not None and not isinstance(body, dict) else None,
        retries=2,
        url_sanitizer=lambda raw_url: redact_url(raw_url, path_params=path_params, query=query),
    )
    try:
        parsed = response.json()
    except Exception:
        parsed = {"text": response.text()}
    return {
        "status": response.status,
        "url": redact_url(response.url, path_params=path_params, query=query),
        "body": _redact(parsed),
    }


def _build_plan(ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> dict[str, Any]:
    risk_reasons = ["make-write", f"method:{str(op['method']).upper()}"]
    if bool(op.get("no_snapshot")):
        risk_reasons.append("no-snapshot")
    if any(term in str(op.get("path", "")).lower() for term in ("scenario", "hook", "connection", "token", "key", "team", "organization", "sso")):
        risk_reasons.append("sensitive-make-resource")
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "credential_fingerprint": credential_fingerprint(ctx["cfg"].token),
        "command": ctx.get("command_str"),
        "operation": {
            "family": op.get("family_slug"),
            "command": op.get("command"),
            "summary": op.get("summary"),
            "method": str(op.get("method")).upper(),
            "path": op.get("path"),
            "source_url": op.get("source_url"),
            "scopes": op.get("scopes") or [],
        },
        "target": {"path_params": _redact(path_params), "query": _redact(query)},
        "target_fingerprints": _target_fingerprints(path_params=path_params, query=query),
        "request_body": _redact(body),
        "request_body_sha256": _stable_sha256(body),
        "risk_level": "high" if any(r in risk_reasons for r in ("no-snapshot", "sensitive-make-resource")) else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": [
            "review operation, target IDs, query, and redacted body",
            "apply must use this saved plan with --plan-in",
            "base URL must match the plan env_fingerprint",
            "Make credential fingerprint must match the reviewed plan",
        ],
        "snapshot": {"available": False, "warning": NO_SNAPSHOT_NOTE},
        "verification_plan": {"type": "http-status-and-response", "notes": "Verify the Make API response and, when available, follow with a read command for the target."},
        "rollback": {"supported": False, "notes": "No generic rollback is promised for Make API writes."},
    }


def _validate_plan(
    plan: dict[str, Any],
    ctx: dict[str, Any],
    op: dict[str, Any],
    *,
    path_params: dict[str, str],
    query: dict[str, str],
    body: Any,
) -> None:
    if str(plan.get("env_fingerprint") or "") != ctx["cfg"].base_url:
        raise SafetyError("Refused: plan base URL does not match current Make base URL")
    if plan.get("credential_fingerprint") != credential_fingerprint(ctx["cfg"].token):
        raise SafetyError("Refused: current Make credential fingerprint does not match the reviewed plan")
    planned = plan.get("operation")
    if not isinstance(planned, dict):
        raise SafetyError("Refused: plan is missing operation details")
    if str(planned.get("family")) != str(op.get("family_slug")) or str(planned.get("command")) != str(op.get("command")):
        raise SafetyError("Refused: plan operation does not match this command")
    planned_target = plan.get("target")
    if not isinstance(planned_target, dict):
        raise SafetyError("Refused: plan is missing target")
    planned_fingerprints = plan.get("target_fingerprints")
    if isinstance(planned_fingerprints, dict):
        current_fingerprints = _target_fingerprints(path_params=path_params, query=query)
        if planned_fingerprints.get("path_params_sha256") != current_fingerprints["path_params_sha256"]:
            raise SafetyError("Refused: plan path parameters do not match this command")
        if planned_fingerprints.get("query_sha256") != current_fingerprints["query_sha256"]:
            raise SafetyError("Refused: plan query parameters do not match this command")
    else:
        if planned_target.get("path_params") != path_params:
            raise SafetyError("Refused: plan path parameters do not match this command")
        if planned_target.get("query") != _redact(query):
            raise SafetyError("Refused: plan query parameters do not match this command")
    if plan.get("request_body_sha256") != _stable_sha256(body):
        raise SafetyError("Refused: request body does not match the reviewed plan")


def cmd_api_list(args: Any, ctx: dict[str, Any]) -> int:
    inventory = load_inventory(str(getattr(args, "inventory", "") or "") or None)
    families = operations_by_family(inventory)
    out = {
        "ok": True,
        "operation_count": len(inventory.get("operations") or []),
        "family_count": len(families),
        "families": [
            {"family": family, "commands": [str(op.get("command")) for op in ops], "count": len(ops)}
            for family, ops in families.items()
        ],
    }
    ctx["audit"].write("api.list", {"operation_count": out["operation_count"]})
    ctx["out"].emit(out)
    return 0


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    inventory = load_inventory(str(getattr(args, "inventory", "") or "") or None)
    family = str(getattr(args, "family", "") or "")
    command = str(getattr(args, "operation", "") or "")
    op = find_operation(inventory, family, command)
    if not op:
        raise ValidationError(f"Unknown Make API command: {family} {command}")
    path_params = _parse_pairs(getattr(args, "path_param", None), label="--path-param")
    query = _parse_pairs(getattr(args, "query", None), label="--query")
    body = _load_body(args)
    _validate_required(op, path_params=path_params, query=query, body=body)

    if not operation_is_write(op):
        result = _request(ctx, op, path_params=path_params, query=query, body=body)
        out = {"ok": True, "dry_run": False, "operation": op.get("operation_key"), "response": result}
        ctx["audit"].write("api.read", {"operation": op.get("operation_key"), "status": result["status"]})
        ctx["out"].emit(out)
        return 0

    if ctx.get("plan_in"):
        plan = read_json_file(str(ctx["plan_in"]))
        if not isinstance(plan, dict):
            raise ValidationError("Plan file must be a JSON object")
    else:
        plan = _build_plan(ctx, op, path_params=path_params, query=query, body=body)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(str(plan_out), plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("api.write.plan", {"operation": op.get("operation_key"), "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: Make writes must apply from a reviewed --plan-in file")
    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: Make writes require --yes after plan review")
    if bool(op.get("no_snapshot")) and not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError("Refused: this Make write requires --ack-no-snapshot")
    if bool(op.get("destructive")) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: destructive Make writes require --ack-irreversible")

    _validate_plan(plan, ctx, op, path_params=path_params, query=query, body=body)
    result = _request(ctx, op, path_params=path_params, query=query, body=body)
    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "credential_fingerprint": credential_fingerprint(ctx["cfg"].token),
        "operation": plan.get("operation"),
        "target": plan.get("target"),
        "snapshot": plan.get("snapshot"),
        "verification": {"ok": 200 <= int(result["status"]) < 300, "response_status": result["status"]},
        "response": result,
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(str(receipt_out), receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("api.write.apply", {"operation": op.get("operation_key"), "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_api_schema(args: Any, ctx: dict[str, Any]) -> int:
    inventory = load_inventory(str(getattr(args, "inventory", "") or "") or None)
    op = find_operation(inventory, str(args.family), str(args.operation))
    if not op:
        raise ValidationError(f"Unknown Make API command: {args.family} {args.operation}")
    ctx["audit"].write("api.schema", {"operation": op.get("operation_key")})
    ctx["out"].emit({"ok": True, "operation": _redact(op)})
    return 0
