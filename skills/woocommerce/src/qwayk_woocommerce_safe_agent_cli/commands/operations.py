from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from ..catalog import OperationSpec, load_operation_catalog
from ..client import ResponseEnvelope, WooCommerceClient
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file


_BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this WooCommerce write has no saved before-state snapshot. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _json_sha256(obj: Any) -> str | None:
    if obj is None:
        return None
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_json_arg(*, file_value: str | None, inline_value: str | None, label: str) -> Any:
    if file_value and inline_value:
        raise ValidationError(f"Use either --{label}-file or --{label}-json, not both")
    if file_value:
        return read_json_file(file_value)
    if inline_value:
        try:
            return json.loads(inline_value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(f"Invalid --{label}-json: {type(exc).__name__}: {exc}") from exc
    return None


def _require_json_object(value: Any, *, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return dict(value)


def _coerce_positive_int(value: int | None, *, label: str) -> int | None:
    if value is None:
        return None
    if int(value) <= 0:
        raise ValidationError(f"{label} must be > 0")
    return int(value)


def _path_flag_name(path_param: str) -> str:
    return path_param.replace("_", "-")


def _path_values_from_args(spec: OperationSpec, args: Any) -> dict[str, str]:
    values: dict[str, str] = {}
    for param in spec.path_parameters:
        raw = getattr(args, param, None)
        if raw is None or str(raw).strip() == "":
            raise ValidationError(f"Missing required --{_path_flag_name(param)}")
        values[param] = str(raw).strip()
    return values


def _render_path(path_template: str, values: dict[str, str]) -> str:
    rendered = path_template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", value)
    if "{" in rendered or "}" in rendered:
        raise ValidationError(f"Could not fully render path: {path_template}")
    return rendered


def _build_request_parts(spec: OperationSpec, args: Any) -> tuple[dict[str, str], str, dict[str, Any], Any]:
    path_values = _path_values_from_args(spec, args)
    rendered_path = _render_path(spec.path, path_values)

    params_value = _read_json_arg(
        file_value=getattr(args, "params_file", None),
        inline_value=getattr(args, "params_json", None),
        label="params",
    )
    params = _require_json_object(params_value, label="Query params")
    page = _coerce_positive_int(getattr(args, "page", None), label="page")
    per_page = _coerce_positive_int(getattr(args, "per_page", None), label="per-page")
    max_pages = _coerce_positive_int(getattr(args, "max_pages", None), label="max-pages")
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if max_pages is not None:
        params["_max_pages_guard"] = max_pages

    body = _read_json_arg(
        file_value=getattr(args, "body_file", None),
        inline_value=getattr(args, "body_json", None),
        label="body",
    )
    if spec.body_mode == "none" and body is not None:
        raise ValidationError(f"{spec.key} does not accept --body-file or --body-json")
    if spec.body_mode == "required" and body is None:
        raise ValidationError(f"{spec.key} requires --body-file or --body-json")
    return path_values, rendered_path, params, body


def _risk_reasons(spec: OperationSpec) -> list[str]:
    reasons = [f"{spec.method.lower()} request"]
    if spec.path.endswith("/batch"):
        reasons.append("batch endpoint")
    if spec.family == "order-actions":
        reasons.append("can trigger customer email")
    if spec.family == "payment-gateways":
        reasons.append("changes checkout payment settings")
    if spec.family == "webhooks":
        reasons.append("changes outbound webhook delivery")
    if spec.family == "system-status-tools":
        reasons.append("runs maintenance or repair tooling")
    if spec.family == "shipping-zone-locations":
        reasons.append("rewrites zone location rules")
    if spec.method == "DELETE":
        reasons.append("delete operation")
    return reasons


def _required_flags(spec: OperationSpec) -> list[str]:
    flags = ["--apply", "--plan-in"]
    if spec.yes_required:
        flags.append("--yes")
    return flags


def _verification_plan(spec: OperationSpec) -> dict[str, Any]:
    if spec.method != "GET":
        return {
            "type": "best_effort_after_apply",
            "requires_no_snapshot_approval": True,
            "notes": "Apply can run after explicit no-snapshot approval, then records the WooCommerce response.",
        }
    if spec.verification_mode == "read-back":
        return {"type": "read_back", "path_template": spec.verify_get_path}
    if spec.verification_mode == "delete-response":
        return {"type": "delete_response", "notes": "Check deleted=true in WooCommerce response."}
    if spec.verification_mode == "response":
        return {"type": "response_only", "notes": "Use the provider response as the proof surface."}
    return {"type": "none", "notes": "Read-only operation."}


def _before_state_contract(spec: OperationSpec) -> dict[str, Any]:
    if spec.method == "GET":
        return {
            "required": False,
            "supported": False,
            "status": "not-required",
            "notes": "This is a read operation, so no before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "notes": (
            "No useful before-state snapshot is captured for this WooCommerce write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _refuse_write_without_before_state() -> None:
    raise SafetyError(_BEFORE_STATE_REFUSAL_REASON)


def _build_plan(spec: OperationSpec, *, path: str, params: dict[str, Any], body: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    cleaned_params = {key: value for key, value in params.items() if key != "_max_pages_guard"}
    return {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].api_base_url,
        "command": ctx["command_str"],
        "selector": {
            "operation": spec.key,
            "method": spec.method,
            "path": path,
        },
        "risk_level": spec.risk_level,
        "risk_reasons": _risk_reasons(spec),
        "required_flags": _required_flags(spec),
        "baseline": {
            "env_fingerprint": ctx["cfg"].api_base_url,
            "operation": spec.key,
            "method": spec.method,
            "path": path,
            "query": cleaned_params,
            "body_sha256": _json_sha256(body),
        },
        "request": {
            "method": spec.method,
            "path": path,
            "query": cleaned_params,
            "body": body,
        },
        "before_state": _before_state_contract(spec),
        "verification_plan": _verification_plan(spec),
        "rollback": {
            "supported": False,
            "notes": (
                "No WooCommerce snapshots, provider backups, or machine rollback plans are "
                "created by this tool, so there is no built-in undo."
            ),
        },
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    spec: OperationSpec,
    path: str,
    params: dict[str, Any],
    body: Any,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    selector = plan.get("selector")
    if not isinstance(baseline, dict) or not isinstance(selector, dict):
        raise SafetyError("Refused: plan is missing selector/baseline data")
    cleaned_params = {key: value for key, value in params.items() if key != "_max_pages_guard"}
    expected_hash = _json_sha256(body)
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].api_base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match this WooCommerce store")
    if str(selector.get("operation") or "") != spec.key:
        raise SafetyError("Refused: plan operation does not match this command")
    if str(baseline.get("method") or "") != spec.method:
        raise SafetyError("Refused: plan method does not match this command")
    if str(baseline.get("path") or "") != path:
        raise SafetyError("Refused: plan path does not match this command")
    if baseline.get("query") != cleaned_params:
        raise SafetyError("Refused: plan query params do not match this command")
    if baseline.get("body_sha256") != expected_hash:
        raise SafetyError("Refused: plan body does not match this command")


def _pagination_headers(envelope: ResponseEnvelope) -> dict[str, Any]:
    total_raw = envelope.response.headers.get("x-wp-total")
    pages_raw = envelope.response.headers.get("x-wp-totalpages")
    total = int(total_raw) if total_raw and str(total_raw).isdigit() else None
    total_pages = int(pages_raw) if pages_raw and str(pages_raw).isdigit() else None
    return {"total": total, "total_pages": total_pages}


def _collect_paginated_read(
    client: WooCommerceClient,
    spec: OperationSpec,
    *,
    path: str,
    params: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    collected: list[Any] = []
    page = int(params.get("page") or 1)
    per_page = int(params.get("per_page") or 100)
    max_pages = int(params.pop("_max_pages_guard", 10) or 10)
    params["page"] = page
    params["per_page"] = per_page
    pages_fetched = 0
    totals: dict[str, Any] = {"total": None, "total_pages": None}

    while True:
        envelope = client.request_json("GET", path, params=params, auth_required=spec.auth_required)
        if not isinstance(envelope.payload, list):
            raise RuntimeError(f"{spec.key} returned a non-list payload, so --all cannot continue")
        collected.extend(envelope.payload)
        pages_fetched += 1
        totals = _pagination_headers(envelope)
        total_pages = totals.get("total_pages")
        if not total_pages or page >= total_pages or pages_fetched >= max_pages:
            break
        page += 1
        params["page"] = page

    return collected, {"pages_fetched": pages_fetched, **totals}


def cmd_operations_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    operations = [
        {
            "key": spec.key,
            "family": spec.family,
            "action": spec.action,
            "method": spec.method,
            "path": spec.path,
            "risk_level": spec.risk_level,
            "docs_url": spec.docs_url,
        }
        for spec in load_operation_catalog()
    ]
    ctx["out"].emit({"ok": True, "count": len(operations), "operations": operations})
    return 0


def cmd_execute_operation(args: Any, ctx: dict[str, Any]) -> int:
    spec: OperationSpec = getattr(args, "operation_spec")
    _path_values, rendered_path, params, body = _build_request_parts(spec, args)
    client = WooCommerceClient(
        cfg=ctx["cfg"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
        user_agent=f'{ctx["tool"]}/{ctx["tool_version"]}',
    )

    if spec.method == "GET":
        if getattr(args, "all", False):
            if not spec.supports_pagination:
                raise ValidationError(f"{spec.key} does not support --all pagination")
            data, pagination = _collect_paginated_read(client, spec, path=rendered_path, params=dict(params))
            out = {
                "ok": True,
                "operation": spec.key,
                "method": spec.method,
                "path": rendered_path,
                "docs_url": spec.docs_url,
                "pagination": pagination,
                "data": data,
            }
            ctx["audit"].write("operation.read", {"operation": spec.key, "path": rendered_path, "pagination": pagination})
            ctx["out"].emit(out)
            return 0

        params.pop("_max_pages_guard", None)
        envelope = client.request_json(spec.method, rendered_path, params=params, auth_required=spec.auth_required)
        out = {
            "ok": True,
            "operation": spec.key,
            "method": spec.method,
            "path": rendered_path,
            "docs_url": spec.docs_url,
            "pagination": _pagination_headers(envelope),
            "data": envelope.payload,
        }
        ctx["audit"].write("operation.read", {"operation": spec.key, "path": rendered_path})
        ctx["out"].emit(out)
        return 0

    plan = _build_plan(spec, path=rendered_path, params=params, body=body, ctx=ctx)
    plan_out = ctx.get("plan_out")
    plan_out_path = write_json_file(plan_out, plan) if plan_out else None
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_out_path}
        ctx["audit"].write("operation.plan", {"operation": spec.key, "path": rendered_path, "plan_out": plan_out_path})
        ctx["out"].emit(out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: write commands must be applied from a reviewed --plan-in file")
    if spec.yes_required and not bool(ctx.get("yes")):
        raise SafetyError("Refused: this WooCommerce write is high-risk and needs --yes")

    plan_obj = read_json_file(ctx["plan_in"])
    if not isinstance(plan_obj, dict):
        raise ValidationError("Plan file must be a JSON object")
    _validate_plan_for_apply(plan_obj, spec=spec, path=rendered_path, params=params, body=body, ctx=ctx)
    if not bool(ctx.get("ack_no_snapshot")):
        _refuse_write_without_before_state()

    params.pop("_max_pages_guard", None)
    envelope = client.request_json(
        spec.method,
        rendered_path,
        params=params,
        json_body=body,
        auth_required=spec.auth_required,
    )
    receipt = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "applied_at_utc": _utc_now(),
        "operation": spec.key,
        "method": spec.method,
        "path": rendered_path,
        "docs_url": spec.docs_url,
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "recovery": plan.get("rollback"),
        "response": {
            "http_status": envelope.response.status,
            "payload": envelope.payload,
        },
        "verification": {
            "type": "provider_response",
            "ok": 200 <= int(envelope.response.status) < 300,
        },
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "plan": plan, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "operation.apply",
        {
            "operation": spec.key,
            "path": rendered_path,
            "http_status": envelope.response.status,
            "receipt_out": receipt_path,
            "no_snapshot_approval": True,
        },
    )
    ctx["out"].emit(out)
    return 0
