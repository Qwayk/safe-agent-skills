from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from ..config import credential_fingerprint
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..inventory import find_operation, find_operation_by_id, load_inventory, operation_is_write, operations_by_family
from ..json_files import read_json_file, write_json_file
from ..sanitize import redact_pair_map, redact_url, redact_value


NO_SNAPSHOT_NOTE = (
    "n8n does not guarantee a safe before-state read for this operation from the pinned "
    "public API spec. Live apply requires explicit no-snapshot approval."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _parse_pairs(pairs: list[str] | None, *, label: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs or []:
        if "=" not in raw:
            raise ValidationError(f"{label} values must use name=value")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"{label} name cannot be empty")
        out[key] = value
    return out


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


def _validate_required(op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> None:
    missing: list[str] = []
    for param in op.get("parameters") or []:
        if not isinstance(param, dict) or not bool(param.get("required")):
            continue
        location = str(param.get("in") or "")
        name = str(param.get("name") or "")
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


def _client(ctx: dict[str, Any]) -> HttpClient:
    return HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"n8n-safe-agent-cli/{ctx.get('tool_version')}",
    )


def _headers(ctx: dict[str, Any]) -> dict[str, str]:
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise ValidationError("Missing N8N_API_KEY")
    return {"Accept": "application/json", "Content-Type": "application/json", "X-N8N-API-KEY": cfg.api_key}


def _request(ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> dict[str, Any]:
    response = _client(ctx).request(
        str(op["method"]).upper(),
        _build_url(ctx["cfg"].base_url, str(op["path"]), path_params),
        headers=_headers(ctx),
        params=query or None,
        json_body=body if isinstance(body, dict) else None,
        data=body if body is not None and not isinstance(body, dict) else None,
        retries=1,
        url_sanitizer=redact_url,
    )
    try:
        parsed = response.json()
    except Exception:
        parsed = {"text": response.text()}
    return {"status": response.status, "url": redact_url(response.url), "body": _redact_response(op, parsed)}


def _redact_response(op: dict[str, Any], parsed: Any) -> Any:
    safe = redact_value(parsed)
    family = str(op.get("family_slug") or "")
    if family not in {"credential", "execution"}:
        return safe

    def scrub(value: Any) -> Any:
        if isinstance(value, dict):
            out: dict[str, Any] = {}
            for key, inner in value.items():
                if str(key).lower() == "data":
                    out[str(key)] = "[REDACTED]"
                else:
                    out[str(key)] = scrub(inner)
            return out
        if isinstance(value, list):
            return [scrub(v) for v in value]
        return value

    return scrub(safe)


def _snapshot(ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str]) -> dict[str, Any]:
    snap_op = find_operation_by_id(str(op.get("snapshot_operation_id") or ""))
    if not snap_op:
        return {"available": False, "warning": NO_SNAPSHOT_NOTE}
    try:
        before = _request(ctx, snap_op, path_params=path_params, query={}, body=None)
        return {"available": True, "operation_id": snap_op.get("operation_id"), "before_state": before}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "operation_id": snap_op.get("operation_id"), "warning": f"{NO_SNAPSHOT_NOTE} Snapshot attempt failed: {type(e).__name__}."}


def _risk_reasons(op: dict[str, Any]) -> list[str]:
    text = " ".join([str(op.get("family_slug") or ""), str(op.get("command") or ""), str(op.get("path") or ""), str(op.get("summary") or "")]).lower()
    reasons = ["n8n-write", f"method:{str(op.get('method')).upper()}"]
    for marker, reason in (
        ("delete", "destructive"),
        ("stop", "production-risk"),
        ("activate", "production-risk"),
        ("deactivate", "production-risk"),
        ("archive", "production-risk"),
        ("transfer", "permission-or-ownership-change"),
        ("user", "permission-change"),
        ("role", "permission-change"),
        ("credential", "auth-or-secret-risk"),
        ("source-control", "production-risk"),
        ("package", "code-or-package-change"),
        ("execution", "execution-change"),
        ("data-table", "data-change"),
    ):
        if marker in text:
            reasons.append(reason)
    return sorted(set(reasons))


def _build_plan(ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> dict[str, Any]:
    snapshot = _snapshot(ctx, op, path_params=path_params) if ctx["cfg"].api_key else {"available": False, "warning": NO_SNAPSHOT_NOTE}
    reasons = _risk_reasons(op)
    if not snapshot.get("available"):
        reasons.append("no-snapshot")
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "credential_fingerprint": credential_fingerprint(ctx["cfg"].api_key),
        "command": ctx.get("command_str"),
        "operation": {
            "family": op.get("family_slug"),
            "command": op.get("command"),
            "operation_id": op.get("operation_id"),
            "summary": op.get("summary"),
            "method": op.get("method"),
            "path": op.get("path"),
            "scopes": op.get("scopes") or [],
        },
        "target": {"path_params": redact_pair_map(path_params), "query": redact_pair_map(query)},
        "target_sha256": _stable_sha256({"path_params": path_params, "query": query}),
        "request_body": redact_value(body),
        "request_body_sha256": _stable_sha256(body),
        "risk_level": "high" if any(r in reasons for r in ("destructive", "production-risk", "permission-change", "auth-or-secret-risk", "no-snapshot")) else "medium",
        "risk_reasons": sorted(set(reasons)),
        "snapshot": snapshot,
        "preconditions": [
            "review operation, target IDs, query, and redacted body",
            "apply must use this saved plan with --plan-in",
            "base URL and credential fingerprint must match the reviewed plan",
            "no-snapshot apply also needs --ack-no-snapshot",
        ],
        "verification_plan": {"type": "http-status-and-response", "notes": "After apply, inspect the n8n response and follow with the closest read command when the API allows it."},
        "rollback": {"supported": False, "notes": "No generic rollback is promised for n8n workflow, credential, user, package, execution, or source-control changes."},
    }


def _validate_plan(plan: dict[str, Any], ctx: dict[str, Any], op: dict[str, Any], *, path_params: dict[str, str], query: dict[str, str], body: Any) -> None:
    if str(plan.get("env_fingerprint") or "") != ctx["cfg"].base_url:
        raise SafetyError("Refused: plan base URL does not match current N8N_BASE_URL")
    if plan.get("credential_fingerprint") != credential_fingerprint(ctx["cfg"].api_key):
        raise SafetyError("Refused: current API key fingerprint does not match the reviewed plan")
    planned = plan.get("operation")
    if not isinstance(planned, dict):
        raise SafetyError("Refused: plan is missing operation details")
    if str(planned.get("family")) != str(op.get("family_slug")) or str(planned.get("command")) != str(op.get("command")):
        raise SafetyError("Refused: plan operation does not match this command")
    if plan.get("target_sha256") != _stable_sha256({"path_params": path_params, "query": query}):
        raise SafetyError("Refused: path or query target does not match the reviewed plan")
    if plan.get("request_body_sha256") != _stable_sha256(body):
        raise SafetyError("Refused: request body does not match the reviewed plan")


def _write_if_requested(path: str | None, payload: dict[str, Any]) -> None:
    if path:
        write_json_file(Path(path), payload)


def cmd_api_list(args: Any, ctx: dict[str, Any]) -> int:
    inventory = load_inventory()
    families = operations_by_family(inventory)
    payload = {
        "ok": True,
        "operation_count": len(inventory.get("operations") or []),
        "family_count": len(families),
        "families": [{"family": family, "commands": [str(op.get("command")) for op in ops], "count": len(ops)} for family, ops in families.items()],
    }
    ctx["out"].emit(payload)
    return 0


def cmd_api_operation(args: Any, ctx: dict[str, Any]) -> int:
    family = str(getattr(args, "api_family"))
    command = str(getattr(args, "api_command"))
    op = find_operation(family, command)
    path_params = _parse_pairs(getattr(args, "path_param", None), label="--path-param")
    query = _parse_pairs(getattr(args, "query", None), label="--query")
    body = _load_body(args)
    _validate_required(op, path_params=path_params, query=query, body=body)

    if not operation_is_write(op):
        result = _request(ctx, op, path_params=path_params, query=query, body=body)
        payload = {"ok": True, "operation": op, "request": {"path_params": redact_pair_map(path_params), "query": redact_pair_map(query)}, "response": result}
        ctx["audit"].write("api.read", payload)
        ctx["out"].emit(payload)
        return 0

    plan = _build_plan(ctx, op, path_params=path_params, query=query, body=body)

    if not bool(ctx.get("apply")):
        _write_if_requested(ctx.get("plan_out"), plan)
        payload = {"ok": True, "dry_run": True, "operation": op, "plan": plan, "plan_path": ctx.get("plan_out")}
        ctx["audit"].write("api.plan", payload)
        ctx["out"].emit(payload)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: live n8n writes require --apply --yes")
    if not ctx.get("plan_in"):
        raise SafetyError("Refused: live n8n writes require --plan-in from the reviewed dry-run plan")
    reviewed_plan = read_json_file(str(ctx["plan_in"]))
    _validate_plan(reviewed_plan, ctx, op, path_params=path_params, query=query, body=body)
    if not bool((reviewed_plan.get("snapshot") or {}).get("available")) and not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError("Refused: this n8n write has no verified before-state snapshot; add --ack-no-snapshot only after reviewing that risk")
    if any(r in set(reviewed_plan.get("risk_reasons") or []) for r in {"destructive", "production-risk", "permission-change", "auth-or-secret-risk", "code-or-package-change"}) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: this high-risk n8n write requires --ack-irreversible")

    response = _request(ctx, op, path_params=path_params, query=query, body=body)
    receipt = {
        "ok": True,
        "applied": True,
        "generated_at_utc": _utc_now(),
        "operation": plan["operation"],
        "target": plan["target"],
        "request_body_sha256": plan.get("request_body_sha256"),
        "risk_reasons": plan.get("risk_reasons"),
        "response": response,
        "verification": {"status": "response-captured", "notes": "Follow with the closest read command when the target still exists."},
    }
    _write_if_requested(ctx.get("receipt_out"), receipt)
    payload = {"ok": True, "applied": True, "receipt": receipt, "receipt_path": ctx.get("receipt_out")}
    ctx["audit"].write("api.apply", payload)
    ctx["out"].emit(payload)
    return 0
