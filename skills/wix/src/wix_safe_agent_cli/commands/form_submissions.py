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
        raise ValidationError(f"Missing --{field}")
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


def _read_str_list(raw: Any, field: str, *, required: bool = True, max_count: int | None = None) -> list[str] | None:
    if raw is None:
        if required:
            raise ValidationError(f"Missing --{field}")
        return None

    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")

    if required and not value:
        raise ValidationError(f"--{field} cannot be empty")

    if max_count is not None and len(value) > max_count:
        raise ValidationError(f"--{field} supports at most {max_count} values")

    items: list[str] = []
    for i, raw_value in enumerate(value):
        if not isinstance(raw_value, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        item = raw_value.strip()
        if not item:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        items.append(item)

    return items


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_bool(raw: Any, field: str) -> bool | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be true or false")
    normalized = raw.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValidationError(f"--{field} must be true or false")


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


def _ensure_forms_app_is_installed(*, cfg, env_file: str, verbose: bool) -> dict[str, str]:
    auth = resolve_auth_mode(
        cfg=cfg,
        env_file=env_file,
        verbose=verbose,
        command_family="form-submissions",
    )
    instance_payload = _request_json(
        method="GET",
        base_url=cfg.base_url,
        path="/apps/v1/instance",
        headers=auth["headers"],
        params=None,
        json_body=None,
        timeout_s=float(cfg.timeout_s),
        verbose=verbose,
    )
    if not _app_has_wix_forms(payload=instance_payload):
        raise ValidationError("Required app wix_forms is not installed on this site.")
    return auth["headers"]


def _app_has_wix_forms(*, payload: dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    site = payload.get("site")
    if not isinstance(site, dict):
        return False
    installed = site.get("installedWixApps")
    if not isinstance(installed, list):
        return False
    return any(isinstance(name, str) and name == "wix_forms" for name in installed)


def _coerce_required_text_like(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if isinstance(raw, bool):
        raise ValidationError(f"--{field} must be a string")
    if not isinstance(raw, str):
        raw = str(raw)
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _http_status_from_error(exc: RuntimeError) -> int | None:
    text = str(exc)
    if not text.startswith("HTTP "):
        return None
    parts = text.split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _read_submission_json(raw: Any, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    requires_ack: bool = False,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")

    risk_reasons = ["wix-form-submission-write"]
    if requires_ack:
        risk_reasons.append("irreversible")

    if has_before_state:
        capture_notes = state_capture_notes or "Captured current provider state before planning."
    else:
        capture_notes = state_capture_notes or "No useful before-state snapshot exists for this create-style write."

    rollback_default = (
        "No automatic rollback. Use the saved before-state snapshot as a manual reference."
        if has_before_state
        else "No automatic rollback and no useful before-state snapshot is available."
    )

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": capture_notes,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": rollback_notes or rollback_default,
        },
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
        raise SafetyError("Refused: plan baseline missing")
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
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and requires_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: apply requires --ack-irreversible")

    review_ctx = dict(ctx)
    review_ctx["enforce_reviewed_plan"] = True
    return reviewed_plan_apply_requested(
        review_ctx,
        requires_ack=requires_ack,
        command_label="form-submissions",
    )


def _assert_submission_state_unchanged(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if before_state != current_state:
        raise SafetyError("Refused: form-submission state changed since plan was created")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
    recovery_notes: str | None = None,
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": plan.get("state_capture", {}).get(
                "notes",
                "No useful before-state snapshot was available.",
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                recovery_notes
                or plan.get("rollback", {}).get(
                    "notes",
                    (
                        "Recovery is manual only."
                        if has_before_state
                        else "Recovery is manual only and no useful before-state snapshot is available."
                    ),
                )
            ),
        },
    }


def _get_submission(
    *,
    submission_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/form-submission-service/v4/submissions/{submission_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _get_submission_optional(
    *,
    submission_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_submission(submission_id=submission_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _build_namespace_query_body(raw_query_json: Any) -> dict[str, Any]:
    query_json = _read_json_arg(raw_query_json, field="query-json")
    if not isinstance(query_json, dict):
        raise ValidationError("--query-json must be a JSON object")

    if "query" in query_json:
        query_obj = query_json.get("query")
        if not isinstance(query_obj, dict):
            raise ValidationError("--query-json must include a query object at `query`")
        body = dict(query_json)
        query_object = body["query"]
    else:
        query_object = query_json
        body = {"query": query_object}

    filter_obj = query_object.get("filter")
    if not isinstance(filter_obj, dict):
        filter_obj = {}
    else:
        filter_obj = dict(filter_obj)

    namespace = None
    if isinstance(filter_obj.get("namespace"), str) and filter_obj["namespace"].strip():
        namespace = filter_obj["namespace"].strip()
    elif isinstance(query_object.get("namespace"), str) and query_object["namespace"].strip():
        namespace = query_object["namespace"].strip()

    if not namespace:
        raise ValidationError("--query-json must include a namespace filter inside query")

    body["query"] = dict(query_object)
    body["query"].pop("namespace", None)
    filter_obj["namespace"] = namespace
    body["query"]["filter"] = filter_obj
    return body


def cmd_form_submissions_create_submission(args, ctx) -> int:
    try:
        submission = _read_submission_json(getattr(args, "submission_json", None), field="submission-json")
        form_id = _coerce_required_text_like(submission.get("formId"), field="submission-json.formId")
        payload_submission = dict(submission)
        payload_submission.pop("id", None)
        payload_submission["formId"] = form_id

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        request = {
            "method": "POST",
            "path": "/form-submission-service/v4/submissions",
            "body": {"submission": payload_submission},
        }
        selector = {
            "kind": "wix-form-submission",
            "operation": "create",
            "form_id": form_id,
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="form-submissions.create-submission",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="form-submissions.create-submission",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create-submission", "submission": payload_submission}],
                verification_plan={"type": "provider-response", "notes": "Create verification uses the API response payload."},
                state_capture_notes="No useful before-state snapshot exists for this create-style write.",
                rollback_notes="No automatic rollback. No useful before-state snapshot is available for this create operation.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "form-submissions.create-submission",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="form-submissions.create-submission",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_submission = response.get("submission")
        verification = {
            "ok": isinstance(created_submission, dict),
            "type": "provider-response",
            "path": request["path"],
            "method": request["method"],
            "after": created_submission,
            "notes": "Creation verification is based on response content.",
        }
        receipt = _build_receipt(
            method="form-submissions.create-submission",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "form-submissions.create-submission",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "form-submissions.create-submission",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "form-submissions.create-submission"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "form-submissions.create-submission"}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_update_submission(args, ctx) -> int:
    try:
        submission = _read_submission_json(getattr(args, "submission_json", None), field="submission-json")
        submission_id = _coerce_required_text_like(submission.get("id"), field="submission-json.id")
        form_id = _coerce_required_text_like(submission.get("formId"), field="submission-json.formId")
        requested_revision = _coerce_required_text_like(submission.get("revision"), field="submission-json.revision")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        current_submission = _get_submission(submission_id=submission_id, ctx=ctx, headers=headers)
        current_form_id = _coerce_required_text_like(current_submission.get("formId"), field="current submission formId")
        if current_form_id != form_id:
            raise SafetyError("Refused: submission.formId does not match the current submission.")

        current_revision = _coerce_required_text_like(current_submission.get("revision"), field="current submission revision")
        if requested_revision != current_revision:
            raise SafetyError("Refused: submission.revision is stale. Read current submission and retry the write.")

        payload_submission = dict(submission)
        payload_submission["id"] = submission_id
        payload_submission["formId"] = form_id
        payload_submission["revision"] = current_revision

        request = {
            "method": "PATCH",
            "path": f"/form-submission-service/v4/submissions/{submission_id}",
            "body": {"submission": payload_submission},
        }
        selector = {
            "kind": "wix-form-submission",
            "operation": "update",
            "submission_id": submission_id,
        }
        before_state = {"submission": current_submission}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="form-submissions.update-submission",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="form-submissions.update-submission",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update-submission", "submission_id": submission_id}],
                verification_plan={"type": "read-after-write", "notes": "Re-read submission and verify key fields."},
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "form-submissions.update-submission",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="form-submissions.update-submission",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_submission_state_unchanged(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_submission = _get_submission(submission_id=submission_id, ctx=ctx, headers=headers)
        verification = {
            "ok": _coerce_required_text_like(after_submission.get("id"), field="submission.id") == submission_id
            and _coerce_required_text_like(after_submission.get("formId"), field="submission.formId") == form_id,
            "type": "read-after-write",
            "path": request["path"],
            "method": "GET",
            "before": current_submission,
            "after": after_submission,
            "checks": [
                {"field": "id", "expected": submission_id, "actual": after_submission.get("id")},
                {"field": "formId", "expected": form_id, "actual": after_submission.get("formId")},
            ],
            "notes": "Update verification re-reads the submission after apply.",
        }
        receipt = _build_receipt(
            method="form-submissions.update-submission",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "form-submissions.update-submission",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "form-submissions.update-submission",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "form-submissions.update-submission"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "form-submissions.update-submission"}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_delete_submission(args, ctx) -> int:
    try:
        submission_id = _coerce_required_text_like(getattr(args, "submission_id", ""), field="submission-id")
        permanent = _coerce_optional_bool(getattr(args, "permanent", None), field="permanent")
        preserve_files = _coerce_optional_bool(getattr(args, "preserve_files", None), field="preserve-files")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        current_submission = _get_submission(submission_id=submission_id, ctx=ctx, headers=headers)
        request_params: dict[str, Any] = {}
        if permanent is not None:
            request_params["permanent"] = permanent
        if preserve_files is not None:
            request_params["preserveFiles"] = preserve_files

        request = {
            "method": "DELETE",
            "path": f"/form-submission-service/v4/submissions/{submission_id}",
            "params": request_params or None,
        }
        selector = {
            "kind": "wix-form-submission",
            "operation": "delete",
            "submission_id": submission_id,
        }
        before_state = {"submission": current_submission}
        plan_in = ctx.get("plan_in")
        recovery_notes = (
            f"Delete recovery is manual only. permanent={permanent} preserveFiles={preserve_files}. "
            "If permanent is true, this may prevent normal recovery."
        )
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="form-submissions.delete-submission",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="form-submissions.delete-submission",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete-submission", "submission_id": submission_id}],
                verification_plan={"type": "read-after-write", "notes": "GET submission should return 404 after delete."},
                requires_ack=True,
                rollback_notes=recovery_notes,
            )

        if not _should_apply(ctx, requires_ack=True):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "form-submissions.delete-submission",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="form-submissions.delete-submission",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_submission_state_unchanged(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=request_params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_submission, after_status = _get_submission_optional(submission_id=submission_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_status == 404 and after_submission is None,
            "type": "read-after-write",
            "path": request["path"],
            "method": "GET",
            "before": current_submission,
            "after": after_submission,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects GET to return 404.",
        }
        out_receipt = _build_receipt(
            method="form-submissions.delete-submission",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
            recovery_notes=recovery_notes,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "form-submissions.delete-submission",
            "receipt": out_receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=out_receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "form-submissions.delete-submission",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "form-submissions.delete-submission"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "form-submissions.delete-submission"}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_confirm_submission(args, ctx) -> int:
    try:
        submission_id = _coerce_required_text_like(getattr(args, "submission_id", ""), field="submission-id")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        current_submission = _get_submission(submission_id=submission_id, ctx=ctx, headers=headers)
        current_status = _coerce_required_text_like(current_submission.get("status"), field="current submission status")
        if current_status != "PENDING":
            raise SafetyError("Refused: submission status is not PENDING and cannot be confirmed.")

        request = {
            "method": "POST",
            "path": f"/form-submission-service/v4/submissions/{submission_id}/confirm",
            "body": {},
        }
        selector = {
            "kind": "wix-form-submission",
            "operation": "confirm",
            "submission_id": submission_id,
        }
        before_state = {"submission": current_submission}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="form-submissions.confirm-submission",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="form-submissions.confirm-submission",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "confirm-submission", "submission_id": submission_id}],
                verification_plan={"type": "read-after-write", "notes": "Re-read submission and verify status is CONFIRMED."},
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "form-submissions.confirm-submission",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="form-submissions.confirm-submission",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_submission_state_unchanged(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_submission = _get_submission(submission_id=submission_id, ctx=ctx, headers=headers)
        after_status = _coerce_required_text_like(after_submission.get("status"), field="after submission status")
        verification = {
            "ok": after_status == "CONFIRMED",
            "type": "read-after-write",
            "path": request["path"],
            "method": "GET",
            "before": current_submission,
            "after": after_submission,
            "checks": [{"field": "status", "expected": "CONFIRMED", "actual": after_status}],
            "notes": "Confirm verification reads submission after apply.",
        }
        out_receipt = _build_receipt(
            method="form-submissions.confirm-submission",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "form-submissions.confirm-submission",
            "receipt": out_receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=out_receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "form-submissions.confirm-submission",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "form-submissions.confirm-submission"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "form-submissions.confirm-submission"}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_bulk_mark_submissions_as_seen(args, ctx) -> int:
    try:
        form_id = _coerce_required_text_like(getattr(args, "form_id", ""), field="form-id")
        submission_ids = _read_str_list(
            getattr(args, "ids_json", None),
            field="ids-json",
            required=False,
            max_count=100,
        )
        all_unseen = bool(getattr(args, "all_unseen", False))
        if not submission_ids and not all_unseen:
            raise SafetyError("Refused: provide --ids-json or --all-unseen.")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        if submission_ids:
            current_submissions = []
            for submission_id in submission_ids:
                current_submissions.append(_get_submission(submission_id=submission_id, ctx=ctx, headers=headers))
            before_state: dict[str, Any] = {"submissions": current_submissions}
        else:
            before_state = {"all_unseen": True, "form_id": form_id}

        request_body: dict[str, Any] = {"formId": form_id}
        if submission_ids:
            request_body["ids"] = submission_ids

        request = {
            "method": "POST",
            "path": "/form-submission-service/v4/bulk/submissions/mark-as-seen",
            "body": request_body,
        }
        selector = {
            "kind": "wix-form-submission",
            "operation": "bulk-mark-submissions-as-seen",
            "form_id": form_id,
            "all_unseen": all_unseen,
            "ids": submission_ids or [],
        }
        plan_in = ctx.get("plan_in")
        capture_notes = None if submission_ids else "No precise bounded before-state snapshot was captured for --all-unseen."
        recovery_notes = (
            "No precise bounded before-state is available when using --all-unseen."
            if not submission_ids
            else "Recovered per-submission state was captured before planning."
        )
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="form-submissions.bulk-mark-submissions-as-seen",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="form-submissions.bulk-mark-submissions-as-seen",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-mark-submissions-as-seen",
                        "form_id": form_id,
                        "ids": submission_ids or [],
                    }
                ],
                verification_plan={"type": "read-after-write", "notes": "Re-fetch submissions when ids are explicit."},
                state_capture_notes=capture_notes,
                rollback_notes=recovery_notes,
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "form-submissions.bulk-mark-submissions-as-seen",
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="form-submissions.bulk-mark-submissions-as-seen",
            expected_selector=selector,
            ctx=ctx,
        )
        if submission_ids:
            refreshed_before_state: list[dict[str, Any]] = []
            for submission_id in submission_ids:
                refreshed_before_state.append(_get_submission(submission_id=submission_id, ctx=ctx, headers=headers))
            _assert_submission_state_unchanged(plan=loaded_plan, current_state={"submissions": refreshed_before_state})

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        checks: list[dict[str, Any]] = []
        verification_ok = True
        seen_after: list[dict[str, Any]] = []
        if submission_ids:
            for submission_id in submission_ids:
                after_submission, status = _get_submission_optional(
                    submission_id=submission_id,
                    ctx=ctx,
                    headers=headers,
                )
                if status == 404:
                    verification_ok = False
                    checks.append(
                        {"submission_id": submission_id, "field": "http_status", "expected": 200, "actual": status}
                    )
                elif after_submission is None:
                    verification_ok = False
                    checks.append(
                        {"submission_id": submission_id, "field": "seen", "expected": True, "actual": None}
                    )
                else:
                    seen_value = after_submission.get("seen")
                    if seen_value is not True:
                        verification_ok = False
                    checks.append(
                        {"submission_id": submission_id, "field": "seen", "expected": True, "actual": seen_value}
                    )
                    seen_after.append(after_submission)
        else:
            checks.append(
                {
                    "field": "response",
                    "expected": "all unseen submissions marked",
                    "actual": response.get("updatedCount") if isinstance(response.get("updatedCount"), int) else None,
                }
            )

        verification = {
            "ok": bool(verification_ok),
            "type": "read-after-write",
            "path": request["path"],
            "method": "POST",
            "before": before_state,
            "after": {"submissions": seen_after},
            "checks": checks,
            "notes": (
                "For explicit ids, each submission is re-fetched and expected to be seen=true."
                if submission_ids
                else "No bounded read-back is practical for --all-unseen."
            ),
        }
        receipt = _build_receipt(
            method="form-submissions.bulk-mark-submissions-as-seen",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
            recovery_notes=recovery_notes,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "form-submissions.bulk-mark-submissions-as-seen",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "form-submissions.bulk-mark-submissions-as-seen",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "form-submissions.bulk-mark-submissions-as-seen"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "form-submissions.bulk-mark-submissions-as-seen"}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_get_submission(args, ctx) -> int:
    try:
        submission_id = _coerce_required_text(getattr(args, "submission_id", ""), field="submission-id")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/form-submission-service/v4/submissions/{submission_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "form-submissions.get-submission",
            "request": {
                "method": "GET",
                "path": f"/form-submission-service/v4/submissions/{submission_id}",
            },
            "response": payload,
        }
        ctx["audit"].write("form-submissions.get-submission", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_query_submissions_by_namespace(args, ctx) -> int:
    try:
        body = _build_namespace_query_body(getattr(args, "query_json", None))

        only_your_own = _coerce_optional_bool(
            getattr(args, "only_your_own", None), field="only-your-own"
        )
        if only_your_own is not None:
            body["onlyYourOwn"] = only_your_own

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/form-submission-service/v4/submissions/namespace/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "form-submissions.query-submissions-by-namespace",
            "request": {
                "method": "POST",
                "path": "/form-submission-service/v4/submissions/namespace/query",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("form-submissions.query-submissions-by-namespace", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_count_submissions(args, ctx) -> int:
    try:
        form_ids = _read_str_list(getattr(args, "form_ids_json", None), field="form-ids-json", required=True, max_count=100)
        namespace = _coerce_required_text(getattr(args, "namespace", ""), field="namespace")
        statuses = _read_str_list(getattr(args, "statuses_json", None), field="statuses-json", required=False, max_count=4)

        body = {"formIds": form_ids, "namespace": namespace}
        if statuses is not None:
            body["statuses"] = statuses

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/form-submission-service/v4/submissions/count",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "form-submissions.count-submissions",
            "request": {
                "method": "POST",
                "path": "/form-submission-service/v4/submissions/count",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("form-submissions.count-submissions", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_form_submissions_get_media_upload_url(args, ctx) -> int:
    try:
        form_id = _coerce_required_text(getattr(args, "form_id", ""), field="form-id")
        filename = _coerce_required_text(getattr(args, "filename", ""), field="filename")
        mime_type = _coerce_required_text(getattr(args, "mime_type", ""), field="mime-type")

        headers = _ensure_forms_app_is_installed(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/form-submission-service/v4/submissions/media-upload-url",
            headers=headers,
            params=None,
            json_body={
                "formId": form_id,
                "fileName": filename,
                "mimeType": mime_type,
            },
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "form-submissions.get-media-upload-url",
            "request": {
                "method": "POST",
                "path": "/form-submission-service/v4/submissions/media-upload-url",
                "body": {
                    "formId": form_id,
                    "filename": filename,
                    "mimeType": mime_type,
                },
            },
            "response": payload,
        }
        ctx["audit"].write("form-submissions.get-media-upload-url", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1
