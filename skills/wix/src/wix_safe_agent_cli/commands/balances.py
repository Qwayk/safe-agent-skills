from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _normalize_query_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="query-json")
    if not isinstance(payload, dict):
        raise ValidationError("--query-json must be a JSON object")
    return payload


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _has_pricing_plans_app(payload: dict[str, Any]) -> bool:
    site = payload.get("site")
    if not isinstance(site, dict):
        return False
    installed = site.get("installedWixApps")
    if not isinstance(installed, list):
        return False
    installed_values = {str(value).strip().lower() for value in installed if isinstance(value, str)}
    return "pricingplans" in installed_values


def _resolve_balances_auth_and_preflight(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="balances",
    )
    instance_payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/apps/v1/instance",
        headers=auth["headers"],
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    if not _has_pricing_plans_app(instance_payload):
        raise ValidationError("Required installed Wix app missing for balances. Expected pricingPlans.")
    return auth["headers"], auth["mode"]


def _extract_balance(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    balance = payload.get("balance")
    if isinstance(balance, dict):
        return balance
    if isinstance(payload.get("id"), str):
        return payload
    raise ValidationError(f"{operation} response did not include a balance object")


def _extract_balances(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    for key in ("balances", "results"):
        raw_balances = payload.get(key)
        if isinstance(raw_balances, list):
            balances = [balance for balance in raw_balances if isinstance(balance, dict)]
            if balances or raw_balances == []:
                return balances
    raise ValidationError(f"{operation} response did not include a balances list")


def _get_balance(*, pool_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/benefit-programs/v1/balances/{pool_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_balance(payload, operation="balances.get")


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-balance-write"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                state_capture_notes
                or (
                    "Captured current provider state before planning."
                    if has_before_state
                    else "No useful before-state snapshot exists for this transaction-based write."
                )
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                rollback_notes
                or (
                    "No general automatic rollback. Use the official revert-change method for a specific prior transaction when possible."
                )
            ),
        },
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _should_apply(ctx: dict[str, Any], *, command_label: str) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=command_label)


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any], label: str) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError(f"Refused: {label} state changed since plan was created")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No deterministic before-state snapshot was available for this transaction-based write."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Use the official revert-change method only for a specific transaction when applicable.",
        },
    }


def _find_pool_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("poolId", "pool_id"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            found = _find_pool_id(value)
            if found:
                return found
    if isinstance(payload, list):
        for item in payload:
            found = _find_pool_id(item)
            if found:
                return found
    return None


def _emit_validation_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _emit_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": method,
        }
    )
    return 0


def cmd_balances_get(args, ctx) -> int:
    try:
        pool_id = _coerce_non_empty_text(getattr(args, "pool_id", None), field="pool-id")
        headers, auth_mode = _resolve_balances_auth_and_preflight(ctx=ctx)
        balance = _get_balance(pool_id=pool_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "balances.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/benefit-programs/v1/balances/{pool_id}"},
                "response": {"balance": balance},
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="balances.get", exc=exc)


def cmd_balances_list(args, ctx) -> int:
    _ = args
    try:
        headers, auth_mode = _resolve_balances_auth_and_preflight(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/balances",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        balances = _extract_balances(payload, operation="balances.list")
        ctx["out"].emit(
            {
                "ok": True,
                "method": "balances.list",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/benefit-programs/v1/balances"},
                "response": {"balances": balances},
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="balances.list", exc=exc)


def cmd_balances_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_balances_auth_and_preflight(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/balances/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        balances = _extract_balances(payload, operation="balances.query")
        ctx["out"].emit(
            {
                "ok": True,
                "method": "balances.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/benefit-programs/v1/balances/query", "body": body},
                "response": {"balances": balances},
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="balances.query", exc=exc)


def cmd_balances_change(args, ctx) -> int:
    try:
        pool_id = _coerce_non_empty_text(getattr(args, "pool_id", None), field="pool-id")
        body = _coerce_json_object(getattr(args, "change_json", None), field="change-json")
        apply_requested = _should_apply(ctx, command_label="balances.change")
        headers, auth_mode = _resolve_balances_auth_and_preflight(ctx=ctx)
        before_balance = _get_balance(pool_id=pool_id, ctx=ctx, headers=headers)
        selector = {"poolId": pool_id}
        request = {
            "method": "POST",
            "path": f"/benefit-programs/v1/balances/{pool_id}/change",
            "body": body,
        }
        plan = _build_plan(
            method="balances.change",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state={"balance": before_balance},
            proposed_changes=[
                {
                    "summary": "Change available credits for one pool balance.",
                    "pool_id": pool_id,
                }
            ],
            verification_plan={
                "strategy": "readback",
                "command": f"wix-safe-agent-cli balances get --pool-id {pool_id}",
            },
        )
        plan_path = _plan_out_if_needed(ctx, plan=plan)

        if not apply_requested:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "balances.change",
                    "auth_mode": auth_mode,
                    "request": request,
                    "plan": plan,
                    "plan_path": plan_path,
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=ctx.get("plan_in"),
            expected_method="balances.change",
            expected_selector=selector,
            ctx=ctx,
        )
        current_before = {"balance": _get_balance(pool_id=pool_id, ctx=ctx, headers=headers)}
        _assert_no_state_drift(plan=loaded_plan, current_state=current_before, label="balance")

        response_payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/benefit-programs/v1/balances/{pool_id}/change",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_balance = _get_balance(pool_id=pool_id, ctx=ctx, headers=headers)
        verification = {
            "ok": True,
            "strategy": "provider-response-plus-readback",
            "before_balance": before_balance,
            "after_balance": after_balance,
        }
        receipt = _build_receipt(
            method="balances.change",
            selector=selector,
            request=request,
            response=response_payload,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        receipt_path = _receipt_out_if_needed(ctx, receipt=receipt)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "balances.change",
                "auth_mode": auth_mode,
                "request": request,
                "response": response_payload,
                "verification": verification,
                "receipt": receipt,
                "receipt_path": receipt_path,
            }
        )
        return 0
    except SafetyError as exc:
        return _emit_refusal(ctx, method="balances.change", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="balances.change", exc=exc)


def cmd_balances_revert_change(args, ctx) -> int:
    try:
        transaction_id = _coerce_non_empty_text(getattr(args, "transaction_id", None), field="transaction-id")
        apply_requested = _should_apply(ctx, command_label="balances.revert-change")
        headers, auth_mode = _resolve_balances_auth_and_preflight(ctx=ctx)
        selector = {"transactionId": transaction_id}
        request = {
            "method": "POST",
            "path": f"/benefit-programs/v1/balances/changes/{transaction_id}/revert",
            "body": {},
        }
        plan = _build_plan(
            method="balances.revert-change",
            request=request,
            selector=selector,
            ctx=ctx,
            before_state={},
            proposed_changes=[
                {
                    "summary": "Revert one prior balance change transaction.",
                    "transaction_id": transaction_id,
                }
            ],
            verification_plan={
                "strategy": "provider-response-or-readback",
                "notes": "If the response exposes a poolId, reread that balance. Otherwise verify provider acceptance only.",
            },
            state_capture_notes=(
                "No deterministic before-state snapshot exists in this boundary because the write is keyed by transactionId, not by a direct balance read target."
            ),
        )
        plan_path = _plan_out_if_needed(ctx, plan=plan)

        if not apply_requested:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "balances.revert-change",
                    "auth_mode": auth_mode,
                    "request": request,
                    "plan": plan,
                    "plan_path": plan_path,
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=ctx.get("plan_in"),
            expected_method="balances.revert-change",
            expected_selector=selector,
            ctx=ctx,
        )
        response_payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/benefit-programs/v1/balances/changes/{transaction_id}/revert",
            headers=headers,
            params=None,
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        pool_id = _find_pool_id(response_payload)
        verification: dict[str, Any]
        if pool_id:
            after_balance = _get_balance(pool_id=pool_id, ctx=ctx, headers=headers)
            verification = {
                "ok": True,
                "strategy": "provider-response-plus-readback",
                "pool_id": pool_id,
                "after_balance": after_balance,
            }
        else:
            verification = {
                "ok": True,
                "strategy": "provider-response-only",
                "notes": "No poolId was exposed for a stronger readback in this boundary.",
            }
        receipt = _build_receipt(
            method="balances.revert-change",
            selector=selector,
            request=request,
            response=response_payload,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        receipt_path = _receipt_out_if_needed(ctx, receipt=receipt)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "balances.revert-change",
                "auth_mode": auth_mode,
                "request": request,
                "response": response_payload,
                "verification": verification,
                "receipt": receipt,
                "receipt_path": receipt_path,
            }
        )
        return 0
    except SafetyError as exc:
        return _emit_refusal(ctx, method="balances.revert-change", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="balances.revert-change", exc=exc)
