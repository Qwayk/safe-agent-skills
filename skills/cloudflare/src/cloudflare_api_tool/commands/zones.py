from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..json_files import read_json_file
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    sha256_of_file,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)
from ..zone_settings_allowlist import ALLOWED_ZONE_SETTING_PATHS


def cmd_zones_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    params: dict[str, object] = {}
    name = str(getattr(args, "name", "") or "").strip()
    status = str(getattr(args, "status", "") or "").strip()
    account_id = str(getattr(args, "account_id", "") or "").strip()
    page = int(getattr(args, "page", 1) or 1)
    per_page = int(getattr(args, "per_page", 50) or 50)

    if name:
        params["name"] = name
    if status:
        params["status"] = status
    if account_id:
        params["account.id"] = account_id
    params["page"] = page
    params["per_page"] = per_page

    res = ctx["cf"].get_json("/zones", params=params)
    items = res.result or []
    out = {
        "ok": True,
        "command": "zones.list",
        "page": page,
        "per_page": per_page,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["audit"].write("zones.list", {"count": out.get("count")})
    ctx["out"].emit(out)
    return 0


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _base_plan(ctx: dict, *, selector: dict[str, Any], risk_level: str, risk_reasons: list[str]) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": str(risk_level),
        "risk_reasons": list(risk_reasons),
        "preconditions": [
            "API token has least-privilege permissions needed for this action.",
            "Review the plan output before applying.",
        ],
        "proposed_changes": [],
        "verification_plan": [],
        "notes": [],
    }


def _base_receipt(ctx: dict, *, selector: dict[str, Any], changed: bool) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if cfg and base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed),
        "verification": {"ok": False, "details": {}},
        "diff_applied": [],
        "notes": [],
    }


def _emit_plan(ctx: dict, *, command: str, plan: dict, extra: dict[str, Any] | None = None) -> int:
    _ = write_plan_if_requested(ctx, plan)
    ctx["audit"].write("plan", {"command": command, "selector": plan.get("selector"), "proposed_changes": plan.get("proposed_changes")})
    out = {"ok": True, "dry_run": True, "command": command, "plan": plan}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def _emit_receipt(ctx: dict, *, command: str, receipt: dict, extra: dict[str, Any] | None = None) -> int:
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write(
        "receipt",
        {
            "command": command,
            "selector": receipt.get("selector"),
            "changed": bool(receipt.get("changed")),
            "verification_ok": bool((receipt.get("verification") or {}).get("ok")),
        },
    )
    out = {"ok": True, "dry_run": False, "command": command, "changed": bool(receipt.get("changed")), "receipt": receipt}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def _emit_refused(ctx: dict, *, command: str, reasons: list[str], extra: dict[str, Any] | None = None) -> int:
    out = {"ok": True, "refused": True, "command": command, "reasons": list(reasons)}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def _require_zone_id(args) -> str:
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return zone_id


def _require_setting_path(args) -> str:
    raw = str(getattr(args, "setting_path", "") or "")
    sp = raw.strip()
    if not sp:
        raise ValidationError("Missing --setting-path")
    if sp not in ALLOWED_ZONE_SETTING_PATHS:
        raise ValidationError(
            "Unknown/unsupported zone setting path (refusing). "
            "This command only allows allowlisted setting paths derived from the tool's local OpenAPI snapshot extracts."
        )
    return sp


def cmd_zones_resolve(args, ctx) -> int:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    name = str(getattr(args, "name", "") or "").strip()
    if not name:
        raise ValidationError("Missing --name")
    account_id = str(getattr(args, "account_id", "") or "").strip()

    params: dict[str, object] = {"name": name, "match": "all", "per_page": 50}
    if account_id:
        params["account.id"] = account_id

    res = ctx["cf"].get_json("/zones", params=params)
    items = res.result or []
    if not isinstance(items, list):
        raise ValidationError("Unexpected response shape for zones resolve")

    if len(items) == 0:
        out = {"ok": False, "command": "zones.resolve", "error_type": "NotFound", "error": f"Zone not found: {name}"}
        ctx["out"].emit(out)
        return 1
    if len(items) > 1:
        shortlist = [
            {"id": z.get("id"), "name": z.get("name"), "account": (z.get("account") or {}).get("id")}
            for z in items[:5]
            if isinstance(z, dict)
        ]
        out = {
            "ok": False,
            "command": "zones.resolve",
            "error_type": "Ambiguous",
            "error": f"Multiple zones matched: {name}",
            "matches": shortlist,
            "match_count": len(items),
        }
        ctx["out"].emit(out)
        return 1

    zone = items[0]
    if not isinstance(zone, dict):
        raise ValidationError("Unexpected response shape for zones resolve")
    out = {"ok": True, "command": "zones.resolve", "zone": {"id": zone.get("id"), "name": zone.get("name")}}
    ctx["out"].emit(out)
    return 0


def cmd_zones_settings_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = _require_zone_id(args)
    res = ctx["cf"].get_json(f"/zones/{zone_id}/settings")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zones.settings.list",
            "zone_id": zone_id,
            "result": res.result,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zones_settings_patch(args, ctx) -> int:
    _require_token(ctx)
    zone_id = _require_zone_id(args)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body_obj = read_json_file(body_json_file)
    body_sha256 = sha256_of_file(Path(body_json_file))

    selector = {"zone_id": zone_id, "path": "/zones/{zone_id}/settings", "body_json_sha256": body_sha256}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Zone settings changes can affect production behavior and caching."],
    )
    plan["proposed_changes"] = [
        {
            "resource": "zone_settings",
            "action": "patch",
            "zone_id": zone_id,
            "path": f"/zones/{zone_id}/settings",
            "body_json_sha256": body_sha256,
            "body_json": body_obj,
        }
    ]
    plan["verification_plan"] = ["GET /zones/{zone_id}/settings and confirm the expected settings are reflected in the response."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="zones.settings.patch", plan=plan)

    if not bool(ctx.get("yes")):
        return _emit_refused(ctx, command="zones.settings.patch", reasons=["Cloudflare API writes require --yes."])

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "zones_settings_patch", "zone_id": zone_id})
    patch_res = ctx["cf"].patch_json(f"/zones/{zone_id}/settings", json_body=body_obj).result
    verified = ctx["cf"].get_json(f"/zones/{zone_id}/settings").result
    ok = verified is not None

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {"resource": "zone_settings", "action": "patched", "zone_id": zone_id, "path": f"/zones/{zone_id}/settings", "body_json_sha256": body_sha256}
    ]
    receipt["verification"] = {"ok": bool(ok), "method": "read_back_get", "details": {"path": f"/zones/{zone_id}/settings", "result": verified}}
    receipt["notes"] = ["PATCH result is included separately for convenience; verification uses the read-back GET result."]
    return _emit_receipt(ctx, command="zones.settings.patch", receipt=receipt, extra={"patch_result": patch_res})


def cmd_zones_settings_setting_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = _require_zone_id(args)
    setting_path = _require_setting_path(args)
    res = ctx["cf"].get_json(f"/zones/{zone_id}/settings/{setting_path}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zones.settings.setting_get",
            "zone_id": zone_id,
            "setting_path": setting_path,
            "result": res.result,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zones_settings_setting_patch(args, ctx) -> int:
    _require_token(ctx)
    zone_id = _require_zone_id(args)
    setting_path = _require_setting_path(args)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body_obj = read_json_file(body_json_file)
    body_sha256 = sha256_of_file(Path(body_json_file))

    selector = {
        "zone_id": zone_id,
        "setting_path": setting_path,
        "path": "/zones/{zone_id}/settings/{setting_path}",
        "body_json_sha256": body_sha256,
    }
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Changing individual zone settings can affect production behavior and caching."],
    )
    plan["proposed_changes"] = [
        {
            "resource": "zone_setting",
            "action": "patch",
            "zone_id": zone_id,
            "setting_path": setting_path,
            "path": f"/zones/{zone_id}/settings/{setting_path}",
            "body_json_sha256": body_sha256,
            "body_json": body_obj,
        }
    ]
    plan["verification_plan"] = [f"GET /zones/{zone_id}/settings/{setting_path} and confirm the expected value is reflected."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="zones.settings.setting_patch", plan=plan)

    if not bool(ctx.get("yes")):
        return _emit_refused(ctx, command="zones.settings.setting_patch", reasons=["Cloudflare API writes require --yes."])

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "zones_setting_patch", "zone_id": zone_id, "setting_path": setting_path})
    patch_res = ctx["cf"].patch_json(f"/zones/{zone_id}/settings/{setting_path}", json_body=body_obj).result
    verified = ctx["cf"].get_json(f"/zones/{zone_id}/settings/{setting_path}").result
    ok = verified is not None

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {
            "resource": "zone_setting",
            "action": "patched",
            "zone_id": zone_id,
            "setting_path": setting_path,
            "path": f"/zones/{zone_id}/settings/{setting_path}",
            "body_json_sha256": body_sha256,
        }
    ]
    receipt["verification"] = {
        "ok": bool(ok),
        "method": "read_back_get",
        "details": {"path": f"/zones/{zone_id}/settings/{setting_path}", "result": verified},
    }
    receipt["notes"] = ["PATCH result is included separately for convenience; verification uses the read-back GET result."]
    return _emit_receipt(ctx, command="zones.settings.setting_patch", receipt=receipt, extra={"patch_result": patch_res})
