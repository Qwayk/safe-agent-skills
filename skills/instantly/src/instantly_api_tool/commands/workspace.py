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


def cmd_workspace_get_current(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/workspaces/current")
    ctx["audit"].write("workspace.get_current", {"ok": True})
    ctx["out"].emit({"ok": True, "workspace": res.data})
    return 0


def cmd_workspace_patch_current(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="workspace patch-current")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    if plan_in:
        plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="workspace.patch-current")
        _, path, body = request_from_plan(plan_obj, expected_method="PATCH")
        if path != "/workspaces/current":
            raise SafetyError("Refused: plan path mismatch for workspace patch-current")
        plan = plan_obj
    else:
        file_path = str(getattr(args, "file", "") or "").strip()
        if not file_path:
            raise ValidationError("Missing --file")
        body = _load_file_json(file_path)
        path = "/workspaces/current"
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "workspace.patch-current", "value": "workspaces/current"},
            risk_level="high",
            risk_reasons=["updates-workspace"],
            request={"method": "PATCH", "path": path, "body": body},
            verification_plan={"type": "read-back", "notes": "Read-back GET /workspaces/current after apply."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace.patch_current.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/workspaces/current").data
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
        "verification": {"ok": verify is not None, "details": {"type": "workspaces.current.get"}},
        "result": {"operation_result": result, "workspace_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace.patch_current.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_workspace_create(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/workspaces/create"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "workspace.create", "value": file_path},
        risk_level="high",
        risk_reasons=["creates-workspace"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Read-back GET /workspaces/current after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/workspaces/current").data
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
        "verification": {"ok": verify is not None, "details": {"type": "workspaces.current.get"}},
        "result": {"operation_result": result, "workspace_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_workspace_change_owner(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="workspace change-owner")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    if plan_in:
        plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="workspace.change-owner")
        _, path, body = request_from_plan(plan_obj, expected_method="POST")
        if path != "/workspaces/current/change-owner":
            raise SafetyError("Refused: plan path mismatch for workspace change-owner")
        plan = plan_obj
    else:
        file_path = str(getattr(args, "file", "") or "").strip()
        if not file_path:
            raise ValidationError("Missing --file")
        body = _load_file_json(file_path)
        path = "/workspaces/current/change-owner"
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "workspace.change-owner", "value": "workspaces/current/change-owner"},
            risk_level="high",
            risk_reasons=["changes-workspace-owner"],
            request={"method": "POST", "path": path, "body": body},
            verification_plan={"type": "read-back", "notes": "Read-back GET /workspaces/current after apply."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace.change_owner.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/workspaces/current").data
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
        "verification": {"ok": verify is not None, "details": {"type": "workspaces.current.get"}},
        "result": {"operation_result": result, "workspace_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace.change_owner.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_workspace_whitelabel_get(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/workspaces/current/whitelabel-domain")
    ctx["audit"].write("workspace.whitelabel.get", {"ok": True})
    ctx["out"].emit({"ok": True, "whitelabel_domain": res.data})
    return 0


def cmd_workspace_whitelabel_set(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/workspaces/current/whitelabel-domain"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "workspace.whitelabel-domain.set", "value": file_path},
        risk_level="medium",
        risk_reasons=["updates-whitelabel-domain"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Read-back GET /workspaces/current/whitelabel-domain after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace.whitelabel.set.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
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
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "workspaces.whitelabel-domain.get"}},
        "result": {"operation_result": result, "whitelabel_domain_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace.whitelabel.set.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_workspace_whitelabel_delete(args: Any, ctx: dict) -> int:
    _ = args
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="workspace whitelabel-domain delete")
    if apply and not yes:
        raise SafetyError("Refused: workspace whitelabel-domain delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    path = "/workspaces/current/whitelabel-domain"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "workspace.whitelabel-domain.delete", "value": "workspaces/current/whitelabel-domain"},
        risk_level="high",
        risk_reasons=["deletes-whitelabel-domain"],
        request={"method": "DELETE", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "Read-back GET /workspaces/current/whitelabel-domain after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("workspace.whitelabel.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="workspace.whitelabel-domain.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if plan_path_val != path:
        raise SafetyError("Refused: plan path mismatch for whitelabel-domain delete")

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
        "verification": {"ok": verify is not None, "details": {"type": "workspaces.whitelabel-domain.get"}},
        "result": {"operation_result": result, "whitelabel_domain_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path2 = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("workspace.whitelabel.delete.apply", {"ok": True, "receipt_out": receipt_path2})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path2})
    return 0
