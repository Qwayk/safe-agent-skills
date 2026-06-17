from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

request_data = api_runtime.request_data

def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _attachment_items(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    if isinstance(body, dict):
        for key in ("Attachments", "Attachment", "attachments", "attachment"):
            value = body.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                return [value]
        if any(
            key in body
            for key in ("entityId", "entityType", "fileId", "id", "includeOnSend", "EntityId", "EntityType", "FileId", "Id", "IncludeOnSend")
        ):
            return [body]
    return []


def _extract_attachment_id(item: dict[str, Any] | None) -> str | None:
    if not isinstance(item, dict):
        return None
    return _string_value(item.get("id"))


def _validate_entity_type(value: Any, *, field_name: str) -> str:
    text = _string_value(value)
    if text is None:
        raise ValidationError(f"{field_name} is required")
    return text


def _normalize_entity_ids(values: Any, *, field_name: str) -> list[int]:
    if not values:
        raise ValidationError(f"At least one {field_name} is required")
    out: list[int] = []
    for value in values:
        try:
            out.append(int(value))
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"{field_name} must contain integers") from e
    if not out:
        raise ValidationError(f"At least one {field_name} is required")
    return out


def _load_attachment_object_file(path_str: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain one top-level attachment object")
    _require_attachment_fields(obj, require_id=False)
    return path, obj


def _load_attachment_list_file(path_str: str) -> tuple[Path, list[dict[str, Any]]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, list):
        raise ValidationError("JSON file must contain a top-level array of attachment objects")
    items = [item for item in obj if isinstance(item, dict)]
    if len(items) != len(obj) or not items:
        raise ValidationError("JSON file must contain a non-empty array of attachment objects")
    for item in items:
        _require_attachment_fields(item, require_id=False)
    return path, items


def _require_attachment_fields(item: dict[str, Any], *, require_id: bool) -> None:
    if not isinstance(item, dict):
        raise ValidationError("Attachment payload must be an object")
    entity_id = item.get("entityId")
    if entity_id is None:
        raise ValidationError("Attachment payload must contain entityId")
    try:
        int(entity_id)
    except Exception as e:  # noqa: BLE001
        raise ValidationError("Attachment payload entityId must be an integer") from e
    _validate_entity_type(item.get("entityType"), field_name="Attachment payload entityType")
    if _string_value(item.get("fileId")) is None:
        raise ValidationError("Attachment payload must contain fileId")
    if require_id and _string_value(item.get("id")) is None:
        raise ValidationError("Attachment payload must contain id")


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: Any,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _entity_query(entity_type: str, entity_ids: list[int], *, key: str) -> dict[str, Any]:
    return {"entitytype": entity_type, key: entity_ids}


def _verify_entity_attachments(
    *,
    ctx: dict[str, Any],
    entity_type: str,
    entity_ids: list[int],
    expected_items: list[dict[str, Any]],
    query_key: str,
) -> dict[str, Any]:
    path = "/api/fileattachments/attachments-v1"
    query_params = _entity_query(entity_type, entity_ids, key=query_key)
    try:
        payload = request_data(
            ctx=ctx,
            method="GET",
            path=path,
            query_params=query_params,
            expect_json=True,
            expect_json_object=False,
        )
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "query_params": query_params, "error": str(e)}
    actual_items = _attachment_items(payload["body"])
    missing: list[dict[str, Any]] = []
    for expected in expected_items:
        if not any(_attachment_matches(expected, actual) for actual in actual_items):
            missing.append(expected)
    verification = {
        "ok": not missing,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "requested_count": len(expected_items),
        "response_count": len(actual_items),
        "data": payload["body"],
    }
    if missing:
        verification["missing"] = missing
        verification["error"] = "Expected attachment(s) to be present after write verification"
    return verification


def _verify_attachment_absent(
    *,
    ctx: dict[str, Any],
    entity_type: str,
    entity_id: int,
    attachment_id: str,
) -> dict[str, Any]:
    path = "/api/fileattachments/attachments-v1"
    query_params = _entity_query(entity_type, [entity_id], key="entityid")
    try:
        payload = request_data(
            ctx=ctx,
            method="GET",
            path=path,
            query_params=query_params,
            expect_json=True,
            expect_json_object=False,
        )
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "query_params": query_params, "error": str(e)}
    actual_items = _attachment_items(payload["body"])
    absent = all(_extract_attachment_id(item) != attachment_id for item in actual_items)
    verification = {
        "ok": absent,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "target_attachment_id": attachment_id,
        "data": payload["body"],
    }
    if not absent:
        verification["error"] = "Expected attachment to be absent after delete verification"
    return verification


def _attachment_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    expected_entity_id = _string_value(expected.get("entityId"))
    expected_entity_type = _string_value(expected.get("entityType"))
    expected_file_id = _string_value(expected.get("fileId"))
    expected_id = _string_value(expected.get("id"))
    actual_entity_id = _string_value(actual.get("entityId"))
    actual_entity_type = _string_value(actual.get("entityType"))
    actual_file_id = _string_value(actual.get("fileId"))
    actual_id = _string_value(actual.get("id"))
    if expected_entity_id is not None and actual_entity_id != expected_entity_id:
        return False
    if expected_entity_type is not None and actual_entity_type != expected_entity_type:
        return False
    if expected_file_id is not None and actual_file_id != expected_file_id:
        return False
    if expected_id is not None and actual_id != expected_id:
        return False
    if expected.get("includeOnSend") is not None and actual.get("includeOnSend") != expected.get("includeOnSend"):
        return False
    return True


def _verify_response_matches_items(
    *,
    items: list[dict[str, Any]],
    body: Any,
    response_kind: str,
) -> dict[str, Any]:
    actual_items = _attachment_items(body)
    matches: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for item in items:
        match = next((candidate for candidate in actual_items if _attachment_matches(item, candidate)), None)
        if match is None:
            missing.append(item)
        else:
            matches.append(match)
    ok = not missing
    verification = {
        "ok": ok,
        "response_kind": response_kind,
        "requested_count": len(items),
        "response_count": len(actual_items),
        "matched_count": len(matches),
        "data": body,
    }
    if missing:
        verification["missing"] = missing
        verification["error"] = "Expected attachment response to include all requested attachment items"
    return verification


def _emit_read(ctx: dict[str, Any], *, audit_key: str, path: str, payload: dict[str, Any]) -> int:
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        audit_key,
        {
            "ok": True,
            "path": path,
            "http_status": payload["status"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_attachment_get(args: Any, ctx: dict[str, Any]) -> int:
    entity_ids = _normalize_entity_ids(getattr(args, "entity_id", None), field_name="--entity-id")
    entity_type = _validate_entity_type(getattr(args, "entity_type", None), field_name="--entity-type")
    payload = request_data(
        ctx=ctx,
        method="GET",
        path="/api/fileattachments/attachments-v1",
        query_params={"entityid": entity_ids, "entitytype": entity_type},
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(ctx, audit_key="attachment.get", path="/api/fileattachments/attachments-v1", payload=payload)


def cmd_attachment_list(args: Any, ctx: dict[str, Any]) -> int:
    entity_ids = _normalize_entity_ids(getattr(args, "entity_id", None), field_name="--entity-id")
    entity_type = _validate_entity_type(getattr(args, "entity_type", None), field_name="--entity-type")
    payload = request_data(
        ctx=ctx,
        method="GET",
        path="/api/fileattachments/attachments-v1/numberofattachments",
        query_params={"entityids": entity_ids, "entitytype": entity_type},
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(
        ctx,
        audit_key="attachment.list",
        path="/api/fileattachments/attachments-v1/numberofattachments",
        payload=payload,
    )


def cmd_attachment_attach(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, attachments = _load_attachment_list_file(str(getattr(args, "json_file", "") or "").strip())
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for item in attachments:
        entity_type = _string_value(item.get("entityType"))
        entity_id = _string_value(item.get("entityId"))
        if entity_type is None or entity_id is None:
            raise ValidationError("Attachment payload must contain entityId and entityType")
        try:
            entity_id_int = int(entity_id)
        except Exception as e:  # noqa: BLE001
            raise ValidationError("Attachment payload entityId must be an integer") from e
        grouped.setdefault((entity_type, entity_id_int), []).append(item)
    selector = {
        "kind": "attachment",
        "action": "attach",
        "path": "/api/fileattachments/attachments-v1",
        "count": len(attachments),
    }
    plan = _build_plan(
        action="attach",
        selector=selector,
        payload_file=payload_file,
        payload_obj=attachments,
        risk_level="medium",
        risk_reasons=["fortnox-write", "attachment-attach"],
        verification_plan={"type": "read-after-write", "path": "/api/fileattachments/attachments-v1"},
        rollback_notes="No generic rollback. Detach each created attachment explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("attachment.attach.plan", {"plan_out": plan_path, "count": len(attachments)})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="attach", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/fileattachments/attachments-v1",
        json_body=attachments,  # type: ignore[arg-type]
        expect_json=False,
        expect_json_object=False,
    )
    verification_groups: list[dict[str, Any]] = []
    verified = True
    for (entity_type, entity_id), items in sorted(grouped.items()):
        verification = _verify_entity_attachments(
            ctx=ctx,
            entity_type=entity_type,
            entity_ids=[entity_id],
            expected_items=items,
            query_key="entityid",
        )
        verification_groups.append(verification)
        verified = verified and bool(verification.get("ok"))
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "verification": verification_groups,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verified, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("attachment.attach.apply", {"receipt_out": receipt_path, "verified": verified})
    ctx["out"].emit(out)
    return 0 if verified else 1


def cmd_attachment_update(args: Any, ctx: dict[str, Any]) -> int:
    attachment_id = _string_value(getattr(args, "attachment_id", None))
    if attachment_id is None:
        raise ValidationError("--attachment-id is required")
    payload_file, attachment = _load_attachment_object_file(str(getattr(args, "json_file", "") or "").strip())
    body_id = _extract_attachment_id(attachment)
    if body_id is None:
        raise ValidationError("Attachment payload must contain id")
    if body_id != attachment_id:
        raise ValidationError("Attachment payload id must match --attachment-id")
    entity_type = _validate_entity_type(attachment.get("entityType"), field_name="Attachment payload entityType")
    try:
        entity_id = int(attachment.get("entityId"))
    except Exception as e:  # noqa: BLE001
        raise ValidationError("Attachment payload entityId must be an integer") from e
    selector = {
        "kind": "attachment",
        "action": "update",
        "path": f"/api/fileattachments/attachments-v1/{attachment_id}",
        "attachment_id": attachment_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=attachment,
        risk_level="medium",
        risk_reasons=["fortnox-write", "attachment-update"],
        verification_plan={"type": "read-after-write", "path": "/api/fileattachments/attachments-v1"},
        rollback_notes="No generic rollback. Reapply the previous attachment fields explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("attachment.update.plan", {"plan_out": plan_path, "attachment_id": attachment_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="PUT",
        path=f"/api/fileattachments/attachments-v1/{attachment_id}",
        json_body=attachment,
        expect_json=False,
        expect_json_object=False,
    )
    verification = _verify_entity_attachments(
        ctx=ctx,
        entity_type=entity_type,
        entity_ids=[entity_id],
        expected_items=[attachment],
        query_key="entityid",
    )
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("attachment.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_attachment_detach(args: Any, ctx: dict[str, Any]) -> int:
    attachment_id = _string_value(getattr(args, "attachment_id", None))
    if attachment_id is None:
        raise ValidationError("--attachment-id is required")
    selector = {
        "kind": "attachment",
        "action": "detach",
        "path": f"/api/fileattachments/attachments-v1/{attachment_id}",
        "attachment_id": attachment_id,
    }
    plan = _build_plan(
        action="detach",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", "attachment-detach", "irreversible"],
        verification_plan={
            "type": "response-only",
            "note": "Fortnox docs do not expose a documented GET-by-attachment-id follow-up for detached attachments.",
        },
        rollback_notes="No generic rollback. Reattach the file manually if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("attachment.detach.plan", {"plan_out": plan_path, "attachment_id": attachment_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: detaching an attachment requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: detaching an attachment requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="detach", selector=selector, payload_file=None, ctx=ctx)
    payload = request_data(
        ctx=ctx,
        method="DELETE",
        path=f"/api/fileattachments/attachments-v1/{attachment_id}",
        expect_json=False,
        expect_json_object=False,
    )
    verification = {
        "ok": payload["status"] == 204,
        "note": "Fortnox docs do not expose a documented GET-by-attachment-id follow-up for detached attachments.",
    }
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("attachment.detach.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_attachment_validate_included_on_send(args: Any, ctx: dict[str, Any]) -> int:
    _, attachments = _load_attachment_list_file(str(getattr(args, "json_file", "") or "").strip())
    payload = request_data(
        ctx=ctx,
        method="POST",
        path="/api/fileattachments/attachments-v1/validateincludedonsend",
        json_body=attachments,  # type: ignore[arg-type]
        expect_json=False,
        expect_json_object=False,
    )
    out = {
        "ok": 200 <= payload["status"] < 300,
        "path": "/api/fileattachments/attachments-v1/validateincludedonsend",
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "validated_count": len(attachments),
    }
    ctx["audit"].write(
        "attachment.validate_included_on_send",
        {
            "ok": out["ok"],
            "path": out["path"],
            "http_status": payload["status"],
            "validated_count": len(attachments),
        },
    )
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1
