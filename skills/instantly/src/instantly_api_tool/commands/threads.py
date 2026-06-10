from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plan_apply import load_apply_plan, request_from_plan, require_plan_in_on_apply
from ..plans import build_plan, sha256_text, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def cmd_threads_mark_as_read(args: Any, ctx: dict) -> int:
    thread_id = str(getattr(args, "thread_id", "") or "").strip()
    if not thread_id:
        raise ValidationError("Missing --thread-id")
    path = f"/emails/threads/{thread_id}/mark-as-read"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "threads.mark-as-read", "value": thread_id},
        risk_level="medium",
        risk_reasons=["marks-thread-read"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort thread read-back after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "thread_id": thread_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("threads.mark_as_read.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    verify = None
    try:
        verify = client.get(f"/emails/threads/{thread_id}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "emails.thread.get", "thread_id": thread_id}},
        "result": {"operation_result": result, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("threads.mark_as_read.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_threads_reply(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack = bool(ctx.get("ack_irreversible"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None

    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="threads reply")
    if apply and (not yes or not ack):
        raise SafetyError("Refused: threads reply requires --apply --yes --ack-irreversible")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    if apply:
        assert plan_in is not None
        plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="threads.reply")
        _, path, body = request_from_plan(plan_obj, expected_method="POST")
        if path != "/emails/reply":
            raise SafetyError("Refused: plan path mismatch for threads reply")
        thread_id = str(body.get("thread_id") or "").strip()
        if not thread_id:
            raise ValidationError("Plan request body missing thread_id")
        plan = plan_obj
    else:
        thread_id = str(getattr(args, "thread_id", "") or "").strip()
        reply_to_uuid = str(getattr(args, "reply_to_uuid", "") or "").strip()
        message = str(getattr(args, "message", "") or "").strip()
        if not thread_id:
            raise ValidationError("Missing --thread-id")
        if not reply_to_uuid:
            raise ValidationError("Missing --reply-to-uuid")
        if not message:
            raise ValidationError("Missing --message")
        body = {"thread_id": thread_id, "reply_to_uuid": reply_to_uuid, "message": message}
        subject = str(getattr(args, "subject", "") or "").strip()
        if subject:
            body["subject"] = subject
        eaccount = str(getattr(args, "eaccount", "") or "").strip()
        if eaccount:
            body["eaccount"] = eaccount

        extra_json = str(getattr(args, "extra_json", "") or "").strip()
        if extra_json:
            extra_any = read_json_file(extra_json)
            if not isinstance(extra_any, dict):
                raise ValidationError("--extra-json must be a JSON object")
            for k, v in extra_any.items():
                if k not in body:
                    body[k] = v

        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "threads.reply", "value": thread_id},
            risk_level="irreversible",
            risk_reasons=["sends-email-reply"],
            request={"method": "POST", "path": "/emails/reply", "body": body},
            verification_plan={"type": "best-effort", "notes": "Best-effort thread read-back after apply."},
            baseline={
                "env_fingerprint": str(ctx["cfg"].base_url),
                "thread_id": thread_id,
                "reply_to_uuid": reply_to_uuid,
                "message_sha256": sha256_text(str(body.get("message") or "")),
            },
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("threads.reply.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post("/emails/reply", json_body=body).data
    verify = None
    try:
        verify = client.get(f"/emails/threads/{thread_id}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "emails.thread.get", "thread_id": thread_id}},
        "result": {"operation_result": result, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("threads.reply.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0
