from __future__ import annotations

import time
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


def _coerce_text(raw: Any, *, field: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    return _coerce_text(raw, field=field)


def _resolve_folders_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="data-folders",
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


def _http_status_from_error(exc: RuntimeError) -> int | None:
    msg = str(exc)
    parts = msg.split()
    if len(parts) < 2 or parts[0] != "HTTP":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False, command_label: str) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=command_label)


def _extract_folder(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    folder = payload.get("folder", payload)
    if not isinstance(folder, dict):
        raise ValidationError(f"{operation} response did not include a folder object")
    return folder


def _extract_collection_references(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    refs = payload.get("collectionReferences")
    if not isinstance(refs, list):
        raise ValidationError(f"{operation} response did not include a collectionReferences array")
    out: list[dict[str, Any]] = []
    for item in refs:
        if isinstance(item, dict):
            out.append(item)
    return out


def _folder_id_key(folder_id: str | None) -> str:
    value = (folder_id or "").strip()
    return value if value else "__ROOT__"


def _find_collection_reference(
    references: list[dict[str, Any]],
    *,
    collection_name: str,
    folder_id: str | None,
) -> dict[str, Any] | None:
    expected_name = collection_name.strip()
    expected_folder = _folder_id_key(folder_id)
    for item in references:
        if str(item.get("collectionName") or "").strip() != expected_name:
            continue
        current_folder = _folder_id_key(item.get("folderId") if isinstance(item.get("folderId"), str) else None)
        if current_folder == expected_folder:
            return item
    return None


def _find_child_folder(root_folder: dict[str, Any], *, folder_id: str) -> dict[str, Any] | None:
    folders = root_folder.get("folders")
    if not isinstance(folders, list):
        return None
    for item in folders:
        if isinstance(item, dict) and str(item.get("id") or "").strip() == folder_id:
            return item
    return None


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: Any,
    before_state_available: bool,
    state_capture_notes: str,
    proposed_changes: list[dict[str, Any]],
    verification_notes: str,
    recovery_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["cms-folder-write", "manage-data-collections"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": before_state_available,
            "notes": state_capture_notes,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "read-after-write",
            "notes": verification_notes,
        },
        "rollback": {
            "supported": False,
            "notes": recovery_notes,
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


def _assert_plan_state_matches(*, plan: dict[str, Any], current_state: Any) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: folder state changed since the plan was created")


def _get_folder(*, ctx: dict[str, Any], headers: dict[str, str], folder_id: str | None) -> dict[str, Any]:
    params = {"folderId": folder_id} if folder_id else None
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v1/folders",
        headers=headers,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _get_collection_references(
    *,
    ctx: dict[str, Any],
    headers: dict[str, str],
    collection_name: str,
) -> dict[str, Any]:
    return _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v1/folders/collection-references/get",
        headers=headers,
        params=None,
        json_body={"collectionName": collection_name},
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def cmd_data_folders_get(args, ctx) -> int:
    try:
        folder_id = _coerce_optional_text(getattr(args, "folder_id", None), field="folder-id")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        payload = _get_folder(ctx=ctx, headers=headers, folder_id=folder_id)
        folder = _extract_folder(payload, operation="data-folders.get")
        request: dict[str, Any] = {"method": "GET", "path": "/wix-data/v1/folders"}
        if folder_id:
            request["params"] = {"folderId": folder_id}
        out = {
            "ok": True,
            "method": "data-folders.get",
            "auth_mode": auth_mode,
            "request": request,
            "response": payload,
            "folder": folder,
        }
        ctx["audit"].write("data-folders.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.get"}
        ctx["audit"].write("data-folders.get.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.get"}
        ctx["audit"].write("data-folders.get.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_create(args, ctx) -> int:
    try:
        name = _coerce_text(getattr(args, "name", None), field="name")
        description = _coerce_optional_text(getattr(args, "description", None), field="description")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        before_payload = _get_folder(ctx=ctx, headers=headers, folder_id=None)
        before_folder = _extract_folder(before_payload, operation="data-folders.create")
        request_body: dict[str, Any] = {"folderDetails": {"name": name}}
        if description is not None:
            request_body["folderDetails"]["description"] = description
        selector = {"kind": "wix-data-folder", "operation": "create", "name": name}
        request = {"method": "POST", "path": "/wix-data/v1/folders", "body": request_body}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-folders.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                state_capture_notes="Captured the current root folder before planning a new CMS folder.",
                proposed_changes=[{"operation": "create", "name": name}],
                verification_notes="Verify by reading the created folder back by returned folder ID.",
                recovery_notes="No automatic rollback. Delete the folder manually if you need to undo it.",
            )

        if not _should_apply(ctx, command_label="data-folders.create"):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-folders.create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
                "root_folder": before_folder,
            }
            ctx["audit"].write("data-folders.create.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.create", expected_selector=selector, ctx=ctx)
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/folders",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        response_folder = _extract_folder(response, operation="data-folders.create")
        created_folder_id = str(response_folder.get("id") or "").strip()
        if not created_folder_id:
            raise SafetyError("Refused: create-folder response did not include a folder id for readback verification")
        after_payload = _get_folder(ctx=ctx, headers=headers, folder_id=created_folder_id)
        after_folder = _extract_folder(after_payload, operation="data-folders.create")
        if str(after_folder.get("name") or "") != name:
            raise SafetyError("Refused: created folder name did not match readback")
        if description is not None and str(after_folder.get("description") or "") != description:
            raise SafetyError("Refused: created folder description did not match readback")
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v1/folders",
            "method": "GET",
            "before": before_folder,
            "after": after_folder,
            "notes": "Create verification rereads the returned folder ID.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-folders.create",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved root-folder snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Delete the folder if you need to undo it.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-folders.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-folders.create.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-folders.create"}
        ctx["audit"].write("data-folders.create.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.create"}
        ctx["audit"].write("data-folders.create.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.create"}
        ctx["audit"].write("data-folders.create.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_update(args, ctx) -> int:
    try:
        folder_id = _coerce_text(getattr(args, "folder_id", None), field="folder-id")
        name = _coerce_optional_text(getattr(args, "name", None), field="name")
        description = _coerce_optional_text(getattr(args, "description", None), field="description")
        if name is None and description is None:
            raise ValidationError("Provide at least one of --name or --description")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        before_payload = _get_folder(ctx=ctx, headers=headers, folder_id=folder_id)
        before_folder = _extract_folder(before_payload, operation="data-folders.update")
        if not str(before_folder.get("id") or "").strip():
            raise SafetyError("Refused: the root folder cannot be updated")
        folder_details: dict[str, Any] = {}
        if name is not None:
            folder_details["name"] = name
        if description is not None:
            folder_details["description"] = description
        request = {
            "method": "PATCH",
            "path": f"/wix-data/v1/folders/{folder_id}/details",
            "body": {"folderDetails": folder_details},
        }
        selector = {"kind": "wix-data-folder", "operation": "update", "folder_id": folder_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-folders.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                state_capture_notes="Captured the current folder before planning a details update.",
                proposed_changes=[{"operation": "update", "folder_id": folder_id, "fields": sorted(folder_details.keys())}],
                verification_notes="Verify by rereading the folder and checking the requested fields.",
                recovery_notes="No automatic rollback. Use the saved before-state only as a manual reference.",
            )

        if not _should_apply(ctx, command_label="data-folders.update"):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-folders.update",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
                "folder": before_folder,
            }
            ctx["audit"].write("data-folders.update.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.update", expected_selector=selector, ctx=ctx)
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v1/folders/{folder_id}/details",
            headers=headers,
            params=None,
            json_body={"folderDetails": folder_details},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_payload = _get_folder(ctx=ctx, headers=headers, folder_id=folder_id)
        after_folder = _extract_folder(after_payload, operation="data-folders.update")
        if name is not None and str(after_folder.get("name") or "") != name:
            raise SafetyError("Refused: updated folder name did not match readback")
        if description is not None and str(after_folder.get("description") or "") != description:
            raise SafetyError("Refused: updated folder description did not match readback")
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v1/folders",
            "method": "GET",
            "before": before_folder,
            "after": after_folder,
            "notes": "Update verification rereads the folder by ID and checks the requested fields.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-folders.update",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved folder snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Use the saved before-state snapshot as a reference.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-folders.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-folders.update.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-folders.update"}
        ctx["audit"].write("data-folders.update.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.update"}
        ctx["audit"].write("data-folders.update.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.update"}
        ctx["audit"].write("data-folders.update.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_delete(args, ctx) -> int:
    try:
        folder_id = _coerce_text(getattr(args, "folder_id", None), field="folder-id")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        before_payload = _get_folder(ctx=ctx, headers=headers, folder_id=folder_id)
        before_folder = _extract_folder(before_payload, operation="data-folders.delete")
        if not str(before_folder.get("id") or "").strip():
            raise SafetyError("Refused: the root folder cannot be deleted")
        request = {
            "method": "DELETE",
            "path": f"/wix-data/v1/folders/{folder_id}",
        }
        selector = {"kind": "wix-data-folder", "operation": "delete", "folder_id": folder_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-folders.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                state_capture_notes="Captured the current folder before planning deletion.",
                proposed_changes=[{"operation": "delete", "folder_id": folder_id}],
                verification_notes="Verify by expecting folder readback to return 404 after apply.",
                recovery_notes="No automatic rollback. Collection references move to the root folder when the folder is deleted.",
            )

        if not _should_apply(ctx, requires_ack=True, command_label="data-folders.delete"):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-folders.delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
                "folder": before_folder,
            }
            ctx["audit"].write("data-folders.delete.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-folders.delete", expected_selector=selector, ctx=ctx)
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v1/folders/{folder_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        deleted = False
        try:
            _get_folder(ctx=ctx, headers=headers, folder_id=folder_id)
        except RuntimeError as exc:
            if _http_status_from_error(exc) == 404:
                deleted = True
            else:
                raise
        if not deleted:
            raise SafetyError("Refused: deleted folder is still readable after apply")
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v1/folders",
            "method": "GET",
            "before": before_folder,
            "after": {"found": False, "folder_id": folder_id, "status": "DELETED"},
            "notes": "Delete verification rereads the folder by ID and expects 404.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-folders.delete",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved folder snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Deleted folders are gone, and collection references move back to the root folder.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-folders.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-folders.delete.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-folders.delete"}
        ctx["audit"].write("data-folders.delete.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.delete"}
        ctx["audit"].write("data-folders.delete.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.delete"}
        ctx["audit"].write("data-folders.delete.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_create_collection_reference(args, ctx) -> int:
    try:
        collection_name = _coerce_text(getattr(args, "collection_name", None), field="collection-name")
        folder_id = _coerce_optional_text(getattr(args, "folder_id", None), field="folder-id")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        before_payload = _get_collection_references(ctx=ctx, headers=headers, collection_name=collection_name)
        before_refs = _extract_collection_references(before_payload, operation="data-folders.create-collection-reference")
        if _find_collection_reference(before_refs, collection_name=collection_name, folder_id=folder_id):
            raise SafetyError("Refused: the collection reference already exists for the requested folder")
        collection_reference: dict[str, Any] = {"collectionName": collection_name}
        if folder_id is not None:
            collection_reference["folderId"] = folder_id
        request = {
            "method": "POST",
            "path": "/wix-data/v1/folders/collection-references/create",
            "body": {"collectionReference": collection_reference},
        }
        selector = {
            "kind": "wix-data-collection-reference",
            "operation": "create",
            "collection_name": collection_name,
            "folder_id": _folder_id_key(folder_id),
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="data-folders.create-collection-reference",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="data-folders.create-collection-reference",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                state_capture_notes="Captured the current folder references for the collection before planning this shortcut.",
                proposed_changes=[{"operation": "create-reference", "collection_name": collection_name, "folder_id": _folder_id_key(folder_id)}],
                verification_notes="Verify by rereading collection references and finding the requested folder reference.",
                recovery_notes="No automatic rollback. Remove the collection reference manually if you need to undo it.",
            )

        if not _should_apply(ctx, command_label="data-folders.create-collection-reference"):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-folders.create-collection-reference",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
                "collection_references": before_refs,
            }
            ctx["audit"].write("data-folders.create-collection-reference.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="data-folders.create-collection-reference",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/folders/collection-references/create",
            headers=headers,
            params=None,
            json_body={"collectionReference": collection_reference},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_payload = _get_collection_references(ctx=ctx, headers=headers, collection_name=collection_name)
        after_refs = _extract_collection_references(after_payload, operation="data-folders.create-collection-reference")
        matched_ref = _find_collection_reference(after_refs, collection_name=collection_name, folder_id=folder_id)
        if matched_ref is None:
            raise SafetyError("Refused: created collection reference did not appear in readback")
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v1/folders/collection-references/get",
            "method": "POST",
            "before": before_refs,
            "after": matched_ref,
            "notes": "Create-reference verification rereads collection references for the collection.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-folders.create-collection-reference",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved collection-reference snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Delete the collection reference if you need to undo it.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-folders.create-collection-reference",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-folders.create-collection-reference.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-folders.create-collection-reference"}
        ctx["audit"].write("data-folders.create-collection-reference.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.create-collection-reference"}
        ctx["audit"].write("data-folders.create-collection-reference.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.create-collection-reference"}
        ctx["audit"].write("data-folders.create-collection-reference.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_get_collection_references(args, ctx) -> int:
    try:
        collection_name = _coerce_text(getattr(args, "collection_name", None), field="collection-name")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        payload = _get_collection_references(ctx=ctx, headers=headers, collection_name=collection_name)
        refs = _extract_collection_references(payload, operation="data-folders.get-collection-references")
        request = {
            "method": "POST",
            "path": "/wix-data/v1/folders/collection-references/get",
            "body": {"collectionName": collection_name},
        }
        out = {
            "ok": True,
            "method": "data-folders.get-collection-references",
            "auth_mode": auth_mode,
            "request": request,
            "response": payload,
            "collection_references": refs,
        }
        ctx["audit"].write("data-folders.get-collection-references", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.get-collection-references"}
        ctx["audit"].write("data-folders.get-collection-references.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.get-collection-references"}
        ctx["audit"].write("data-folders.get-collection-references.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_folders_delete_collection_reference(args, ctx) -> int:
    try:
        collection_name = _coerce_text(getattr(args, "collection_name", None), field="collection-name")
        folder_id = _coerce_optional_text(getattr(args, "folder_id", None), field="folder-id")
        headers, auth_mode = _resolve_folders_auth(ctx=ctx)
        before_payload = _get_collection_references(ctx=ctx, headers=headers, collection_name=collection_name)
        before_refs = _extract_collection_references(before_payload, operation="data-folders.delete-collection-reference")
        matched_ref = _find_collection_reference(before_refs, collection_name=collection_name, folder_id=folder_id)
        if matched_ref is None:
            raise SafetyError("Refused: the requested collection reference does not exist")
        request_body: dict[str, Any] = {"collectionName": collection_name}
        if folder_id is not None:
            request_body["folderId"] = folder_id
        request = {
            "method": "POST",
            "path": "/wix-data/v1/folders/collection-references/delete",
            "body": request_body,
        }
        selector = {
            "kind": "wix-data-collection-reference",
            "operation": "delete",
            "collection_name": collection_name,
            "folder_id": _folder_id_key(folder_id),
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="data-folders.delete-collection-reference",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="data-folders.delete-collection-reference",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                state_capture_notes="Captured the current collection references before planning this delete.",
                proposed_changes=[{"operation": "delete-reference", "collection_name": collection_name, "folder_id": _folder_id_key(folder_id)}],
                verification_notes="Verify by rereading collection references and expecting the requested folder reference to be absent.",
                recovery_notes="No automatic rollback. Recreate the collection reference manually if you need to undo it.",
            )

        if not _should_apply(ctx, command_label="data-folders.delete-collection-reference"):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-folders.delete-collection-reference",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
                "collection_references": before_refs,
            }
            ctx["audit"].write("data-folders.delete-collection-reference.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="data-folders.delete-collection-reference",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v1/folders/collection-references/delete",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_payload = _get_collection_references(ctx=ctx, headers=headers, collection_name=collection_name)
        after_refs = _extract_collection_references(after_payload, operation="data-folders.delete-collection-reference")
        if _find_collection_reference(after_refs, collection_name=collection_name, folder_id=folder_id):
            raise SafetyError("Refused: collection reference is still present after apply")
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v1/folders/collection-references/get",
            "method": "POST",
            "before": before_refs,
            "after": after_refs,
            "notes": "Delete-reference verification rereads collection references for the collection.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-folders.delete-collection-reference",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved collection-reference snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Recreate the collection reference if you need to undo it.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-folders.delete-collection-reference",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-folders.delete-collection-reference.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-folders.delete-collection-reference"}
        ctx["audit"].write("data-folders.delete-collection-reference.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-folders.delete-collection-reference"}
        ctx["audit"].write("data-folders.delete-collection-reference.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-folders.delete-collection-reference"}
        ctx["audit"].write("data-folders.delete-collection-reference.error", out)
        ctx["out"].emit(out)
        return 1
