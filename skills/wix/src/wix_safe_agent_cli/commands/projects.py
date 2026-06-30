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


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_project_type(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --type")

    project_type = str(raw).strip().upper()
    if not project_type:
        raise ValidationError("Missing --type")
    if project_type != "WIX":
        raise ValidationError("Only --type WIX is supported in this slice")
    return project_type


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        return None
    return value


def _coerce_apps(raw: Any) -> list[dict[str, str]] | None:
    if raw is None:
        return None

    value = _read_json_arg(raw, field="apps-json")
    if not isinstance(value, list):
        raise ValidationError("--apps-json must be a JSON array")
    if len(value) > 100:
        raise ValidationError("--apps-json can contain at most 100 items")

    apps: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"--apps-json[{i}] must be a JSON object")

        raw_app_def_id = item.get("appDefId")
        if raw_app_def_id is None:
            raise ValidationError(f"--apps-json[{i}].appDefId is required")
        if not isinstance(raw_app_def_id, str):
            raise ValidationError(f"--apps-json[{i}].appDefId must be a non-empty string")
        app_def_id = raw_app_def_id.strip()
        if not app_def_id:
            raise ValidationError(f"--apps-json[{i}].appDefId cannot be empty")

        if app_def_id in seen:
            raise ValidationError(f"--apps-json contains duplicate appDefId: {app_def_id}")

        seen.add(app_def_id)
        apps.append({"appDefId": app_def_id})

    return apps


def _resolve_projects_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="projects",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _build_selector(*, project_type: str, name: str) -> dict[str, Any]:
    return {"kind": "wix-project", "operation": "create-project", "type": project_type, "name": name}


def _build_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "projects.create-project",
        "risk_level": "high",
        "risk_reasons": ["funnel-project-create"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --apply and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
        },
        "proposed_changes": [{"operation": "create", "type": selector.get("type", ""), "name": selector.get("name", "")}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "No post-write readback exists yet because no projects read command is shipped.",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan missing baseline")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="projects")


def _build_receipt(
    *,
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    selector: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "projects.create-project",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _verify_create_response(
    *,
    response: dict[str, Any],
    requested_template_id: str | None,
    requested_apps: list[dict[str, str]] | None,
) -> dict[str, Any]:
    notes = ["No post-write readback exists yet because no projects read command is shipped."]
    project = response.get("project")
    if not isinstance(project, dict):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "; ".join([*notes, "Response did not include a project object"]),
            "response": response,
        }

    meta_site_id = str(project.get("metaSiteId") or "").strip()
    site_id = str(project.get("siteId") or "").strip()

    ok = True
    if not meta_site_id:
        ok = False
        notes.append("Response project.metaSiteId is required")
    if not site_id:
        ok = False
        notes.append("Response project.siteId is required")

    if requested_template_id is not None and "templateId" in project:
        response_template_id = str(project.get("templateId") or "").strip()
        if response_template_id != requested_template_id:
            ok = False
            notes.append("Response project.templateId does not match requested templateId")

    if requested_apps and "apps" in project:
        response_apps = project.get("apps")
        if not isinstance(response_apps, list):
            ok = False
            notes.append("Response project.apps is not a list")
        else:
            response_app_def_ids = {
                str(item.get("appDefId") or "").strip()
                for item in response_apps
                if isinstance(item, dict) and str(item.get("appDefId") or "").strip()
            }
            requested_ids = [app.get("appDefId", "") for app in requested_apps]
            missing = [app_id for app_id in requested_ids if app_id not in response_app_def_ids]
            if missing:
                ok = False
                notes.append("Response project.apps does not include requested appDefId values: " + ", ".join(missing))

    return {
        "ok": ok,
        "type": "provider-response",
        "notes": " ".join(notes),
        "response": response,
    }


def _normalize_request(
    *,
    project_type: str,
    name: str,
    template_id: str | None,
    folder_id: str | None,
    apps: list[dict[str, str]] | None,
) -> dict[str, Any]:
    body = {"type": project_type, "name": name}
    if template_id:
        body["templateId"] = template_id
    if folder_id:
        body["folderId"] = folder_id
    if apps is not None:
        body["apps"] = apps
    return {
        "method": "POST",
        "path": "/funnel/projects/v1/create",
        "body": body,
    }


def cmd_projects_create_project(args, ctx) -> int:
    try:
        project_type = _coerce_project_type(getattr(args, "type", None))
        name = _coerce_required_text(getattr(args, "name", None), field="name")
        template_id = _coerce_optional_text(getattr(args, "template_id", None), field="template-id")
        folder_id = _coerce_optional_text(getattr(args, "folder_id", None), field="folder-id")
        apps = _coerce_apps(getattr(args, "apps_json", None))

        request = _normalize_request(
            project_type=project_type,
            name=name,
            template_id=template_id,
            folder_id=folder_id,
            apps=apps,
        )
        selector = _build_selector(project_type=project_type, name=name)
        if template_id:
            selector["template_id"] = template_id
        if folder_id:
            selector["folder_id"] = folder_id
        if apps is not None:
            selector["apps"] = [app.get("appDefId", "") for app in apps]

        auth_headers, auth_mode = _resolve_projects_auth(ctx=ctx)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="projects.create-project",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(request=request, selector=selector, ctx=ctx)

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "projects.create-project",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="projects.create-project",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        response = _request_json(
            method=request["method"],
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_create_response(
            response=response,
            requested_template_id=template_id,
            requested_apps=apps,
        )

        receipt = _build_receipt(
            request=request,
            response=response,
            verification=verification,
            selector=selector,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "projects.create-project",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "projects.create-project",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "projects.create-project"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "projects.create-project",
        }
        ctx["out"].emit(out)
        return 1
