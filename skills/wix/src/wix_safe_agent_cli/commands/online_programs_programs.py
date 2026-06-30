from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "online-programs-programs"
BASE_PATH = "/online-programs/v3/programs"


def _text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _object_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _array_arg(raw: Any, *, field: str, max_items: int) -> list[Any]:
    value = _text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    if len(payload) > max_items:
        raise ValidationError(f"--{field} supports at most {max_items} items")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if json_body is not None:
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    ctx["out"].emit({"ok": False, "method": method, "error": str(exc), "error_type": exc.__class__.__name__})
    return 1


def _read(method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Online Programs plans in this slice do not capture full program before-state."},
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use online-programs-programs get, query, or search to inspect provider state."},
    }


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _plan(method_name=method_name, request=request, selector=selector, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons, verification_notes=verification_notes)
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    loaded_plan = _load_plan(ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": request,
        "response": response,
        "verified": {"type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def _bool_option(raw: Any) -> bool | None:
    if raw is None:
        return None
    return str(raw).lower() == "true"


def _program_body(raw: Any, *, field: str) -> dict[str, Any]:
    body = _object_arg(raw, field=field)
    return body if "program" in body else {"program": body}


def _program_id_from_body(body: dict[str, Any], *, field: str) -> str:
    program = body.get("program")
    if not isinstance(program, dict):
        raise ValidationError(f"--{field} must include program")
    program_id = program.get("id") or program.get("_id")
    if not isinstance(program_id, str) or not program_id.strip():
        raise ValidationError(f"--{field} must include program.id")
    if not str(program.get("revision") or "").strip():
        raise ValidationError(f"--{field} must include program.revision")
    return program_id.strip()


def _bulk_body(args: Any) -> dict[str, Any]:
    programs = _array_arg(getattr(args, "programs_json", None), field="programs-json", max_items=100)
    for item in programs:
        if not isinstance(item, dict):
            raise ValidationError("--programs-json items must be objects")
        program = item.get("program")
        if not isinstance(program, dict):
            raise ValidationError("--programs-json items must include program")
        if not str(program.get("id") or program.get("_id") or "").strip():
            raise ValidationError("--programs-json items must include program.id")
        if not str(program.get("revision") or "").strip():
            raise ValidationError("--programs-json items must include program.revision")
    body: dict[str, Any] = {"programs": programs}
    return_entity = _bool_option(getattr(args, "return_entity", None))
    if return_entity is not None:
        body["returnEntity"] = return_entity
    return body


def cmd_online_programs_programs_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _program_body(getattr(args, "program_json", None), field="program-json")
        return _write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"operation": "create", "title": body.get("program", {}).get("description", {}).get("title")}, ctx=ctx, requires_ack=False, risk_reasons=["online-program-create-draft"], verification_notes="Inspect returned program id and revision.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        program_id = _text(getattr(args, "program_id", None), field="program-id")
        return _read(method, "GET", f"{BASE_PATH}/{program_id}", None, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _program_body(getattr(args, "program_json", None), field="program-json")
        program_id = _program_id_from_body(body, field="program-json")
        return _write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{program_id}", body=body, selector={"programId": program_id, "revision": body["program"]["revision"]}, ctx=ctx, requires_ack=False, risk_reasons=["online-program-update"], verification_notes="Inspect provider response and reread the program if needed.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        program_id = _text(getattr(args, "program_id", None), field="program-id")
        return _write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{program_id}", body=None, selector={"programId": program_id}, ctx=ctx, requires_ack=True, risk_reasons=["online-program-delete", "permanent-delete"], verification_notes="Provider response is the deletion proof; a later get should fail or stop returning the program.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _object_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _read(method, "POST", f"{BASE_PATH}/query", body if "query" in body else {"query": body}, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_search(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search"
    try:
        body = _object_arg(getattr(args, "search_json", "{}"), field="search-json", allow_empty=True)
        return _read(method, "POST", f"{BASE_PATH}/search", body if "search" in body else {"search": body}, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _object_arg(getattr(args, "filter_json", "{}"), field="filter-json", allow_empty=True)
        return _read(method, "POST", f"{BASE_PATH}/count", body if "filter" in body else {"filter": body}, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _bulk_body(args)
        selector = {"count": len(body["programs"]), "programIds": [item["program"].get("id") or item["program"].get("_id") for item in body["programs"]]}
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH.rsplit('/', 1)[0]}/bulk/programs/update", body=body, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["online-program-bulk-update", "multi-entity-write"], verification_notes="Inspect each bulk result and reread changed programs if needed.")
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _program_lifecycle_command(args: Any, ctx: dict[str, Any], *, command: str, suffix: str, requires_ack: bool, risk_reasons: list[str], notes: str) -> int:
    method = f"{COMMAND_FAMILY}.{command}"
    try:
        program_id = _text(getattr(args, "program_id", None), field="program-id")
        return _write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{program_id}/{suffix}", body=None, selector={"programId": program_id}, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons, verification_notes=notes)
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_archive(args, ctx) -> int:
    return _program_lifecycle_command(args, ctx, command="archive", suffix="archive", requires_ack=True, risk_reasons=["online-program-archive", "changes-public-discovery", "seo-slug-replaced"], notes="Inspect returned program status/revision and reread the program if needed.")


def cmd_online_programs_programs_duplicate(args, ctx) -> int:
    return _program_lifecycle_command(args, ctx, command="duplicate", suffix="duplicate", requires_ack=False, risk_reasons=["online-program-duplicate", "creates-new-draft"], notes="Inspect returned duplicated program id and revision.")


def cmd_online_programs_programs_end(args, ctx) -> int:
    return _program_lifecycle_command(args, ctx, command="end", suffix="end", requires_ack=True, risk_reasons=["online-program-end", "cancels-scheduled-end-task"], notes="Inspect returned program status/revision and reread the program if needed.")


def cmd_online_programs_programs_list_samples(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-samples"
    try:
        _ = args
        return _read(method, "GET", f"{BASE_PATH}/samples", None, ctx)
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_online_programs_programs_publish(args, ctx) -> int:
    return _program_lifecycle_command(args, ctx, command="publish", suffix="publish", requires_ack=False, risk_reasons=["online-program-publish", "makes-draft-visible"], notes="Inspect returned program status/revision and reread the program if needed.")
