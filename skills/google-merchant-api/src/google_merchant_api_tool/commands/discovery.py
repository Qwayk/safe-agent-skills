from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
from typing import Any

from ..discovery import MethodSpec, is_read_like_post, load_shipped_methods
from ..errors import SafetyError, ToolError, ValidationError
from ..google_auth import load_credentials_from_config
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..method_inventory import method_to_command_tokens


_PATH_PARAM_RE = re.compile(r"{(\+?[^}]+)}")
_HIGH_RISK_FINAL_TOKENS = {
    "approve",
    "reject",
    "enable",
    "disable",
    "manage",
    "applyorderupdate",
    "requestinventoryverification",
}


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _safe_bool(raw: str) -> bool:
    v = str(raw).strip().lower()
    if v in {"1", "true", "t", "yes", "y"}:
        return True
    if v in {"0", "false", "f", "no", "n"}:
        return False
    raise ValidationError("Boolean flag must be one of: true, false, 1, 0")


def _convert_value(param: str | None, raw: str) -> Any:
    if param == "boolean":
        return _safe_bool(raw)
    if param in {"integer", "int", "uint32", "int32", "uint64", "int64"}:
        try:
            return int(raw)
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Expected integer value: {raw}: {type(e).__name__}: {e}") from e
    if param in {"number", "float", "double"}:
        try:
            return float(raw)
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Expected numeric value: {raw}: {type(e).__name__}: {e}") from e
    return raw


def _flag_name(name: str) -> str | None:
    if not name:
        return None
    if any(ch in name for ch in "/[]{}()"):
        return None
    out = []
    for ch in name:
        if ch == "_":
            out.append("-")
        elif ch.isupper():
            if out:
                out.append("-")
            out.append(ch.lower())
        else:
            out.append(ch)
    flag = "--" + "".join(out)
    return flag if len(flag) > 2 else None


def _dest_from_flag(name: str) -> str:
    out = []
    for ch in name:
        if ch in ".-":
            out.append("_")
        elif ch == "+":
            out.append("plus_")
        else:
            out.append(ch.lower())
    return "".join(out)


def _ordered_params(spec: MethodSpec) -> list[tuple[str, Any]]:
    out = []
    for p in sorted(spec.parameters, key=lambda p: ((0 if (p.location or "").lower() == "path" else 1), p.name)):
        out.append(
            (p.name, {"location": str(p.location or "query"), "required": bool(p.required), "type": p.type})
        )
    return out


def _normalize_body(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {k: _normalize_body(v) for k, v in sorted(payload.items(), key=lambda item: item[0])}
    if isinstance(payload, list):
        return [_normalize_body(v) for v in payload]
    return payload


def _stable_json_text(payload: Any) -> str:
    return json.dumps(_normalize_body(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _risk_level(method: MethodSpec) -> str:
    if str(method.http_method).upper() == "DELETE":
        return "irreversible"
    if str(method.http_method).upper() != "GET" and not is_read_like_post(method):
        final_token = method.command_id.rsplit(".", 1)[-1].lower() if method.command_id else ""
        if final_token.startswith("batch"):
            return "high"
        if final_token in _HIGH_RISK_FINAL_TOKENS:
            return "high"
        return "medium"
    return "read"


def _risk_reasons(method: MethodSpec, risk_level: str) -> list[str]:
    if risk_level == "read":
        return ["read-like-post" if is_read_like_post(method) else "read-only"]

    reasons: list[str] = ["write-operation"]
    if str(method.http_method).upper() == "DELETE":
        reasons.append("http-delete")
        return reasons

    final_token = method.command_id.rsplit(".", 1)[-1].lower() if method.command_id else ""
    if final_token.startswith("batch"):
        reasons.append("batch-operation")
    if final_token in _HIGH_RISK_FINAL_TOKENS:
        reasons.append(f"high-risk-action:{final_token}")
    if risk_level == "medium":
        reasons.append("single-write")
    return reasons


def _selector_for_method(method: MethodSpec, path_params: dict[str, Any]) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "family": method.family,
        "method_id": method.command_id,
    }
    normalized_params = _normalize_body(path_params)
    if normalized_params:
        selector["path_params"] = normalized_params
        primary = normalized_params.get("name") or normalized_params.get("parent")
        if primary is None:
            primary = next(iter(normalized_params.values()))
        selector["resource"] = str(primary)
    return selector


def _preconditions_for_method(risk_level: str) -> list[str]:
    preconditions = ["Review the computed path, query, and request body before applying."]
    if risk_level in {"high", "irreversible"}:
        preconditions.append("Apply requires a reviewed matching --plan-in file.")
        preconditions.append("Apply requires --yes.")
    if risk_level == "irreversible":
        preconditions.append("Apply requires --ack-irreversible.")
    return preconditions


def _verification_plan_for_method(method: MethodSpec) -> dict[str, Any]:
    if str(method.http_method).upper() != "GET" and not is_read_like_post(method):
        return {
            "mode": "best_effort_after_apply",
            "expected_outcome": "provider-response-recorded",
            "notes": (
                "Generic Merchant verification currently confirms the applied call returned 2xx. "
                "No generic before-state snapshot is available for every provider method, so apply requires explicit no-snapshot approval."
            ),
            "suggested_follow_up": "Run the matching explicit read/list/get command for the same resource when the API family provides one.",
        }
    return {
        "mode": "transport-status",
        "expected_status": "2xx",
        "notes": (
            "Generic Merchant verification currently confirms the applied call returned 2xx. "
            "This tool does not auto-generate a follow-up read for every provider method yet."
        ),
        "suggested_follow_up": (
            "Run the matching explicit read/list/get command for the same resource when the API family provides one."
            if str(method.http_method).upper() != "GET"
            else "No extra verification needed for read-only calls."
        ),
    }


def _rollback_for_method(method: MethodSpec, risk_level: str) -> dict[str, Any]:
    if risk_level == "irreversible":
        return {
            "supported": False,
            "notes": "This action is treated as irreversible. Use the receipt and provider UI/history for manual follow-up.",
        }
    if str(method.http_method).upper() == "GET":
        return {
            "supported": True,
            "notes": "Read-only command. No rollback needed.",
        }
    return {
        "supported": False,
        "notes": (
            "This tool does not generate a generic rollback plan for Merchant writes. "
            "Use the saved plan/receipt values to prepare a reverse change if needed."
        ),
    }


def _before_state_for_method(risk_level: str) -> dict[str, Any]:
    if risk_level == "read":
        return {
            "required": False,
            "supported": False,
            "statement": "Read operation. No before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "statement": (
            "This Google Merchant command has no reliable generic before-state snapshot. "
            "Apply may continue only after explicit no-snapshot approval."
        ),
    }


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise SafetyError(
        "Refused: this Google Merchant write has no reliable generic before-state snapshot. "
        "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
    )


def _cli_command_for_method(method: MethodSpec) -> str:
    return "google-merchant-api-tool " + " ".join(method_to_command_tokens(method))


def _extract_plan_sections(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": plan.get("family"),
        "method_id": plan.get("method_id"),
        "http_method": plan.get("http_method"),
        "path": plan.get("path"),
        "query": plan.get("query"),
        "risk_level": plan.get("risk_level"),
        "body": plan.get("body"),
    }


def _validate_plan_in(
    *,
    plan: dict[str, Any],
    method: MethodSpec,
    full_path: str,
    query: dict[str, Any],
    body: Any | None,
    risk_level: str,
    env_fingerprint: str,
) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("--plan-in JSON must be an object")

    extracted = _extract_plan_sections(plan)
    expected = {
        "env_fingerprint": str(env_fingerprint or ""),
        "family": method.family,
        "method_id": method.command_id,
        "http_method": method.http_method,
        "path": full_path,
        "risk_level": risk_level,
        "query": query,
        "body": _normalize_body(body),
    }

    for key in ("family", "method_id", "http_method", "path", "risk_level"):
        if str(extracted.get(key)) != str(expected[key]):
            raise SafetyError(f"Refused: plan does not match current command ({key})")
    if _stable_json_text(extracted.get("query")) != _stable_json_text(expected["query"]):
        raise SafetyError("Refused: plan query changed since plan was generated")
    if _stable_json_text(extracted.get("body")) != _stable_json_text(expected["body"]):
        raise SafetyError("Refused: plan body changed since plan was generated")
    if str(plan.get("env_fingerprint") or "") != str(expected["env_fingerprint"]):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")


def _add_method_parser(parser: argparse.ArgumentParser, spec: MethodSpec) -> None:
    help_text = spec.description or ""
    for param_name, pinfo in _ordered_params(spec):
        flag = _flag_name(param_name)
        if not flag:
            continue
        dest = _dest_from_flag(param_name)
        location = pinfo["location"]
        is_required = bool(pinfo["required"] and location == "path")
        parser.add_argument(
            flag,
            type=str,
            required=is_required,
            help=f"[{location}] {param_name}",
            metavar=param_name,
            default=argparse.SUPPRESS,
        )
        parser.set_defaults(**{f"{dest}_is_path": location == "path"})

    parser.add_argument("--body-json", help="JSON body string")
    parser.add_argument("--body-file", help="Path to JSON body file")

    parser.set_defaults(
        func=cmd_discovery_method,
        discovery_method=spec,
        write_capable=bool(spec.http_method != "GET" and not is_read_like_post(spec)),
    )


def _build_path(path_template: str, path_params: dict[str, Any]) -> str:
    out = str(path_template)
    for raw in _PATH_PARAM_RE.findall(path_template):
        is_reserved = raw.startswith("+")
        token = raw[1:] if is_reserved else raw
        name = token.split("=", 1)[0]
        if name not in path_params:
            raise ValidationError(f"Missing required path parameter: {name}")
        value = path_params[name]
        preserve_slashes = is_reserved or "=" in token
        quoted = urllib.parse.quote(str(value), safe="/" if preserve_slashes else "")
        out = out.replace("{" + raw + "}", quoted)
    return out


def _load_body(*, args: argparse.Namespace, required: bool) -> Any | None:
    raw_json = getattr(args, "body_json", None)
    raw_file = getattr(args, "body_file", None)
    if raw_json and raw_file:
        raise ValidationError("Pass only one of --body-json or --body-file")
    if not raw_json and not raw_file:
        if not required:
            return None
        raise ValidationError("This method requires a request body. Pass --body-json or --body-file")
    if raw_json:
        try:
            return json.loads(str(raw_json))
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Invalid --body-json: {type(e).__name__}: {e}") from e
    return read_json_file(raw_file)


def _build_plan(
    *,
    method: MethodSpec,
    full_path: str,
    path_params: dict[str, Any],
    query: dict[str, Any],
    body: Any | None,
    env_fingerprint: str,
    ctx: dict,
) -> dict[str, Any]:
    risk_level = _risk_level(method)
    normalized_body = _normalize_body(body)
    normalized_query = _normalize_body(query)
    selector = _selector_for_method(method, path_params)
    return {
        "tool": str(ctx.get("tool") or "google-merchant-api-tool"),
        "version": str(ctx.get("tool_version") or "0.0.0"),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": env_fingerprint,
        "command": _cli_command_for_method(method),
        "family": method.family,
        "method_id": method.command_id,
        "http_method": method.http_method,
        "path": full_path,
        "path_params": _normalize_body(path_params),
        "query": normalized_query,
        "body": normalized_body,
        "has_body": body is not None,
        "risk_level": risk_level,
        "risk_reasons": _risk_reasons(method, risk_level),
        "write": bool(method.http_method != "GET" and not is_read_like_post(method)),
        "selector": selector,
        "proposed_changes": [
            {
                "kind": "api-call",
                "http_method": method.http_method,
                "path": full_path,
                "query": normalized_query,
                "body": normalized_body,
            }
        ],
        "preconditions": _preconditions_for_method(risk_level),
        "verification_plan": _verification_plan_for_method(method),
        "verification": {
            "mode": "plan-match",
            "expected_status": "2xx",
            "notes": "Plan validation compares env_fingerprint, family, method, http_method, path, query, body, and risk_level.",
        },
        "before_state": _before_state_for_method(risk_level),
        "rollback": _rollback_for_method(method, risk_level),
    }


def _write_if_requested(ctx: dict, *, filename: str | None, payload: dict[str, Any]) -> str | None:
    if not filename:
        return None
    return write_json_file(filename, payload)


def _response_payload(
    *,
    response: HttpClient.HttpResponse,
    method: MethodSpec,
    body: Any | None,
    query: dict[str, Any],
    apply: bool,
    path_params: dict[str, Any],
) -> dict[str, Any]:
    parsed: dict[str, Any] | None = None
    raw_text: str | None = None
    try:
        parsed = response.json()
    except Exception:
        raw_text = response.text()
    out: dict[str, Any] = {
        "ok": 200 <= int(response.status) < 300,
        "dry_run": not apply,
        "verified": bool(200 <= int(response.status) < 300),
        "family": method.family,
        "method_id": method.command_id,
        "http_method": method.http_method,
        "risk_level": _risk_level(method),
        "selector": _selector_for_method(method, path_params),
        "status": response.status,
        "url": response.url,
        "query": query,
        "body_present": body is not None,
    }
    if parsed is not None:
        out["json"] = parsed
    else:
        out["text"] = raw_text
    return out


def cmd_discovery_method(args: argparse.Namespace, ctx: dict) -> int:
    method: MethodSpec | None = getattr(args, "discovery_method", None)
    if not method:
        raise ToolError("Missing method metadata")

    path_param_defs = {p[0]: p[1] for p in _ordered_params(method) if (p[1]["location"] or "").lower() == "path"}
    query_param_defs = {p[0]: p[1] for p in _ordered_params(method) if (p[1]["location"] or "").lower() == "query"}

    params: dict[str, Any] = {}
    for pname, pinfo in {**path_param_defs, **query_param_defs}.items():
        raw = getattr(args, _dest_from_flag(pname), None)
        if raw is None:
            continue
        params[pname] = _convert_value(pinfo["type"], raw)

    path_params = {k: v for k, v in params.items() if k in path_param_defs}
    query_params = {k: v for k, v in params.items() if k in query_param_defs}

    request_path = _build_path(method.path, path_params)
    body = _load_body(args=args, required=bool(method.has_request_body))

    write_capable = bool(getattr(method, "http_method", "").upper() != "GET" and not is_read_like_post(method))
    risk_level = _risk_level(method)
    apply = bool(ctx.get("apply"))
    env_fingerprint = str(ctx["cfg"].base_url)
    plan_in = str(ctx.get("plan_in") or "").strip() if ctx.get("plan_in") else None
    plan_obj: dict[str, Any] | None = None

    if write_capable and not apply:
        plan = _build_plan(
            method=method,
            full_path=request_path,
            path_params=path_params,
            query=query_params,
            body=body,
            env_fingerprint=env_fingerprint,
            ctx=ctx,
        )
        plan_out = _write_if_requested(ctx=ctx, filename=str(ctx.get("plan_out") or ""), payload=plan)
        ctx["audit"].write("merchant.method.plan", {"method_id": method.command_id, "plan_out": plan_out})
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "plan": plan,
                "plan_out": plan_out,
                "risk_level": risk_level,
                "write_capable": write_capable,
                "selector": plan["selector"],
            }
        )
        return 0

    if write_capable:
        if risk_level == "irreversible":
            if not bool(ctx.get("apply")):
                raise SafetyError("Refusing irreversible write without --apply")
            if not bool(ctx.get("yes")):
                raise SafetyError("Refusing irreversible write without --yes")
            if not bool(ctx.get("ack_irreversible")):
                raise SafetyError("Refusing irreversible write without --ack-irreversible")
            if not plan_in:
                raise SafetyError("Refusing irreversible write without --plan-in")
        elif risk_level == "high":
            if not bool(ctx.get("apply")):
                raise SafetyError("Refusing high-risk write without --apply")
            if not bool(ctx.get("yes")):
                raise SafetyError("Refusing high-risk write without --yes")
            if not plan_in:
                raise SafetyError("Refusing high-risk write without --plan-in")

        if plan_in:
            raw_plan = read_json_file(plan_in)
            if not isinstance(raw_plan, dict):
                raise ValidationError("--plan-in JSON must be an object")
            plan_obj = raw_plan
            _validate_plan_in(
                plan=plan_obj,
                method=method,
                full_path=request_path,
                query=query_params,
                body=body,
                risk_level=risk_level,
                env_fingerprint=env_fingerprint,
            )

        _require_no_snapshot_approval(ctx)

    creds, creds_status = load_credentials_from_config(cfg=ctx["cfg"], env_file=ctx["env_file"])
    client = HttpClient(
        timeout_s=float(ctx.get("timeout_s") or ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"google-merchant-api-tool/{ctx.get('tool_version') or '0.0.0'}",
    )
    headers = {"Authorization": f"Bearer {creds.token}"} if getattr(creds, "token", None) else {}
    resp = client.request(
        method=method.http_method,
        url=f"{ctx['cfg'].base_url.rstrip('/')}/{request_path.lstrip('/')}",
        headers=headers,
        params=query_params,
        json_body=body,
        retries=1,
    )

    out = _response_payload(
        response=resp,
        method=method,
        body=body,
        query=query_params,
        apply=apply,
        path_params=path_params,
    )
    if write_capable and risk_level == "irreversible":
        out["recovery_hint"] = {
            "kind": "irreversible",
            "notes": "Delete may be hard to rollback. Keep receipts and verify in downstream checks.",
        }

    if write_capable and apply:
        plan = _build_plan(
            method=method,
            full_path=request_path,
            path_params=path_params,
            query=query_params,
            body=body,
            env_fingerprint=env_fingerprint,
            ctx=ctx,
        )
        requested_plan = plan_obj if plan_obj is not None else plan
        out["receipt"] = {
            "tool": str(ctx.get("tool") or "google-merchant-api-tool"),
            "version": str(ctx.get("tool_version") or "0.0.0"),
            "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "env_fingerprint": env_fingerprint,
            "command": _cli_command_for_method(method),
            "selector": _selector_for_method(method, path_params),
            "family": method.family,
            "risk_level": risk_level,
            "risk_reasons": _risk_reasons(method, risk_level),
            "method_id": method.command_id,
            "before_state": plan["before_state"],
            "no_snapshot_approval": {
                "acknowledged": True,
                "flag": "--ack-no-snapshot",
                "reason": "No reliable generic before-state snapshot is available for this Google Merchant method.",
            },
            "applied": True,
            "changed": bool(200 <= int(resp.status) < 300),
            "status": resp.status,
            "query": _normalize_body(query_params),
            "body": _normalize_body(body),
            "path": request_path,
            "auth": {
                "mode": ctx["cfg"].auth_mode,
                "kind": creds_status.kind,
                "valid": creds_status.valid,
                "scopes": list(creds_status.scopes),
            },
            "response_status": resp.status,
            "requested_plan": requested_plan,
            "verification": {
                "ok": 200 <= int(resp.status) < 300,
                "mode": "transport-status",
                "details": {
                    "expected_status": "2xx",
                    "status": resp.status,
                    "notes": _verification_plan_for_method(method)["notes"],
                },
            },
            "diff_applied": plan["proposed_changes"],
            "rollback": _rollback_for_method(method, risk_level),
        }
        receipt_out = _write_if_requested(ctx=ctx, filename=str(ctx.get("receipt_out") or ""), payload=out["receipt"])
        if receipt_out:
            out["receipt_out"] = receipt_out

    ctx["audit"].write("merchant.method.call", {"method_id": method.command_id, "status": resp.status})
    ctx["out"].emit(out)
    return 0


def _get_or_create_branch(
    *,
    parent_subparsers: argparse._SubParsersAction,
    token: str,
) -> argparse._SubParsersAction:
    existing = getattr(parent_subparsers, "_name_parser_map", {}).get(token)
    if existing is None:
        node = parent_subparsers.add_parser(token, help=f"{token}", description=f"{token}")
        sub = node.add_subparsers(dest="discovery_cmd", required=True, parser_class=_ToolArgumentParser)
        setattr(node, "_google_merchant_discovery_subparsers", sub)
        return sub

    existing_defaults = getattr(existing, "_defaults", {})
    if "func" in existing_defaults and existing_defaults.get("discovery_method") is not None:
        raise RuntimeError(f"Discovery parser conflict for token: {token}")

    sub = getattr(existing, "_google_merchant_discovery_subparsers", None)
    if sub is None:
        sub = existing.add_subparsers(dest="discovery_cmd", required=True, parser_class=_ToolArgumentParser)
        setattr(existing, "_google_merchant_discovery_subparsers", sub)
    return sub


def _add_method_leaf(*, parent_subparsers: argparse._SubParsersAction, token: str, spec: MethodSpec) -> None:
    existing = getattr(parent_subparsers, "_name_parser_map", {}).get(token)
    if existing is None:
        parser = parent_subparsers.add_parser(token, help=spec.description or spec.command_id, description=spec.description)
        _add_method_parser(parser, spec)
        return

    existing_defaults = getattr(existing, "_defaults", {})
    if existing_defaults.get("discovery_method") is not None:
        if existing_defaults.get("discovery_method") == spec:
            return
        raise RuntimeError(
            "Duplicate discovery parser for "
            + " ".join(method_to_command_tokens(spec))
        )

    _add_method_parser(existing, spec)


def register_discovery_commands(subparsers: argparse._SubParsersAction) -> None:
    for method in load_shipped_methods():
        tokens = method_to_command_tokens(method)
        if not tokens:
            continue

        current = subparsers
        for token in tokens[:-1]:
            current = _get_or_create_branch(parent_subparsers=current, token=token)
        _add_method_leaf(parent_subparsers=current, token=tokens[-1], spec=method)


def command_ids_from_inventory() -> list[str]:
    return [f"{m.family}:{m.command_id}" for m in load_shipped_methods()]
