from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from ..api_dispatch import build_api_call_plan, load_operations_from_pinned_snapshot, operations_by_command
from ..errors import ValidationError
from ..http import HttpClient
from ..session_store import access_token_from_session, pds_url_from_session, read_session_json, refresh_token_from_session
from .write_safety import (
    before_state_contract,
    before_state_refusal_output,
    before_state_refusal_verification_plan,
)


IRREVERSIBLE_KEYWORDS = (
    "delete",
    "revoke",
    "remove",
    "deactivate",
    "disable",
)

RISKY_KEYWORDS = (
    "account",
    "admin",
    "apply-writes",
    "applywrites",
    "import",
    "moderation",
    "password",
    "report",
    "upload",
    "verification",
)

IRREVERSIBLE_WRITE_MODE = "irreversible_and_clearly_labeled"
API_WRITE_REFUSAL_REASON = (
    "Refused: this Bluesky API write has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _classify_operation(op: Any) -> dict[str, Any]:
    lower = str(op.operation_command or "").lower()
    is_read = str(op.kind) in {"query", "subscription"}
    is_write = str(op.kind) == "procedure"
    irreversible = is_write and any(keyword in lower for keyword in IRREVERSIBLE_KEYWORDS)
    risky = is_write and (irreversible or any(keyword in lower for keyword in RISKY_KEYWORDS))
    return {
        "is_read": is_read,
        "is_write": is_write,
        "irreversible": irreversible,
        "risky": risky,
        "gates": {
            "live": True,
            "apply": is_write,
            "yes": risky,
            "ack_irreversible": irreversible,
        },
    }


def _risk_level(classification: dict[str, Any]) -> str:
    if bool(classification.get("risky")):
        return "high"
    if bool(classification.get("is_write")):
        return "medium"
    return "low"


def _risk_reasons(classification: dict[str, Any]) -> list[str]:
    if bool(classification.get("is_read")):
        return ["read-only-operation"]
    reasons = ["write-operation"]
    if bool(classification.get("risky")):
        reasons.append("risky-write")
    if bool(classification.get("irreversible")):
        reasons.append("irreversible-write")
    return reasons


def _preconditions(classification: dict[str, Any], missing_required: list[dict[str, Any]]) -> list[str]:
    out = ["env_fingerprint must match the reviewed plan"]
    if bool(classification.get("is_write")):
        out.append("live writes require --live --apply")
    gates = classification.get("gates") or {}
    if bool(gates.get("yes")):
        out.append("risky apply requires --yes")
    if bool(gates.get("ack_irreversible")):
        out.append("irreversible apply requires --ack-irreversible")
    if missing_required:
        out.append("fill every required input before a live call")
    return out


def _verification_plan(classification: dict[str, Any], op: Any) -> dict[str, Any]:
    if str(op.kind) == "subscription":
        return {
            "type": "frame-capture-only",
            "notes": "Subscription endpoints return raw websocket frames and do not have generic read-back verification.",
        }
    if bool(classification.get("is_read")):
        return {
            "type": "provider-response-only",
            "notes": "Read execution is accepted from the live provider response only in this build.",
        }
    return before_state_refusal_verification_plan()


def _legacy_write_verification_plan() -> dict[str, Any]:
    return {
        "type": "provider-response-only",
        "notes": "Write execution is accepted from the live provider response only. No generic read-back target exists in this build.",
    }


def _rollback_contract(classification: dict[str, Any]) -> dict[str, Any]:
    if not bool(classification.get("is_write")):
        return {
            "supported": False,
            "notes": "No changes in dry-run or read-only output.",
        }
    return {
        "supported": False,
        "mode": IRREVERSIBLE_WRITE_MODE,
        "automatic_rollback": False,
        "requires_ack_irreversible": bool((classification.get("gates") or {}).get("ack_irreversible")),
        "notes": (
            "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
            "Treat current Bluesky write families as irreversible_and_clearly_labeled and use the saved plan and refusal output "
            "for manual follow-up only."
        ),
    }


def _compute_plan_hash(plan: dict[str, Any]) -> str:
    plan_copy = {key: value for key, value in plan.items() if key != "plan_hash"}
    encoded = json.dumps(plan_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ensure_write_safety_contract(plan: dict[str, Any], op: Any, classification: dict[str, Any]) -> dict[str, Any]:
    if not bool(classification.get("is_write")):
        return plan
    operation = plan.get("operation") or {}
    plan["before_state"] = before_state_contract(
        reason=(
            "This source tool can build and review Bluesky write plans, but no reliable "
            "operation-specific before-state snapshot is available for this generic API operation."
        ),
        provider_write={
            "operation_command": str(getattr(op, "operation_command", "") or ""),
            "lexicon_id": str(getattr(op, "lexicon_id", "") or ""),
            "kind": str(getattr(op, "kind", "") or ""),
            "http_method": str(getattr(op, "http_method", "") or ""),
            "path": str(getattr(op, "path", "") or ""),
            "service_url": operation.get("service_url"),
        },
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["legacy_verification_plan"] = _legacy_write_verification_plan()
    plan["rollback"] = _rollback_contract(classification)
    return plan


def _write_json_file(path_value: str | None, payload: dict[str, Any]) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)


def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in headers.items():
        if str(key).lower() in {"authorization", "cookie", "set-cookie"}:
            continue
        out[str(key).lower()] = value
    return out


def _redact_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            if lower in {"accessjwt", "refreshjwt", "access_token", "refresh_token", "token", "password"}:
                out[key] = "<redacted>"
            else:
                out[key] = _redact_json_value(item)
        return out
    if isinstance(value, list):
        return [_redact_json_value(item) for item in value]
    return value


def _build_response_body_summary(response: Any) -> dict[str, Any]:
    content_type = str(response.headers.get("content-type") or "")
    if "json" in content_type.lower():
        try:
            payload = _redact_json_value(response.json())
            return {"type": "json", "body_json": payload}
        except Exception:
            pass
    try:
        text = response.body.decode("utf-8")
        return {"type": "text", "body_text": text[:4000], "truncated": len(text) > 4000}
    except Exception:
        import base64

        return {
            "type": "bytes",
            "body_base64": base64.b64encode(response.body).decode("ascii"),
            "size": len(response.body),
        }


def _sanitize_for_output(value: Any) -> Any:
    return _redact_json_value(value)


def _client(ctx: dict[str, Any]) -> HttpClient:
    return HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"linux:{ctx.get('tool') or 'bluesky-safe-cli'}:v{ctx.get('tool_version') or '0.1.0'}",
    )


def _create_session(cfg: Any, ctx: dict[str, Any], *, persist: bool) -> dict[str, Any]:
    if not cfg.identifier:
        raise ValidationError("Missing BLUESKY_IDENTIFIER")
    if not cfg.app_password:
        raise ValidationError("Missing BLUESKY_APP_PASSWORD")
    client = _client(ctx)
    response = client.request(
        "POST",
        cfg.entryway_url.rstrip("/") + "/xrpc/com.atproto.server.createSession",
        headers={"Accept": "application/json"},
        json_body={"identifier": cfg.identifier, "password": cfg.app_password},
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Session response must be a JSON object")
    if persist:
        write_session_json(ctx["env_file"], payload)
    return payload


def _refresh_session(cfg: Any, ctx: dict[str, Any], *, persist: bool) -> dict[str, Any]:
    saved = read_session_json(ctx["env_file"])
    refresh_token = cfg.refresh_jwt or refresh_token_from_session(saved)
    if not refresh_token:
        raise ValidationError("Missing refresh JWT. Run `bluesky-safe-cli auth login` first.")
    base_url = pds_url_from_session(saved) or cfg.default_pds_url or cfg.entryway_url
    client = _client(ctx)
    response = client.request(
        "POST",
        base_url.rstrip("/") + "/xrpc/com.atproto.server.refreshSession",
        headers={"Authorization": f"Bearer {refresh_token}", "Accept": "application/json"},
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Refresh response must be a JSON object")
    if persist:
        write_session_json(ctx["env_file"], payload)
    return payload


def _resolve_auth(op: Any, cfg: Any, ctx: dict[str, Any]) -> tuple[dict[str, str], str | None, dict[str, Any] | None]:
    if op.namespace == "tools.ozone" and cfg.admin_token:
        return {"Authorization": f"Bearer {cfg.admin_token}"}, "env_admin_token", None

    saved = read_session_json(ctx["env_file"])
    env_access = str(cfg.access_jwt or "").strip()
    if env_access:
        return {"Authorization": f"Bearer {env_access}"}, "env_access_jwt", saved

    saved_access = access_token_from_session(saved)
    if saved_access:
        return {"Authorization": f"Bearer {saved_access}"}, "saved_session", saved

    if cfg.identifier and cfg.app_password:
        session = _create_session(cfg, ctx, persist=False)
        access = access_token_from_session(session)
        if access:
            return {"Authorization": f"Bearer {access}"}, "ephemeral_session", session

    refresh = cfg.refresh_jwt or refresh_token_from_session(saved)
    if refresh:
        session = _refresh_session(cfg, ctx, persist=False)
        access = access_token_from_session(session)
        if access:
            return {"Authorization": f"Bearer {access}"}, "refreshed_session", session

    return {}, None, saved


def _emit_refusal(ctx: dict[str, Any], op_cmd: str, reasons: list[str], plan: dict[str, Any], plan_path: str | None) -> int:
    payload = {
        "ok": True,
        "dry_run": True,
        "plan": plan,
        "plan_out": plan_path,
        "refused": True,
        "reasons": reasons,
        "refusal_type": "SafetyError",
    }
    ctx["audit"].write(
        "api.call.refused",
        {"operation_command": op_cmd, "reasons": reasons, "plan_hash": plan.get("plan_hash")},
    )
    ctx["out"].emit(payload)
    return 0


def cmd_api_ops_list(args: Any, ctx: dict[str, Any]) -> int:
    method = str(getattr(args, "method", "") or "").strip().upper()
    namespace = str(getattr(args, "namespace", "") or "").strip()
    group = str(getattr(args, "group", "") or "").strip()
    kind = str(getattr(args, "kind", "") or "").strip().lower()
    docs_source = str(getattr(args, "docs_source", "") or "").strip().lower()
    stability = str(getattr(args, "stability", "") or "").strip().lower()

    rows: list[dict[str, Any]] = []
    for op in load_operations_from_pinned_snapshot():
        if method and op.http_method != method:
            continue
        if namespace and op.namespace != namespace:
            continue
        if group and op.group != group:
            continue
        if kind and op.kind.lower() != kind:
            continue
        if docs_source and op.docs_source.lower() != docs_source:
            continue
        if stability and op.stability.lower() != stability:
            continue
        rows.append(
            {
                "lexicon_id": op.lexicon_id,
                "operation_command": op.operation_command,
                "namespace": op.namespace,
                "group": op.group,
                "kind": op.kind,
                "http_method": op.http_method,
                "docs_source": op.docs_source,
                "stability": op.stability,
                "route_hint": op.route_hint,
                "primary_cli": op.primary_cli,
                "doc_url": op.doc_url,
            }
        )

    payload = {"ok": True, "ops": rows, "count": len(rows)}
    ctx["audit"].write(
        "api.ops.list",
        {
            "count": len(rows),
            "method": method or None,
            "namespace": namespace or None,
            "group": group or None,
            "kind": kind or None,
            "docs_source": docs_source or None,
            "stability": stability or None,
        },
    )
    ctx["out"].emit(payload)
    return 0


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    op_cmd = str(getattr(args, "op", "") or "").strip()
    if not op_cmd:
        raise ValidationError("Missing operation")

    op = operations_by_command(load_operations_from_pinned_snapshot()).get(op_cmd)
    if not op:
        raise ValidationError(f"Unknown operation command: {op_cmd}")

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "bluesky-safe-cli",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx.get("env_fingerprint") or getattr(ctx.get("cfg"), "base_url", "")),
        op=op,
        cfg=ctx.get("cfg"),
        query_json=getattr(args, "query_json", None),
        body_json=getattr(args, "body_json", None),
        query_pairs=getattr(args, "query", None),
        body_pairs=getattr(args, "body", None),
        input_file=getattr(args, "input_file", None),
        input_content_type=getattr(args, "input_content_type", None),
        service_url=getattr(args, "service_url", None),
    )
    classification = _classify_operation(op)
    missing_required = plan.get("requirements", {}).get("missing_required") or []
    plan["generated_at_utc"] = _utc_now()
    plan["classification"] = classification
    plan["risk_level"] = _risk_level(classification)
    plan["risk_reasons"] = _risk_reasons(classification)
    plan["preconditions"] = _preconditions(classification, missing_required)
    plan["verification_plan"] = _verification_plan(classification, op)
    plan["rollback"] = _rollback_contract(classification)
    plan = _ensure_write_safety_contract(plan, op, classification)
    plan["plan_hash"] = _compute_plan_hash(plan)
    sanitized_plan = _sanitize_for_output(plan)

    plan_path = _write_json_file(ctx.get("plan_out"), sanitized_plan)
    if ctx.get("plan_out") and plan_path is None:
        raise ValidationError("Unable to write --plan-out file")

    apply = bool(ctx.get("apply"))
    live = bool(ctx.get("live"))
    gates = classification["gates"]
    reasons: list[str] = []

    if apply and not live:
        reasons.append("Refused: --live is required for apply")
    if apply and gates["yes"] and not bool(ctx.get("yes")):
        reasons.append("Refused: --yes is required for risky operations")
    if apply and gates["ack_irreversible"] and not bool(ctx.get("ack_irreversible")):
        reasons.append("Refused: --ack-irreversible is required for irreversible operations")
    if missing_required and live:
        desc = ", ".join(f"{item.get('in')}:{item.get('name')}" for item in missing_required)
        reasons.append(f"Refused: missing required inputs ({desc})")
    if reasons:
        return _emit_refusal(ctx, op_cmd, reasons, sanitized_plan, plan_path)

    if not apply and not (classification["is_read"] and live):
        payload = {"ok": True, "dry_run": True, "plan": sanitized_plan, "plan_out": plan_path}
        ctx["audit"].write(
            "api.call.plan",
            {"operation_command": op_cmd, "plan_hash": plan["plan_hash"], "plan_out": plan_path},
        )
        ctx["out"].emit(payload)
        return 0

    if classification["is_write"]:
        if not bool(ctx.get("ack_no_snapshot")):
            out = before_state_refusal_output(sanitized_plan, reason=API_WRITE_REFUSAL_REASON)
            ctx["audit"].write(
                "api.call.refused",
                {
                    "operation_command": op_cmd,
                    "plan_hash": plan["plan_hash"],
                    "reason": API_WRITE_REFUSAL_REASON,
                    "before_state": sanitized_plan.get("before_state"),
                },
            )
            ctx["out"].emit(out)
            return 0

    cfg = ctx["cfg"]
    headers = {"Accept": "application/json"}
    auth_headers, token_source, session_obj = _resolve_auth(op, cfg, ctx)
    headers.update(auth_headers)

    if classification["is_write"] and op.lexicon_id not in {
        "com.atproto.server.createAccount",
        "com.atproto.server.createSession",
    } and "Authorization" not in headers:
        raise ValidationError("Live write requires a stored session, env JWT, or app-password credentials")

    client = _client(ctx)

    live_base_url = plan["operation"]["service_url"]
    if op.route_hint == "entryway-or-pds":
        if op.namespace == "app.bsky" and classification["is_read"] and "Authorization" not in headers:
            live_base_url = cfg.public_api_url
        else:
            live_base_url = pds_url_from_session(session_obj) or pds_url_from_session(read_session_json(ctx["env_file"])) or cfg.default_pds_url or cfg.entryway_url

    live_url = str(live_base_url).rstrip("/") + op.path
    receipt: dict[str, Any]

    if op.kind == "subscription":
        frames = client.capture_websocket_frames(
            live_url,
            headers=headers,
            event_limit=int(getattr(args, "event_limit", 5) or 5),
            idle_timeout_s=getattr(args, "idle_timeout_s", None),
        )
        receipt = {
            "tool": ctx.get("tool") or "bluesky-safe-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": plan.get("env_fingerprint"),
            "command": ctx.get("command_str") or None,
            "plan_hash": plan["plan_hash"],
            "token_source": token_source,
            "operation": {**plan["operation"], "service_url": live_base_url, "url": live_url},
            "classification": classification,
            "response": {
                "type": "subscription",
                "frame_count": len(frames),
                "frames": frames,
            },
            "verification": {"status": "skipped", "details": "Subscription endpoints return raw frames"},
            "rollback_plan": _rollback_contract(classification),
        }
    else:
        body = plan["inputs"]["body"] or {}
        headers = dict(headers)
        json_body = None
        data = None
        content = None
        if op.input_encoding == "application/json" and body and op.http_method == "POST":
            headers["Content-Type"] = "application/json"
            json_body = body
        elif op.input_encoding and op.input_encoding != "application/json":
            file_path = plan["inputs"].get("input_file")
            if not file_path:
                raise ValidationError("This endpoint requires --input-file")
            content = Path(str(file_path)).read_bytes()
            headers["Content-Type"] = str(plan["inputs"].get("input_content_type") or op.input_encoding or "application/octet-stream")

        response = client.request(
            method=op.http_method,
            url=live_url,
            headers=headers,
            params=plan["inputs"]["query"],
            json_body=json_body,
            data=data,
            content=content,
        )
        receipt = {
            "tool": ctx.get("tool") or "bluesky-safe-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": plan.get("env_fingerprint"),
            "command": ctx.get("command_str") or None,
            "plan_hash": plan["plan_hash"],
            "token_source": token_source,
            "operation": {**plan["operation"], "service_url": live_base_url, "url": live_url},
            "classification": classification,
            "before_state": plan.get("before_state"),
            "no_snapshot_approval": {
                "acknowledged": bool(classification.get("is_write")),
                "flag": "--ack-no-snapshot",
                "reason": "No reliable before-state snapshot is available for this Bluesky API write.",
            } if classification.get("is_write") else None,
            "response": {
                "status": response.status,
                "url": response.url,
                "headers": _sanitize_headers(response.headers),
                "body": _build_response_body_summary(response),
            },
            "verification": {"status": "skipped", "details": "No generic read-back target for this endpoint"},
            "rollback_plan": _rollback_contract(classification),
        }

    sanitized_receipt = _sanitize_for_output(receipt)
    receipt_path = _write_json_file(ctx.get("receipt_out"), sanitized_receipt)
    payload = {"ok": True, "dry_run": False, "plan": sanitized_plan, "receipt": sanitized_receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "api.call.apply",
        {"operation_command": op_cmd, "plan_hash": plan["plan_hash"], "receipt_out": receipt_path, "token_source": token_source},
    )
    ctx["out"].emit(payload)
    return 0
