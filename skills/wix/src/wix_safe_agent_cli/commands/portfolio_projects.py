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


COMMAND_FAMILY = "portfolio-projects"
BASE_PATH = "/portfolio/v1/projects"
BULK_UPDATE_PATH = "/portfolio/projects/projects/api/v1/bulk/portfolio/projects/update"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    if raw is None and allow_empty:
        return {}
    text = _coerce_text(raw, field=field)
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
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
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _project_object(payload: dict[str, Any]) -> dict[str, Any]:
    project = payload.get("project")
    if isinstance(project, dict):
        return project
    return payload


def _revision_from_payload(payload: dict[str, Any]) -> str | None:
    revision = _project_object(payload).get("revision")
    if revision is None:
        return None
    value = str(revision).strip()
    return value or None


def _body_with_id_and_current_revision(*, body: dict[str, Any], project_id: str, current_revision: str) -> dict[str, Any]:
    updated = dict(body)
    project = updated.get("project")
    if isinstance(project, dict):
        provided_id = project.get("id")
        if provided_id is not None and str(provided_id).strip() != project_id:
            raise SafetyError("Refused: provided project.id does not match --project-id")
        provided_revision = project.get("revision")
        if provided_revision is not None and str(provided_revision).strip() != current_revision:
            raise SafetyError("Refused: provided project.revision does not match current revision")
        revised_project = dict(project)
        revised_project["id"] = project_id
        revised_project["revision"] = current_revision
        updated["project"] = revised_project
        return updated

    provided_id = updated.get("id")
    if provided_id is not None and str(provided_id).strip() != project_id:
        raise SafetyError("Refused: provided project id does not match --project-id")
    provided_revision = updated.get("revision")
    if provided_revision is not None and str(provided_revision).strip() != current_revision:
        raise SafetyError("Refused: provided project revision does not match current revision")
    updated["id"] = project_id
    updated["revision"] = current_revision
    return {"project": updated}


def _project_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValidationError("Each project entry must be a JSON object")
    project = entry.get("project")
    if isinstance(project, dict):
        return project
    return entry


def _project_id_from_entry(entry: dict[str, Any]) -> str:
    project_id = _project_entry(entry).get("id")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValidationError("Each bulk project update entry must include project.id")
    return project_id.strip()


def _with_bulk_current_revisions(*, body: dict[str, Any], before_states: dict[str, dict[str, Any]]) -> dict[str, Any]:
    projects = body.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValidationError("--projects-json must contain a non-empty projects array")
    updated_projects: list[dict[str, Any]] = []
    for entry in projects:
        project_id = _project_id_from_entry(entry)
        current_revision = _revision_from_payload(before_states[project_id])
        if not current_revision:
            raise SafetyError(f"Refused: current project revision was not found for {project_id}")
        project = _project_entry(entry)
        provided_revision = project.get("revision")
        if provided_revision is not None and str(provided_revision).strip() != current_revision:
            raise SafetyError(f"Refused: provided project.revision does not match current revision for {project_id}")
        revised_project = dict(project)
        revised_project["id"] = project_id
        revised_project["revision"] = current_revision
        if "project" in entry:
            revised_entry = dict(entry)
            revised_entry["project"] = revised_project
            updated_projects.append(revised_entry)
        else:
            updated_projects.append(revised_project)
    updated = dict(body)
    updated["projects"] = updated_projects
    return updated


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    before_state: Any,
    requires_ack: bool,
    risk_reasons: list[str],
    verification_type: str,
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": before_state},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": verification_type, "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use before-state as a manual reference."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _emit_read(*, method_name: str, http_method: str, path: str, params: dict[str, Any] | None, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _emit_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    before_state: Any,
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_type: str,
    verification_notes: str,
    verification_paths: list[str] | None = None,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        before_state=before_state,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_type=verification_type,
        verification_notes=verification_notes,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
    verification: dict[str, Any] = {"ok": True, "type": verification_type, "notes": verification_notes}
    if verification_paths:
        verification["after"] = [
            _request_json(method="GET", path=read_path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for read_path in verification_paths
        ]
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": verification,
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response, "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_portfolio_projects_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _read_json_arg(getattr(args, "params_json", None), field="params-json", allow_empty=True)
        return _emit_read(method_name=method, http_method="GET", path=BASE_PATH, params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        project_id = _coerce_text(getattr(args, "project_id", None), field="project-id")
        params = _read_json_arg(getattr(args, "params_json", None), field="params-json", allow_empty=True)
        return _emit_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{project_id}", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", None), field="query-json", allow_empty=True)
        return _emit_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "project_json", None), field="project-json")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-project"}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-create"],
            verification_type="provider-response",
            verification_notes="Create is verified by Wix provider response; reread the returned project id when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        project_id = _coerce_text(getattr(args, "project_id", None), field="project-id")
        body = _read_json_arg(getattr(args, "project_json", None), field="project-json")
        auth = _resolve_auth(ctx)
        path = f"{BASE_PATH}/{project_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        current_revision = _revision_from_payload(before_state)
        if not current_revision:
            raise SafetyError("Refused: current project revision was not found")
        body = _body_with_id_and_current_revision(body=body, project_id=project_id, current_revision=current_revision)
        return _emit_write(
            method_name=method,
            http_method="PATCH",
            path=path,
            body=body,
            selector={"kind": COMMAND_FAMILY, "project_id": project_id},
            proposed_changes=[{"operation": "update-project", "project_id": project_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-update", "requires-current-revision"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading the project after update.",
            verification_paths=[path],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        project_id = _coerce_text(getattr(args, "project_id", None), field="project-id")
        auth = _resolve_auth(ctx)
        path = f"{BASE_PATH}/{project_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        return _emit_write(
            method_name=method,
            http_method="DELETE",
            path=path,
            body=None,
            selector={"kind": COMMAND_FAMILY, "project_id": project_id},
            proposed_changes=[{"operation": "delete-project", "project_id": project_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["portfolio-project-delete", "irreversible-delete"],
            verification_type="provider-response",
            verification_notes="Delete is verified by Wix provider response; before-state is captured in the reviewed plan.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_projects_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "projects_json", None), field="projects-json")
        projects = body.get("projects")
        if not isinstance(projects, list) or not projects:
            raise ValidationError("--projects-json must contain a non-empty projects array with project ids")
        project_ids = [_project_id_from_entry(entry) for entry in projects]
        auth = _resolve_auth(ctx)
        before_states = {
            project_id: _request_json(method="GET", path=f"{BASE_PATH}/{project_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for project_id in project_ids
        }
        body = _with_bulk_current_revisions(body=body, before_states=before_states)
        return _emit_write(
            method_name=method,
            http_method="PATCH",
            path=BULK_UPDATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "project_ids": project_ids},
            proposed_changes=[{"operation": "bulk-update-projects", "project_ids": project_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-bulk-update", "requires-current-revisions"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading each project after bulk update.",
            verification_paths=[f"{BASE_PATH}/{project_id}" for project_id in project_ids],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
