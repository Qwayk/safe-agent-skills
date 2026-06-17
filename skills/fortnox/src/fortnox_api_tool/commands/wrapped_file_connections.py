from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_json = api_runtime.request_json


@dataclass(frozen=True)
class WrappedFileConnectionSpec:
    family_slug: str
    item_slug: str
    collection_key: str
    item_key: str
    payload_key: str
    path: str
    list_query_params: tuple[tuple[str, str], ...]
    payload_required_keys: tuple[str, ...]
    singular_label: str
    plural_label: str


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


def _extract_wrapped_payload(body: Any, *, payload_key: str) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    wrapped = body.get(payload_key)
    if isinstance(wrapped, dict):
        return wrapped
    if _string_value(body.get("FileId")):
        return body
    return None


def _extract_file_id(body: Any, *, payload_key: str) -> str | None:
    wrapped = _extract_wrapped_payload(body, payload_key=payload_key)
    if not isinstance(wrapped, dict):
        return None
    return _string_value(wrapped.get("FileId"))


def _extract_collection_items(body: Any, *, collection_key: str, payload_key: str) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    items = body.get(collection_key)
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    wrapped = _extract_wrapped_payload(body, payload_key=payload_key)
    if isinstance(wrapped, dict):
        return [wrapped]
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


def _build_query_params(args: Any, query_map: tuple[tuple[str, str], ...]) -> dict[str, Any] | None:
    query_params: dict[str, Any] = {}
    for attr_name, query_name in query_map:
        value = getattr(args, attr_name, None)
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        query_params[query_name] = value
    return query_params or None


def _load_wrapped_payload_file(
    path_str: str,
    *,
    payload_key: str,
    required_keys: tuple[str, ...],
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    wrapped = obj.get(payload_key)
    if not isinstance(wrapped, dict):
        raise ValidationError(f"JSON file must contain a top-level {payload_key} object")
    for key in required_keys:
        if _string_value(wrapped.get(key)) is None:
            raise ValidationError(f"JSON file must contain {key} inside {payload_key}")
    return path, obj, wrapped


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


def _verify_present(*, ctx: dict[str, Any], spec: WrappedFileConnectionSpec, file_id: str) -> dict[str, Any]:
    path = f"{spec.path}/{file_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "target_file_id": file_id, "error": str(e)}
    present = _extract_file_id(payload["body"], payload_key=spec.payload_key) == file_id
    verification = {
        "ok": present,
        "path": path,
        "http_status": payload["status"],
        "target_file_id": file_id,
        "data": payload["body"],
    }
    if not present:
        verification["error"] = f"Expected {spec.singular_label} to be present after write verification"
    return verification


def _verify_absent(*, ctx: dict[str, Any], spec: WrappedFileConnectionSpec, file_id: str) -> dict[str, Any]:
    path = f"{spec.path}/{file_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        if "HTTP 404" in str(e):
            return {"ok": True, "path": path, "target_file_id": file_id, "expected_http_status": 404}
        return {"ok": False, "path": path, "target_file_id": file_id, "error": str(e)}
    if payload["status"] == 404:
        return {"ok": True, "path": path, "target_file_id": file_id, "expected_http_status": 404}
    absent = _extract_file_id(payload["body"], payload_key=spec.payload_key) != file_id
    verification = {
        "ok": absent,
        "path": path,
        "http_status": payload["status"],
        "target_file_id": file_id,
        "data": payload["body"],
    }
    if not absent:
        verification["error"] = f"Expected {spec.singular_label} to be absent after remove verification"
    return verification


def cmd_list(args: Any, ctx: dict[str, Any], *, spec: WrappedFileConnectionSpec) -> int:
    query_params = _build_query_params(args, spec.list_query_params)
    payload = request_json(ctx=ctx, method="GET", path=spec.path, query_params=query_params, expect_json=True)
    return _emit_read(ctx, audit_key=f"{spec.family_slug}.list", path=spec.path, payload=payload)


def cmd_get(args: Any, ctx: dict[str, Any], *, spec: WrappedFileConnectionSpec) -> int:
    file_id = str(getattr(args, "file_id", "") or "").strip()
    path = f"{spec.path}/{file_id}"
    payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    return _emit_read(ctx, audit_key=f"{spec.family_slug}.get", path=path, payload=payload)


def cmd_create(args: Any, ctx: dict[str, Any], *, spec: WrappedFileConnectionSpec) -> int:
    payload_file, payload_obj, payload_body = _load_wrapped_payload_file(
        str(getattr(args, "json_file", "") or "").strip(),
        payload_key=spec.payload_key,
        required_keys=spec.payload_required_keys,
    )
    selector = {
        "kind": spec.item_slug,
        "action": "create",
        "path": spec.path,
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", f"{spec.family_slug}-create"],
        verification_plan={"type": "read-after-write", "path_template": f"{spec.path}/{{FileId}}"},
        rollback_notes=f"No generic rollback. Recreate the {spec.singular_label} explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"{spec.family_slug}.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path=spec.path,
        json_body=payload_obj,
        expect_json=True,
    )
    file_id = _extract_file_id(payload.get("body"), payload_key=spec.payload_key) or _extract_file_id(
        payload_body,
        payload_key=spec.payload_key,
    )
    if not file_id:
        raise ValidationError(f"Could not determine FileId for {spec.family_slug} create verification")
    verification = _verify_present(ctx=ctx, spec=spec, file_id=file_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_file_id": file_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"{spec.family_slug}.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_remove(args: Any, ctx: dict[str, Any], *, spec: WrappedFileConnectionSpec) -> int:
    file_id = str(getattr(args, "file_id", "") or "").strip()
    selector = {
        "kind": spec.item_slug,
        "action": "remove",
        "path": f"{spec.path}/{file_id}",
        "file_id": file_id,
    }
    plan = _build_plan(
        action="remove",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", f"{spec.family_slug}-remove", "irreversible"],
        verification_plan={"type": "get-absent", "path_template": f"{spec.path}/{{FileId}}"},
        rollback_notes=f"No generic rollback. Recreate the {spec.singular_label} explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"{spec.family_slug}.remove.plan", {"plan_out": plan_path, "file_id": file_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: removing a {spec.singular_label} requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"Refused: removing a {spec.singular_label} requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="remove", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(ctx=ctx, method="DELETE", path=f"{spec.path}/{file_id}", expect_json=False)
    verification = _verify_absent(ctx=ctx, spec=spec, file_id=file_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_file_id": file_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"{spec.family_slug}.remove.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
