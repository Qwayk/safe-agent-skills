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


COMMAND_FAMILY = "function-spi-configurations"
BASE_PATH = "/functions/v1/function-spi-configurations"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
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
    if not payload and not allow_empty:
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
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
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
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


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


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _configuration_body(
    raw: Any,
    *,
    field: str,
    require_id: bool = False,
    require_revision: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field=field)
    body = dict(payload) if "functionSpiConfiguration" in payload else {"functionSpiConfiguration": payload}
    configuration = body.get("functionSpiConfiguration")
    if not isinstance(configuration, dict) or not configuration:
        raise ValidationError(f"--{field} must include a non-empty functionSpiConfiguration object")
    if require_id:
        _coerce_text(configuration.get("id"), field=f"{field} functionSpiConfiguration.id")
    if require_revision:
        _coerce_text(configuration.get("revision"), field=f"{field} functionSpiConfiguration.revision")
    return body, configuration


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
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
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Function SPI Configuration plans do not capture a full before-state snapshot in this slice.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual only."},
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


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
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
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
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
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
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
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.receipt", out)
    ctx["out"].emit(out)
    return 0


def cmd_function_spi_configurations_create(args, ctx) -> int:
    method = "functionSpiConfigurations.createFunctionSpiConfiguration"
    try:
        body, configuration = _configuration_body(args.spi_configuration_json, field="spi-configuration-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"functionSpiConfiguration": configuration},
            proposed_changes=[{"operation": "create-function-spi-configuration", "functionSpiConfiguration": configuration}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-function-spi-configuration-create"],
            verification_notes="Inspect the provider response, then use function-spi-configurations get to verify the created configuration.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_function_spi_configurations_get(args, ctx) -> int:
    method = "functionSpiConfigurations.getFunctionSpiConfiguration"
    try:
        configuration_id = _coerce_text(args.spi_configuration_id, field="spi-configuration-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{configuration_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_function_spi_configurations_update(args, ctx) -> int:
    method = "functionSpiConfigurations.updateFunctionSpiConfiguration"
    try:
        body, configuration = _configuration_body(
            args.spi_configuration_json,
            field="spi-configuration-json",
            require_id=True,
            require_revision=True,
        )
        configuration_id = _coerce_text(configuration.get("id"), field="spi-configuration-json functionSpiConfiguration.id")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{configuration_id}",
            body=body,
            selector={"functionSpiConfiguration": configuration},
            proposed_changes=[{"operation": "update-function-spi-configuration", "functionSpiConfiguration": configuration}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-function-spi-configuration-update", "requires-current-revision"],
            verification_notes="Inspect the provider response, then use function-spi-configurations get to verify the updated configuration. Reactivate the function when the updated configuration should go live.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_function_spi_configurations_delete(args, ctx) -> int:
    method = "functionSpiConfigurations.deleteFunctionSpiConfiguration"
    try:
        configuration_id = _coerce_text(args.spi_configuration_id, field="spi-configuration-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{configuration_id}",
            body=None,
            selector={"functionSpiConfigurationId": configuration_id},
            proposed_changes=[
                {"operation": "delete-function-spi-configuration", "functionSpiConfigurationId": configuration_id}
            ],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-function-spi-configuration-delete", "irreversible"],
            verification_notes="Inspect the provider response, then use function-spi-configurations get or query to confirm removal.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_function_spi_configurations_query(args, ctx) -> int:
    method = "functionSpiConfigurations.queryFunctionSpiConfigurations"
    try:
        raw_query = getattr(args, "query_json", None)
        body = _read_json_arg(raw_query, field="query-json", allow_empty=True) if raw_query is not None else {}
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_function_spi_configurations_validate(args, ctx) -> int:
    method = "functionSpiConfigurations.validateFunctionSpiConfiguration"
    try:
        body, _configuration = _configuration_body(args.spi_configuration_json, field="spi-configuration-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/validate", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
