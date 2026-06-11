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


def cmd_webhooks_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/webhooks", params=_pagination_params(args))
    out = {"ok": True, "webhooks": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("webhooks.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_webhooks_get(args: Any, ctx: dict) -> int:
    webhook_id = str(getattr(args, "webhook_id", "") or "").strip()
    if not webhook_id:
        raise ValidationError("Missing --webhook-id")
    client = _client(ctx)
    res = client.get(f"/webhooks/{webhook_id}")
    ctx["audit"].write("webhooks.get", {"ok": True})
    ctx["out"].emit({"ok": True, "webhook": res.data})
    return 0


def cmd_webhooks_event_types(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/webhooks/event-types")
    ctx["audit"].write("webhooks.event_types", {"ok": True})
    ctx["out"].emit({"ok": True, "event_types": res.data})
    return 0


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)

def cmd_webhooks_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (webhook JSON)")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "webhooks.create", "value": file_path},
        risk_level="medium",
        risk_reasons=["creates-webhook"],
        request={"method": "POST", "path": "/webhooks", "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: list webhooks after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("webhooks.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post("/webhooks", json_body=body).data
    verify = None
    try:
        verify = client.get("/webhooks", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "webhooks.list", "limit": 20}},
        "result": {"operation_result": result, "webhooks_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("webhooks.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_webhooks_patch(args: Any, ctx: dict) -> int:
    webhook_id = str(getattr(args, "webhook_id", "") or "").strip()
    if not webhook_id:
        raise ValidationError("Missing --webhook-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (webhook patch JSON)")
    body = _load_file_json(file_path)
    path = f"/webhooks/{webhook_id}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "webhooks.patch", "value": webhook_id},
        risk_level="medium",
        risk_reasons=["updates-webhook"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: list webhooks after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "webhook_id": webhook_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("webhooks.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/webhooks", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "webhooks.list", "limit": 20}},
        "result": {"operation_result": result, "webhooks_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("webhooks.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_webhooks_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="webhooks delete")

    webhook_id = str(getattr(args, "webhook_id", "") or "").strip() or None
    if not webhook_id and not apply:
        raise ValidationError("Missing --webhook-id (or provide --plan-in with --apply)")
    if apply and not yes:
        raise SafetyError("Refused: webhooks delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    path = f"/webhooks/{webhook_id}" if webhook_id else ""

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "webhooks.delete", "value": webhook_id or "<from-plan>"},
        risk_level="high",
        risk_reasons=["deletes-webhook"],
        request={"method": "DELETE", "path": path or "/webhooks/<id>", "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort: list webhooks after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "webhook_id": webhook_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("webhooks.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="webhooks.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if webhook_id and plan_path_val != f"/webhooks/{webhook_id}":
        raise SafetyError("Refused: plan path mismatch for webhooks delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/webhooks", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "webhooks.list", "limit": 20}},
        "result": {"operation_result": result, "webhooks_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("webhooks.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_webhooks_test(args: Any, ctx: dict) -> int:
    webhook_id = str(getattr(args, "webhook_id", "") or "").strip()
    if not webhook_id:
        raise ValidationError("Missing --webhook-id")
    path = f"/webhooks/{webhook_id}/test"
    body: dict[str, Any] = {}

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "webhooks.test", "value": webhook_id},
        risk_level="medium",
        risk_reasons=["webhook-test-delivery"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: list webhooks after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "webhook_id": webhook_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("webhooks.test.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/webhooks", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "webhooks.list", "limit": 20}},
        "result": {"operation_result": result, "webhooks_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("webhooks.test.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_webhooks_resume(args: Any, ctx: dict) -> int:
    webhook_id = str(getattr(args, "webhook_id", "") or "").strip()
    if not webhook_id:
        raise ValidationError("Missing --webhook-id")
    path = f"/webhooks/{webhook_id}/resume"
    body: dict[str, Any] = {}

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "webhooks.resume", "value": webhook_id},
        risk_level="medium",
        risk_reasons=["webhook-resume"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: list webhooks after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "webhook_id": webhook_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("webhooks.resume.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/webhooks", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "webhooks.list", "limit": 20}},
        "result": {"operation_result": result, "webhooks_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("webhooks.resume.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0
