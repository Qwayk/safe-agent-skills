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


COMMAND_FAMILY = "suppliers-hub-suppliers"
SUPPLIERS_PATH = "/suppliers-hub/v1/suppliers"
QUERY_PATH = "/suppliers-hub/v1/suppliers/query"
BULK_CREATE_PATH = "/suppliers-hub/v1/bulk/suppliers/create"
BULK_DELETE_PATH = "/suppliers-hub/v1/bulk/suppliers/delete"
BULK_UPDATE_PATH = "/suppliers-hub/v1/bulk/suppliers/update"
BULK_UPDATE_TAGS_PATH = "/suppliers-hub/v1/bulk/suppliers/update-tags"
BULK_UPDATE_TAGS_BY_FILTER_PATH = "/suppliers-hub/v1/bulk/suppliers/update-tags-by-filter"


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


def _supplier_object(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Supplier payload must be a JSON object")
    supplier = payload.get("supplier")
    if isinstance(supplier, dict):
        return supplier
    return payload


def _current_revision(before_state: dict[str, Any]) -> str:
    supplier = _supplier_object(before_state)
    revision = supplier.get("revision")
    if revision is None or str(revision).strip() == "":
        raise SafetyError("Refused: current supplier revision was not available from Wix before-state")
    return str(revision).strip()


def _body_with_supplier_id_and_revision(*, body: dict[str, Any], supplier_id: str, before_state: dict[str, Any]) -> dict[str, Any]:
    updated = dict(body)
    supplier = updated.get("supplier")
    if isinstance(supplier, dict):
        provided_id = supplier.get("id")
        if provided_id is not None and str(provided_id).strip() != supplier_id:
            raise SafetyError("Refused: provided supplier.id does not match --supplier-id")
        revised_supplier = dict(supplier)
        revised_supplier["id"] = supplier_id
        current_revision = _current_revision(before_state)
        provided_revision = revised_supplier.get("revision")
        if provided_revision is not None and str(provided_revision).strip() != current_revision:
            raise SafetyError("Refused: provided supplier.revision does not match current supplier revision")
        revised_supplier["revision"] = current_revision
        updated["supplier"] = revised_supplier
        return updated

    provided_id = updated.get("id")
    if provided_id is not None and str(provided_id).strip() != supplier_id:
        raise SafetyError("Refused: provided supplier id does not match --supplier-id")
    updated["id"] = supplier_id
    current_revision = _current_revision(before_state)
    provided_revision = updated.get("revision")
    if provided_revision is not None and str(provided_revision).strip() != current_revision:
        raise SafetyError("Refused: provided supplier.revision does not match current supplier revision")
    updated["revision"] = current_revision
    return {"supplier": updated}


def _supplier_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValidationError("Each supplier entry must be a JSON object")
    supplier = entry.get("supplier")
    if isinstance(supplier, dict):
        return supplier
    return entry


def _supplier_id_from_entry(entry: dict[str, Any]) -> str:
    supplier_id = _supplier_entry(entry).get("id")
    if not isinstance(supplier_id, str) or not supplier_id.strip():
        raise ValidationError("Each bulk supplier update entry must include supplier.id")
    return supplier_id.strip()


def _body_with_bulk_supplier_ids_and_revisions(*, body: dict[str, Any], before_states: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    suppliers = body.get("suppliers")
    if not isinstance(suppliers, list) or not suppliers:
        raise ValidationError("--suppliers-json must contain a non-empty suppliers array")
    supplier_ids: list[str] = []
    updated_suppliers: list[dict[str, Any]] = []
    for entry in suppliers:
        if not isinstance(entry, dict):
            raise ValidationError("Each supplier entry must be a JSON object")
        supplier_id = _supplier_id_from_entry(entry)
        supplier = dict(_supplier_entry(entry))
        supplier["id"] = supplier_id
        before_state = before_states.get(supplier_id)
        if not before_state:
            raise SafetyError("Refused: current supplier revision was not available from Wix before-state")
        current_revision = _current_revision(before_state)
        provided_revision = supplier.get("revision")
        if provided_revision is not None and str(provided_revision).strip() != current_revision:
            raise SafetyError("Refused: provided supplier.revision does not match current supplier revision")
        supplier["revision"] = current_revision
        if "supplier" in entry:
            revised_entry = dict(entry)
            revised_entry["supplier"] = supplier
            updated_suppliers.append(revised_entry)
        else:
            updated_suppliers.append({"supplier": supplier})
        supplier_ids.append(supplier_id)
    updated = dict(body)
    updated["suppliers"] = updated_suppliers
    return updated, supplier_ids


def _supplier_ids_from_body(body: dict[str, Any], *, field: str) -> list[str]:
    raw_ids = body.get("supplierIds")
    if raw_ids is None:
        raw_ids = body.get("ids")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError(f"--{field} must contain a non-empty supplierIds array")
    supplier_ids: list[str] = []
    for raw_id in raw_ids:
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise ValidationError("Each supplier ID must be a non-empty string")
        supplier_ids.append(raw_id.strip())
    return supplier_ids


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
    if ctx.get("plan_out"):
        write_json_file(ctx["plan_out"], plan)
    apply_requested = reviewed_plan_apply_requested(ctx)
    if not apply_requested or (requires_ack and not ctx.get("ack_irreversible")):
        out = {
            "ok": True,
            "dry_run": True,
            "method": method_name,
            "plan": plan,
            "apply_hint": "Review the plan, then rerun with --plan-in, --apply, and --yes.",
        }
        if requires_ack:
            out["apply_hint"] = "Review the plan, then rerun with --plan-in, --apply, --yes, and --ack-irreversible."
        ctx["audit"].write(method_name, out)
        ctx["out"].emit(out)
        return 0

    _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
    verification: dict[str, Any] = {"type": verification_type, "notes": verification_notes}
    if verification_paths:
        verification["readbacks"] = [
            {
                "path": verify_path,
                "response": _request_json(method="GET", path=verify_path, headers=auth["headers"], params=None, json_body=None, ctx=ctx),
            }
            for verify_path in verification_paths
        ]
    receipt = {
        "method": method_name,
        "applied_at_utc": _utc_now(),
        "selector": selector,
        "request": request,
        "response": response,
        "verification": verification,
    }
    if ctx.get("receipt_out"):
        write_json_file(ctx["receipt_out"], receipt)
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response, "receipt": receipt}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def cmd_suppliers_hub_suppliers_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        supplier_id = _coerce_text(getattr(args, "supplier_id", None), field="supplier-id")
        return _emit_read(method_name=method, http_method="GET", path=f"{SUPPLIERS_PATH}/{supplier_id}", params=None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        return _emit_read(method_name=method, http_method="POST", path=QUERY_PATH, params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "supplier_json", None), field="supplier-json")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=SUPPLIERS_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-suppliers-hub-supplier"}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["suppliers-hub-supplier-create", "developer-preview", "approved-business-partner-only"],
            verification_type="provider-response",
            verification_notes="Create is verified by Wix provider response; reread the returned supplier id when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        supplier_id = _coerce_text(getattr(args, "supplier_id", None), field="supplier-id")
        body = _read_json_arg(getattr(args, "supplier_json", None), field="supplier-json")
        auth = _resolve_auth(ctx)
        path = f"{SUPPLIERS_PATH}/{supplier_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        body = _body_with_supplier_id_and_revision(body=body, supplier_id=supplier_id, before_state=before_state)
        return _emit_write(
            method_name=method,
            http_method="PATCH",
            path=path,
            body=body,
            selector={"kind": COMMAND_FAMILY, "supplier_id": supplier_id},
            proposed_changes=[{"operation": "update-suppliers-hub-supplier", "supplier_id": supplier_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["suppliers-hub-supplier-update", "developer-preview", "approved-business-partner-only"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading the supplier after update.",
            verification_paths=[path],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        supplier_id = _coerce_text(getattr(args, "supplier_id", None), field="supplier-id")
        auth = _resolve_auth(ctx)
        path = f"{SUPPLIERS_PATH}/{supplier_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        return _emit_write(
            method_name=method,
            http_method="DELETE",
            path=path,
            body=None,
            selector={"kind": COMMAND_FAMILY, "supplier_id": supplier_id},
            proposed_changes=[{"operation": "delete-suppliers-hub-supplier", "supplier_id": supplier_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["suppliers-hub-supplier-delete", "irreversible-delete", "developer-preview", "approved-business-partner-only"],
            verification_type="provider-response",
            verification_notes="Delete is verified by Wix provider response; before-state is captured in the reviewed plan.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _read_json_arg(getattr(args, "suppliers_json", None), field="suppliers-json")
        suppliers = body.get("suppliers")
        if not isinstance(suppliers, list) or not suppliers:
            raise ValidationError("--suppliers-json must contain a non-empty suppliers array")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_CREATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create-suppliers-hub-suppliers", "count": len(suppliers)}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["suppliers-hub-supplier-bulk-create", "developer-preview", "approved-business-partner-only"],
            verification_type="provider-response",
            verification_notes="Bulk create is verified by Wix provider response; inspect itemMetadata and reread returned supplier ids when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "suppliers_json", None), field="suppliers-json")
        suppliers = body.get("suppliers")
        if not isinstance(suppliers, list) or not suppliers:
            raise ValidationError("--suppliers-json must contain a non-empty suppliers array")
        supplier_ids = [_supplier_id_from_entry(entry) for entry in suppliers]
        auth = _resolve_auth(ctx)
        before_states = {
            supplier_id: _request_json(method="GET", path=f"{SUPPLIERS_PATH}/{supplier_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for supplier_id in supplier_ids
        }
        body, supplier_ids = _body_with_bulk_supplier_ids_and_revisions(body=body, before_states=before_states)
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_UPDATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "supplier_ids": supplier_ids},
            proposed_changes=[{"operation": "bulk-update-suppliers-hub-suppliers", "supplier_ids": supplier_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["suppliers-hub-supplier-bulk-update", "developer-preview", "approved-business-partner-only"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading each supplier after bulk update and inspecting itemMetadata for partial failures.",
            verification_paths=[f"{SUPPLIERS_PATH}/{supplier_id}" for supplier_id in supplier_ids],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _read_json_arg(getattr(args, "supplier_ids_json", None), field="supplier-ids-json")
        supplier_ids = _supplier_ids_from_body(body, field="supplier-ids-json")
        auth = _resolve_auth(ctx)
        before_states = {
            supplier_id: _request_json(method="GET", path=f"{SUPPLIERS_PATH}/{supplier_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for supplier_id in supplier_ids
        }
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_DELETE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "supplier_ids": supplier_ids},
            proposed_changes=[{"operation": "bulk-delete-suppliers-hub-suppliers", "supplier_ids": supplier_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["suppliers-hub-supplier-bulk-delete", "irreversible-delete", "developer-preview", "approved-business-partner-only"],
            verification_type="provider-response",
            verification_notes="Bulk delete is verified by Wix provider response and itemMetadata; before-state is captured in the reviewed plan.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        supplier_ids = _supplier_ids_from_body(body, field="tags-json")
        auth = _resolve_auth(ctx)
        before_states = {
            supplier_id: _request_json(method="GET", path=f"{SUPPLIERS_PATH}/{supplier_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for supplier_id in supplier_ids
        }
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_UPDATE_TAGS_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "supplier_ids": supplier_ids, "operation": "bulk-update-tags"},
            proposed_changes=[{"operation": "bulk-update-suppliers-hub-supplier-tags", "supplier_ids": supplier_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["suppliers-hub-supplier-bulk-update-tags", "developer-preview", "approved-business-partner-only"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading each supplier after tag update and inspecting itemMetadata for partial failures.",
            verification_paths=[f"{SUPPLIERS_PATH}/{supplier_id}" for supplier_id in supplier_ids],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_suppliers_hub_suppliers_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        selector = {"kind": COMMAND_FAMILY, "operation": "bulk-update-tags-by-filter", "filter": body.get("filter")}
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_UPDATE_TAGS_BY_FILTER_PATH,
            body=body,
            selector=selector,
            proposed_changes=[{"operation": "bulk-update-suppliers-hub-supplier-tags-by-filter", "filter": body.get("filter")}],
            before_state={},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[
                "suppliers-hub-supplier-bulk-update-tags-by-filter",
                "async-large-filtered-write",
                "empty-filter-can-update-all-suppliers",
                "developer-preview",
                "approved-business-partner-only",
            ],
            verification_type="provider-response-plus-async-job",
            verification_notes="Verify returned jobId, then inspect progress with async-jobs get or list-items. An empty filter updates all matching suppliers per official docs.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
