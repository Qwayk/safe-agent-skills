from __future__ import annotations

import time
from typing import Any

from . import online_programs_programs as _shared
from ..authz import resolve_auth_mode
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "b2b-site-transfer"
BASE_PATH = "/b2b-site-management/v1/transfer-site"


ValidationError = _shared.ValidationError
SafetyError = _shared.SafetyError


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, method: str, path: str, headers: dict[str, str], json_body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
            "apply also requires --ack-irreversible",
        ],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "B2B site transfer plans cannot safely capture cross-account site state before transfer."},
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response-and-follow-up-read", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. A reverse transfer, if allowed by Wix and the account relationship, must be planned separately."},
    }


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _write(*, method_name: str, http_method: str, path: str, body: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], risk_reasons: list[str], verification_notes: str) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": http_method, "path": path, "body": body}
    plan = _plan(method_name=method_name, request=request, selector=selector, ctx=ctx, risk_reasons=risk_reasons, verification_notes=verification_notes)
    if not reviewed_plan_apply_requested(ctx, requires_ack=True, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    loaded_plan = _load_plan(ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": request,
        "response": response,
        "verified": {"type": "provider-response-and-follow-up-read", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def _transfer_body(args: Any) -> dict[str, Any]:
    body = _shared._object_arg(getattr(args, "site_transfer_json", None), field="site-transfer-json")
    if "siteTransfer" not in body:
        body = {"siteTransfer": body}
    site_transfer = body.get("siteTransfer")
    if not isinstance(site_transfer, dict):
        raise ValidationError("--site-transfer-json must include siteTransfer")
    for field in ("siteId", "sourceAccountId"):
        if not isinstance(site_transfer.get(field), str) or not site_transfer[field].strip():
            raise ValidationError(f"--site-transfer-json must include siteTransfer.{field}")
    return body


def cmd_b2b_site_transfer_transfer(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.transfer"
    try:
        body = _transfer_body(args)
        site_transfer = body["siteTransfer"]
        selector = {
            "siteId": site_transfer["siteId"],
            "sourceAccountId": site_transfer["sourceAccountId"],
            "targetAccountHeader": getattr(ctx["cfg"], "account_id", None),
        }
        return _write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector=selector,
            ctx=ctx,
            risk_reasons=["b2b-site-transfer", "moves-site-between-accounts", "strategic-partner-only"],
            verification_notes="Inspect provider response and query the target/source account sites after transfer.",
        )
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)
