from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..write_safety import enforce_write_apply_contract

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


def _load_asset_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    asset = obj.get("Asset")
    if not isinstance(asset, dict):
        raise ValidationError("JSON file must contain a top-level Asset object")
    return path, obj, asset


def _load_raw_payload_file(path_str: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    return path, obj


def _extract_asset_id(asset: dict[str, Any] | None) -> str | None:
    if not isinstance(asset, dict):
        return None
    return _string_value(asset.get("Id"))


def _extract_asset_number(asset: dict[str, Any] | None) -> str | None:
    if not isinstance(asset, dict):
        return None
    return _string_value(asset.get("Number"))


def _extract_asset_from_body(body: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    asset = body.get("Asset")
    if isinstance(asset, dict):
        return asset
    asset = body.get("Assets")
    if isinstance(asset, dict):
        return asset
    return None


def _assets_from_body(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    items = body.get("Assets")
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    if isinstance(items, dict):
        return [items]
    asset = body.get("Asset")
    if isinstance(asset, dict):
        return [asset]
    return []


def _extract_depreciation_rows(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    rows = body.get("AssetsDepreciation")
    if isinstance(rows, list):
        return [item for item in rows if isinstance(item, dict)]
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


def _verify_present(*, ctx: dict[str, Any], asset_id: str) -> dict[str, Any]:
    path = f"/assets/{asset_id}"
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


def _verify_absent(*, ctx: dict[str, Any], asset_id: str) -> dict[str, Any]:
    path = f"/assets/{asset_id}"
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
        "error": "Expected asset to be absent after delete verification",
    }


def _find_asset_id_by_number(*, ctx: dict[str, Any], number: str) -> str | None:
    payload = request_json(ctx=ctx, method="GET", path="/assets", expect_json=True)
    for item in _assets_from_body(payload["body"]):
        if _extract_asset_number(item) == number:
            return _extract_asset_id(item)
    return None


def _asset_changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_asset = _extract_asset_from_body(before.get("data"))
    after_asset = _extract_asset_from_body(after.get("data"))
    if not isinstance(after_asset, dict):
        return False
    if not isinstance(before_asset, dict):
        return True
    return before_asset != after_asset


def _run_asset_state_action(
    *,
    args: Any,
    ctx: dict[str, Any],
    action: str,
    endpoint: str,
    payload_loader: str,
    audit_plan_key: str,
    audit_apply_key: str,
    risk_reasons: list[str],
    require_ack: bool = False,
) -> int:
    asset_id = str(getattr(args, "id", "") or "").strip()
    if payload_loader == "asset":
        payload_file, payload_obj, asset = _load_asset_payload_file(str(getattr(args, "json_file", "") or "").strip())
        payload_id = _extract_asset_id(asset)
        if payload_id and payload_id != asset_id:
            raise ValidationError("Asset.Id in the JSON file must match --id")
    else:
        payload_file, payload_obj = _load_raw_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "asset", "action": action, "path": f"/assets/{endpoint}/{asset_id}", "id": asset_id}
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=risk_reasons,
        verification_plan={"type": "read-after-write", "path": f"/assets/{asset_id}"},
        rollback_notes="No generic rollback. Use the documented opposite Fortnox flow when available if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(audit_plan_key, {"plan_out": plan_path, "id": asset_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {action} on an asset requires --apply --yes")
    if require_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"Refused: {action} on an asset requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    enforce_write_apply_contract(ctx=ctx, method="PUT", path=f"/assets/{endpoint}/{asset_id}")
    before = _verify_present(ctx=ctx, asset_id=asset_id)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/assets/{endpoint}/{asset_id}",
        json_body=payload_obj,
        expect_json=True,
    )
    after = _verify_present(ctx=ctx, asset_id=asset_id)
    changed = _asset_changed(before, after)
    verification_ok = bool(after.get("ok")) and changed
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": asset_id,
        "verification_before": before,
        "verification": after,
        "verification_asset_changed": changed,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verification_ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(audit_apply_key, {"receipt_out": receipt_path, "verified": verification_ok})
    ctx["out"].emit(out)
    return 0 if verification_ok else 1


def cmd_assets_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/assets"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="assets.list", path=path, payload=payload)


def cmd_assets_get(args: Any, ctx: dict[str, Any]) -> int:
    asset_id = str(getattr(args, "id", "") or "").strip()
    path = f"/assets/{asset_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="assets.get", path=path, payload=payload)


def cmd_assets_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, asset = _load_asset_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "asset", "action": "create", "path": "/assets"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "asset-create"],
        verification_plan={"type": "read-after-write", "path_template": "/assets/{id}"},
        rollback_notes="No generic rollback. Delete or update the asset explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("assets.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/assets", json_body=payload_obj, expect_json=True)
    response_asset = _extract_asset_from_body(payload["body"])
    asset_id = _extract_asset_id(response_asset) or _extract_asset_id(asset)
    if not asset_id:
        number = _extract_asset_number(response_asset) or _extract_asset_number(asset)
        if number:
            asset_id = _find_asset_id_by_number(ctx=ctx, number=number)
    if not asset_id:
        raise ValidationError("Could not determine asset id for create verification")
    verification = _verify_present(ctx=ctx, asset_id=asset_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": asset_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("assets.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_assets_update(args: Any, ctx: dict[str, Any]) -> int:
    asset_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj, asset = _load_asset_payload_file(str(getattr(args, "json_file", "") or "").strip())
    payload_id = _extract_asset_id(asset)
    if payload_id and payload_id != asset_id:
        raise ValidationError("Asset.Id in the JSON file must match --id")
    selector = {"kind": "asset", "action": "update", "path": f"/assets/{asset_id}", "id": asset_id}
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "asset-update"],
        verification_plan={"type": "read-after-write", "path": f"/assets/{asset_id}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("assets.update.plan", {"plan_out": plan_path, "id": asset_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="PUT", path=f"/assets/{asset_id}", json_body=payload_obj, expect_json=True)
    verification = _verify_present(ctx=ctx, asset_id=asset_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": asset_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("assets.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_assets_delete(args: Any, ctx: dict[str, Any]) -> int:
    asset_id = str(getattr(args, "id", "") or "").strip()
    selector = {"kind": "asset", "action": "delete", "path": f"/assets/{asset_id}", "id": asset_id}
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", "asset-delete", "irreversible"],
        verification_plan={"type": "absence-check", "path": f"/assets/{asset_id}", "expect_http_status": 404},
        rollback_notes="No generic rollback. Recreate the asset explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("assets.delete.plan", {"plan_out": plan_path, "id": asset_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: deleting an asset requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: deleting an asset requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(ctx=ctx, method="DELETE", path=f"/assets/{asset_id}", expect_json=False)
    verification = _verify_absent(ctx=ctx, asset_id=asset_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": asset_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("assets.delete.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_assets_depreciation_list(args: Any, ctx: dict[str, Any]) -> int:
    to_date = str(getattr(args, "to_date", "") or "").strip()
    path = f"/assets/depreciations/{to_date}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="assets.assets_depreciation_list", path=path, payload=payload)


def cmd_assets_change_manual_ob(args: Any, ctx: dict[str, Any]) -> int:
    return _run_asset_state_action(
        args=args,
        ctx=ctx,
        action="change-manual-ob-value-of-an-asset",
        endpoint="changeob",
        payload_loader="raw",
        audit_plan_key="assets.changeob.plan",
        audit_apply_key="assets.changeob.apply",
        risk_reasons=["fortnox-write", "asset-change-manual-ob", "status-change"],
    )


def cmd_assets_depreciate(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, _asset = _load_asset_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "asset", "action": "perform-a-depreciation-of-an-asset", "path": "/assets/depreciate"}
    plan = _build_plan(
        action="perform-a-depreciation-of-an-asset",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="high",
        risk_reasons=["fortnox-write", "asset-depreciate", "status-change"],
        verification_plan={"type": "response-check", "path": "/assets/depreciate"},
        rollback_notes="No generic rollback. Use the documented Fortnox accounting correction flow if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("assets.depreciate.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: perform-a-depreciation-of-an-asset requires --apply --yes")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="perform-a-depreciation-of-an-asset", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/assets/depreciate", json_body=payload_obj, expect_json=True)
    depreciation_rows = _extract_depreciation_rows(payload["body"])
    verification_ok = len(depreciation_rows) > 0
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "verification_response_rows": len(depreciation_rows),
        "verification": {"ok": verification_ok, "rows": depreciation_rows},
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": verification_ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("assets.depreciate.apply", {"receipt_out": receipt_path, "verified": verification_ok})
    ctx["out"].emit(out)
    return 0 if verification_ok else 1


def cmd_assets_scrap(args: Any, ctx: dict[str, Any]) -> int:
    return _run_asset_state_action(
        args=args,
        ctx=ctx,
        action="scrap-an-asset",
        endpoint="scrap",
        payload_loader="asset",
        audit_plan_key="assets.scrap.plan",
        audit_apply_key="assets.scrap.apply",
        risk_reasons=["fortnox-write", "asset-scrap", "irreversible", "status-change"],
        require_ack=True,
    )


def cmd_assets_sell(args: Any, ctx: dict[str, Any]) -> int:
    return _run_asset_state_action(
        args=args,
        ctx=ctx,
        action="sell-an-asset",
        endpoint="sell",
        payload_loader="asset",
        audit_plan_key="assets.sell.plan",
        audit_apply_key="assets.sell.apply",
        risk_reasons=["fortnox-write", "asset-sell", "irreversible", "status-change"],
        require_ack=True,
    )


def cmd_assets_write_down(args: Any, ctx: dict[str, Any]) -> int:
    return _run_asset_state_action(
        args=args,
        ctx=ctx,
        action="write-down-an-asset",
        endpoint="writedown",
        payload_loader="asset",
        audit_plan_key="assets.writedown.plan",
        audit_apply_key="assets.writedown.apply",
        risk_reasons=["fortnox-write", "asset-write-down", "status-change"],
    )


def cmd_assets_write_up(args: Any, ctx: dict[str, Any]) -> int:
    return _run_asset_state_action(
        args=args,
        ctx=ctx,
        action="write-up-an-asset",
        endpoint="writeup",
        payload_loader="asset",
        audit_plan_key="assets.writeup.plan",
        audit_apply_key="assets.writeup.apply",
        risk_reasons=["fortnox-write", "asset-write-up", "status-change"],
    )
