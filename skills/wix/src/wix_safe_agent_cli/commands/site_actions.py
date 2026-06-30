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


def _coerce_site_ids(raw: Any, field: str) -> list[str]:
    ids = _read_json_arg(raw, field=field)
    if not isinstance(ids, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not ids:
        raise ValidationError(f"--{field} cannot be empty")
    if len(ids) > 20:
        raise ValidationError(f"--{field} supports at most 20 IDs")

    seen: set[str] = set()
    normalized: list[str] = []
    for i, raw_id in enumerate(ids):
        if not isinstance(raw_id, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        site_id = raw_id.strip()
        if not site_id:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if site_id in seen:
            raise ValidationError(f"--{field} contains duplicate site id: {site_id}")
        seen.add(site_id)
        normalized.append(site_id)
    return normalized


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _resolve_site_actions_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="site-actions",
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


def _build_site_query_body(*, ids: list[str]) -> dict[str, Any]:
    return {
        "query": {
            "filter": {"id": {"$in": ids}},
            "cursorPaging": {"limit": len(ids)},
        }
    }


def _query_sites_preflight(*, ids: list[str], ctx: dict[str, Any], headers: dict[str, str]) -> list[dict[str, Any]]:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/site-list/v2/sites/query",
        headers=headers,
        params=None,
        json_body=_build_site_query_body(ids=ids),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    sites = payload.get("sites")
    if not isinstance(sites, list):
        raise ValidationError("Site preflight returned invalid payload")

    return [site for site in sites if isinstance(site, dict)]


def _index_sites_by_id(*, sites: list[dict[str, Any]], expected_ids: list[str]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for site in sites:
        site_id = str(site.get("id") or "").strip()
        if site_id:
            index[site_id] = site

    missing: list[str] = [site_id for site_id in expected_ids if site_id not in index]
    if missing:
        raise SafetyError(f"Refused: requested site ids not found: {', '.join(missing)}")
    return index


def _snapshot_for_state(*, sites: list[dict[str, Any]], site_ids: list[str]) -> dict[str, Any]:
    index = _index_sites_by_id(sites=sites, expected_ids=site_ids)
    return {site_id: index[site_id] for site_id in site_ids}


def _build_selector(*, site_ids: list[str]) -> dict[str, Any]:
    return {
        "kind": "wix-site",
        "operation": "bulk-delete",
        "site_ids": site_ids,
    }


def _build_duplicate_selector(*, source_site_id: str, site_display_name: str) -> dict[str, Any]:
    return {
        "kind": "wix-site",
        "operation": "duplicate",
        "source_site_id": source_site_id,
        "site_display_name": site_display_name,
    }


def _build_publish_selector(*, site_id: str) -> dict[str, Any]:
    return {
        "kind": "wix-site",
        "operation": "publish",
        "site_id": site_id,
    }


def _build_plan(*, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], before_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.bulk-delete",
        "risk_level": "high",
        "risk_reasons": ["site-bulk-delete", "irreversible"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "sites must exist",
            "apply requires --apply, --yes, and --ack-irreversible",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "proposed_changes": [{"operation": "bulk-delete", "site_ids": selector.get("site_ids", [])}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify bulk delete by checking results and bulkActionMetadata counts",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_duplicate_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.duplicate",
        "risk_level": "high",
        "risk_reasons": ["site-duplicate-partial-copy", "no-rollback"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "source site must exist",
            "duplicate is incomplete by design; store orders, contacts, invoices, some 3rd-party app settings, domain, and Premium capabilities are not fully carried over",
            "apply requires --apply and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "proposed_changes": [
            {
                "operation": "duplicate",
                "source_site_id": selector.get("source_site_id", ""),
                "site_display_name": selector.get("site_display_name", ""),
            }
        ],
        "verification_plan": {
            "type": "read-after-write",
            "notes": (
                "Verify by querying /site-list/v2/sites/query for the returned newSiteId to confirm the new site exists."
            ),
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_publish_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.publish",
        "risk_level": "high",
        "risk_reasons": ["site-publish", "state-change"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "site must exist",
            "apply requires --apply and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "proposed_changes": [
            {
                "operation": "publish",
                "site_id": selector.get("site_id", ""),
            }
        ],
        "verification_plan": {
            "type": "read-after-write",
            "notes": "Verify by querying /site-list/v2/sites/query and checking published is true",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
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
        raise SafetyError("Refused: plan missing baseline")
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="site-actions")


def _assert_no_site_drift(*, plan: dict[str, Any], current_state: dict[str, dict[str, Any]]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if baseline_state != current_state:
        raise SafetyError("Refused: site state changed since plan was created")


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _verify_bulk_delete_response(*, response: dict[str, Any], expected_count: int) -> dict[str, Any]:
    results = response.get("results")
    if not isinstance(results, list):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Bulk delete response is missing results list",
            "response": response,
        }

    if len(results) != expected_count:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Bulk delete response results count does not match requested IDs",
            "requested_count": expected_count,
            "results_count": len(results),
            "response": response,
        }

    for i, result in enumerate(results):
        if not isinstance(result, dict):
            return {
                "ok": False,
                "type": "provider-response",
                "notes": f"Result #{i} is not an object",
                "result": result,
                "response": response,
            }
        item_metadata = result.get("itemMetadata")
        if not isinstance(item_metadata, dict):
            return {
                "ok": False,
                "type": "provider-response",
                "notes": "Result is missing itemMetadata",
                "result": result,
                "response": response,
            }
        if item_metadata.get("error") is not None:
            return {
                "ok": False,
                "type": "provider-response",
                "notes": "itemMetadata includes error",
                "result": result,
                "response": response,
            }
        item_success = item_metadata.get("success")
        if item_success is None:
            item_success = result.get("success")
        if not bool(item_success):
            return {
                "ok": False,
                "type": "provider-response",
                "notes": "Item delete was not successful",
                "result": result,
                "response": response,
            }

    metadata = response.get("bulkActionMetadata")
    if not isinstance(metadata, dict):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Bulk delete response is missing bulkActionMetadata",
            "response": response,
        }

    total_failures = _coerce_int(metadata.get("totalFailures"))
    total_successes = _coerce_int(metadata.get("totalSuccesses"))
    if total_failures is None or total_successes is None:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "bulkActionMetadata counts are not integers",
            "response": response,
        }

    if total_failures != 0:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Bulk action reported failures",
            "bulkActionMetadata": metadata,
            "response": response,
        }

    if total_successes + total_failures != expected_count:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Bulk action count summary does not match requested IDs",
            "bulkActionMetadata": metadata,
            "requested_count": expected_count,
            "response": response,
        }

    return {
        "ok": True,
        "type": "provider-response",
        "notes": "All requested sites were moved to trash",
        "response": response,
        "results_count": len(results),
        "totalSuccesses": total_successes,
        "totalFailures": total_failures,
    }


def _verify_duplicate_response(*, response: dict[str, Any], headers: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    new_site_id = str(response.get("newSiteId") or "").strip()
    if not new_site_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Duplicate response did not include a non-empty newSiteId",
            "response": response,
        }

    try:
        new_sites = _query_sites_preflight(ids=[new_site_id], ctx=ctx, headers=headers)
        new_site = _index_sites_by_id(sites=new_sites, expected_ids=[new_site_id]).get(new_site_id, {})
        return {
            "ok": True,
            "type": "read-after-write",
            "notes": "Verified duplicated site exists by querying /site-list/v2/sites/query",
            "newSiteId": new_site_id,
            "new_site": new_site,
        }
    except (SafetyError, ValidationError) as exc:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Failed to verify duplicated site exists after creation",
            "newSiteId": new_site_id,
            "error": str(exc),
            "response": response,
        }


def _verify_publish_response(
    *,
    response: dict[str, Any],
    headers: dict[str, str],
    ctx: dict[str, Any],
    site_id: str,
    before_state: dict[str, Any],
) -> dict[str, Any]:
    before_site = before_state.get(site_id)
    if not isinstance(before_site, dict):
        before_site = {}

    _ = response
    try:
        after_sites = _query_sites_preflight(ids=[site_id], ctx=ctx, headers=headers)
        after_state = _snapshot_for_state(sites=after_sites, site_ids=[site_id])
        after_site = after_state.get(site_id, {})
        if not bool(after_site.get("published")):
            return {
                "ok": False,
                "type": "read-after-write",
                "notes": "Publish request was accepted but site still reports published=false after publish action",
                "site_id": site_id,
                "before": before_site,
                "after": after_site,
            }

        notes = "Verified site reports published=true after publish action."
        if before_site.get("published") is True:
            notes = (
                "Verified site reports published=true after publish action. "
                "The site was already published before, so draft-delta changes were not validated."
            )
        return {
            "ok": True,
            "type": "read-after-write",
            "notes": notes,
            "site_id": site_id,
            "before": before_site,
            "after": after_site,
        }
    except (SafetyError, ValidationError) as exc:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Failed to verify published flag after publish action",
            "site_id": site_id,
            "error": str(exc),
            "response": response,
        }


def _build_receipt(
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
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.bulk-delete",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _build_duplicate_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    changed = bool(verification.get("ok"))
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.duplicate",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": changed,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _build_publish_receipt(
    *,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    before_site: dict[str, Any] = {}
    baseline = plan.get("baseline")
    if isinstance(baseline, dict):
        baseline_before = baseline.get("before_state")
        if isinstance(baseline_before, dict):
            site_id = selector.get("site_id")
            if isinstance(site_id, str):
                candidate = baseline_before.get(site_id)
                if isinstance(candidate, dict):
                    before_site = candidate

    changed = bool(verification.get("ok")) and not bool(before_site.get("published"))
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "site-actions.publish",
        "selector": selector,
        "request": request,
        "response": response,
        "changed": changed,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_site_actions_bulk_delete(args, ctx) -> int:
    try:
        site_ids = _coerce_site_ids(getattr(args, "site_ids_json", None), field="site-ids-json")
        auth_headers, auth_mode = _resolve_site_actions_auth(ctx=ctx)

        preflight_sites = _query_sites_preflight(ids=site_ids, ctx=ctx, headers=auth_headers)
        preflight_state = _snapshot_for_state(sites=preflight_sites, site_ids=site_ids)

        request = {
            "method": "POST",
            "path": "/site-actions/v1/bulk/sites/delete",
            "body": {"ids": site_ids},
        }
        selector = _build_selector(site_ids=site_ids)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="site-actions.bulk-delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(request=request, selector=selector, ctx=ctx, before_state=preflight_state)

        if not _should_apply(ctx, requires_ack=True):
            if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
                raise SafetyError("Refused: live bulk delete requires --ack-irreversible")
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-actions.bulk-delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="site-actions.bulk-delete",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        live_sites = _query_sites_preflight(ids=site_ids, ctx=ctx, headers=auth_headers)
        live_state = _snapshot_for_state(sites=live_sites, site_ids=site_ids)
        if plan_in:
            _assert_no_site_drift(plan=loaded_plan, current_state=live_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-actions/v1/bulk/sites/delete",
            headers=auth_headers,
            params=None,
            json_body={"ids": site_ids},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = _verify_bulk_delete_response(response=response, expected_count=len(site_ids))
        receipt = _build_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-actions.bulk-delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-actions.bulk-delete",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "site-actions.bulk-delete",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-actions.bulk-delete",
        }
        ctx["out"].emit(out)
        return 1


def cmd_site_actions_duplicate(args, ctx) -> int:
    try:
        source_site_id = _coerce_non_empty_text(getattr(args, "source_site_id", None), field="source-site-id")
        site_display_name = _coerce_non_empty_text(
            getattr(args, "site_display_name", None),
            field="site-display-name",
        )
        auth_headers, auth_mode = _resolve_site_actions_auth(ctx=ctx)

        preflight_sites = _query_sites_preflight(ids=[source_site_id], ctx=ctx, headers=auth_headers)
        preflight_state = _snapshot_for_state(sites=preflight_sites, site_ids=[source_site_id])

        request = {
            "method": "POST",
            "path": "/site-actions/v1/sites/duplicate",
            "body": {
                "sourceSiteId": source_site_id,
                "siteDisplayName": site_display_name,
            },
        }
        selector = _build_duplicate_selector(
            source_site_id=source_site_id,
            site_display_name=site_display_name,
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="site-actions.duplicate",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_duplicate_plan(request=request, selector=selector, ctx=ctx, before_state=preflight_state)

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-actions.duplicate",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="site-actions.duplicate",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        live_sites = _query_sites_preflight(ids=[source_site_id], ctx=ctx, headers=auth_headers)
        live_state = _snapshot_for_state(sites=live_sites, site_ids=[source_site_id])
        if plan_in:
            _assert_no_site_drift(plan=loaded_plan, current_state=live_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-actions/v1/sites/duplicate",
            headers=auth_headers,
            params=None,
            json_body={"sourceSiteId": source_site_id, "siteDisplayName": site_display_name},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        if not str(response.get("newSiteId") or "").strip():
            raise ValidationError("Duplicate response did not include newSiteId")

        verification = _verify_duplicate_response(response=response, headers=auth_headers, ctx=ctx)
        receipt = _build_duplicate_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-actions.duplicate",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-actions.duplicate",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "site-actions.duplicate",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-actions.duplicate",
        }
        ctx["out"].emit(out)
        return 1


def cmd_site_actions_publish(args, ctx) -> int:
    try:
        site_id = _coerce_non_empty_text(getattr(args, "site_id", None), field="site-id")
        auth_headers, auth_mode = _resolve_site_actions_auth(ctx=ctx)

        preflight_sites = _query_sites_preflight(ids=[site_id], ctx=ctx, headers=auth_headers)
        preflight_state = _snapshot_for_state(sites=preflight_sites, site_ids=[site_id])

        request = {
            "method": "POST",
            "path": "/site-publisher/v1/site/publish",
            "body": {},
        }
        selector = _build_publish_selector(site_id=site_id)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="site-actions.publish",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_publish_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=preflight_state,
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "site-actions.publish",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="site-actions.publish",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        live_sites = _query_sites_preflight(ids=[site_id], ctx=ctx, headers=auth_headers)
        live_state = _snapshot_for_state(sites=live_sites, site_ids=[site_id])
        if plan_in:
            _assert_no_site_drift(plan=loaded_plan, current_state=live_state)

        publish_headers = dict(auth_headers)
        if auth_mode == "account_api_key":
            publish_headers.pop("wix-account-id", None)
            publish_headers["wix-site-id"] = site_id

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/site-publisher/v1/site/publish",
            headers=publish_headers,
            params=None,
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = _verify_publish_response(
            response=response,
            headers=auth_headers,
            ctx=ctx,
            site_id=site_id,
            before_state=preflight_state,
        )
        receipt = _build_publish_receipt(
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "site-actions.publish",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "site-actions.publish",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "site-actions.publish",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-actions.publish",
        }
        ctx["out"].emit(out)
        return 1
