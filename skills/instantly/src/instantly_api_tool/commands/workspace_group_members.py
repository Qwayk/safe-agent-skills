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


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)


def cmd_workspace_group_members_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/workspace-group-members", params=_pagination_params(args))
    ctx["audit"].write("workspace_group_members.list", {"ok": True})
    ctx["out"].emit({"ok": True, "workspace_group_members": res.data, "next_starting_after": res.next_starting_after})
    return 0


def cmd_workspace_group_members_admin(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/workspace-group-members/admin")
    ctx["audit"].write("workspace_group_members.admin", {"ok": True})
    ctx["out"].emit({"ok": True, "admin_group_memberships": res.data})
    return 0


def cmd_workspace_group_members_get(args: Any, ctx: dict) -> int:
    member_id = str(getattr(args, "id", "") or "").strip()
    if not member_id:
        raise ValidationError("Missing --id")
    client = _client(ctx)
    res = client.get(f"/workspace-group-members/{member_id}")
    ctx["audit"].write("workspace_group_members.get", {"ok": True})
    ctx["out"].emit({"ok": True, "workspace_group_member": res.data})
    return 0


def cmd_workspace_group_members_create(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/workspace-group-members"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "workspace-group-members.create", "value": file_path},
        risk_level="high",
        risk_reasons=["creates-workspace-group-member"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort: GET /workspace-group-members/{id} using returned id."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace_group_members.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        mid = str((result or {}).get("id") or "").strip() if isinstance(result, dict) else ""
        verify = client.get(f"/workspace-group-members/{mid}").data if mid else None
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
        "verification": {"ok": verify is not None, "details": {"type": "workspace-group-members.get", "id": (result or {}).get("id") if isinstance(result, dict) else None}},
        "result": {"operation_result": result, "workspace_group_member_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace_group_members.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_workspace_group_members_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="workspace-group-members delete")
    if apply and not yes:
        raise SafetyError("Refused: workspace-group-members delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    member_id = str(getattr(args, "id", "") or "").strip() or None
    path = f"/workspace-group-members/{member_id}" if member_id else ""

    if not apply:
        if not member_id:
            raise ValidationError("Missing --id (or provide --plan-in with --apply)")
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "workspace-group-members.delete", "value": member_id},
            risk_level="high",
            risk_reasons=["deletes-workspace-group-member"],
            request={"method": "DELETE", "path": path, "body": {}},
            verification_plan={"type": "best-effort", "notes": "Best-effort: GET /workspace-group-members/{id} after delete."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url), "id": member_id},
        )
        plan_out = ctx.get("plan_out")
        plan_path_out = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("workspace_group_members.delete.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="workspace-group-members.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if member_id and plan_path_val != f"/workspace-group-members/{member_id}":
        raise SafetyError("Refused: plan path mismatch for workspace-group-members delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get(path).data
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
        "verification": {"ok": verify is not None, "details": {"type": "workspace-group-members.get", "id": path.rsplit('/', 1)[-1]}},
        "result": {"operation_result": result, "workspace_group_member_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace_group_members.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0
