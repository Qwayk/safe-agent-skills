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


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON object or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return value


def _read_json_array(raw: Any, *, field: str) -> list[Any]:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON array or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    return value


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _maybe_wrap_policy(value: dict[str, Any]) -> dict[str, Any]:
    if "dataSharingPolicy" in value:
        body = value
    else:
        body = {"dataSharingPolicy": value}
    policy = body.get("dataSharingPolicy")
    if not isinstance(policy, dict):
        raise ValidationError("--policy-json must include dataSharingPolicy object or be the policy object")
    return body


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="data-sharing",
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


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_selector(*, operation: str, policy_id: str | None = None, namespace: str | None = None) -> dict[str, Any]:
    selector: dict[str, Any] = {"kind": "wix-data-sharing", "operation": operation}
    if policy_id:
        selector["data_sharing_policy_id"] = policy_id
    if namespace:
        selector["namespace"] = namespace
    return selector


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    proposed_changes: list[dict[str, Any]],
    destructive: bool,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high" if destructive else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": "Verify with the provider response and follow-up list/get command where useful."},
        "rollback": {"supported": False, "notes": "No automatic rollback is available for data sharing policy or connection changes."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
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


def _write_plan_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _write_receipt_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
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
        "changed": True,
        "verification": {"ok": True, "type": "provider-response", "response": response},
        "diff_applied": plan.get("proposed_changes") or [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _handle_write(
    *,
    ctx: dict[str, Any],
    auth_mode: str,
    headers: dict[str, str],
    method_id: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    plan: dict[str, Any],
    destructive: bool,
) -> int:
    requires_ack = destructive
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_id):
        out = {
            "ok": True,
            "dry_run": True,
            "method": method_id,
            "auth_mode": auth_mode,
            "plan": plan,
            "plan_out": _write_plan_if_needed(ctx, plan=plan),
        }
        ctx["audit"].write(f"{method_id}.plan", out)
        ctx["out"].emit(out)
        return 0

    loaded_plan = _load_plan(
        plan_in=ctx.get("plan_in"),
        expected_method=method_id,
        expected_selector=selector,
        ctx=ctx,
    )
    response = _request_json(
        method=request["method"],
        base_url=ctx["cfg"].base_url,
        path=request["path"],
        headers=headers,
        params=request.get("params"),
        json_body=request.get("body"),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(
        method=method_id,
        selector=selector,
        request=request,
        response=response,
        plan=loaded_plan,
        ctx=ctx,
    )
    out = {
        "ok": True,
        "dry_run": False,
        "method": method_id,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
        "receipt": receipt,
        "receipt_out": _write_receipt_if_needed(ctx, receipt=receipt),
    }
    ctx["audit"].write(f"{method_id}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_data_sharing_list_policies(args, ctx) -> int:
    method_id = "data-sharing.list-policies"
    try:
        headers, auth_mode = _resolve_auth(ctx=ctx)
        params: dict[str, Any] = {}
        if getattr(args, "data_collection_ids_json", None):
            data_collection_ids = _read_json_array(getattr(args, "data_collection_ids_json"), field="data-collection-ids-json")
            params["dataCollectionIds"] = data_collection_ids
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/data/v1/data-collection-sharing/policies",
            headers=headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": method_id, "auth_mode": auth_mode, "request": {"method": "GET", "path": "/data/v1/data-collection-sharing/policies", "params": params or None}, "response": payload}
        ctx["audit"].write(method_id, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_get_policy(args, ctx) -> int:
    method_id = "data-sharing.get-policy"
    try:
        policy_id = _coerce_required_text(getattr(args, "policy_id", None), field="policy-id")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/data/v1/data-collection-sharing/policies/{policy_id}"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": method_id, "auth_mode": auth_mode, "request": {"method": "GET", "path": path}, "response": payload}
        ctx["audit"].write(method_id, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_list_shared_collections(args, ctx) -> int:
    method_id = "data-sharing.list-shared-collections"
    try:
        headers, auth_mode = _resolve_auth(ctx=ctx)
        params = {}
        if getattr(args, "shared_with_current_site", None) is not None:
            params["sharedWithCurrentSite"] = bool(getattr(args, "shared_with_current_site"))
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/data/v1/data-collection-sharing/shared",
            headers=headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": method_id, "auth_mode": auth_mode, "request": {"method": "GET", "path": "/data/v1/data-collection-sharing/shared", "params": params or None}, "response": payload}
        ctx["audit"].write(method_id, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_create_policy(args, ctx) -> int:
    method_id = "data-sharing.create-policy"
    try:
        body = _maybe_wrap_policy(_read_json_arg(getattr(args, "policy_json", None), field="policy-json"))
        policy = body["dataSharingPolicy"]
        data_collection_id = _coerce_required_text(policy.get("dataCollectionId"), field="policy-json.dataSharingPolicy.dataCollectionId")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request = {"method": "POST", "path": "/data/v1/data-collection-sharing/policies", "body": body}
        selector = _build_selector(operation="create-policy", policy_id=data_collection_id)
        plan = _build_plan(
            method=method_id,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["cms-data-sharing-write", "policy-creates-cross-site-sharing-access"],
            proposed_changes=[{"operation": "create-data-sharing-policy", "data_collection_id": data_collection_id}],
            destructive=False,
        )
        return _handle_write(ctx=ctx, auth_mode=auth_mode, headers=headers, method_id=method_id, request=request, selector=selector, plan=plan, destructive=False)
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_update_policy(args, ctx) -> int:
    method_id = "data-sharing.update-policy"
    try:
        policy_id = _coerce_required_text(getattr(args, "policy_id", None), field="policy-id")
        body = _maybe_wrap_policy(_read_json_arg(getattr(args, "policy_json", None), field="policy-json"))
        body["dataSharingPolicy"]["id"] = policy_id
        headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/data/v1/data-collection-sharing/policies/{policy_id}"
        request = {"method": "POST", "path": path, "body": body}
        selector = _build_selector(operation="update-policy", policy_id=policy_id)
        plan = _build_plan(
            method=method_id,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["cms-data-sharing-write", "policy-filter-change-affects-connected-sites"],
            proposed_changes=[{"operation": "update-data-sharing-policy", "data_sharing_policy_id": policy_id}],
            destructive=False,
        )
        return _handle_write(ctx=ctx, auth_mode=auth_mode, headers=headers, method_id=method_id, request=request, selector=selector, plan=plan, destructive=False)
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_delete_policy(args, ctx) -> int:
    method_id = "data-sharing.delete-policy"
    try:
        policy_id = _coerce_required_text(getattr(args, "policy_id", None), field="policy-id")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/data/v1/data-collection-sharing/policies/{policy_id}"
        request = {"method": "DELETE", "path": path, "body": None}
        selector = _build_selector(operation="delete-policy", policy_id=policy_id)
        plan = _build_plan(
            method=method_id,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["cms-data-sharing-delete", "disconnects-all-associated-connections", "target-sites-lose-access"],
            proposed_changes=[{"operation": "delete-data-sharing-policy", "data_sharing_policy_id": policy_id}],
            destructive=True,
        )
        return _handle_write(ctx=ctx, auth_mode=auth_mode, headers=headers, method_id=method_id, request=request, selector=selector, plan=plan, destructive=True)
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_connect(args, ctx) -> int:
    method_id = "data-sharing.connect"
    try:
        body = _read_json_arg(getattr(args, "connection_json", None), field="connection-json")
        namespace = _coerce_required_text(body.get("namespace"), field="connection-json.namespace")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request = {"method": "POST", "path": "/data/v1/data-collection-sharing/connect-to-shared-collection", "body": body}
        selector = _build_selector(operation="connect-to-shared-collection", namespace=namespace)
        plan = _build_plan(
            method=method_id,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["cms-data-sharing-write", "adds-shared-collection-namespace"],
            proposed_changes=[{"operation": "connect-to-shared-collection", "namespace": namespace}],
            destructive=False,
        )
        return _handle_write(ctx=ctx, auth_mode=auth_mode, headers=headers, method_id=method_id, request=request, selector=selector, plan=plan, destructive=False)
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_data_sharing_disconnect(args, ctx) -> int:
    method_id = "data-sharing.disconnect"
    try:
        body = _read_json_arg(getattr(args, "connection_json", None), field="connection-json")
        namespace = _coerce_required_text(body.get("namespace"), field="connection-json.namespace")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request = {"method": "POST", "path": "/data/v1/data-collection-sharing/disconnect-from-shared-collection", "body": body}
        selector = _build_selector(operation="disconnect-from-shared-collection", namespace=namespace)
        plan = _build_plan(
            method=method_id,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_reasons=["cms-data-sharing-disconnect", "removes-local-shared-collection-view"],
            proposed_changes=[{"operation": "disconnect-from-shared-collection", "namespace": namespace}],
            destructive=True,
        )
        return _handle_write(ctx=ctx, auth_mode=auth_mode, headers=headers, method_id=method_id, request=request, selector=selector, plan=plan, destructive=True)
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)
