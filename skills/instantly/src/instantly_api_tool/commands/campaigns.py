from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plan_apply import load_apply_plan, request_from_plan, require_plan_in_on_apply
from ..plans import build_plan, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    return params


def _extract_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("id", "campaign_id", "campaignId"):
            v = obj.get(k)
            if v:
                s = str(v).strip()
                if s:
                    return s
    return None


def _load_file_json_obj(file_path: str, *, label: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError(f"{label} JSON file must be a JSON object")
    return dict(body_any)


def cmd_campaigns_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/campaigns", params=_pagination_params(args))
    out = {"ok": True, "campaigns": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("campaigns.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_campaigns_get(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    client = _client(ctx)
    res = client.get(f"/campaigns/{campaign_id}")
    out = {"ok": True, "campaign": res.data}
    ctx["audit"].write("campaigns.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_campaigns_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (campaign JSON)")
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Campaign JSON file must be a JSON object")
    body: dict[str, Any] = dict(body_any)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.create", "value": str(p)},
        risk_level="medium",
        risk_reasons=["creates-campaign"],
        request={"method": "POST", "path": "/campaigns", "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by returned campaign id."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("campaigns.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/campaigns", json_body=body).data
    verify = None
    cid = _extract_id(created)
    if cid:
        try:
            verify = client.get(f"/campaigns/{cid}").data
        except Exception:  # noqa: BLE001
            verify = None
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": cid}},
        "result": {"created": created, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("campaigns.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def _status_change_common(args: Any, ctx: dict, *, op: str) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    if op not in {"activate", "pause"}:
        raise ValidationError("Invalid operation")
    path = f"/campaigns/{campaign_id}/{op}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": f"campaigns.{op}", "value": campaign_id},
        risk_level="medium",
        risk_reasons=[f"campaign-{op}"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "GET campaign by id after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"campaigns.{op}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    changed = client.post(path, json_body={}).data
    verified = client.get(f"/campaigns/{campaign_id}").data

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "campaign-get", "campaign_id": campaign_id}},
        "result": {"operation_result": changed, "verified_campaign": verified},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"campaigns.{op}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_campaigns_activate(args: Any, ctx: dict) -> int:
    return _status_change_common(args, ctx, op="activate")


def cmd_campaigns_pause(args: Any, ctx: dict) -> int:
    return _status_change_common(args, ctx, op="pause")


def cmd_campaigns_patch(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (campaign patch JSON)")
    body = _load_file_json_obj(file_path, label="Campaign patch")
    path = f"/campaigns/{campaign_id}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.patch", "value": campaign_id},
        risk_level="medium",
        risk_reasons=["patches-campaign"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET campaign by id after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    changed = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get(f"/campaigns/{campaign_id}").data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": campaign_id}},
        "result": {"operation_result": changed, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="campaigns delete")
    if apply and not yes:
        raise SafetyError("Refused: campaigns delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    campaign_id = str(getattr(args, "campaign_id", "") or "").strip() or None
    if not campaign_id and not apply:
        raise ValidationError("Missing --campaign-id (or provide --plan-in with --apply)")

    path = f"/campaigns/{campaign_id}" if campaign_id else ""
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.delete", "value": campaign_id or "<from-plan>"},
        risk_level="high",
        risk_reasons=["deletes-campaign"],
        request={"method": "DELETE", "path": path or "/campaigns/<id>", "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort: list campaigns after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        ctx["audit"].write("campaigns.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="campaigns.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if campaign_id and plan_path_val != f"/campaigns/{campaign_id}":
        raise SafetyError("Refused: plan path mismatch for campaigns delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/campaigns", params={"limit": 20}).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan_obj.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaigns.list", "limit": 20}},
        "result": {"operation_result": result, "campaigns_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_sending_status(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    params: dict[str, Any] = {}
    if bool(getattr(args, "with_ai_summary", False)):
        params["with_ai_summary"] = True
    client = _client(ctx)
    res = client.get(f"/campaigns/{campaign_id}/sending-status", params=params or None)
    ctx["audit"].write("campaigns.sending_status", {"ok": True})
    ctx["out"].emit({"ok": True, "sending_status": res.data})
    return 0


def cmd_campaigns_search_by_contact(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    params: dict[str, Any] = {"search": email}
    sort_column = str(getattr(args, "sort_column", "") or "").strip()
    sort_order = str(getattr(args, "sort_order", "") or "").strip()
    if sort_column:
        params["sort_column"] = sort_column
    if sort_order:
        params["sort_order"] = sort_order
    client = _client(ctx)
    res = client.get("/campaigns/search-by-contact", params=params)
    ctx["audit"].write("campaigns.search_by_contact", {"ok": True})
    ctx["out"].emit({"ok": True, "campaigns": res.data})
    return 0


def cmd_campaigns_share(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: campaigns share requires --apply --yes")
    path = f"/campaigns/{campaign_id}/share"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx['cfg'].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.share", "value": campaign_id},
        risk_level="high",
        risk_reasons=["shares-campaign"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort GET campaign by id after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.share.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    verify = None
    try:
        verify = client.get(f"/campaigns/{campaign_id}").data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": campaign_id}},
        "result": {"operation_result": result, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.share.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_create_from_export(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: campaigns create-from-export requires --apply --yes")

    path = f"/campaigns/{campaign_id}/from-export"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx['cfg'].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.create-from-export", "value": campaign_id},
        risk_level="high",
        risk_reasons=["creates-campaign-from-export"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by returned campaign id."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.create_from_export.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    new_id = _extract_id(result)
    verify = None
    if new_id:
        try:
            verify = client.get(f"/campaigns/{new_id}").data
        except Exception:  # noqa: BLE001
            verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": new_id}},
        "result": {"operation_result": result, "new_campaign_id": new_id, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.create_from_export.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_export(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    path = f"/campaigns/{campaign_id}/export"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx['cfg'].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.export", "value": campaign_id},
        risk_level="medium",
        risk_reasons=["exports-campaign"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "response-only", "notes": "Response-only; export payload returned by API."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.export.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.export.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_duplicate(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (duplicate JSON)")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: campaigns duplicate requires --apply --yes")
    body = _load_file_json_obj(file_path, label="Duplicate")
    path = f"/campaigns/{campaign_id}/duplicate"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx['cfg'].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.duplicate", "value": campaign_id},
        risk_level="high",
        risk_reasons=["duplicates-campaign"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by returned campaign id."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.duplicate.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    new_id = _extract_id(result)
    verify = None
    if new_id:
        try:
            verify = client.get(f"/campaigns/{new_id}").data
        except Exception:  # noqa: BLE001
            verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": new_id}},
        "result": {"operation_result": result, "new_campaign_id": new_id, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.duplicate.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_campaigns_count_launched(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/campaigns/count-launched")
    ctx["audit"].write("campaigns.count_launched", {"ok": True})
    ctx["out"].emit({"ok": True, "count": res.data})
    return 0


def cmd_campaigns_add_variables(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (variables JSON)")
    body = _load_file_json_obj(file_path, label="Variables")
    path = f"/campaigns/{campaign_id}/variables"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx['cfg'].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "campaigns.add-variables", "value": campaign_id},
        risk_level="medium",
        risk_reasons=["adds-campaign-variables"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET campaign by id after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("campaigns.add_variables.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get(f"/campaigns/{campaign_id}").data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "campaign-get", "campaign_id": campaign_id}},
        "result": {"operation_result": result, "verified_campaign": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("campaigns.add_variables.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0
