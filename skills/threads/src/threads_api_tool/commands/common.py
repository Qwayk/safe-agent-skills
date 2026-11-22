from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    refusal_output,
    rollback_contract,
)


def split_csv_arg(raw: str | None) -> list[str]:
    if raw is None:
        return []
    text = str(raw).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def parse_bool_arg(raw: Any, *, name: str) -> bool:
    if isinstance(raw, bool):
        return raw
    if raw is None:
        raise ValidationError(f"Missing --{name}")
    v = str(raw).strip().lower()
    if v in {"true", "1", "yes", "on", "y"}:
        return True
    if v in {"false", "0", "no", "off", "n"}:
        return False
    raise ValidationError(f"--{name} must be true/false")


def build_read_params(
    *,
    args: Any,
    include_fields: bool = True,
    include_pagination: bool = True,
    include_reverse: bool = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if include_fields:
        fields = str(getattr(args, "fields", "") or "").strip()
        if fields:
            params["fields"] = fields

    if include_pagination:
        limit = getattr(args, "limit", None)
        if limit is not None:
            params["limit"] = limit
        before = str(getattr(args, "before", "") or "").strip()
        if before:
            params["before"] = before
        after = str(getattr(args, "after", "") or "").strip()
        if after:
            params["after"] = after
        since = str(getattr(args, "since", "") or "").strip()
        if since:
            params["since"] = since
        until = str(getattr(args, "until", "") or "").strip()
        if until:
            params["until"] = until

    if include_reverse and bool(getattr(args, "reverse", False)):
        params["reverse"] = True

    return params


def build_optional_params(
    *,
    args: Any,
    include_q: bool = False,
    include_metric: bool = False,
    include_search_mode: bool = False,
    include_search_type: bool = False,
    include_media_type: bool = False,
    include_maxwidth: bool = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    if include_q:
        q = str(getattr(args, "q", "") or "").strip()
        if q:
            params["q"] = q

    if include_metric:
        metric = str(getattr(args, "metric", "") or "").strip()
        if metric:
            params["metric"] = metric

    if include_search_mode:
        search_mode = str(getattr(args, "search_mode", "") or "").strip()
        if search_mode:
            params["search_mode"] = search_mode

    if include_search_type:
        search_type = str(getattr(args, "search_type", "") or "").strip()
        if search_type:
            params["search_type"] = search_type

    if include_media_type:
        media_type = str(getattr(args, "media_type", "") or "").strip()
        if media_type:
            params["media_type"] = media_type

    if include_maxwidth:
        raw = getattr(args, "maxwidth", None)
        if raw is not None:
            try:
                params["maxwidth"] = int(raw)
            except Exception:
                raise ValidationError("--maxwidth must be an integer") from None

    return params


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_write_plan(
    *,
    ctx: dict[str, Any],
    command: str,
    selector: dict[str, Any],
    risk_level: str = "medium",
    risk_reasons: list[str] | None = None,
    proposed_changes: list[dict[str, Any]] | None = None,
    preconditions: list[str] | None = None,
    verification: dict[str, Any] | None = None,
    rollback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if proposed_changes is None:
        proposed_changes = []
    if preconditions is None:
        preconditions = ["dry-run reviewed by user"]
    if verification is None:
        verification = before_state_refusal_verification_plan()
    if rollback is None:
        rollback = rollback_contract()

    return {
        "tool": ctx.get("tool") or "threads-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": getattr(ctx["cfg"], "base_url", None),
        "command_id": command,
        "command": str(ctx.get("command_str") or command),
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons or ["write-operation"],
        "preconditions": preconditions,
        "baseline": {
            "env_fingerprint": getattr(ctx["cfg"], "base_url", None),
            "api_version": getattr(ctx["cfg"], "api_version", None),
        },
        "proposed_changes": proposed_changes,
        "before_state": blocked_before_state(
            action=command,
            proposed_changes=proposed_changes,
            local_state={"kind": "token_store", "writes_token_file": True} if command.startswith("auth.") else None,
        ),
        "verification_plan": verification,
        "rollback": rollback,
    }


def _load_plan_for_apply(
    ctx: dict[str, Any],
    *,
    expected_command: str,
    expected_selector: dict[str, Any],
    expected_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    plan_path = str(ctx.get("plan_in") or "").strip()
    if not plan_path:
        return {}

    plan = read_json_file(plan_path)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")

    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    env_fingerprint = str(getattr(ctx["cfg"], "base_url", ""))
    if str(baseline.get("env_fingerprint") or "") and str(baseline.get("env_fingerprint")) != env_fingerprint:
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan.get("command_id") or "") != str(expected_command):
        raise SafetyError("Refused: plan command does not match current write action")
    if plan.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match the current target")
    if expected_changes is not None and (
        baseline.get("env_fingerprint") != env_fingerprint
        or baseline.get("api_version") != ctx["cfg"].api_version
        or plan.get("proposed_changes") != expected_changes
    ):
        raise SafetyError("The request or API settings changed. Save a new plan and get it reviewed.")

    return plan


def run_write_command(
    *,
    ctx: dict[str, Any],
    selector: dict[str, Any],
    command: str,
    proposed_changes: list[dict[str, Any]] | None = None,
    execute: Callable[[], Any],
    requires_yes: bool = False,
    requires_ack: bool = False,
    risk_level: str = "medium",
    requires_reviewed_plan: bool = False,
    verify_result: Callable[[Any], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    has_saved_plan = bool(str(ctx.get("plan_in") or "").strip())
    plan = build_write_plan(
        ctx=ctx,
        command=command,
        selector=selector,
        risk_level=risk_level,
        proposed_changes=proposed_changes or [],
    )
    if requires_reviewed_plan:
        plan["preconditions"].append("Use the matching reviewed plan with --plan-in.")
    if verify_result:
        plan["verification_plan"]["steps"].append("Read the published post using the ID Threads returns.")

    if bool(ctx.get("apply")) is False:
        if has_saved_plan:
            _load_plan_for_apply(ctx, expected_command=command, expected_selector=selector)
        plan_out = str(ctx.get("plan_out")) if ctx.get("plan_out") else None
        if plan_out:
            plan_out = write_json_file(plan_out, plan)
        return {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_out,
            "command": command,
        }

    if requires_yes and not bool(ctx.get("yes")):
        raise SafetyError(f"{command} requires --yes")
    if requires_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"{command} requires --ack-irreversible")

    if not bool(ctx.get("ack_no_snapshot")):
        out = refusal_output(plan=plan)
        out["command"] = command
        return out

    if requires_reviewed_plan and not has_saved_plan:
        raise SafetyError("Use --plan-in with the reviewed plan for this post.")
    if has_saved_plan:
        _load_plan_for_apply(
            ctx,
            expected_command=command,
            expected_selector=selector,
            expected_changes=plan["proposed_changes"] if requires_reviewed_plan else None,
        )

    result = execute()
    if verify_result:
        verification = verify_result(result)
    elif requires_reviewed_plan:
        verification = {"ok": None, "mode": "response-only"}
    else:
        verification = {"ok": True, "mode": "provider-response-or-local-result"}
    changed: bool | None = True
    if requires_reviewed_plan and not (isinstance(result, dict) and result.get("id")):
        changed = None
    receipt = {
        "tool": ctx.get("tool") or "threads-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": getattr(ctx["cfg"], "base_url", None),
        "command_id": command,
        "command": str(ctx.get("command_str") or command),
        "selector": selector,
        "risk_level": risk_level,
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Threads write.",
        },
        "changed": changed,
        "result": result,
        "verification": verification,
        "rollback": plan.get("rollback"),
    }
    receipt_out = str(ctx.get("receipt_out") or "").strip() or None
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    return {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path, "command": command}
