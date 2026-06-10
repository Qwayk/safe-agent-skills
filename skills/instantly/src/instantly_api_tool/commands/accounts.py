from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plans import build_plan, utc_now, validate_plan_env, validate_plan_kind
from ..redaction import sanitize


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

def _require_apply_yes_for_sensitive_read(*, ctx: dict, action: str) -> None:
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {action} is a sensitive read and requires --apply --yes")


def _require_receipt_out_for_sensitive_apply(*, ctx: dict, action: str) -> str:
    receipt_out = ctx.get("receipt_out")
    if not receipt_out:
        raise SafetyError(
            f"Refused: {action} is a sensitive read and requires a receipt file. "
            "Pass --receipt-out or omit --no-artifacts."
        )
    return str(receipt_out)


def _emit_sensitive_read_dry_run(*, ctx: dict, plan: dict[str, Any], plan_path: str | None, action: str) -> None:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "note": f"{action} is a sensitive read. Use --apply --yes to execute; on apply the redacted response is saved to a receipt file only.",
        }
    )


def _emit_sensitive_read_applied(*, ctx: dict, receipt_path: str, action: str) -> None:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "receipt_out": receipt_path,
            "saved": {"receipt_out": receipt_path},
            "note": f"{action} is a sensitive read; response body is saved to the receipt file only.",
        }
    )


def cmd_accounts_list(args: Any, ctx: dict) -> int:
    _require_apply_yes_for_sensitive_read(ctx=ctx, action="accounts list")
    params = _pagination_params(args)
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.list", "value": params or {}},
        risk_level="high",
        risk_reasons=["sensitive-read", "credential-bearing"],
        request={"method": "GET", "path": "/accounts", "params": params},
        verification_plan={"type": "response-only", "notes": "Response is saved to receipt file only."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("accounts.list.plan", {"ok": True, "plan_out": plan_path})
        _emit_sensitive_read_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, action="accounts list")
        return 0

    receipt_out = _require_receipt_out_for_sensitive_apply(ctx=ctx, action="accounts list")
    client = _client(ctx)
    res = client.get("/accounts", params=params)
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": False,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"accounts": sanitize(res.data), "next_starting_after": res.next_starting_after},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = write_json_file(receipt_out, sanitize(receipt))
    ctx["audit"].write("accounts.list.apply", {"ok": True, "receipt_out": receipt_path})
    _emit_sensitive_read_applied(ctx=ctx, receipt_path=receipt_path, action="accounts list")
    return 0


def cmd_accounts_get(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    _require_apply_yes_for_sensitive_read(ctx=ctx, action="accounts get")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.get", "value": email},
        risk_level="high",
        risk_reasons=["sensitive-read", "credential-bearing"],
        request={"method": "GET", "path": f"/accounts/{email}"},
        verification_plan={"type": "response-only", "notes": "Response is saved to receipt file only."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("accounts.get.plan", {"ok": True, "plan_out": plan_path})
        _emit_sensitive_read_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, action="accounts get")
        return 0

    receipt_out = _require_receipt_out_for_sensitive_apply(ctx=ctx, action="accounts get")
    client = _client(ctx)
    res = client.get(f"/accounts/{email}")
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": False,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"account": sanitize(res.data)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = write_json_file(receipt_out, sanitize(receipt))
    ctx["audit"].write("accounts.get.apply", {"ok": True, "receipt_out": receipt_path})
    _emit_sensitive_read_applied(ctx=ctx, receipt_path=receipt_path, action="accounts get")
    return 0


def cmd_accounts_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (account JSON)")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.create", "value": file_path},
        risk_level="medium",
        risk_reasons=["creates-account", "credential-bearing"],
        request={"method": "POST", "path": "/accounts", "body": sanitize(body)},
        verification_plan={"type": "best-effort", "notes": "Best-effort: re-fetch the created account by email."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/accounts", json_body=body).data
    verify = None
    try:
        created_email = str(body.get("email") or "").strip()
        if created_email:
            verify = client.get(f"/accounts/{created_email}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "accounts.get", "email": str(body.get("email") or "")}},
        "result": {"created": sanitize(created), "verified_account": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_patch(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (account patch JSON)")
    body = _load_file_json(file_path)
    path = f"/accounts/{email}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.patch", "value": email},
        risk_level="medium",
        risk_reasons=["updates-account", "credential-bearing"],
        request={"method": "PATCH", "path": path, "body": sanitize(body)},
        verification_plan={"type": "best-effort", "notes": "Best-effort: re-fetch the account after patch."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    changed = client.patch(path, json_body=body).data
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
        "verification": {"ok": verify is not None, "details": {"type": "accounts.get", "email": email}},
        "result": {"operation_result": sanitize(changed), "verified_account": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = ctx.get("plan_in")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")
    if apply:
        if not yes:
            raise SafetyError("Refused: accounts delete requires --apply --yes")
        if not plan_in:
            raise SafetyError("Refused: accounts delete on apply requires --plan-in (plan-file workflow)")

    if plan_in:
        plan_obj_any = read_json_file(plan_in)
        if not isinstance(plan_obj_any, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan_obj: dict[str, Any] = dict(plan_obj_any)
        validate_plan_env(plan_obj, env_fingerprint=str(ctx["cfg"].base_url))
        validate_plan_kind(plan_obj, kind="accounts.delete")

        baseline = plan_obj.get("baseline") or {}
        if not isinstance(baseline, dict):
            raise ValidationError("Plan baseline must be a JSON object")
        email = str(baseline.get("email") or "").strip()
        if not email:
            raise ValidationError("Plan baseline missing email")
    else:
        email = str(getattr(args, "email", "") or "").strip()
        if not email:
            raise ValidationError("Missing --email (or provide --plan-in)")

    path = f"/accounts/{email}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.delete", "value": email},
        risk_level="high",
        risk_reasons=["deletes-account"],
        request={"method": "DELETE", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: try GET account after delete (should fail/404)."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.delete(path, json_body={}).data
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
        "verification": {"ok": verify is None, "details": {"type": "accounts.get", "email": email}},
        "result": {"operation_result": sanitize(result), "account_after": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def _warmup_common(args: Any, ctx: dict, *, op: str) -> int:
    if op not in {"enable", "disable"}:
        raise ValidationError("Invalid operation")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (warmup JSON)")
    body = _load_file_json(file_path)

    apply = bool(ctx.get("apply"))
    if apply and not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: accounts warmup {op} requires --apply --yes (batch write)")

    path = f"/accounts/warmup/{op}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": f"accounts.warmup.{op}", "value": file_path},
        risk_level="high",
        risk_reasons=["batch-account-warmup-toggle"],
        request={"method": "POST", "path": path, "body": sanitize(body)},
        verification_plan={"type": "best-effort", "notes": "Best-effort: list accounts after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"accounts.warmup.{op}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/accounts", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "accounts.list", "limit": 20}},
        "result": {"operation_result": sanitize(result), "accounts_after": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"accounts.warmup.{op}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_warmup_enable(args: Any, ctx: dict) -> int:
    return _warmup_common(args, ctx, op="enable")


def cmd_accounts_warmup_disable(args: Any, ctx: dict) -> int:
    return _warmup_common(args, ctx, op="disable")


def _pause_resume_common(args: Any, ctx: dict, *, op: str) -> int:
    if op not in {"pause", "resume"}:
        raise ValidationError("Invalid operation")
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    path = f"/accounts/{email}/{op}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": f"accounts.{op}", "value": email},
        risk_level="medium",
        risk_reasons=[f"account-{op}"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: re-fetch the account after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"accounts.{op}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    verify = None
    try:
        verify = client.get(f"/accounts/{email}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "accounts.get", "email": email}},
        "result": {"operation_result": sanitize(result), "verified_account": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"accounts.{op}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_pause(args: Any, ctx: dict) -> int:
    return _pause_resume_common(args, ctx, op="pause")


def cmd_accounts_resume(args: Any, ctx: dict) -> int:
    return _pause_resume_common(args, ctx, op="resume")

def cmd_accounts_mark_fixed(args: Any, ctx: dict) -> int:
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        raise ValidationError("Missing --email")
    path = f"/accounts/{email}/mark-fixed"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.mark-fixed", "value": email},
        risk_level="medium",
        risk_reasons=["account-mark-fixed"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: re-fetch the account after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "email": email},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.mark_fixed.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    verify = None
    try:
        verify = client.get(f"/accounts/{email}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "accounts.get", "email": email}},
        "result": {"operation_result": sanitize(result), "verified_account": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.mark_fixed.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_move(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (move accounts JSON)")
    body = _load_file_json(file_path)
    apply = bool(ctx.get("apply"))
    if apply and not bool(ctx.get("yes")):
        raise SafetyError("Refused: accounts move requires --apply --yes (batch)")

    path = "/accounts/move"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.move", "value": file_path},
        risk_level="high",
        risk_reasons=["batch-move-accounts"],
        request={"method": "POST", "path": path, "body": sanitize(body)},
        verification_plan={"type": "response-only", "notes": "Response-only (moving accounts is a sensitive operation)."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.move.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
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
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": sanitize(result)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.move.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_test_vitals(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (vitals JSON)")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.test-vitals", "value": file_path},
        risk_level="medium",
        risk_reasons=["account-vitals-check", "sensitive-read"],
        request={"method": "POST", "path": "/accounts/test/vitals", "body": sanitize(body)},
        verification_plan={"type": "best-effort", "notes": "No separate verification; response is the result."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("accounts.test_vitals.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post("/accounts/test/vitals", json_body=body).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": sanitize(result)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("accounts.test_vitals.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_ctd_status(args: Any, ctx: dict) -> int:
    _ = args
    _require_apply_yes_for_sensitive_read(ctx=ctx, action="accounts ctd-status")
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "accounts.ctd_status", "value": "accounts/ctd/status"},
        risk_level="high",
        risk_reasons=["sensitive-read", "credential-bearing"],
        request={"method": "GET", "path": "/accounts/ctd/status"},
        verification_plan={"type": "response-only", "notes": "Response is saved to receipt file only."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("accounts.ctd_status.plan", {"ok": True, "plan_out": plan_path})
        _emit_sensitive_read_dry_run(ctx=ctx, plan=plan, plan_path=plan_path, action="accounts ctd-status")
        return 0

    receipt_out = _require_receipt_out_for_sensitive_apply(ctx=ctx, action="accounts ctd-status")
    client = _client(ctx)
    res = client.get("/accounts/ctd/status")
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": False,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"ctd_status": sanitize(res.data)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = write_json_file(receipt_out, sanitize(receipt))
    ctx["audit"].write("accounts.ctd_status.apply", {"ok": True, "receipt_out": receipt_path})
    _emit_sensitive_read_applied(ctx=ctx, receipt_path=receipt_path, action="accounts ctd-status")
    return 0
