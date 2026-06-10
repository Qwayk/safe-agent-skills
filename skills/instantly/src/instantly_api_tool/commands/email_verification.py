from __future__ import annotations

from typing import Any

from ..arg_parsing import quote_path_segment
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import write_json_file
from ..plans import build_plan, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def cmd_email_verification_status(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    client = _client(ctx)
    res = client.get(f"/email-verification/{quote_path_segment(email, field='email')}")
    out = {"ok": True, "verification_status": res.data}
    ctx["audit"].write("email_verification.status", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_email_verification_create(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")

    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: email-verification create requires --apply --yes")

    body = {"email": email}
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "email_verification.create", "value": email},
        risk_level="medium",
        risk_reasons=["email-verification-trigger"],
        request={"method": "POST", "path": "/email-verification", "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: fetch status for the same email after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("email_verification.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/email-verification", json_body=body).data
    status = None
    try:
        status = client.get(f"/email-verification/{quote_path_segment(email, field='email')}").data
    except Exception:  # noqa: BLE001
        status = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": status is not None, "details": {"type": "email-verification.status", "email": email}},
        "result": {"created": created, "status_after": status},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("email_verification.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0

