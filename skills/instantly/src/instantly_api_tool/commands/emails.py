from __future__ import annotations

import json
from pathlib import Path
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


def _is_http_404(err: Exception) -> bool:
    s = str(err or "")
    return "HTTP 404" in s


def cmd_emails_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/emails", params=_pagination_params(args))
    out = {"ok": True, "emails": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("emails.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_emails_get(args: Any, ctx: dict) -> int:
    email_id = str(getattr(args, "email_id", "") or "").strip()
    if not email_id:
        raise ValidationError("Missing --email-id")
    client = _client(ctx)
    res = client.get(f"/emails/{email_id}")
    out = {"ok": True, "email": res.data}
    ctx["audit"].write("emails.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_emails_unread_count(args: object, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/emails/unread/count")
    out = {"ok": True, "unread_count": res.data}
    ctx["audit"].write("emails.unread_count", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_emails_forward(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack = bool(ctx.get("ack_irreversible"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None

    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="emails forward")
    if apply and (not yes or not ack):
        raise SafetyError("Refused: emails forward requires --apply --yes --ack-irreversible")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    if apply:
        assert plan_in is not None
        plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="emails.forward")
        _, path, body = request_from_plan(plan_obj, expected_method="POST")
        if path != "/emails/forward":
            raise SafetyError("Refused: plan path mismatch for emails forward")
        if not isinstance(body, dict):
            raise ValidationError("Plan request body must be a JSON object")
        plan = plan_obj
    else:
        file_path = str(getattr(args, "file", "") or "").strip()
        if not file_path:
            raise ValidationError("Missing --file (forward email JSON)")
        body = _load_file_json(file_path)
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "emails.forward", "value": sha256_text(json.dumps(body, sort_keys=True, ensure_ascii=False))},
            risk_level="irreversible",
            risk_reasons=["forwards-email"],
            request={"method": "POST", "path": "/emails/forward", "body": body},
            verification_plan={
                "type": "best-effort",
                "notes": "Best-effort: attempt GET /emails/{id} if the request body contains an email id.",
            },
            baseline={"env_fingerprint": str(ctx["cfg"].base_url), "body_sha256": sha256_text(str(body))},
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("emails.forward.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post("/emails/forward", json_body=body).data

    verify = None
    verify_id = None
    for k in ("email_id", "id"):
        v = body.get(k)
        if isinstance(v, str) and v.strip():
            verify_id = v.strip()
            try:
                verify = client.get(f"/emails/{verify_id}").data
            except Exception:  # noqa: BLE001
                verify = None
            break

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {
            "ok": verify is not None,
            "details": {"type": "emails.get", "email_id": verify_id, "notes": "Only when email_id/id is present in request body."},
        },
        "result": {"operation_result": result, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("emails.forward.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_emails_patch(args: Any, ctx: dict) -> int:
    email_id = str(getattr(args, "email_id", "") or "").strip()
    if not email_id:
        raise ValidationError("Missing --email-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (email patch JSON)")
    body = _load_file_json(file_path)

    path = f"/emails/{email_id}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "emails.patch", "value": email_id},
        risk_level="medium",
        risk_reasons=["patch-email"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "GET /emails/{id} after apply."},
        baseline={
            "env_fingerprint": str(ctx["cfg"].base_url),
            "email_id": email_id,
            "body_sha256": sha256_text(json.dumps(body, sort_keys=True, ensure_ascii=False)),
        },
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("emails.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
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
        "verification": {"ok": verify is not None, "details": {"type": "emails.get", "email_id": email_id}},
        "result": {"operation_result": result, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("emails.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_emails_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="emails delete")

    email_id = str(getattr(args, "email_id", "") or "").strip() or None
    if not email_id and not apply:
        raise ValidationError("Missing --email-id (or provide --plan-in with --apply)")
    if apply and not yes:
        raise SafetyError("Refused: emails delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    path = f"/emails/{email_id}" if email_id else ""
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "emails.delete", "value": email_id or "<from-plan>"},
        risk_level="high",
        risk_reasons=["delete-email"],
        request={"method": "DELETE", "path": path or "/emails/<id>", "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort GET /emails/{id} expecting 404 after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email_id": email_id},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("emails.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="emails.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if email_id and plan_path_val != f"/emails/{email_id}":
        raise SafetyError("Refused: plan path mismatch for emails delete")
    if body not in (None, {}, []):
        raise ValidationError("Plan request body must be empty for emails delete")

    client = _client(ctx)
    result = client.delete(plan_path_val, json_body={}).data

    verify = None
    verify_ok = False
    try:
        _ = client.get(plan_path_val).data
        verify_ok = False
        verify = {"notes": "Unexpectedly still retrievable after delete."}
    except Exception as e:  # noqa: BLE001
        verify_ok = _is_http_404(e)
        verify = {"notes": "GET after delete raised an error (expected 404).", "is_404": verify_ok}

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan_obj.get("selector"),
        "changed": True,
        "verification": {"ok": verify_ok, "details": {"type": "emails.get_after_delete", "path": plan_path_val, "expected": "HTTP 404"}},
        "result": {"operation_result": result, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("emails.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0
