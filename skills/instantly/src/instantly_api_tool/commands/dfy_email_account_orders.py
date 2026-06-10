from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plan_apply import load_apply_plan, request_from_plan, require_plan_in_on_apply
from ..plans import build_plan, utc_now
from ..sensitive_store import write_sensitive_json


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
    if bool(getattr(args, "with_passwords", False)):
        params["with_passwords"] = True
    return params


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)


def _is_sensitive_key(key: str) -> bool:
    lk = str(key).lower()
    return ("password" in lk) or ("secret" in lk) or ("token" in lk) or (lk == "key") or lk.endswith("_key")


def _redact_sensitive(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if _is_sensitive_key(str(k)):
                continue
            out[k] = _redact_sensitive(v)
        return out
    if isinstance(obj, list):
        return [_redact_sensitive(x) for x in obj]
    return obj


def cmd_dfy_list_orders(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/dfy-email-account-orders", params=_pagination_params(args))
    ctx["audit"].write("dfy_email_account_orders.list_orders", {"ok": True})
    ctx["out"].emit({"ok": True, "orders": res.data, "next_starting_after": res.next_starting_after})
    return 0


def cmd_dfy_list_accounts(args: Any, ctx: dict) -> int:
    with_passwords = bool(getattr(args, "with_passwords", False))
    ack_store = bool(getattr(args, "ack_store_secret_locally", False))
    if with_passwords and not ack_store:
        raise SafetyError("Refused: dfy list-accounts --with-passwords requires --ack-store-secret-locally")

    client = _client(ctx)
    res = client.get("/dfy-email-account-orders/accounts", params=_pagination_params(args))
    data = res.data

    if with_passwords:
        secret_path, secret_sha256 = write_sensitive_json(
            env_file=str(ctx.get("env_file") or ".env"),
            kind="dfy-email-account-orders.list-accounts.with-passwords",
            obj=data,
        )
        ctx["audit"].write(
            "dfy_email_account_orders.list_accounts.passwords_stored",
            {"ok": True, "sensitive_path": secret_path, "sensitive_sha256": secret_sha256},
        )
        ctx["out"].emit(
            {
                "ok": True,
                "accounts_redacted": _redact_sensitive(data),
                "next_starting_after": res.next_starting_after,
                "sensitive_output": {"path": secret_path, "sha256": secret_sha256},
            }
        )
        return 0

    ctx["audit"].write("dfy_email_account_orders.list_accounts", {"ok": True})
    ctx["out"].emit({"ok": True, "accounts": data, "next_starting_after": res.next_starting_after})
    return 0


def cmd_dfy_create_order(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/dfy-email-account-orders"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "dfy-email-account-orders.create-order", "value": file_path},
        risk_level="high",
        risk_reasons=["creates-dfy-order"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: list orders after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path_out = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("dfy_email_account_orders.create_order.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/dfy-email-account-orders", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "dfy-email-account-orders.list-orders", "limit": 20}},
        "result": {"operation_result": _redact_sensitive(result), "orders_after": _redact_sensitive(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("dfy_email_account_orders.create_order.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_dfy_cancel_accounts(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="dfy cancel-accounts")
    if apply and not yes:
        raise SafetyError("Refused: dfy cancel-accounts requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    path = "/dfy-email-account-orders/accounts/cancel"

    if not apply:
        file_path = str(getattr(args, "file", "") or "").strip()
        if not file_path:
            raise ValidationError("Missing --file")
        body = _load_file_json(file_path)
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "dfy-email-account-orders.cancel-accounts", "value": file_path},
            risk_level="high",
            risk_reasons=["cancels-dfy-accounts"],
            request={"method": "POST", "path": path, "body": body},
            verification_plan={"type": "best-effort", "notes": "Best-effort: list accounts after apply."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
        )
        plan_out = ctx.get("plan_out")
        plan_path_out = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("dfy_email_account_orders.cancel_accounts.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(
        plan_in=plan_in,
        env_fingerprint=str(ctx["cfg"].base_url),
        kind="dfy-email-account-orders.cancel-accounts",
    )
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="POST")
    if plan_path_val != path:
        raise SafetyError("Refused: plan path mismatch for dfy cancel-accounts")

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/dfy-email-account-orders/accounts", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "dfy-email-account-orders.list-accounts", "limit": 20}},
        "result": {"operation_result": _redact_sensitive(result), "accounts_after": _redact_sensitive(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("dfy_email_account_orders.cancel_accounts.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_dfy_check_domains(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/dfy-email-account-orders/domains/check"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "dfy-email-account-orders.check-domains", "value": file_path},
        risk_level="low",
        risk_reasons=["domain-availability-check"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "none", "notes": "Read-only validation request."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path_out = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("dfy_email_account_orders.check_domains.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
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
        "changed": False,
        "verification": {"ok": True, "details": {"type": "none"}},
        "result": {"operation_result": _redact_sensitive(result)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("dfy_email_account_orders.check_domains.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_dfy_similar_domains(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file")
    body = _load_file_json(file_path)
    path = "/dfy-email-account-orders/domains/similar"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "dfy-email-account-orders.similar-domains", "value": file_path},
        risk_level="low",
        risk_reasons=["domain-similarity-check"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "none", "notes": "Read-only validation request."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path_out = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("dfy_email_account_orders.similar_domains.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
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
        "changed": False,
        "verification": {"ok": True, "details": {"type": "none"}},
        "result": {"operation_result": _redact_sensitive(result)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("dfy_email_account_orders.similar_domains.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_dfy_prewarmed_domains(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/dfy-email-account-orders/domains/pre-warmed-up-list")
    ctx["audit"].write("dfy_email_account_orders.prewarmed_domains", {"ok": True})
    ctx["out"].emit({"ok": True, "prewarmed_domains": _redact_sensitive(res.data)})
    return 0

