from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_json = api_runtime.request_json


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


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    asset_type = obj.get("Type")
    if not isinstance(asset_type, dict):
        raise ValidationError("JSON file must contain a top-level Type object")
    return path, obj, asset_type


def _extract_type_id(asset_type: dict[str, Any] | None) -> str | None:
    if not isinstance(asset_type, dict):
        return None
    return _string_value(asset_type.get("Id"))


def _extract_type_number(asset_type: dict[str, Any] | None) -> str | None:
    if not isinstance(asset_type, dict):
        return None
    return _string_value(asset_type.get("Number"))


def _extract_type_from_body(body: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    asset_type = body.get("Type")
    if isinstance(asset_type, dict):
        return asset_type
    return None


def _types_from_body(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    items = body.get("Types")
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


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


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
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


def _verify_present(*, ctx: dict[str, Any], type_id: str) -> dict[str, Any]:
    path = f"/assets/types/{type_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _verify_absent(*, ctx: dict[str, Any], type_id: str) -> dict[str, Any]:
    path = f"/assets/types/{type_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        if "HTTP 404" in str(e):
            return {"ok": True, "path": path, "expected_http_status": 404}
        return {"ok": False, "path": path, "error": str(e)}
    if payload["status"] == 404:
        return {"ok": True, "path": path, "expected_http_status": 404}
    return {
        "ok": False,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
        "error": "Expected asset type to be absent after delete verification",
    }


def _find_type_id_by_number(*, ctx: dict[str, Any], number: str) -> str | None:
    payload = request_json(ctx=ctx, method="GET", path="/assets/types", expect_json=True)
    for item in _types_from_body(payload["body"]):
        if _extract_type_number(item) == number:
            return _extract_type_id(item)
    return None


def cmd_asset_types_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/assets/types"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="asset_types.list", path=path, payload=payload)


def cmd_asset_types_get(args: Any, ctx: dict[str, Any]) -> int:
    type_id = str(getattr(args, "id", "") or "").strip()
    path = f"/assets/types/{type_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="asset_types.get", path=path, payload=payload)


def cmd_asset_types_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, asset_type = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "asset-type", "action": "create", "path": "/assets/types"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "asset-type-create"],
        verification_plan={"type": "read-after-write", "path_template": "/assets/types/{id}"},
        rollback_notes="No generic rollback. Delete the asset type explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("asset_types.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/assets/types", json_body=payload_obj, expect_json=True)
    response_type = _extract_type_from_body(payload["body"])
    type_id = _extract_type_id(response_type) or _extract_type_id(asset_type)
    if not type_id:
        number = _extract_type_number(response_type) or _extract_type_number(asset_type)
        if number:
            type_id = _find_type_id_by_number(ctx=ctx, number=number)
    if not type_id:
        raise ValidationError("Could not determine asset type id for create verification")
    verification = _verify_present(ctx=ctx, type_id=type_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": type_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("asset_types.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_asset_types_update(args: Any, ctx: dict[str, Any]) -> int:
    type_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj, asset_type = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    payload_id = _extract_type_id(asset_type)
    if payload_id and payload_id != type_id:
        raise ValidationError("Type.Id in the JSON file must match --id")
    selector = {"kind": "asset-type", "action": "update", "path": f"/assets/types/{type_id}", "id": type_id}
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "asset-type-update"],
        verification_plan={"type": "read-after-write", "path": f"/assets/types/{type_id}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("asset_types.update.plan", {"plan_out": plan_path, "id": type_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/assets/types/{type_id}",
        json_body=payload_obj,
        expect_json=True,
    )
    verification = _verify_present(ctx=ctx, type_id=type_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": type_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("asset_types.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_asset_types_delete(args: Any, ctx: dict[str, Any]) -> int:
    type_id = str(getattr(args, "id", "") or "").strip()
    selector = {"kind": "asset-type", "action": "delete", "path": f"/assets/types/{type_id}", "id": type_id}
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", "asset-type-delete", "irreversible"],
        verification_plan={"type": "absence-check", "path": f"/assets/types/{type_id}", "expect_http_status": 404},
        rollback_notes="No generic rollback. Recreate the asset type explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("asset_types.delete.plan", {"plan_out": plan_path, "id": type_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: deleting an asset type requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: deleting an asset type requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(ctx=ctx, method="DELETE", path=f"/assets/types/{type_id}", expect_json=False)
    verification = _verify_absent(ctx=ctx, type_id=type_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": type_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("asset_types.delete.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
