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


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_string_array(
    raw: Any,
    *,
    field: str,
    required: bool = False,
    min_items: int = 0,
    max_items: int | None = None,
) -> list[str] | None:
    if raw is None:
        if required:
            raise ValidationError(f"Missing --{field}")
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON string array")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field}[{index}] must be a non-empty string")
        items.append(item.strip())
    if len(items) < min_items:
        raise ValidationError(f"--{field} must contain at least {min_items} item(s)")
    if max_items is not None and len(items) > max_items:
        raise ValidationError(f"--{field} must contain at most {max_items} item(s)")
    return items


def _coerce_schema_payload(raw: Any, *, field: str, for_update: bool) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict) or not value:
        raise ValidationError(f"--{field} must be a non-empty JSON object")

    payload = dict(value)
    payload["fqdn"] = _coerce_non_empty_text(payload.get("fqdn"), field=f"{field}.fqdn")
    payload["namespace"] = _coerce_non_empty_text(payload.get("namespace"), field=f"{field}.namespace")
    json_schema = payload.get("jsonSchema")
    if not isinstance(json_schema, dict) or not json_schema:
        raise ValidationError(f"--{field}.jsonSchema must be a non-empty JSON object")
    payload["jsonSchema"] = json_schema

    if for_update:
        payload["id"] = _coerce_non_empty_text(payload.get("id"), field=f"{field}.id")
        payload["revision"] = _coerce_non_empty_text(payload.get("revision"), field=f"{field}.revision")

    return payload


def _resolve_data_extension_schemas_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="data-extension-schemas",
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


def _extract_schemas(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    data_extension_schemas = payload.get("dataExtensionSchemas")
    if not isinstance(data_extension_schemas, list):
        raise ValidationError(f"{operation} response did not include a dataExtensionSchemas array")
    return [item for item in data_extension_schemas if isinstance(item, dict)]


def _extract_schema(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    data_extension_schema = payload.get("dataExtensionSchema")
    if not isinstance(data_extension_schema, dict):
        raise ValidationError(f"{operation} response did not include a dataExtensionSchema object")
    return data_extension_schema


def _find_schema_by_id(schemas: list[dict[str, Any]], schema_id: str) -> dict[str, Any] | None:
    for schema in schemas:
        if isinstance(schema.get("id"), str) and schema.get("id") == schema_id:
            return schema
    return None


def _find_schema_by_namespace(schemas: list[dict[str, Any]], namespace: str) -> dict[str, Any] | None:
    for schema in schemas:
        if isinstance(schema.get("namespace"), str) and schema.get("namespace") == namespace:
            return schema
    return None


def _list_schemas(
    *,
    fqdn: str,
    namespaces: list[str] | None,
    fields: list[str] | None,
    extension_points: list[str] | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"fqdn": fqdn}
    if namespaces:
        params["namespaces"] = namespaces
    if fields:
        params["fields"] = fields
    if extension_points:
        params["extensionPoints"] = extension_points
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/schema-service/v1/schemas",
        headers=headers,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_schemas(payload, operation="data-extension-schemas.list")


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["data-extension-schema-write"] + (["irreversible"] if requires_ack else []),
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
            "notes": (
                "Captured current data extension schema state before planning."
                if has_before_state
                else "No useful before-state snapshot exists for this create-style write."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved before-state only as a manual reference."
                if has_before_state
                else "No automatic rollback and no useful before-state snapshot."
            ),
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="data-extension-schemas")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: data extension schema state changed since plan was created")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
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
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No useful before-state snapshot was available for this create-style write."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the reviewed plan snapshot as a reference."
                if has_before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
        },
    }


def _build_schema_checks(expected_schema: dict[str, Any], actual_schema: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for field in ("id", "fqdn", "namespace"):
        if field in expected_schema:
            checks.append({"field": field, "expected": expected_schema.get(field), "actual": actual_schema.get(field)})
    if "jsonSchema" in expected_schema:
        checks.append(
            {"field": "jsonSchema", "expected": expected_schema.get("jsonSchema"), "actual": actual_schema.get("jsonSchema")}
        )
    return checks


def _schema_contains_field_path(json_schema: dict[str, Any], field_path: str) -> bool:
    current = json_schema
    parts = [part for part in field_path.split(".") if part]
    if not parts:
        return False
    for index, part in enumerate(parts):
        properties = current.get("properties")
        if not isinstance(properties, dict) or part not in properties:
            return False
        next_value = properties.get(part)
        if index == len(parts) - 1:
            return True
        if not isinstance(next_value, dict):
            return False
        current = next_value
    return False


def cmd_data_extension_schemas_list(args, ctx) -> int:
    try:
        fqdn = _coerce_non_empty_text(getattr(args, "fqdn", None), field="fqdn")
        namespaces = _coerce_string_array(getattr(args, "namespaces_json", None), field="namespaces-json", max_items=100)
        fields = _coerce_string_array(getattr(args, "fields_json", None), field="fields-json", max_items=5)
        extension_points = _coerce_string_array(
            getattr(args, "extension_points_json", None), field="extension-points-json", max_items=20
        )
        headers, auth_mode = _resolve_data_extension_schemas_auth(ctx=ctx)
        schemas = _list_schemas(
            fqdn=fqdn,
            namespaces=namespaces,
            fields=fields,
            extension_points=extension_points,
            ctx=ctx,
            headers=headers,
        )
        params: dict[str, Any] = {"fqdn": fqdn}
        if namespaces:
            params["namespaces"] = namespaces
        if fields:
            params["fields"] = fields
        if extension_points:
            params["extensionPoints"] = extension_points
        ctx["out"].emit(
            {
                "ok": True,
                "method": "data-extension-schemas.list",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/schema-service/v1/schemas", "params": params},
                "response": {"dataExtensionSchemas": schemas},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "data-extension-schemas.list",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "data-extension-schemas.list",
            }
        )
        return 1


def cmd_data_extension_schemas_create(args, ctx) -> int:
    try:
        payload = _coerce_schema_payload(getattr(args, "data_extension_schema_json", None), field="data-extension-schema-json", for_update=False)
        headers, auth_mode = _resolve_data_extension_schemas_auth(ctx=ctx)
        current_schemas = _list_schemas(
            fqdn=payload["fqdn"],
            namespaces=None,
            fields=None,
            extension_points=None,
            ctx=ctx,
            headers=headers,
        )
        existing_namespace = _find_schema_by_namespace(current_schemas, payload["namespace"])
        if existing_namespace is not None:
            raise SafetyError("Refused: a schema with this fqdn and namespace already exists; use update instead")
        request = {"method": "POST", "path": "/schema-service/v1/schemas", "body": {"dataExtensionSchema": payload}}
        selector = {
            "kind": "wix-data-extension-schema",
            "operation": "create",
            "fqdn": payload["fqdn"],
            "namespace": payload["namespace"],
        }
        before_state = {"dataExtensionSchemas": current_schemas}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="data-extension-schemas.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="data-extension-schemas.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "create",
                        "fqdn": payload["fqdn"],
                        "namespace": payload["namespace"],
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and re-read the schema list for the same fqdn.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-extension-schemas.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="data-extension-schemas.create",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "dataExtensionSchemas": _list_schemas(
                    fqdn=payload["fqdn"],
                    namespaces=None,
                    fields=None,
                    extension_points=None,
                    ctx=ctx,
                    headers=headers,
                )
            },
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/schema-service/v1/schemas",
            headers=headers,
            params=None,
            json_body={"dataExtensionSchema": payload},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_schema = _extract_schema(response, operation="data-extension-schemas.create")
        created_id = _coerce_non_empty_text(created_schema.get("id"), field="response.dataExtensionSchema.id")
        after_schema = _find_schema_by_id(
            _list_schemas(
                fqdn=payload["fqdn"],
                namespaces=None,
                fields=None,
                extension_points=None,
                ctx=ctx,
                headers=headers,
            ),
            created_id,
        )
        if after_schema is None:
            raise ValidationError("Create verification could not find the created schema in the read-back list")
        expected_after = dict(payload)
        expected_after["id"] = created_id
        checks = _build_schema_checks(expected_after, after_schema)
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": "/schema-service/v1/schemas",
            "method": "GET",
            "checks": checks,
            "after": after_schema,
            "notes": "Create verification uses response id plus read-back list for the same fqdn.",
        }
        receipt = _build_receipt(
            method="data-extension-schemas.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "data-extension-schemas.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "data-extension-schemas.create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "data-extension-schemas.create",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "data-extension-schemas.create",
            }
        )
        return 1


def cmd_data_extension_schemas_update(args, ctx) -> int:
    try:
        payload = _coerce_schema_payload(getattr(args, "data_extension_schema_json", None), field="data-extension-schema-json", for_update=True)
        headers, auth_mode = _resolve_data_extension_schemas_auth(ctx=ctx)
        current_schemas = _list_schemas(
            fqdn=payload["fqdn"],
            namespaces=None,
            fields=None,
            extension_points=None,
            ctx=ctx,
            headers=headers,
        )
        current_schema = _find_schema_by_id(current_schemas, payload["id"])
        if current_schema is None:
            raise SafetyError("Refused: current schema was not found in the read-back list for this fqdn")
        request = {"method": "PUT", "path": "/schema-service/v1/schemas", "body": {"dataExtensionSchema": payload}}
        selector = {"kind": "wix-data-extension-schema", "operation": "update", "schema_id": payload["id"], "fqdn": payload["fqdn"]}
        before_state = {"dataExtensionSchema": current_schema}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="data-extension-schemas.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="data-extension-schemas.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {"operation": "update", "schema_id": payload["id"], "fields": sorted(payload.keys())}
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify changed schema fields by re-reading the schema list for the same fqdn.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-extension-schemas.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="data-extension-schemas.update",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "dataExtensionSchema": _find_schema_by_id(
                    _list_schemas(
                        fqdn=payload["fqdn"],
                        namespaces=None,
                        fields=None,
                        extension_points=None,
                        ctx=ctx,
                        headers=headers,
                    ),
                    payload["id"],
                )
            },
        )
        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path="/schema-service/v1/schemas",
            headers=headers,
            params=None,
            json_body={"dataExtensionSchema": payload},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_schema = _find_schema_by_id(
            _list_schemas(
                fqdn=payload["fqdn"],
                namespaces=None,
                fields=None,
                extension_points=None,
                ctx=ctx,
                headers=headers,
            ),
            payload["id"],
        )
        if after_schema is None:
            raise ValidationError("Update verification could not find the schema in the read-back list")
        expected_after = dict(payload)
        checks = _build_schema_checks(expected_after, after_schema)
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": "/schema-service/v1/schemas",
            "method": "GET",
            "before": current_schema,
            "after": after_schema,
            "checks": checks,
            "notes": "Update verification uses read-back list for the same fqdn.",
        }
        receipt = _build_receipt(
            method="data-extension-schemas.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "data-extension-schemas.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "data-extension-schemas.update",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "data-extension-schemas.update",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "data-extension-schemas.update",
            }
        )
        return 1


def cmd_data_extension_schemas_delete_user_defined_fields(args, ctx) -> int:
    try:
        schema_id = _coerce_non_empty_text(getattr(args, "data_extension_schema_id", None), field="data-extension-schema-id")
        fqdn = _coerce_non_empty_text(getattr(args, "fqdn", None), field="fqdn")
        fields_to_delete = _coerce_string_array(
            getattr(args, "fields_to_delete_json", None),
            field="fields-to-delete-json",
            required=True,
            min_items=1,
            max_items=10,
        )
        headers, auth_mode = _resolve_data_extension_schemas_auth(ctx=ctx)
        current_schemas = _list_schemas(
            fqdn=fqdn,
            namespaces=None,
            fields=["ARCHIVED"],
            extension_points=None,
            ctx=ctx,
            headers=headers,
        )
        current_schema = _find_schema_by_id(current_schemas, schema_id)
        if current_schema is None:
            raise SafetyError("Refused: current schema was not found in the read-back list for this fqdn")
        request = {
            "method": "POST",
            "path": "/schema-service/v1/schemas/delete-user-defined-fields",
            "body": {"dataExtensionSchemaId": schema_id, "fieldsToDelete": fields_to_delete},
        }
        selector = {"kind": "wix-data-extension-schema", "operation": "delete-user-defined-fields", "schema_id": schema_id, "fqdn": fqdn}
        before_state = {"dataExtensionSchema": current_schema}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="data-extension-schemas.delete-user-defined-fields",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="data-extension-schemas.delete-user-defined-fields",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {"operation": "delete-user-defined-fields", "schema_id": schema_id, "fieldsToDelete": fields_to_delete}
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify deleted field paths are gone from the re-read schema.",
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "data-extension-schemas.delete-user-defined-fields",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="data-extension-schemas.delete-user-defined-fields",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "dataExtensionSchema": _find_schema_by_id(
                    _list_schemas(
                        fqdn=fqdn,
                        namespaces=None,
                        fields=["ARCHIVED"],
                        extension_points=None,
                        ctx=ctx,
                        headers=headers,
                    ),
                    schema_id,
                )
            },
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/schema-service/v1/schemas/delete-user-defined-fields",
            headers=headers,
            params=None,
            json_body={"dataExtensionSchemaId": schema_id, "fieldsToDelete": fields_to_delete},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_schema = _find_schema_by_id(
            _list_schemas(
                fqdn=fqdn,
                namespaces=None,
                fields=["ARCHIVED"],
                extension_points=None,
                ctx=ctx,
                headers=headers,
            ),
            schema_id,
        )
        if after_schema is None:
            raise ValidationError("Delete verification could not find the schema in the read-back list")
        checks = [
            {
                "field_path": field_path,
                "expected_present": False,
                "actual_present": _schema_contains_field_path(after_schema.get("jsonSchema") or {}, field_path),
            }
            for field_path in fields_to_delete or []
        ]
        verification = {
            "ok": all(check["actual_present"] is False for check in checks),
            "type": "read-after-write",
            "path": "/schema-service/v1/schemas",
            "method": "GET",
            "before": current_schema,
            "after": after_schema,
            "checks": checks,
            "notes": "Delete verification confirms the requested field paths are absent from the re-read schema.",
        }
        receipt = _build_receipt(
            method="data-extension-schemas.delete-user-defined-fields",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "data-extension-schemas.delete-user-defined-fields",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "data-extension-schemas.delete-user-defined-fields",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "data-extension-schemas.delete-user-defined-fields",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "data-extension-schemas.delete-user-defined-fields",
            }
        )
        return 1
