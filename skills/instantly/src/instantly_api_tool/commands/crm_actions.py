from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import write_json_file
from ..plan_apply import load_apply_plan, request_from_plan, require_plan_in_on_apply
from ..plans import build_plan, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def cmd_crm_actions_list_phone_numbers(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/crm-actions/phone-numbers")
    ctx["audit"].write("crm_actions.list_phone_numbers", {"ok": True})
    ctx["out"].emit({"ok": True, "phone_numbers": res.data})
    return 0


def cmd_crm_actions_delete_phone_number(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="crm-actions delete-phone-number")
    if apply and not yes:
        raise SafetyError("Refused: crm-actions delete-phone-number requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    phone_id = str(getattr(args, "id", "") or "").strip() or None
    path = f"/crm-actions/phone-numbers/{phone_id}" if phone_id else ""

    if not apply:
        if not phone_id:
            raise ValidationError("Missing --id (or provide --plan-in with --apply)")
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "crm-actions.delete-phone-number", "value": phone_id},
            risk_level="high",
            risk_reasons=["deletes-crm-phone-number"],
            request={"method": "DELETE", "path": path, "body": {}},
            verification_plan={"type": "best-effort", "notes": "Best-effort: list phone numbers after apply."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url), "id": phone_id},
        )
        plan_out = ctx.get("plan_out")
        plan_path_out = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("crm_actions.delete_phone_number.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(
        plan_in=plan_in,
        env_fingerprint=str(ctx["cfg"].base_url),
        kind="crm-actions.delete-phone-number",
    )
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if phone_id and plan_path_val != f"/crm-actions/phone-numbers/{phone_id}":
        raise SafetyError("Refused: plan path mismatch for crm-actions delete-phone-number")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/crm-actions/phone-numbers").data
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
        "verification": {"ok": verify is not None, "details": {"type": "crm-actions.list-phone-numbers"}},
        "result": {"operation_result": result, "phone_numbers_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("crm_actions.delete_phone_number.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0

