from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_json = api_runtime.request_json


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    project = obj.get("Project")
    if not isinstance(project, dict):
        raise ValidationError("JSON file must contain a top-level Project object")
    return path, obj, project


def _extract_project_number_from_payload(project: dict[str, Any]) -> str | None:
    raw = project.get("ProjectNumber")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _extract_project_number_from_response(body: dict[str, Any] | None) -> str | None:
    if not isinstance(body, dict):
        return None
    project = body.get("Project")
    if not isinstance(project, dict):
        return None
    return _extract_project_number_from_payload(project)


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _verify_present(*, ctx: dict[str, Any], project_number: str) -> dict[str, Any]:
    path = f"/projects/{project_number}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _verify_absent(*, ctx: dict[str, Any], project_number: str) -> dict[str, Any]:
    path = f"/projects/{project_number}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        if "HTTP 404" in str(e):
            return {"ok": True, "path": path, "expected_http_status": 404}
        return {"ok": False, "path": path, "error": str(e)}
    if payload["status"] == 404:
        return {"ok": True, "path": path, "expected_http_status": 404}
    return {
        "ok": False,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
        "error": "Expected project to be absent after remove verification",
    }


def cmd_projects_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, project = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {
        "kind": "project",
        "action": "create",
        "path": "/projects",
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "project-create"],
        verification_plan={"type": "read-after-write", "path_template": "/projects/{ProjectNumber}"},
        rollback_notes="No generic rollback. Recreate the project explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("projects.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path="/projects",
        json_body=payload_obj,
        expect_json=True,
    )
    project_number = _extract_project_number_from_response(payload.get("body")) or _extract_project_number_from_payload(project)
    if not project_number:
        raise ValidationError("Could not determine ProjectNumber for create verification")
    verification = _verify_present(ctx=ctx, project_number=project_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_project_number": project_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("projects.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_projects_update(args: Any, ctx: dict[str, Any]) -> int:
    project_number = str(getattr(args, "project_number", "") or "").strip()
    payload_file, payload_obj, project = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    payload_project_number = _extract_project_number_from_payload(project)
    if payload_project_number and payload_project_number != project_number:
        raise ValidationError("Project.ProjectNumber in the JSON file must match --project-number")
    selector = {
        "kind": "project",
        "action": "update",
        "path": f"/projects/{project_number}",
        "project_number": project_number,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "project-update"],
        verification_plan={"type": "read-after-write", "path": f"/projects/{project_number}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("projects.update.plan", {"plan_out": plan_path, "project_number": project_number})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/projects/{project_number}",
        json_body=payload_obj,
        expect_json=True,
    )
    verification = _verify_present(ctx=ctx, project_number=project_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_project_number": project_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("projects.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_projects_remove(args: Any, ctx: dict[str, Any]) -> int:
    project_number = str(getattr(args, "project_number", "") or "").strip()
    selector = {
        "kind": "project",
        "action": "remove",
        "path": f"/projects/{project_number}",
        "project_number": project_number,
    }
    plan = _build_plan(
        action="remove",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", "project-remove", "irreversible"],
        verification_plan={"type": "absence-check", "path": f"/projects/{project_number}", "expect_http_status": 404},
        rollback_notes="No generic rollback. Recreate the project explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("projects.remove.plan", {"plan_out": plan_path, "project_number": project_number})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: removing a project requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: removing a project requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="remove", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(ctx=ctx, method="DELETE", path=f"/projects/{project_number}", expect_json=False)
    verification = _verify_absent(ctx=ctx, project_number=project_number)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_project_number": project_number,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("projects.remove.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
