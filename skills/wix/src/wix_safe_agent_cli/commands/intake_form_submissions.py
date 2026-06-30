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


COMMAND_FAMILY = "intake-form-submissions"
BASE_PATH = "/_api/intake-forms/v1/submissions"
COUNT_PATH = "/_api/intake-forms/v1/submissions/count"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_object(raw: Any, *, field: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if raw is None:
        return dict(default or {})
    value = _coerce_text(raw, field=field)
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
    return payload


def _required_id(raw: Any, *, field: str) -> str:
    return _coerce_text(raw, field=field)


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=body,
    )
    try:
        payload = response.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"rawText": response.text(), "contentType": response.headers.get("content-type")}
    if isinstance(payload, dict):
        return payload
    return {"json": payload}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": method,
            }
        )
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_helper(*, method_name: str, path: str, body: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request(method="POST", path=path, headers=auth["headers"], body=body, ctx=ctx)
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": "POST", "path": path, "body": body},
        "response": response,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
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
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": {"method": http_method, "path": path, "body": body},
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "This Intake Form Submissions slice uses provider-response verification only; deleted or orphaned records are not returned by official query methods.",
        },
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback is promised for intake form submission lifecycle changes."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> None:
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


def _run_write(
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
    plan = _build_plan(
        method_name=method_name,
        http_method=http_method,
        path=path,
        body=body,
        selector=selector,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request(method=http_method, path=path, headers=auth["headers"], body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": plan["request"],
        "response": response,
        "verified": {"type": "provider-response", "notes": verification_notes},
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def cmd_intake_form_submissions_query(args, ctx) -> int:
    method = "intake-form-submissions.query"
    try:
        return _run_helper(method_name=method, path=f"{BASE_PATH}/query", body=_read_object(args.query_json, field="query-json", default={}), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_search(args, ctx) -> int:
    method = "intake-form-submissions.search"
    try:
        return _run_helper(method_name=method, path=f"{BASE_PATH}/search", body=_read_object(args.search_json, field="search-json", default={}), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_count_by_intake_form_ids(args, ctx) -> int:
    method = "intake-form-submissions.count-by-intake-form-ids"
    try:
        return _run_helper(method_name=method, path=COUNT_PATH, body=_read_object(args.request_json, field="request-json"), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_list_data_by_contacts(args, ctx) -> int:
    method = "intake-form-submissions.list-data-by-contacts"
    try:
        return _run_helper(method_name=method, path=f"{BASE_PATH}/list-data-by-contacts", body=_read_object(args.request_json, field="request-json"), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_cancel(args, ctx) -> int:
    method = "intake-form-submissions.cancel"
    try:
        submission_id = _required_id(args.submission_id, field="submission-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{submission_id}/cancel",
            body={},
            selector={"intakeFormSubmissionId": submission_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["changes-status-to-canceled", "official-docs-say-canceled-submission-cannot-be-reactivated"],
            verification_notes="Provider response only. Official docs say the contact must create a new submission after cancel.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_extend(args, ctx) -> int:
    method = "intake-form-submissions.extend"
    try:
        submission_id = _required_id(args.submission_id, field="submission-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{submission_id}/extend",
            body={},
            selector={"intakeFormSubmissionId": submission_id},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["resets-submission-expiration-date"],
            verification_notes="Provider response only. Wix sets the new expiration from the call time plus the intake form expiration period.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_exempt(args, ctx) -> int:
    method = "intake-form-submissions.exempt"
    try:
        form_id = _required_id(args.intake_form_id, field="intake-form-id")
        body = _read_object(args.exemption_json, field="exemption-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{form_id}/exempt",
            body=body,
            selector={"intakeFormId": form_id},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["creates-exempt-intake-form-submission"],
            verification_notes="Provider response only. Official docs say this creates a submission with EXEMPT status.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_intake_form_submissions_delete(args, ctx) -> int:
    method = "intake-form-submissions.delete"
    try:
        submission_id = _required_id(args.submission_id, field="submission-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{submission_id}",
            body=None,
            selector={"intakeFormSubmissionId": submission_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["deletes-intake-form-submission"],
            verification_notes="Provider response only. Official docs mark Delete Intake Form Submission as Developer Preview.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
