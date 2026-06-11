from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .api_runner import build_headers, build_request_metadata, execute_call, parse_payload_json
from .config import load_config
from .project_config import load_project_config
from .errors import SafetyError, ToolError, ValidationError
from .json_files import read_json_file, write_json_file
from .output import Output
from .runs import (
    RunContext,
    build_deterministic_summary,
    init_run_context,
    list_runs,
    find_run,
    write_summary_md,
    append_index_row,
    runs_index_path_for_env_file,
 )


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
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
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = (Path(ad) / "summary.md")
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


_INTEGRATION_WRITE_TYPES = ("webhooks", "custom")
_TRACKER_CREATE_TYPES = {
    "trackers create-session": "session",
    "trackers create-source": "source",
}
_TRACKER_UPDATE_TYPES = {
    "trackers update-session": "session",
    "trackers update-source": "source",
}

_OFFSET_PAGINATION_QUERY_PARAMS: tuple[tuple[str, str], ...] = (
    ("page", "page"),
    ("per_page", "per_page"),
)

_SHARED_QUERY_PARAMS: tuple[tuple[str, str], ...] = (
    *_OFFSET_PAGINATION_QUERY_PARAMS,
    ("sort", "sort"),
    ("order", "order"),
    ("search", "search"),
    ("fields", "fields"),
    ("date_range", "date_range"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("time_zone", "time_zone"),
    ("relative_pagination", "relative_pagination"),
    ("offset", "offset"),
)

_API_COMMAND_QUERY_PARAMS: dict[str, tuple[tuple[str, str], ...]] = {
    "accounts list": ((*_SHARED_QUERY_PARAMS, ("hipaa_account", "hipaa_account"))),
    "accounts get": (("fields", "fields"),),
    "calls list": (
        *tuple(_SHARED_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("tracker_id", "tracker_id"),
        ("call_type", "call_type"),
        ("answer_status", "answer_status"),
        ("device", "device"),
        ("direction", "direction"),
        ("lead_status", "lead_status"),
        ("tags", "tags"),
    ),
    "calls get": (("fields", "fields"),),
    "calls summary": (
        ("company_id", "company_id"),
        ("group_by", "group_by"),
        ("fields", "fields"),
        ("device", "device"),
        ("min_duration", "min_duration"),
        ("max_duration", "max_duration"),
        ("tags", "tags"),
        ("tracker_ids", "tracker_ids"),
        ("direction", "direction"),
        ("answer_status", "answer_status"),
        ("first_time_callers", "first_time_callers"),
        ("lead_status", "lead_status"),
        ("agent", "agent"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("time_zone", "time_zone"),
        ("search", "search"),
    ),
    "calls timeseries": (
        ("company_id", "company_id"),
        ("fields", "fields"),
        ("device", "device"),
        ("interval", "interval"),
        ("min_duration", "min_duration"),
        ("max_duration", "max_duration"),
        ("tags", "tags"),
        ("tracker_ids", "tracker_ids"),
        ("direction", "direction"),
        ("answer_status", "answer_status"),
        ("first_time_callers", "first_time_callers"),
        ("lead_status", "lead_status"),
        ("agent", "agent"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("time_zone", "time_zone"),
    ),
    "companies list": (
        *tuple(_SHARED_QUERY_PARAMS),
        ("status", "status"),
    ),
    "companies get": (("fields", "fields"),),
    "form-submissions list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("person_lead", "person_lead"),
        ("lead_status", "lead_status"),
        ("tags", "tags"),
        ("sort", "sort"),
        ("order", "order"),
        ("fields", "fields"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("time_zone", "time_zone"),
    ),
    "form-submissions summary": (
        ("company_id", "company_id"),
        ("group_by", "group_by"),
        ("fields", "fields"),
        ("tags", "tags"),
        ("custom_form_ids", "custom_form_ids"),
        ("form_URL", "form_url"),
        ("lead_status", "lead_status"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("time_zone", "time_zone"),
    ),
    "integrations list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("fields", "fields"),
    ),
    "integrations get": (("fields", "fields"),),
    "integration-filters list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
    ),
    "notifications list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("notification_type", "notification_type"),
    ),
    "outbound-caller-ids list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
    ),
    "page-views list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("time_zone", "time_zone"),
    ),
    "sms-threads list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("search", "search"),
        ("fields", "fields"),
    ),
    "sms-threads get": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("with_msg_errors", "with_msg_errors"),
        ("fields", "fields"),
    ),
    "summary-emails list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("frequency", "frequency"),
        ("company_id", "company_id"),
        ("user_id", "user_id"),
        ("email", "email"),
    ),
    "text-messages list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("date_range", "date_range"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
        ("time_zone", "time_zone"),
        ("search", "search"),
        ("fields", "fields"),
    ),
    "text-messages get": (("fields", "fields"),),
    "message-flows list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
    ),
    "trackers list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("type", "type"),
        ("status", "status"),
        ("search", "search"),
        ("fields", "fields"),
        ("sort", "sort"),
        ("order", "order"),
    ),
    "trackers get": (("fields", "fields"),),
    "users list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("sort", "sort"),
        ("order", "order"),
        ("search", "search"),
    ),
    "leads list": (
        *tuple(_OFFSET_PAGINATION_QUERY_PARAMS),
        ("company_id", "company_id"),
        ("fields", "fields"),
        ("sort", "sort"),
        ("order", "order"),
    ),
}

_API_COMMAND_REQUIRED_QUERY_PARAMS: dict[str, tuple[str, ...]] = {
    "integrations list": ("company_id",),
    "integration-filters list": ("company_id",),
    "outbound-caller-ids list": ("company_id",),
}


def _query_flag_name(arg_name: str) -> str:
    return str(arg_name).replace("_", "-").lower()


def _parse_query_param_value(raw: object) -> list[str] | None:
    if raw is None:
        return None
    if isinstance(raw, list):
        raw_items: list[object] = raw
    else:
        raw_items = [raw]

    values: list[str] = []
    for item in raw_items:
        text = str(item).strip()
        if not text:
            continue
        values.extend(part.strip() for part in text.split(","))
    values = [v for v in values if v]
    return values or None


def _build_query_params(args: argparse.Namespace, spec: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for query_key, attr_name in spec.get("query_params", ()):  # type: ignore[assignment]
        raw = getattr(args, attr_name, None)
        values = _parse_query_param_value(raw)
        if values is None:
            continue
        if len(values) == 1:
            out[query_key] = values[0]
        else:
            out[query_key] = values
    return out


def _assert_required_query_params(command_key: str, args: argparse.Namespace, spec: dict[str, object]) -> None:
    required = tuple(spec.get("required_query_params", ()))  # type: ignore[assignment]
    for required_attr in required:
        values = _parse_query_param_value(getattr(args, required_attr, None))
        if values is None:
            raise ValidationError(f"{command_key} requires --{_query_flag_name(required_attr)}")


def _validate_integration_write_type(command_key: str, payload: object) -> None:
    if command_key not in {"integrations create", "integrations update"}:
        return
    if not isinstance(payload, dict):
        raise SafetyError("Refused: integrations write payload must be a JSON object.")
    payload_type = payload.get("type")
    if not isinstance(payload_type, str) or payload_type not in _INTEGRATION_WRITE_TYPES:
        raise SafetyError("Refused: integrations create/update support is only webhooks and custom.")


def _validate_tracker_write_type(command_key: str, payload: object | None) -> None:
    create_type = _TRACKER_CREATE_TYPES.get(command_key)
    update_type = _TRACKER_UPDATE_TYPES.get(command_key)
    if not create_type and not update_type:
        return
    if payload is None:
        raise SafetyError("Refused: tracker write payload is required.")
    if not isinstance(payload, dict):
        raise SafetyError("Refused: tracker write payload must be a JSON object.")

    payload_type = payload.get("type")
    if create_type:
        if payload_type is None:
            payload["type"] = create_type
            return
        if not isinstance(payload_type, str) or payload_type != create_type:
            raise SafetyError(
                f"Refused: {command_key} requires payload.type '{create_type}', not '{payload_type}'."
            )
        return

    if payload_type is None:
        return
    if not isinstance(payload_type, str) or payload_type != update_type:
        raise SafetyError(
            f"Refused: {command_key} only supports existing {update_type} trackers; remove or fix payload.type."
        )


def _validate_plan_in_for_apply(*, plan_in: object, cfg, command_key: str, request_meta: dict[str, object]) -> None:
    if not plan_in:
        return
    plan_obj = read_json_file(str(plan_in))
    if not isinstance(plan_obj, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan_obj.get("env_fingerprint") or "") != str(cfg.base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment.")
    if str(plan_obj.get("command") or "") != command_key:
        raise SafetyError("Refused: plan command does not match current command.")

    plan_request = plan_obj.get("request")
    if not isinstance(plan_request, dict):
        raise ValidationError("Plan file missing request object")
    if str(plan_request.get("method") or "").upper() != str(request_meta.get("method") or "").upper():
        raise SafetyError("Refused: plan request method does not match current write request.")
    if str(plan_request.get("url") or "") != str(request_meta.get("url") or ""):
        raise SafetyError("Refused: plan request url does not match current write request.")
    if plan_request.get("json") != request_meta.get("json"):
        raise SafetyError("Refused: plan request json does not match current write request.")
    if plan_request.get("params") != request_meta.get("params"):
        raise SafetyError("Refused: plan request params do not match current write request.")
    if plan_request.get("form") != request_meta.get("form"):
        raise SafetyError("Refused: plan request form does not match current write request.")


def _build_error_output(
    *, ok: bool, base_url: str, request_meta: dict[str, object], error: Exception, error_type: str | None = None
) -> dict[str, object]:
    return {
        "ok": ok,
        "base_url": base_url,
        "request": request_meta,
        "error": str(error),
        "error_type": error_type or type(error).__name__,
    }


def _extract_path_placeholders(path_template: str) -> tuple[str, ...]:
    return tuple(sorted(set(re.findall(r"{([^{}]+)}", path_template))))


def _build_request_metadata(
    cfg,
    *,
    method: str,
    url: str,
    payload: object | None = None,
    params: dict[str, object] | None = None,
    form_fields: dict[str, object] | None = None,
    media_file: str | None = None,
) -> dict[str, object]:
    return build_request_metadata(
        method=method,
        url=url,
        headers=build_headers(getattr(cfg, "token", None), getattr(cfg, "request_from", None)),
        payload=payload,
        params=params,
        form_fields=form_fields,
        media_file=media_file,
    )


def _build_text_message_form_fields(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValidationError("text-messages send payload must be a JSON object.")
    normalized: dict[str, object] = {}
    for key, value in payload.items():
        if isinstance(value, (dict, list, tuple)):
            normalized[key] = json.dumps(value)
        elif value is None:
            normalized[key] = ""
        else:
            normalized[key] = str(value)
    return normalized


def _resolve_command_arg(cfg, args: argparse.Namespace, arg_name: str) -> str:
    value = str(getattr(args, arg_name, "") or "").strip()
    if arg_name == "account_id":
        if value:
            return value
        value = str(getattr(cfg, "default_account_id", "") or "").strip()
        if value:
            return value
        raise ValidationError("Missing --account-id and CALLRAIL_DEFAULT_ACCOUNT_ID")
    if not value:
        raise ValidationError(f"Missing --{arg_name.replace('_', '-')}")
    return value


def _build_command_url(cfg, spec: dict[str, object], args: argparse.Namespace) -> str:
    path_template = str(spec["path"])
    values: dict[str, str] = {}
    for placeholder in _extract_path_placeholders(path_template):
        values[placeholder] = _resolve_command_arg(cfg=cfg, args=args, arg_name=placeholder)
    return f"{cfg.base_url}{path_template.format(**values)}"


def _build_plan_payload(
    cfg,
    *,
    ctx: dict,
    command: str,
    method: str,
    url: str,
    payload: object | None,
    params: dict[str, object] | None = None,
    form_fields: dict[str, object] | None = None,
    media_file: str | None = None,
) -> dict[str, object]:
    request_meta = _build_request_metadata(
        cfg=cfg,
        method=method,
        url=url,
        payload=payload,
        params=params,
        form_fields=form_fields,
        media_file=media_file,
    )
    before_state = {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "saved_path": None,
        "provider_backup_id": None,
        "reason": (
            "This CallRail write path does not save a useful before-state snapshot today. "
            "Review the exact request, then add --ack-no-snapshot if you approve applying without a saved snapshot."
        ),
    }
    return {
        "tool": ctx.get("tool") or "qwayk-callrail-safe-agent-cli",
        "version": ctx.get("tool_version"),
        "command": command,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": cfg.base_url,
        "request": request_meta,
        "risk_level": "medium",
        "risk_reasons": ["dry-run-no-apply"],
        "before_state": before_state,
        "verification_plan": {
            "status": "best_effort_after_apply",
            "approval_required": "--ack-no-snapshot",
            "steps": [
                "Record the CallRail API response in the receipt.",
                "Run the best available follow-up read when the API exposes one for the target.",
                "Record that no saved before-state snapshot was available for automatic rollback.",
            ],
        },
        "rollback": {
            "supported": False,
            "automatic_rollback": False,
            "notes": "No generic CallRail rollback is available without a saved before-state snapshot.",
        },
        "notes": "Dry-run plan only. Add --apply to execute this action later.",
    }


def _build_receipt_payload(
    cfg,
    *,
    ctx: dict,
    command: str,
    request_meta: dict[str, object],
    response_meta: dict[str, object],
    before_state: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "tool": ctx.get("tool") or "qwayk-callrail-safe-agent-cli",
        "version": ctx.get("tool_version"),
        "command": command,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": cfg.base_url,
        "request": request_meta,
        "response": response_meta,
        "before_state": before_state,
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No useful CallRail before-state snapshot was saved for this write.",
        },
        "verification": {"ok": True, "notes": "CallRail API response captured for this applied write."},
    }


def _run_generic_read(args: argparse.Namespace, ctx: dict, command_key: str, spec: dict[str, object]) -> int:
    cfg = ctx["cfg"]
    try:
        url = _build_command_url(cfg=cfg, spec=spec, args=args)
        _assert_required_query_params(command_key=command_key, args=args, spec=spec)
        query_params = _build_query_params(args=args, spec=spec)
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "error": str(e), "error_type": type(e).__name__}
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 1

    try:
        request_meta, response_meta = execute_call(
            cfg=cfg,
            method=str(spec["method"]),
            url=url,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx["verbose"]),
            user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
            params=query_params,
        )
    except Exception as e:  # noqa: BLE001
        out = _build_error_output(
            ok=False,
            base_url=cfg.base_url,
            request_meta=_build_request_metadata(
                cfg=cfg,
                method=str(spec["method"]),
                url=url,
                params=query_params,
            ),
            error=e,
        )
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 1

    out = {"ok": True, "request": request_meta, "response": response_meta}
    ctx["audit"].write(command_key, out)
    ctx["out"].emit(out)
    return 0


def _run_generic_write(args: argparse.Namespace, ctx: dict, command_key: str, spec: dict[str, object]) -> int:
    cfg = ctx["cfg"]
    media_file: str | None = None
    form_fields: dict[str, object] | None = None
    try:
        url = _build_command_url(cfg=cfg, spec=spec, args=args)
        if bool(spec.get("requires_payload", True)):
            payload = parse_payload_json(getattr(args, "payload_json", None))
        else:
            payload = None
        _validate_integration_write_type(command_key=command_key, payload=payload)
        _validate_tracker_write_type(command_key=command_key, payload=payload)
        if command_key == "text-messages send":
            media_file = str(getattr(args, "media_file", "") or "").strip()
            media_url = ""
            if isinstance(payload, dict):
                media_url_value = payload.get("media_url")
                if media_url_value is not None:
                    media_url = str(media_url_value).strip()
            if media_file and media_url:
                raise SafetyError("Refused: text-messages send accepts either media_url or media_file, not both.")
            if media_file:
                if not isinstance(payload, dict):
                    raise ValidationError("text-messages send payload must be a JSON object.")
                media_path = Path(media_file)
                if not media_path.exists():
                    raise ValidationError(f"media file not found: {media_file}")
                if not media_path.is_file():
                    raise ValidationError(f"media file path is not a file: {media_file}")
                form_fields = _build_text_message_form_fields(payload)
                request_meta = _build_request_metadata(
                    cfg=cfg,
                    method=str(spec["method"]),
                    url=url,
                    form_fields=form_fields,
                    media_file=media_file,
                )
            else:
                request_meta = _build_request_metadata(cfg=cfg, method=str(spec["method"]), url=url, payload=payload)
        else:
            request_meta = _build_request_metadata(cfg=cfg, method=str(spec["method"]), url=url, payload=payload)
    except SafetyError:
        raise
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "error": str(e), "error_type": type(e).__name__}
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 1

    if not bool(ctx.get("apply")):
        plan = _build_plan_payload(
            cfg=cfg,
            ctx=ctx,
            command=command_key,
            method=str(spec["method"]),
            url=url,
            payload=payload,
            form_fields=form_fields,
            media_file=media_file,
        )
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        out = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "request": request_meta,
        }
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"{command_key} requires --yes when used with --apply.")
    if bool(spec.get("ack_irreversible")) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"{command_key} requires --ack-irreversible when used with --apply --yes.")
    plan = _build_plan_payload(
        cfg=cfg,
        ctx=ctx,
        command=command_key,
        method=str(spec["method"]),
        url=url,
        payload=payload,
        form_fields=form_fields,
        media_file=media_file,
    )
    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            f"{command_key} has no saved before-state snapshot; review the dry-run plan, then rerun with --ack-no-snapshot if approved."
        )
    _validate_plan_in_for_apply(
        plan_in=ctx.get("plan_in"),
        cfg=cfg,
        command_key=command_key,
        request_meta=request_meta,
    )

    try:
        request_meta, response_meta = execute_call(
            cfg=cfg,
            method=str(spec["method"]),
            url=url,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx["verbose"]),
            user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
            payload=payload,
            form_fields=form_fields,
            media_file=media_file,
        )
    except Exception as e:  # noqa: BLE001
        out = _build_error_output(ok=False, base_url=cfg.base_url, request_meta=request_meta, error=e)
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 1

    receipt = _build_receipt_payload(
        cfg=cfg,
        ctx=ctx,
        command=command_key,
        request_meta=request_meta,
        response_meta=response_meta,
        before_state=plan.get("before_state") if isinstance(plan.get("before_state"), dict) else None,
    )
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {
        "ok": True,
        "dry_run": False,
        "request": request_meta,
        "response": response_meta,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    ctx["audit"].write(command_key, out)
    ctx["out"].emit(out)
    return 0


def _cmd_generic_api_call(args: argparse.Namespace, ctx: dict) -> int:
    command_key = f"{str(getattr(args, 'cmd', '')).strip()} {str(getattr(args, 'api_cmd', '')).strip()}".strip()
    spec = getattr(args, "api_spec", None)
    if not isinstance(spec, dict):
        out = {"ok": False, "error": "Command specification missing", "error_type": "NotSupportedError"}
        ctx["audit"].write(command_key, out)
        ctx["out"].emit(out)
        return 1
    mode = str(spec.get("mode", "read"))
    if mode == "read":
        return _run_generic_read(args=args, ctx=ctx, command_key=command_key, spec=spec)
    if mode == "write":
        return _run_generic_write(args=args, ctx=ctx, command_key=command_key, spec=spec)
    out = {"ok": False, "error": f"Unsupported command mode: {mode}", "error_type": "NotSupportedError"}
    ctx["audit"].write(command_key, out)
    ctx["out"].emit(out)
    return 1


_API_COMMAND_CATALOG: dict[str, dict[str, dict[str, object]]] = {
    "accounts": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a.json",
            "flags": [],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("accounts list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("accounts get", ()),
        },
    },
    "calls": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("calls list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls/{call_id}.json",
            "flags": [("account-id", "account_id", False), ("call-id", "call_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("calls get", ()),
        },
        "create-outbound": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/calls.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
            "ack_irreversible": True,
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/calls/{call_id}.json",
            "flags": [("account-id", "account_id", False), ("call-id", "call_id", True), ("payload-json", "payload_json", True)],
        },
        "summary": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls/summary.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("calls summary", ()),
        },
        "timeseries": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls/timeseries.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("calls timeseries", ()),
        },
        "recording": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls/{call_id}/recording.json",
            "flags": [("account-id", "account_id", False), ("call-id", "call_id", True)],
        },
    },
    "tags": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/tags.json",
            "flags": [("account-id", "account_id", False)],
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/tags.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/tags/{tag_id}.json",
            "flags": [("account-id", "account_id", False), ("tag-id", "tag_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/tags/{tag_id}.json",
            "flags": [("account-id", "account_id", False), ("tag-id", "tag_id", True)],
            "requires_payload": False,
        },
    },
    "companies": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/companies.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("companies list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/companies/{company_id}.json",
            "flags": [("account-id", "account_id", False), ("company-id", "company_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("companies get", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/companies.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/companies/{company_id}.json",
            "flags": [("account-id", "account_id", False), ("company-id", "company_id", True), ("payload-json", "payload_json", True)],
        },
        "bulk-update": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/companies/bulk_update.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "disable": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/companies/{company_id}.json",
            "flags": [("account-id", "account_id", False), ("company-id", "company_id", True)],
            "requires_payload": False,
        },
    },
    "form-submissions": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/form_submissions.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("form-submissions list", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/form_submissions.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/form_submissions/{submission_id}.json",
            "flags": [("account-id", "account_id", False), ("submission-id", "submission_id", True), ("payload-json", "payload_json", True)],
        },
        "ignore-fields": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/form_submissions/ignored_fields.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "summary": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/forms/summary.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("form-submissions summary", ()),
        },
    },
    "integrations": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/integrations.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("integrations list", ()),
            "required_query_params": _API_COMMAND_REQUIRED_QUERY_PARAMS.get("integrations list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/integrations/{integration_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-id", "integration_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("integrations get", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/integrations.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/integrations/{integration_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-id", "integration_id", True), ("payload-json", "payload_json", True)],
        },
        "disable": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/integrations/{integration_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-id", "integration_id", True)],
            "requires_payload": False,
        },
    },
    "integration-filters": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/integration_triggers.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("integration-filters list", ()),
            "required_query_params": _API_COMMAND_REQUIRED_QUERY_PARAMS.get("integration-filters list", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/integration_triggers.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/integration_triggers/{integration_filter_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-filter-id", "integration_filter_id", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/integration_triggers/{integration_filter_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-filter-id", "integration_filter_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/integration_triggers/{integration_filter_id}.json",
            "flags": [("account-id", "account_id", False), ("integration-filter-id", "integration_filter_id", True)],
            "requires_payload": False,
        },
    },
    "notifications": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/notifications.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("notifications list", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/notifications.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/notifications/{notification_id}.json",
            "flags": [("account-id", "account_id", False), ("notification-id", "notification_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/notifications/{notification_id}.json",
            "flags": [("account-id", "account_id", False), ("notification-id", "notification_id", True)],
            "requires_payload": False,
        },
    },
    "outbound-caller-ids": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/caller_ids.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("outbound-caller-ids list", ()),
            "required_query_params": _API_COMMAND_REQUIRED_QUERY_PARAMS.get("outbound-caller-ids list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/caller_ids/{caller_id}.json",
            "flags": [("account-id", "account_id", False), ("caller-id", "caller_id", True)],
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/caller_ids.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/caller_ids/{caller_id}.json",
            "flags": [("account-id", "account_id", False), ("caller-id", "caller_id", True)],
            "requires_payload": False,
        },
    },
    "page-views": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/calls/{call_id}/page_views.json",
            "flags": [("account-id", "account_id", False), ("call-id", "call_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("page-views list", ()),
        },
    },
    "sms-threads": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/sms-threads.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("sms-threads list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/sms-threads/{thread_id}.json",
            "flags": [("account-id", "account_id", False), ("thread-id", "thread_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("sms-threads get", ()),
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/sms-threads/{thread_id}.json",
            "flags": [("account-id", "account_id", False), ("thread-id", "thread_id", True), ("payload-json", "payload_json", True)],
        },
    },
    "summary-emails": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/summary_emails",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("summary-emails list", ()),
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/summary_emails.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/summary_emails/{summary_email_id}.json",
            "flags": [("account-id", "account_id", False), ("summary-email-id", "summary_email_id", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/summary_emails/{summary_email_id}.json",
            "flags": [("account-id", "account_id", False), ("summary-email-id", "summary_email_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/summary_emails/{summary_email_id}.json",
            "flags": [("account-id", "account_id", False), ("summary-email-id", "summary_email_id", True)],
            "requires_payload": False,
        },
    },
    "text-messages": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/text-messages.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("text-messages list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/text-messages/{conversation_id}.json",
            "flags": [("account-id", "account_id", False), ("conversation-id", "conversation_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("text-messages get", ()),
        },
        "send": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/text-messages.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True), ("media-file", "media_file", False)],
            "ack_irreversible": True,
        },
    },
    "message-flows": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/message-flows.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("message-flows list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/message-flows/{message_flow_id}.json",
            "flags": [("account-id", "account_id", False), ("message-flow-id", "message_flow_id", True)],
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/message-flows.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/message-flows/{message_flow_id}.json",
            "flags": [("account-id", "account_id", False), ("message-flow-id", "message_flow_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/message-flows/{message_flow_id}.json",
            "flags": [("account-id", "account_id", False), ("message-flow-id", "message_flow_id", True)],
            "requires_payload": False,
        },
    },
    "trackers": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/trackers.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("trackers list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/trackers/{tracker_id}.json",
            "flags": [("account-id", "account_id", False), ("tracker-id", "tracker_id", True)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("trackers get", ()),
        },
        "create-session": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/trackers.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "create-source": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/trackers.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update-session": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/trackers/{tracker_id}.json",
            "flags": [("account-id", "account_id", False), ("tracker-id", "tracker_id", True), ("payload-json", "payload_json", True)],
        },
        "update-source": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/trackers/{tracker_id}.json",
            "flags": [("account-id", "account_id", False), ("tracker-id", "tracker_id", True), ("payload-json", "payload_json", True)],
        },
        "disable": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/trackers/{tracker_id}.json",
            "flags": [("account-id", "account_id", False), ("tracker-id", "tracker_id", True)],
            "requires_payload": False,
        },
    },
    "users": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/users.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("users list", ()),
        },
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/users/{user_id}.json",
            "flags": [("account-id", "account_id", False), ("user-id", "user_id", True)],
        },
        "create": {
            "mode": "write",
            "method": "POST",
            "path": "/v3/a/{account_id}/users.json",
            "flags": [("account-id", "account_id", False), ("payload-json", "payload_json", True)],
        },
        "update": {
            "mode": "write",
            "method": "PUT",
            "path": "/v3/a/{account_id}/users/{user_id}.json",
            "flags": [("account-id", "account_id", False), ("user-id", "user_id", True), ("payload-json", "payload_json", True)],
        },
        "delete": {
            "mode": "write",
            "method": "DELETE",
            "path": "/v3/a/{account_id}/users/{user_id}.json",
            "flags": [("account-id", "account_id", False), ("user-id", "user_id", True)],
            "requires_payload": False,
        },
    },
    "leads": {
        "list": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/leads.json",
            "flags": [("account-id", "account_id", False)],
            "query_params": _API_COMMAND_QUERY_PARAMS.get("leads list", ()),
        },
    },
    "lead-timelines": {
        "get": {
            "mode": "read",
            "method": "GET",
            "path": "/v3/a/{account_id}/leads/{lead_id}/timeline.json",
            "flags": [("account-id", "account_id", False), ("lead-id", "lead_id", True)],
        },
    },
}


def _add_api_family_parsers(
    parent_subparsers: argparse._SubParsersAction,
    family_name: str,
    command_catalog: dict[str, dict[str, object]],
) -> None:
    family_parser = parent_subparsers.add_parser(family_name, help=f"{family_name} API commands")
    family_subparsers = family_parser.add_subparsers(dest="api_cmd", required=True, parser_class=_ToolArgumentParser)
    for command_name, spec in command_catalog.items():
        mode = str(spec.get("mode", "read"))
        command_parser = family_subparsers.add_parser(command_name, help=f"{mode} command")
        configured_flags = {entry[1] for entry in spec.get("flags", [])}  # type: ignore[union-attr]
        for flag_name, attr_name, required in spec["flags"]:  # type: ignore[index]
            if attr_name == "payload_json":
                required = False
            command_parser.add_argument(f"--{flag_name}", dest=attr_name, required=required, help=f"{attr_name.replace('_', ' ')}")
        seen_query_flags: set[str] = { _query_flag_name(attr) for attr in configured_flags }
        for query_param, attr_name in spec.get("query_params", ()):  # type: ignore[assignment]
            query_flag = _query_flag_name(attr_name)
            if query_flag in seen_query_flags or attr_name in configured_flags:
                continue
            seen_query_flags.add(query_flag)
            command_parser.add_argument(f"--{_query_flag_name(attr_name)}", dest=attr_name, action="append", help=f"{attr_name.replace('_', ' ')}")
        command_parser.set_defaults(
            api_cmd=command_name,
            func=_cmd_generic_api_call,
            api_spec=spec,
            write_capable=str(spec.get("mode", "read")) == "write",
        )


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str | None,
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
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="qwayk-callrail-safe-agent-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    p.add_argument("--run-id", default=None, help="Optional run id (for run history/audit)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing local run artifacts")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    for family_name, command_catalog in _API_COMMAND_CATALOG.items():
        _add_api_family_parsers(
            parent_subparsers=sub,
            family_name=family_name,
            command_catalog=command_catalog,
        )

    return p


def _output_mode_from_argv(argv: list[str]) -> str:
    # Default is json; treat unknown/missing value as json.
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1] or "").strip()
    return v if v in {"json", "text"} else "json"


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        # `--help` and similar argparse exits. For parse errors, we raise ValidationError instead.
        try:
            return int(e.code or 0)
        except Exception:
            return 0
    write_capable = bool(getattr(args, "write_capable", False))
    run_ctx: RunContext = init_run_context(
        env_file=str(args.env_file),
        enabled=write_capable,
        run_id=str(args.run_id) if args.run_id else None,
        artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
        no_artifacts=bool(args.no_artifacts),
    )
    run_audit_log_path = str(run_ctx.audit_log_path) if (run_ctx.enabled and run_ctx.audit_log_path) else None
    global_audit_log_path = str(args.log_file) if args.log_file else None

    project_cfg, config_dir = load_project_config(str(getattr(args, "config", None) or "") or None)
    project_dir_arg = str(getattr(args, "project_dir", "") or "").strip()
    project_dir = Path(project_dir_arg) if project_dir_arg else (Path(config_dir) if config_dir else Path("."))

    loggers: list[AuditLogger] = []
    if run_audit_log_path:
        loggers.append(AuditLogger(path=run_audit_log_path, enabled=True))
    if global_audit_log_path:
        loggers.append(AuditLogger(path=global_audit_log_path, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    runs_index_path = runs_index_path_for_env_file(str(args.env_file))
    if str(getattr(args, "cmd", "") or "") == "runs":
        # `runs` is a local-only command; it still needs to know where the index lives.
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "qwayk-callrail-safe-agent-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"qwayk-callrail-safe-agent-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "qwayk-callrail-safe-agent-cli " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "qwayk-callrail-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Some commands are local-only and don't need API config.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "qwayk-callrail-safe-agent-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_irreversible": bool(args.ack_irreversible),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "qwayk-callrail-safe-agent-cli",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_irreversible": bool(args.ack_irreversible),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "qwayk-callrail-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-callrail-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )

        return rc
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except SafetyError as e:
        # Safety refusals are "safe no-ops" (not errors).
        audit.write("refused", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-callrail-safe-agent-cli",
            version=__version__,
            command="qwayk-callrail-safe-agent-cli " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-callrail-safe-agent-cli",
            version=__version__,
            command="qwayk-callrail-safe-agent-cli " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-callrail-safe-agent-cli",
            version=__version__,
            command="qwayk-callrail-safe-agent-cli " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    finally:
        audit.close()
