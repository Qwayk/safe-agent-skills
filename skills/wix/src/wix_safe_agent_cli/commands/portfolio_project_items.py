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


COMMAND_FAMILY = "portfolio-project-items"
BASE_PATH = "/portfolio/v1/items"
PROJECT_ITEMS_PATH = "/portfolio/v1/projectItems"
BULK_CREATE_PATH = "/portfolio/project-items/api/v1/bulk/portfolio/items/create"
BULK_UPDATE_PATH = "/portfolio/project-items/api/v1/bulk/portfolio/items/update"
BULK_DELETE_PATH = "/portfolio/project-items/api/v1/bulk/portfolio/items/delete"
DUPLICATE_PATH = "/portfolio/project-items/api/v1/items/duplicate"


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


def _item_object(payload: dict[str, Any]) -> dict[str, Any]:
    item = payload.get("item")
    if isinstance(item, dict):
        return item
    return payload


def _body_with_item_id(*, body: dict[str, Any], item_id: str) -> dict[str, Any]:
    updated = dict(body)
    item = updated.get("item")
    if isinstance(item, dict):
        provided_id = item.get("id")
        if provided_id is not None and str(provided_id).strip() != item_id:
            raise SafetyError("Refused: provided item.id does not match --item-id")
        revised_item = dict(item)
        revised_item["id"] = item_id
        updated["item"] = revised_item
        return updated

    provided_id = updated.get("id")
    if provided_id is not None and str(provided_id).strip() != item_id:
        raise SafetyError("Refused: provided item id does not match --item-id")
    updated["id"] = item_id
    return {"item": updated}


def _item_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValidationError("Each project item entry must be a JSON object")
    item = entry.get("item")
    if isinstance(item, dict):
        return item
    return entry


def _item_id_from_entry(entry: dict[str, Any]) -> str:
    item_id = _item_entry(entry).get("id")
    if not isinstance(item_id, str) or not item_id.strip():
        raise ValidationError("Each bulk project item update entry must include item.id")
    return item_id.strip()


def _body_with_bulk_item_ids(*, body: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    items = body.get("items")
    if not isinstance(items, list) or not items:
        raise ValidationError("--items-json must contain a non-empty items array")
    item_ids: list[str] = []
    updated_items: list[dict[str, Any]] = []
    for entry in items:
        item_id = _item_id_from_entry(entry)
        item = _item_entry(entry)
        revised_item = dict(item)
        revised_item["id"] = item_id
        if isinstance(entry, dict) and "item" in entry:
            revised_entry = dict(entry)
            revised_entry["item"] = revised_item
            updated_items.append(revised_entry)
        else:
            updated_items.append(revised_item)
        item_ids.append(item_id)
    updated = dict(body)
    updated["items"] = updated_items
    return updated, item_ids


def _item_ids_from_delete_body(body: dict[str, Any]) -> list[str]:
    raw_ids = body.get("itemIds")
    if raw_ids is None:
        raw_ids = body.get("ids")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError("--item-ids-json must contain a non-empty itemIds array")
    item_ids: list[str] = []
    for raw_id in raw_ids:
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise ValidationError("Each item ID must be a non-empty string")
        item_ids.append(raw_id.strip())
    return item_ids


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


def _emit_read(*, method_name: str, http_method: str, path: str, params: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=None, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
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


def cmd_portfolio_project_items_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        project_id = _coerce_text(getattr(args, "project_id", None), field="project-id")
        params = _read_json_arg(getattr(args, "params_json", None), field="params-json", allow_empty=True)
        return _emit_read(method_name=method, http_method="GET", path=f"{PROJECT_ITEMS_PATH}/{project_id}/items", params=params, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        item_id = _coerce_text(getattr(args, "item_id", None), field="item-id")
        params = _read_json_arg(getattr(args, "params_json", None), field="params-json", allow_empty=True)
        return _emit_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{item_id}", params=params, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "item_json", None), field="item-json")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-project-item"}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-item-create"],
            verification_type="provider-response",
            verification_notes="Create is verified by Wix provider response; reread the returned project item id when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        item_id = _coerce_text(getattr(args, "item_id", None), field="item-id")
        body = _read_json_arg(getattr(args, "item_json", None), field="item-json")
        auth = _resolve_auth(ctx)
        path = f"{BASE_PATH}/{item_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        body = _body_with_item_id(body=body, item_id=item_id)
        return _emit_write(
            method_name=method,
            http_method="PATCH",
            path=path,
            body=body,
            selector={"kind": COMMAND_FAMILY, "item_id": item_id},
            proposed_changes=[{"operation": "update-project-item", "item_id": item_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-item-update"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading the project item after update.",
            verification_paths=[path],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        item_id = _coerce_text(getattr(args, "item_id", None), field="item-id")
        auth = _resolve_auth(ctx)
        path = f"{BASE_PATH}/{item_id}"
        before_state = _request_json(method="GET", path=path, headers=auth["headers"], params=None, json_body=None, ctx=ctx)
        return _emit_write(
            method_name=method,
            http_method="DELETE",
            path=path,
            body=None,
            selector={"kind": COMMAND_FAMILY, "item_id": item_id},
            proposed_changes=[{"operation": "delete-project-item", "item_id": item_id}],
            before_state=before_state,
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["portfolio-project-item-delete", "irreversible-delete"],
            verification_type="provider-response",
            verification_notes="Delete is verified by Wix provider response; before-state is captured in the reviewed plan.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _read_json_arg(getattr(args, "items_json", None), field="items-json")
        if not isinstance(body.get("items"), list) or not body["items"]:
            raise ValidationError("--items-json must contain a non-empty items array")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=BULK_CREATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create-project-items", "count": len(body["items"])}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-item-bulk-create"],
            verification_type="provider-response",
            verification_notes="Bulk create is verified by Wix provider response; reread returned project item ids when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "items_json", None), field="items-json")
        body, item_ids = _body_with_bulk_item_ids(body=body)
        auth = _resolve_auth(ctx)
        before_states = {
            item_id: _request_json(method="GET", path=f"{BASE_PATH}/{item_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for item_id in item_ids
        }
        return _emit_write(
            method_name=method,
            http_method="PATCH",
            path=BULK_UPDATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "item_ids": item_ids},
            proposed_changes=[{"operation": "bulk-update-project-items", "item_ids": item_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-item-bulk-update"],
            verification_type="read-after-write",
            verification_notes="Verify by rereading each project item after bulk update.",
            verification_paths=[f"{BASE_PATH}/{item_id}" for item_id in item_ids],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _read_json_arg(getattr(args, "item_ids_json", None), field="item-ids-json")
        item_ids = _item_ids_from_delete_body(body)
        auth = _resolve_auth(ctx)
        before_states = {
            item_id: _request_json(method="GET", path=f"{BASE_PATH}/{item_id}", headers=auth["headers"], params=None, json_body=None, ctx=ctx)
            for item_id in item_ids
        }
        return _emit_write(
            method_name=method,
            http_method="DELETE",
            path=BULK_DELETE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "item_ids": item_ids},
            proposed_changes=[{"operation": "bulk-delete-project-items", "item_ids": item_ids}],
            before_state=before_states,
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["portfolio-project-item-bulk-delete", "irreversible-delete"],
            verification_type="provider-response",
            verification_notes="Bulk delete is verified by Wix provider response; before-state is captured in the reviewed plan.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_portfolio_project_items_duplicate(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.duplicate"
    try:
        body = _read_json_arg(getattr(args, "duplicate_json", None), field="duplicate-json")
        return _emit_write(
            method_name=method,
            http_method="POST",
            path=DUPLICATE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "duplicate"},
            proposed_changes=[{"operation": "duplicate-project-items"}],
            before_state={},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["portfolio-project-item-duplicate"],
            verification_type="provider-response",
            verification_notes="Duplicate is verified by Wix provider response; reread the target project item list when needed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
