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


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)


def cmd_dnc_list(args: Any, ctx: dict) -> int:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    client = _client(ctx)
    res = client.get("/block-lists-entries", params=params)
    out = {"ok": True, "entries": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("dnc.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_dnc_get(args: Any, ctx: dict) -> int:
    entry_id = str(getattr(args, "entry_id", "") or "").strip()
    if not entry_id:
        raise ValidationError("Missing --entry-id")
    client = _client(ctx)
    res = client.get(f"/block-lists-entries/{entry_id}")
    ctx["audit"].write("dnc.get", {"ok": True})
    ctx["out"].emit({"ok": True, "entry": res.data})
    return 0


def cmd_dnc_create(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: do-not-contact create requires --apply --yes")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "do-not-contact.create", "value": email},
        risk_level="high",
        risk_reasons=["dnc-create"],
        request={"method": "POST", "path": "/block-lists-entries", "body": {"email": email}},
        verification_plan={"type": "read-back", "notes": "Best-effort list after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("dnc.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post("/block-lists-entries", json_body={"email": email}).data
    verify = None
    try:
        verify = client.get("/block-lists-entries", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "block-lists-entries.list", "limit": 20}},
        "result": {"operation_result": result, "entries_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("dnc.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_dnc_patch(args: Any, ctx: dict) -> int:
    entry_id = str(getattr(args, "entry_id", "") or "").strip()
    if not entry_id:
        raise ValidationError("Missing --entry-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (do-not-contact patch JSON)")
    body = _load_file_json(file_path)
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: do-not-contact patch requires --apply --yes")

    path = f"/block-lists-entries/{entry_id}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "do-not-contact.patch", "value": entry_id},
        risk_level="high",
        risk_reasons=["dnc-patch"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: list after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "entry_id": entry_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("dnc.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/block-lists-entries", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "block-lists-entries.list", "limit": 20}},
        "result": {"operation_result": result, "entries_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("dnc.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_dnc_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="do-not-contact delete")

    entry_id = str(getattr(args, "entry_id", "") or "").strip() or None
    if not entry_id and not apply:
        raise ValidationError("Missing --entry-id (or provide --plan-in with --apply)")
    if apply and not yes:
        raise SafetyError("Refused: do-not-contact delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    path = f"/block-lists-entries/{entry_id}" if entry_id else ""

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "do-not-contact.delete", "value": entry_id or "<from-plan>"},
        risk_level="high",
        risk_reasons=["dnc-delete"],
        request={"method": "DELETE", "path": path or "/block-lists-entries/<id>", "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort list after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "entry_id": entry_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("dnc.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="do-not-contact.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if entry_id and plan_path_val != f"/block-lists-entries/{entry_id}":
        raise SafetyError("Refused: plan path mismatch for do-not-contact delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/block-lists-entries", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "block-lists-entries.list", "limit": 20}},
        "result": {"operation_result": result, "entries_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("dnc.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0
