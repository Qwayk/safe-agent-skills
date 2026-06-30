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


def _coerce_query_payload(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="query-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--query-json must be a non-empty JSON object")
    query = value.get("query")
    if not isinstance(query, dict):
        raise ValidationError("--query-json.query must be a JSON object")
    return value


def _resolve_sending_domains_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="sending-domains",
    )
    return auth["headers"], auth["mode"]


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


def _extract_sending_domain(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    sending_domain = payload.get("sendingDomain")
    if not isinstance(sending_domain, dict):
        raise ValidationError(f"{operation} response did not include a sendingDomain object")
    return sending_domain


def _extract_sending_domains(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    sending_domains = payload.get("sendingDomains")
    if not isinstance(sending_domains, list):
        raise ValidationError(f"{operation} response did not include a sendingDomains array")
    return [item for item in sending_domains if isinstance(item, dict)]


def _get_sending_domain(*, sending_domain_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/sending-domains/v1/sending-domains/{sending_domain_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sending_domain(payload, operation="sending-domains.get")


def _build_query_request(args) -> tuple[dict[str, Any], dict[str, Any]]:
    domain = getattr(args, "domain", None)
    sending_domain_id = getattr(args, "sending_domain_id", None)
    query_json = getattr(args, "query_json", None)
    if query_json is not None:
        payload = _coerce_query_payload(query_json)
        return payload, payload.get("query") if isinstance(payload.get("query"), dict) else {}
    filter_query: dict[str, Any] = {}
    if domain is not None:
        filter_query["domain"] = _coerce_non_empty_text(domain, field="domain")
    if sending_domain_id is not None:
        filter_query["id"] = _coerce_non_empty_text(sending_domain_id, field="sending-domain-id")
    if not filter_query:
        raise ValidationError("Provide --domain, --sending-domain-id, or --query-json")
    payload = {"query": {"filter": filter_query}}
    return payload, payload["query"]


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
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "medium",
        "risk_reasons": ["sending-domain-write"],
        "provider_notes": [
            "Authenticate only when the current status is NOT_AUTHENTICATED.",
            "If Wix manages DNS for the domain, the official docs say you do not need to call authenticate.",
        ],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": before_state},
        "state_capture": {"before_state_available": bool(before_state), "notes": "Captured current sending domain state before planning."},
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual only."},
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


def _should_apply(ctx: dict[str, Any]) -> bool:
    return reviewed_plan_apply_requested(ctx, command_label="sending-domains")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: sending domain state changed since plan was created")


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
        "state_capture": {"before_state_available": bool(before_state), "notes": "Receipt stores sending domain metadata only."},
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def cmd_sending_domains_get(args, ctx) -> int:
    try:
        sending_domain_id = _coerce_non_empty_text(getattr(args, "sending_domain_id", None), field="sending-domain-id")
        headers, auth_mode = _resolve_sending_domains_auth(ctx=ctx)
        sending_domain = _get_sending_domain(sending_domain_id=sending_domain_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sending-domains.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/sending-domains/v1/sending-domains/{sending_domain_id}"},
                "response": {"sendingDomain": sending_domain},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sending-domains.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sending-domains.get"})
        return 1


def cmd_sending_domains_query(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_sending_domains_auth(ctx=ctx)
        payload, query = _build_query_request(args)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/sending-domains/v1/sending-domains/query",
            headers=headers,
            params=None,
            json_body=payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        sending_domains = _extract_sending_domains(response, operation="sending-domains.query")
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sending-domains.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/sending-domains/v1/sending-domains/query", "body": payload},
                "response": {"sendingDomains": sending_domains},
                "notes": [
                    "The official docs require a filter by domain or id for this query.",
                    f"Query keys used: {sorted(query.keys())}",
                ],
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sending-domains.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sending-domains.query"})
        return 1


def cmd_sending_domains_authenticate(args, ctx) -> int:
    try:
        sending_domain_id = _coerce_non_empty_text(getattr(args, "sending_domain_id", None), field="sending-domain-id")
        headers, auth_mode = _resolve_sending_domains_auth(ctx=ctx)
        current = _get_sending_domain(sending_domain_id=sending_domain_id, ctx=ctx, headers=headers)
        if current.get("status") != "NOT_AUTHENTICATED":
            raise SafetyError("Refused: authenticate only when the current sending domain status is NOT_AUTHENTICATED")
        request = {
            "method": "POST",
            "path": f"/sending-domains/v1/sending-domains/{sending_domain_id}/authenticate",
            "body": None,
        }
        selector = {"kind": "wix-sending-domain", "operation": "authenticate", "sending_domain_id": sending_domain_id}
        before_state = {"sendingDomain": current}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="sending-domains.authenticate", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="sending-domains.authenticate",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "authenticate", "sendingDomainId": sending_domain_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify the sending domain status becomes AUTHENTICATED after apply."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "sending-domains.authenticate", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="sending-domains.authenticate", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"sendingDomain": _get_sending_domain(sending_domain_id=sending_domain_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/sending-domains/v1/sending-domains/{sending_domain_id}/authenticate",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after = _get_sending_domain(sending_domain_id=sending_domain_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after.get("status") == "AUTHENTICATED",
            "type": "read-after-write",
            "path": f"/sending-domains/v1/sending-domains/{sending_domain_id}",
            "method": "GET",
            "before": current,
            "after": after,
            "checks": [{"field": "status", "expected": "AUTHENTICATED", "actual": after.get("status")}],
        }
        receipt = _build_receipt(method="sending-domains.authenticate", selector=selector, request=request, response=response, verification=verification, plan=loaded_plan, ctx=ctx)
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "sending-domains.authenticate", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "sending-domains.authenticate"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sending-domains.authenticate"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sending-domains.authenticate"})
        return 1
