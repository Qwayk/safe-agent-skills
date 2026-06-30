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
        return None
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


def _read_policy_ids(raw: Any) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field="policy-ids-json")
    if not isinstance(value, list):
        raise ValidationError("--policy-ids-json must be a JSON array")
    if not value:
        raise ValidationError("--policy-ids-json cannot be an empty array")

    policy_ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--policy-ids-json[{index}] must be a string")
        policy_id = item.strip()
        if not policy_id:
            raise ValidationError(f"--policy-ids-json[{index}] cannot be empty")
        policy_ids.append(policy_id)
    return policy_ids


def _read_role_ids(raw: Any) -> list[str]:
    value = _read_json_arg(raw, field="role-ids-json")
    if not isinstance(value, list):
        raise ValidationError("--role-ids-json must be a JSON array")
    if not value:
        raise ValidationError("--role-ids-json cannot be an empty array")

    role_ids: list[str] = []
    seen_role_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--role-ids-json[{index}] must be a string")
        role_id = item.strip()
        if not role_id:
            raise ValidationError(f"--role-ids-json[{index}] cannot be empty")
        if role_id in seen_role_ids:
            raise ValidationError("--role-ids-json cannot contain duplicate role IDs")
        seen_role_ids.add(role_id)
        role_ids.append(role_id)
    return role_ids


def _read_location_ids(raw: Any) -> list[str]:
    value = _read_json_arg(raw, field="location-ids-json")
    if not isinstance(value, list):
        raise ValidationError("--location-ids-json must be a JSON array")
    if not value:
        raise ValidationError("--location-ids-json cannot be an empty array")
    if len(value) > 20:
        raise ValidationError("--location-ids-json cannot contain more than 20 location IDs")

    location_ids: list[str] = []
    seen_location_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--location-ids-json[{index}] must be a string")
        location_id = item.strip()
        if not location_id:
            raise ValidationError(f"--location-ids-json[{index}] cannot be empty")
        if location_id in seen_location_ids:
            raise ValidationError("--location-ids-json cannot contain duplicate location IDs")
        seen_location_ids.add(location_id)
        location_ids.append(location_id)
    return location_ids


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")
    return value


def _build_params(*, policy_ids: list[str] | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if policy_ids is not None:
        params["filter.policyIds"] = policy_ids
    return params


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
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _contributor_headers(*, headers: dict[str, str], site_id: str | None = None) -> dict[str, str]:
    request_headers = dict(headers)
    if site_id:
        request_headers["wix-site-id"] = site_id
    return request_headers


def _query_contributors(
    *,
    ctx: dict[str, Any],
    headers: dict[str, str],
    policy_ids: list[str] | None = None,
) -> dict[str, Any]:
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/roles-management/v2/contributors/query",
        headers=headers,
        params=_build_params(policy_ids=policy_ids) or None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _contributors_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    contributors = payload.get("contributors")
    if not isinstance(contributors, list):
        raise ValidationError("Contributors query returned invalid payload")
    out: list[dict[str, Any]] = []
    for item in contributors:
        if isinstance(item, dict):
            out.append(item)
    return out


def _find_contributor(*, contributors: list[dict[str, Any]], account_id: str) -> dict[str, Any] | None:
    for contributor in contributors:
        if str(contributor.get("accountId") or "").strip() == account_id:
            return contributor
    return None


def _get_current_contributor(
    *,
    ctx: dict[str, Any],
    headers: dict[str, str],
    account_id: str,
    site_id: str,
) -> dict[str, Any]:
    payload = _query_contributors(ctx=ctx, headers=headers)
    contributors = _contributors_list(payload)
    contributor = _find_contributor(contributors=contributors, account_id=account_id)
    if contributor is None:
        raise SafetyError(f"Refused: accountId {account_id} is not currently present for site {site_id}")
    return {
        "site_id": site_id,
        "account_id": account_id,
        "contributors_count": len(contributors),
        "matched_contributor": contributor,
    }


def _build_remove_selector(*, account_id: str, site_id: str) -> dict[str, Any]:
    return {
        "kind": "wix-contributor",
        "operation": "remove",
        "account_id": account_id,
        "site_id": site_id,
    }


def _build_change_role_selector(*, account_id: str, site_id: str, role_ids: list[str]) -> dict[str, Any]:
    return {
        "kind": "wix-contributor",
        "operation": "change-role",
        "account_id": account_id,
        "site_id": site_id,
        "role_ids": role_ids,
    }


def _build_change_location_selector(*, account_id: str, site_id: str, location_ids: list[str]) -> dict[str, Any]:
    return {
        "kind": "wix-contributor",
        "operation": "change-contributor-location",
        "account_id": account_id,
        "site_id": site_id,
        "location_ids": location_ids,
    }


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_remove_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    baseline: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.remove",
        "risk_level": "high",
        "risk_reasons": ["site-contributor-removal", "irreversible"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "target contributor must currently exist on the site",
            "apply requires --apply, --yes, and --ack-irreversible",
            "this tool requires --site-id and reuses wix-site-id on the write and verification requests",
        ],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": [{"operation": "remove-contributor", "account_id": selector["account_id"]}],
        "verification_plan": {
            "type": "read-after-write",
            "notes": "Verify by rerunning contributors query for the same site and confirming the removed accountId no longer appears.",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_change_role_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    baseline: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.change-role",
        "risk_level": "high",
        "risk_reasons": ["site-contributor-role-replacement", "full-replace"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "target contributor must currently exist on the site",
            "role IDs must be supplied explicitly",
            "apply requires --apply and --yes",
            "this tool requires --site-id and reuses wix-site-id on the write and verification requests",
        ],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": [
            {
                "operation": "replace-contributor-roles",
                "account_id": selector["account_id"],
                "role_ids": selector["role_ids"],
            }
        ],
        "verification_plan": {
            "type": "provider-response-plus-readback",
            "notes": (
                "Verify provider newAssignedRoles matches the requested role IDs, then rerun "
                "contributors query for the same site context to confirm the account is still present. "
                "This is not a perfect full role-state proof."
            ),
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_change_location_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    baseline: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.change-contributor-location",
        "risk_level": "high",
        "risk_reasons": ["site-contributor-location-replacement", "full-replace"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "target contributor must currently exist on the site",
            "location IDs must be supplied explicitly",
            "apply requires --apply and --yes",
            "this tool requires --site-id and reuses wix-site-id on the write and verification requests",
        ],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": [
            {
                "operation": "replace-contributor-locations",
                "account_id": selector["account_id"],
                "location_ids": selector["location_ids"],
            }
        ],
        "verification_plan": {
            "type": "provider-response-plus-readback",
            "notes": (
                "Verify provider newAssignedLocations contains the requested location IDs, then rerun "
                "contributors query for the same site context to confirm the account is still present. "
                "This is not a perfect full location-state proof."
            ),
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _load_remove_plan(
    *,
    plan_in: str | None,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != "contributors.remove":
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _load_change_role_plan(
    *,
    plan_in: str | None,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != "contributors.change-role":
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _load_change_location_plan(
    *,
    plan_in: str | None,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != "contributors.change-contributor-location":
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="contributors")


def _assert_remove_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: contributor state changed since plan was created")


def _assert_change_role_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: contributor state changed since plan was created")


def _assert_change_location_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: contributor state changed since plan was created")


def _build_remove_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.remove",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _build_change_role_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.change-role",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _build_change_location_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "contributors.change-contributor-location",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_contributors_query(args, ctx) -> int:
    try:
        policy_ids = _read_policy_ids(getattr(args, "policy_ids_json", None))
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="contributors",
        )
        request_path = "/roles-management/v2/contributors/query"
        params = _build_params(policy_ids=policy_ids)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contributors.query",
            "auth_mode": auth["mode"],
            "request": {"method": "GET", "path": request_path, "params": params},
            "response": payload,
        }
        ctx["audit"].write("contributors.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_contributors_remove(args, ctx) -> int:
    try:
        account_id = _coerce_required_text(getattr(args, "account_id", None), field="account-id")
        site_id = _coerce_required_text(getattr(args, "site_id", None), field="site-id")
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="contributors",
        )
        auth_headers = _contributor_headers(headers=auth["headers"], site_id=site_id)
        auth_mode = auth["mode"]

        before_state = _get_current_contributor(
            ctx=ctx,
            headers=auth_headers,
            account_id=account_id,
            site_id=site_id,
        )
        request = {
            "method": "POST",
            "path": "/roles-management/contributor/remove",
            "body": {"accountId": account_id},
        }
        selector = _build_remove_selector(account_id=account_id, site_id=site_id)
        baseline = {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_remove_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
        else:
            plan = _build_remove_plan(request=request, selector=selector, baseline=baseline, ctx=ctx)

        if not _should_apply(ctx, requires_ack=True):
            if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
                raise SafetyError("Refused: live contributor removal requires --ack-irreversible")
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contributors.remove",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = plan
        if plan_in:
            loaded_plan = _load_remove_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
            live_before_state = _get_current_contributor(
                ctx=ctx,
                headers=auth_headers,
                account_id=account_id,
                site_id=site_id,
            )
            _assert_remove_drift(plan=loaded_plan, current_state=live_before_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/roles-management/contributor/remove",
            headers=auth_headers,
            params=None,
            json_body={"accountId": account_id},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_payload = _query_contributors(ctx=ctx, headers=auth_headers)
        after_contributors = _contributors_list(after_payload)
        if _find_contributor(contributors=after_contributors, account_id=account_id) is not None:
            raise SafetyError(f"Refused: accountId {account_id} still appears after removal")

        verification = {
            "ok": True,
            "type": "read-after-write",
            "notes": "Readback confirms the removed accountId no longer appears in the contributor list for the same site context.",
            "site_id": site_id,
            "account_id": account_id,
            "before": before_state,
            "after": {
                "contributors_count": len(after_contributors),
                "contributors": after_contributors,
                "account_present": False,
            },
        }
        receipt = _build_remove_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": True,
            "dry_run": False,
            "method": "contributors.remove",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("contributors.remove.apply", {"ok": out["ok"]})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not (bool(ctx.get("apply")) and bool(ctx.get("yes"))),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "contributors.remove",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "contributors.remove",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "contributors.remove",
        }
        ctx["out"].emit(out)
        return 1


def cmd_contributors_change_role(args, ctx) -> int:
    try:
        account_id = _coerce_required_text(getattr(args, "account_id", None), field="account-id")
        site_id = _coerce_required_text(getattr(args, "site_id", None), field="site-id")
        role_ids = _read_role_ids(getattr(args, "role_ids_json", None))
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="contributors",
        )
        auth_headers = _contributor_headers(headers=auth["headers"], site_id=site_id)
        auth_mode = auth["mode"]

        before_state = _get_current_contributor(
            ctx=ctx,
            headers=auth_headers,
            account_id=account_id,
            site_id=site_id,
        )
        request = {
            "method": "PUT",
            "path": "/roles-management/contributor/change/role",
            "body": {
                "accountId": account_id,
                "newRoles": [{"roleId": role_id} for role_id in role_ids],
            },
        }
        selector = _build_change_role_selector(account_id=account_id, site_id=site_id, role_ids=role_ids)
        baseline = {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_change_role_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
        else:
            plan = _build_change_role_plan(request=request, selector=selector, baseline=baseline, ctx=ctx)

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contributors.change-role",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = plan
        if plan_in:
            loaded_plan = _load_change_role_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
            live_before_state = _get_current_contributor(
                ctx=ctx,
                headers=auth_headers,
                account_id=account_id,
                site_id=site_id,
            )
            _assert_change_role_drift(plan=loaded_plan, current_state=live_before_state)

        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path="/roles-management/contributor/change/role",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        new_assigned_roles = response.get("newAssignedRoles")
        if not isinstance(new_assigned_roles, list):
            raise SafetyError("Refused: contributor change-role response missing newAssignedRoles")
        returned_role_ids: list[str] = []
        for index, item in enumerate(new_assigned_roles):
            if not isinstance(item, dict):
                raise SafetyError(f"Refused: contributor change-role response newAssignedRoles[{index}] must be an object")
            role_id = str(item.get("roleId") or "").strip()
            if not role_id:
                raise SafetyError(f"Refused: contributor change-role response newAssignedRoles[{index}] is missing roleId")
            returned_role_ids.append(role_id)
        if sorted(returned_role_ids) != sorted(role_ids):
            raise SafetyError("Refused: provider newAssignedRoles did not match the requested role IDs")

        after_payload = _query_contributors(ctx=ctx, headers=auth_headers)
        after_contributors = _contributors_list(after_payload)
        matched_after = _find_contributor(contributors=after_contributors, account_id=account_id)
        if matched_after is None:
            raise SafetyError(f"Refused: accountId {account_id} no longer appears after role change")

        verification = {
            "ok": True,
            "type": "provider-response-plus-readback",
            "notes": (
                "Readback confirms the account is still present for the same site context, after "
                "the provider response returned newAssignedRoles matching the requested role IDs. "
                "This is not a perfect full role-state proof."
            ),
            "site_id": site_id,
            "account_id": account_id,
            "requested_role_ids": role_ids,
            "provider_new_assigned_roles": new_assigned_roles,
            "before": before_state,
            "after": {
                "contributors_count": len(after_contributors),
                "contributors": after_contributors,
                "account_present": True,
                "matched_contributor": matched_after,
            },
        }
        receipt = _build_change_role_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": True,
            "dry_run": False,
            "method": "contributors.change-role",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("contributors.change-role.apply", {"ok": out["ok"]})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")) or not bool(ctx.get("yes")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "contributors.change-role",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "contributors.change-role",
        }
        ctx["out"].emit(out)
        return 1


def cmd_contributors_change_contributor_location(args, ctx) -> int:
    try:
        account_id = _coerce_required_text(getattr(args, "account_id", None), field="account-id")
        site_id = _coerce_required_text(getattr(args, "site_id", None), field="site-id")
        location_ids = _read_location_ids(getattr(args, "location_ids_json", None))
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="contributors",
        )
        auth_headers = _contributor_headers(headers=auth["headers"], site_id=site_id)
        auth_mode = auth["mode"]

        before_state = _get_current_contributor(
            ctx=ctx,
            headers=auth_headers,
            account_id=account_id,
            site_id=site_id,
        )
        request = {
            "method": "PUT",
            "path": "/roles-management/contributor/change/locations",
            "body": {
                "accountId": account_id,
                "newLocations": list(location_ids),
            },
        }
        selector = _build_change_location_selector(
            account_id=account_id,
            site_id=site_id,
            location_ids=location_ids,
        )
        baseline = {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_change_location_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
        else:
            plan = _build_change_location_plan(request=request, selector=selector, baseline=baseline, ctx=ctx)

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contributors.change-contributor-location",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = plan
        if plan_in:
            loaded_plan = _load_change_location_plan(plan_in=str(plan_in), expected_selector=selector, ctx=ctx)
            live_before_state = _get_current_contributor(
                ctx=ctx,
                headers=auth_headers,
                account_id=account_id,
                site_id=site_id,
            )
            _assert_change_location_drift(plan=loaded_plan, current_state=live_before_state)

        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path="/roles-management/contributor/change/locations",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        new_assigned_locations = response.get("newAssignedLocations")
        if not isinstance(new_assigned_locations, list):
            raise SafetyError("Refused: contributor change-contributor-location response missing newAssignedLocations")

        provider_location_ids: set[str] = set()
        for index, item in enumerate(new_assigned_locations):
            if not isinstance(item, dict):
                raise SafetyError(
                    "Refused: contributor change-contributor-location response "
                    f"newAssignedLocations[{index}] must be an object"
                )
            item_location_ids = item.get("locationIds")
            if not isinstance(item_location_ids, list):
                raise SafetyError(
                    "Refused: contributor change-contributor-location response "
                    f"newAssignedLocations[{index}].locationIds must be an array"
                )
            for location_index, raw_location_id in enumerate(item_location_ids):
                if not isinstance(raw_location_id, str):
                    raise SafetyError(
                        "Refused: contributor change-contributor-location response "
                        f"newAssignedLocations[{index}].locationIds[{location_index}] must be a string"
                    )
                provider_location_id = raw_location_id.strip()
                if not provider_location_id:
                    raise SafetyError(
                        "Refused: contributor change-contributor-location response "
                        f"newAssignedLocations[{index}].locationIds[{location_index}] cannot be empty"
                    )
                provider_location_ids.add(provider_location_id)

        if sorted(provider_location_ids) != sorted(location_ids):
            raise SafetyError("Refused: provider newAssignedLocations did not match the requested location IDs")

        after_payload = _query_contributors(ctx=ctx, headers=auth_headers)
        after_contributors = _contributors_list(after_payload)
        matched_after = _find_contributor(contributors=after_contributors, account_id=account_id)
        if matched_after is None:
            raise SafetyError(f"Refused: accountId {account_id} no longer appears after location change")

        verification = {
            "ok": True,
            "type": "provider-response-plus-readback",
            "notes": (
                "Readback confirms the account is still present for the same site context, after "
                "the provider response returned newAssignedLocations containing the requested "
                "location IDs. This is not a perfect full location-state proof."
            ),
            "site_id": site_id,
            "account_id": account_id,
            "requested_location_ids": location_ids,
            "provider_new_assigned_locations": new_assigned_locations,
            "before": before_state,
            "after": {
                "contributors_count": len(after_contributors),
                "contributors": after_contributors,
                "account_present": True,
                "matched_contributor": matched_after,
            },
        }
        receipt = _build_change_location_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": True,
            "dry_run": False,
            "method": "contributors.change-contributor-location",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("contributors.change-contributor-location.apply", {"ok": out["ok"]})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")) or not bool(ctx.get("yes")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "contributors.change-contributor-location",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "contributors.change-contributor-location",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "contributors.change-contributor-location",
        }
        ctx["out"].emit(out)
        return 1
