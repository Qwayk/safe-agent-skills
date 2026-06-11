from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
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


def _cmd_oauth_init(*, args: Any, ctx: dict, kind: str, path: str, audit_prefix: str) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": kind, "value": file_path},
        risk_level="medium",
        risk_reasons=["starts-oauth-session"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "best-effort", "notes": "If response includes a session id, check status via oauth session-status."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write(f"{audit_prefix}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": False, "details": {"type": "manual", "notes": "Use oauth session-status if you have a session id."}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write(f"{audit_prefix}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_oauth_google_init(args: Any, ctx: dict) -> int:
    return _cmd_oauth_init(
        args=args,
        ctx=ctx,
        kind="oauth.google-init",
        path="/oauth/google/init",
        audit_prefix="oauth.google_init",
    )


def cmd_oauth_microsoft_init(args: Any, ctx: dict) -> int:
    return _cmd_oauth_init(
        args=args,
        ctx=ctx,
        kind="oauth.microsoft-init",
        path="/oauth/microsoft/init",
        audit_prefix="oauth.microsoft_init",
    )


def cmd_oauth_session_status(args: Any, ctx: dict) -> int:
    session_id = str(getattr(args, "session_id", "") or "").strip()
    if not session_id:
        raise ValidationError("Missing --session-id")
    client = _client(ctx)
    res = client.get(f"/oauth/session/status/{session_id}")
    ctx["audit"].write("oauth.session_status", {"ok": True})
    ctx["out"].emit({"ok": True, "session_status": res.data})
    return 0
