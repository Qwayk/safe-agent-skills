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
    label = obj.get("Label")
    if not isinstance(label, dict):
        raise ValidationError("JSON file must contain a top-level Label object")
    return path, obj, label


def _extract_label_id_from_payload(label: dict[str, Any] | None) -> str | None:
    if not isinstance(label, dict):
        return None
    return _string_value(label.get("Id"))


def _extract_label_id_from_response(body: dict[str, Any] | None) -> str | None:
    if not isinstance(body, dict):
        return None
    label = body.get("Label")
    if not isinstance(label, dict):
        return None
    return _extract_label_id_from_payload(label)


def _labels_from_body(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    items = body.get("Labels")
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


def _find_label_by_id(*, ctx: dict[str, Any], label_id: str) -> dict[str, Any] | None:
    payload = request_json(ctx=ctx, method="GET", path="/labels", expect_json=True)
    for item in _labels_from_body(payload["body"]):
        if _extract_label_id_from_payload(item) == label_id:
            return item
    return None


def _verify_present(*, ctx: dict[str, Any], label_id: str) -> dict[str, Any]:
    item = _find_label_by_id(ctx=ctx, label_id=label_id)
    if item is None:
        return {"ok": False, "path": "/labels", "error": f"Expected label id {label_id} in follow-up list scan"}
    return {"ok": True, "path": "/labels", "found_id": label_id, "data": item}


def _verify_absent(*, ctx: dict[str, Any], label_id: str) -> dict[str, Any]:
    item = _find_label_by_id(ctx=ctx, label_id=label_id)
    if item is None:
        return {"ok": True, "path": "/labels", "missing_id": label_id}
    return {
        "ok": False,
        "path": "/labels",
        "found_id": label_id,
        "data": item,
        "error": "Expected label to be absent after delete verification",
    }


def cmd_labels_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/labels"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="labels.list", path=path, payload=payload)


def cmd_labels_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, label = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "label", "action": "create", "path": "/labels"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "label-create"],
        verification_plan={"type": "follow-up-list-scan", "path": "/labels", "match_field": "Id"},
        rollback_notes="No generic rollback. Delete the created label explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("labels.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/labels", json_body=payload_obj, expect_json=True)
    label_id = _extract_label_id_from_response(payload.get("body")) or _extract_label_id_from_payload(label)
    if not label_id:
        raise ValidationError("Could not determine Id for create verification")
    verification = _verify_present(ctx=ctx, label_id=label_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_label_id": label_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("labels.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_labels_update(args: Any, ctx: dict[str, Any]) -> int:
    label_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj, label = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    payload_id = _extract_label_id_from_payload(label)
    if payload_id and payload_id != label_id:
        raise ValidationError("Label.Id in the JSON file must match --id")
    selector = {"kind": "label", "action": "update", "path": f"/labels/{label_id}", "id": label_id}
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "label-update"],
        verification_plan={"type": "follow-up-list-scan", "path": "/labels", "match_field": "Id"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("labels.update.plan", {"plan_out": plan_path, "id": label_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="PUT", path=f"/labels/{label_id}", json_body=payload_obj, expect_json=True)
    verification = _verify_present(ctx=ctx, label_id=label_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_label_id": label_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("labels.update.apply", {"receipt_out": receipt_path, "id": label_id, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_labels_delete(args: Any, ctx: dict[str, Any]) -> int:
    label_id = str(getattr(args, "id", "") or "").strip()
    selector = {"kind": "label", "action": "delete", "path": f"/labels/{label_id}", "id": label_id}
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "label-delete", "irreversible"],
        verification_plan={"type": "follow-up-list-scan", "path": "/labels", "match_field": "Id", "expect_absent": True},
        rollback_notes="No generic rollback. Recreate the label manually if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("labels.delete.plan", {"plan_out": plan_path, "id": label_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")) or not bool(ctx.get("ack_irreversible")):
        ctx["out"].emit(
            {
                "ok": True,
                "refused": True,
                "reasons": [
                    "Refused: delete requires --yes",
                    "Refused: delete requires --ack-irreversible",
                ],
            }
        )
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(ctx=ctx, method="DELETE", path=f"/labels/{label_id}", expect_json=True)
    verification = _verify_absent(ctx=ctx, label_id=label_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_label_id": label_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("labels.delete.apply", {"receipt_out": receipt_path, "id": label_id, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
