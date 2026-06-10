from __future__ import annotations

import argparse
import base64
import re
import time
from dataclasses import dataclass
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..operation_catalog import ActionSpec, actions as catalog_actions
from ..paypal_auth import AccessTokenResult, resolve_access_token

_TOOL_NAME = "qwayk-paypal-safe-agent-cli"
_USER_AGENT = f"{_TOOL_NAME}/safe-apis"
_PATH_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")
_BEFORE_STATE_REFUSAL_REASON = (
    "Refused: missing explicit no-snapshot approval for a PayPal write with no reliable generic before-state snapshot in this runtime. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


@dataclass(frozen=True)
class ParsedInput:
    spec: ActionSpec
    path_values: dict[str, str]
    query: dict[str, Any]
    body: Any | None


def _safe_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "snapshots": [],
        "backups": [],
        "rollback_plan": None,
        "verification_mode": "best-effort",
        "restore_note": (
            "No automatic rollback, snapshots, backups, or generated rollback plan are provided. "
            "Recovery, if any, requires a separate explicit command."
        ),
    }


def _before_state_contract(*, spec: ActionSpec) -> dict[str, Any]:
    if not spec.write:
        return {
            "required": False,
            "supported": False,
            "status": "not-required",
            "notes": "Read-only commands do not need before-state capture.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "notes": (
            "This PayPal command has no reliable generic before-state snapshot. "
            "Apply may continue only after explicit no-snapshot approval."
        ),
    }


def _verification_plan(*, spec: ActionSpec) -> Any:
    if spec.write:
        return {
            "type": "best_effort_after_apply",
            "expected_outcome": "provider-response-recorded",
            "notes": "Record the PayPal response and explicit no-snapshot approval in the receipt.",
        }
    return {
        "type": "http-response",
        "notes": "Read-only command returns the PayPal response.",
    }


def _path_names(path: str) -> tuple[str, ...]:
    return tuple(_PATH_RE.findall(path))


def _add_action_parser(parser: argparse.ArgumentParser, spec: ActionSpec) -> None:
    for name in _path_names(spec.path):
        parser.add_argument(f"--{name.replace('_', '-')}", required=True, help=f"Path arg: {name}")

    for arg_name, arg_opts in spec.query_args:
        parser.add_argument(f"--{arg_name.replace('_', '-')}", **arg_opts)

    if spec.requires_body_file:
        parser.add_argument("--body-file", required=True, help="JSON body file")

    parser.set_defaults(
        func=cmd_paypal_api,
        paypal_family=spec.family,
        paypal_action=spec.action,
        paypal_spec=spec,
        write_capable=spec.write,
    )


def register_paypal_commands(
    parent: argparse._SubParsersAction,
    *,
    parser_class: type[argparse.ArgumentParser],
) -> None:
    by_family = actions()
    for family in sorted(by_family):
        family_parser = parent.add_parser(family, help=f"{family} family")
        action_parser = family_parser.add_subparsers(dest="paypal_action", required=True, parser_class=parser_class)

        for action in sorted(by_family[family]):
            spec = by_family[family][action]
            p = action_parser.add_parser(action, help=f"{spec.method} {spec.path}")
            _add_action_parser(p, spec)


def _collect_path_values(*, spec: ActionSpec, args: argparse.Namespace) -> dict[str, str]:
    values: dict[str, str] = {}
    for name in _path_names(spec.path):
        arg = getattr(args, name.replace("-", "_"), None)
        if arg is None or not str(arg).strip():
            raise ValidationError(f"Missing required path arg --{name.replace('_', '-')}")
        values[name] = str(arg).strip()
    return values


def _collect_query(*, spec: ActionSpec, args: argparse.Namespace) -> dict[str, str | int | bool]:
    values: dict[str, str | int | bool] = {}
    for arg_name, _ in spec.query_args:
        key = arg_name.replace("-", "_")
        value = getattr(args, key, None)
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                values[arg_name] = True
            continue
        if isinstance(value, str) and not str(value).strip():
            continue
        values[arg_name] = value
    return values


def _load_body(*, spec: ActionSpec, args: argparse.Namespace) -> Any | None:
    if not spec.requires_body_file:
        return None
    body_path = getattr(args, "body_file", None)
    if not body_path:
        raise ValidationError("Missing --body-file")
    body = read_json_file(str(body_path))
    return body


def _request_id_for(*, spec: ActionSpec, run_id: str | None) -> str:
    raw = f"{_TOOL_NAME}:{spec.family}:{spec.action}:{run_id or _safe_now()}"
    token = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")
    return token[:108]


def _build_headers(*, cfg, token_result: AccessTokenResult, spec: ActionSpec, run_id: str | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Language": cfg.accept_language or "en_US",
        "User-Agent": _USER_AGENT,
        "Authorization": f"{token_result.token_type} {token_result.access_token}",
    }
    if cfg.partner_attribution_id:
        headers["PayPal-Partner-Attribution-Id"] = cfg.partner_attribution_id
    if cfg.auth_assertion:
        headers["PayPal-Auth-Assertion"] = cfg.auth_assertion
    if spec.write:
        headers["PayPal-Request-Id"] = _request_id_for(spec=spec, run_id=run_id)
        headers["Prefer"] = "return=representation"
    return headers


def _assert_write_gates(*, spec: ActionSpec, args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    _ = args
    if spec.require_apply and not bool(ctx.get("apply")):
        raise SafetyError("Refused: write commands require --apply")
    if spec.require_yes and not bool(ctx.get("yes")):
        raise SafetyError("Refused: this write command requires --apply --yes")
    if spec.require_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: this write command requires --ack-irreversible")
    if spec.require_plan_in:
        plan_in = ctx.get("plan_in")
        if not isinstance(plan_in, str) or not plan_in.strip():
            raise SafetyError("Refused: this write command requires --plan-in")
        read_json_file(plan_in)


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise SafetyError(_BEFORE_STATE_REFUSAL_REASON)


def _build_plan(*, spec: ActionSpec, command: str, query: dict[str, Any], path_values: dict[str, str], body: Any | None, ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": _TOOL_NAME,
        "version": ctx.get("tool_version"),
        "generated_at_utc": _safe_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": command,
        "family": spec.family,
        "action": spec.action,
        "method": spec.method,
        "path": spec.path,
        "path_values": path_values,
        "query": query,
        "has_body": body is not None,
        "notes": spec.notes,
        "require_apply": spec.require_apply,
        "require_yes": spec.require_yes,
        "require_ack": spec.require_ack,
        "require_plan_in": spec.require_plan_in,
        "risk_level": (
            "high"
            if (spec.require_yes or spec.require_ack or spec.require_plan_in)
            else ("medium" if spec.write else "low")
        ),
        "risk_reasons": [
            "write-operation" if spec.write else "read-only",
            "live-unverified",
            *(["require-yes"] if spec.require_yes else []),
            *(["require-ack"] if spec.require_ack else []),
            *(["require-plan-in"] if spec.require_plan_in else []),
        ],
        "before_state": _before_state_contract(spec=spec),
        "verification_plan": _verification_plan(spec=spec),
        "recovery": _no_recovery_contract(),
    }


def _build_request_path(*, spec: ActionSpec, path_values: dict[str, str]) -> str:
    return spec.path.format(**path_values)


def _http_request(
    *,
    ctx: dict[str, Any],
    spec: ActionSpec,
    token_result: AccessTokenResult,
    path: str,
    query: dict[str, Any],
    body: Any | None,
) -> Any:
    base = str(ctx["cfg"].base_url).rstrip("/")
    url = base + path
    headers = _build_headers(
        cfg=ctx["cfg"],
        token_result=token_result,
        spec=spec,
        run_id=str(ctx.get("run_id") or ""),
    )

    transport = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=_USER_AGENT,
    )
    response = transport.request(
        spec.method,
        url,
        headers=headers,
        params=query or None,
        json_body=body if isinstance(body, (dict, list)) else None,
    )

    if response.status in (204, 205):
        return {"status": response.status}
    try:
        return response.json()
    except Exception:
        return {"status": response.status, "text": response.text()}


def _emit_plan(*, ctx: dict[str, Any], spec: ActionSpec, query: dict[str, str], path_values: dict[str, str], body: Any | None) -> int:
    path = _build_request_path(spec=spec, path_values=path_values)
    plan = _build_plan(
        spec=spec,
        command=f"{_TOOL_NAME} {spec.family} {spec.action}",
        query=dict(query),
        path_values=path_values,
        body=body,
        ctx=ctx,
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if isinstance(plan_out, str) else None

    ctx["audit"].write(
        "paypal.api.plan",
        {
            "family": spec.family,
            "action": spec.action,
            "command": f"{spec.family} {spec.action}",
            "path": path,
            "plan_out": plan_path,
        },
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "method": spec.method,
            "path": path,
            "query": query,
            "write_gates": {
                "require_apply": spec.require_apply,
                "require_yes": spec.require_yes,
                "require_ack": spec.require_ack,
                "require_plan_in": spec.require_plan_in,
            },
        },
    )
    return 0


def cmd_paypal_api(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    spec = getattr(args, "paypal_spec", None)
    if not isinstance(spec, ActionSpec):
        raise ValidationError("Missing PayPal action spec")

    path_values = _collect_path_values(spec=spec, args=args)
    query = _collect_query(spec=spec, args=args)
    body = _load_body(spec=spec, args=args)
    parsed = ParsedInput(spec=spec, path_values=path_values, query=query, body=body)

    request_path = _build_request_path(spec=spec, path_values=parsed.path_values)

    if spec.write and spec.require_apply and not bool(ctx.get("apply")):
        return _emit_plan(ctx=ctx, spec=spec, query=parsed.query, path_values=parsed.path_values, body=body)

    if spec.write:
        _assert_write_gates(spec=spec, args=args, ctx=ctx)
        _require_no_snapshot_approval(ctx)
        token_result = resolve_access_token(
            cfg=ctx["cfg"],
            verbose=bool(ctx.get("verbose")),
            timeout_s=float(ctx["timeout_s"]),
        )
        response = _http_request(
            ctx=ctx,
            spec=spec,
            token_result=token_result,
            path=request_path,
            query=parsed.query,
            body=parsed.body,
        )
        receipt = {
            "tool": _TOOL_NAME,
            "version": ctx.get("tool_version"),
            "applied_at_utc": _safe_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str"),
            "family": spec.family,
            "action": spec.action,
            "method": spec.method,
            "path": request_path,
            "query": parsed.query,
            "has_body": parsed.body is not None,
            "before_state": _before_state_contract(spec=spec),
            "no_snapshot_approval": {
                "acknowledged": True,
                "flag": "--ack-no-snapshot",
                "reason": "No reliable generic before-state snapshot is available for this PayPal command.",
            },
            "changed": True,
            "token_source": token_result.source,
            "response": response,
            "verification": {
                "ok": True,
                "mode": "provider-response",
                "details": "PayPal HTTP call completed without a transport error.",
            },
            "recovery": _no_recovery_contract(),
        }
        receipt_out = ctx.get("receipt_out")
        receipt_path = write_json_file(receipt_out, receipt) if isinstance(receipt_out, str) else None
        out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
        ctx["audit"].write("paypal.api.apply", {"family": spec.family, "action": spec.action, "receipt_out": receipt_path})
        ctx["out"].emit(out)
        return 0

    token_result = resolve_access_token(
        cfg=ctx["cfg"],
        verbose=bool(ctx.get("verbose")),
        timeout_s=float(ctx["timeout_s"]),
    )

    response = _http_request(
        ctx=ctx,
        spec=spec,
        token_result=token_result,
        path=request_path,
        query=parsed.query,
        body=parsed.body,
    )

    ctx["audit"].write(
        "paypal.api.call",
        {
            "family": spec.family,
            "action": spec.action,
            "method": spec.method,
            "path": request_path,
        },
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": spec.method,
            "path": request_path,
            "query": parsed.query,
            "token_source": token_result.source,
            "response": response,
        },
    )
    return 0


def actions() -> dict[str, dict[str, ActionSpec]]:
    return catalog_actions()
