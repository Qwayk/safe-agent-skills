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


def cmd_api_keys_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/api-keys", params=_pagination_params(args))
    ctx["audit"].write("api_keys.list", {"ok": True})
    ctx["out"].emit(
        {"ok": True, "api_keys": _redact_sensitive(res.data), "next_starting_after": res.next_starting_after}
    )
    return 0


def cmd_api_keys_create(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    ack_store = bool(getattr(args, "ack_store_secret_locally", False))

    if apply:
        require_plan_in_on_apply(apply=True, plan_in=plan_in, reason="api-keys create (apply)")
        if not yes:
            raise SafetyError("Refused: api-keys create requires --apply --yes")
        if not ack_store:
            raise SafetyError("Refused: api-keys create requires --ack-store-secret-locally")
    else:
        if plan_in:
            raise ValidationError("--plan-in can only be used with --apply")

    if apply:
        assert plan_in is not None
        plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="api-keys.create")
        _, path, body = request_from_plan(plan_obj, expected_method="POST")
        if path != "/api-keys":
            raise SafetyError("Refused: plan path mismatch for api-keys create")
        plan = plan_obj
    else:
        file_path = str(getattr(args, "file", "") or "").strip()
        if not file_path:
            raise ValidationError("Missing --file")
        body = _load_file_json(file_path)
        path = "/api-keys"
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "api-keys.create", "value": file_path},
            risk_level="high",
            risk_reasons=["creates-api-key", "response-may-include-raw-key"],
            request={"method": "POST", "path": path, "body": body},
            verification_plan={"type": "best-effort", "notes": "List API keys after apply (response key material is stored locally)."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
        )

    plan_out = ctx.get("plan_out")
    plan_path_out = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("api_keys.create.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data

    secret_path, secret_sha256 = write_sensitive_json(
        env_file=str(ctx.get("env_file") or ".env"),
        kind="api-keys.create.response",
        obj=result,
    )

    verify = None
    try:
        verify = client.get("/api-keys", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "api-keys.list", "limit": 20}},
        "result": {
            "api_key_metadata": _redact_sensitive(result),
            "sensitive_output": {"path": secret_path, "sha256": secret_sha256},
            "api_keys_after": _redact_sensitive(verify),
        },
        "backups": [],
        "rollback_plan": None,
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write(
        "api_keys.create.apply",
        {"ok": True, "receipt_out": receipt_path, "sensitive_path": secret_path, "sensitive_sha256": secret_sha256},
    )
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_api_keys_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="api-keys delete")
    if apply and not yes:
        raise SafetyError("Refused: api-keys delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    key_id = str(getattr(args, "id", "") or "").strip() or None
    path = f"/api-keys/{key_id}" if key_id else ""

    if not apply:
        if not key_id:
            raise ValidationError("Missing --id (or provide --plan-in with --apply)")
        plan = build_plan(
            tool=str(ctx.get("tool") or "instantly-api-tool"),
            version=str(ctx.get("tool_version") or ""),
            env_fingerprint=str(ctx["cfg"].base_url),
            command=str(ctx.get("command_str") or ""),
            selector={"kind": "api-keys.delete", "value": key_id},
            risk_level="high",
            risk_reasons=["deletes-api-key"],
            request={"method": "DELETE", "path": path, "body": {}},
            verification_plan={"type": "read-back", "notes": "Best-effort: list API keys after apply."},
            baseline={"env_fingerprint": str(ctx["cfg"].base_url), "id": key_id},
        )
        plan_out = ctx.get("plan_out")
        plan_path_out = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("api_keys.delete.plan", {"ok": True, "plan_out": plan_path_out})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path_out})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="api-keys.delete")
    _, plan_path_val, body = request_from_plan(plan_obj, expected_method="DELETE")
    if key_id and plan_path_val != f"/api-keys/{key_id}":
        raise SafetyError("Refused: plan path mismatch for api-keys delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body).data
    verify = None
    try:
        verify = client.get("/api-keys", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "api-keys.list", "limit": 20}},
        "result": {"operation_result": _redact_sensitive(result), "api_keys_after": _redact_sensitive(verify)},
        "backups": [],
        "rollback_plan": None,
    }

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("api_keys.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0
