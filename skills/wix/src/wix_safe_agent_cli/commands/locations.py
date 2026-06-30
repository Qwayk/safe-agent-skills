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


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_query_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return value


def _coerce_location_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _resolve_locations_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="locations",
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


def _build_list_params(
    *,
    include_archived: bool,
    authorized_only: bool,
    limit: int | None,
    offset: int | None,
    sort_field: str | None,
    sort_order: str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if include_archived:
        params["includeArchived"] = True
    if authorized_only:
        params["filterAuthorizedLocationEntities"] = True
    if limit is not None:
        params["paging.limit"] = int(limit)
    if offset is not None:
        params["paging.offset"] = int(offset)
    if sort_field is not None:
        params["sort.fieldName"] = str(sort_field)
    if sort_order is not None:
        params["sort.order"] = str(sort_order)
    return params


def _coerce_query_payload_for_locations(*, query: dict[str, Any], authorized_only: bool) -> dict[str, Any]:
    payload = dict(query) if "query" in query or "filterAuthorizedLocationEntities" in query else {"query": dict(query)}
    if authorized_only:
        payload["filterAuthorizedLocationEntities"] = True
    return payload


def _extract_location(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    if "location" in payload:
        location = payload["location"]
        if isinstance(location, dict):
            return location
        raise ValidationError(f"{operation} response must include a location object in `location`")
    if "id" in payload and isinstance(payload.get("id"), (str, int)):
        return payload

    raise ValidationError(f"{operation} response did not include a location object")


def _extract_location_id(location: dict[str, Any], *, operation: str) -> str:
    location_id = location.get("id")
    if isinstance(location_id, str):
        value = location_id.strip()
        if value:
            return value
    if isinstance(location_id, int):
        return str(location_id)

    raise ValidationError(f"{operation} response is missing a usable location id")


def _get_location_by_id(*, location_id: str, base_url: str, auth_headers: dict[str, str], timeout_s: float, verbose: bool) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=base_url,
        path=f"/locations/v1/locations/{location_id}",
        headers=auth_headers,
        params=None,
        json_body=None,
        timeout_s=timeout_s,
        verbose=verbose,
    )
    return _extract_location(payload, operation="locations.get")


def _get_location_by_id_optional(
    *,
    location_id: str,
    base_url: str,
    auth_headers: dict[str, str],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any] | None:
    try:
        return _get_location_by_id(
            location_id=location_id,
            base_url=base_url,
            auth_headers=auth_headers,
            timeout_s=timeout_s,
            verbose=verbose,
        )
    except (ValidationError, SafetyError, RuntimeError):
        return None


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    requires_ack: bool = False,
) -> dict[str, Any]:
    preconditions: list[str] = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --apply and --yes",
    ]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")

    risk_reasons = ["wix-location-write"]
    if requires_ack:
        risk_reasons.append("irreversible")

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": "No rollback available."},
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="locations")


def _assert_plan_state_unchanged(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if not isinstance(before_state, dict):
        raise SafetyError("Refused: plan before_state missing")
    if before_state != current_state:
        raise SafetyError("Refused: location state changed since plan was created")


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
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _compare_expected_fields(*, expected: dict[str, Any], after: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    checks: list[dict[str, Any]] = []
    all_ok = True
    for field, expected_value in expected.items():
        actual_value = after.get(field) if isinstance(after, dict) else None
        check = {"field": field, "expected": expected_value, "actual": actual_value}
        checks.append(check)
        if actual_value != expected_value:
            all_ok = False

    return checks, all_ok


def cmd_locations_list(args, ctx) -> int:
    try:
        params = _build_list_params(
            include_archived=bool(getattr(args, "include_archived", False)),
            authorized_only=bool(getattr(args, "authorized_only", False)),
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            sort_field=getattr(args, "sort_field", None),
            sort_order=getattr(args, "sort_order", None),
        )

        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/locations/v1/locations",
            headers=auth_headers,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "locations.list",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/locations/v1/locations", "params": params},
            "response": payload,
        }
        ctx["audit"].write("locations.list", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.list"})
        return 1


def cmd_locations_query(args, ctx) -> int:
    try:
        query_body = _coerce_query_payload(getattr(args, "query_json", None), field="query-json")
        query_body = _coerce_query_payload_for_locations(
            query=query_body,
            authorized_only=bool(getattr(args, "authorized_only", False)),
        )

        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/locations/v1/locations/query",
            headers=auth_headers,
            params=None,
            json_body=query_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "locations.query",
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": "/locations/v1/locations/query", "body": query_body},
            "response": payload,
        }
        ctx["audit"].write("locations.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.query"})
        return 1


def cmd_locations_get(args, ctx) -> int:
    try:
        location_id = _coerce_text(getattr(args, "location_id", None), field="location-id")
        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)

        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/locations/v1/locations/{location_id}",
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "locations.get",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": f"/locations/v1/locations/{location_id}"},
            "response": payload,
        }
        ctx["audit"].write("locations.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.get"})
        return 1


def cmd_locations_create(args, ctx) -> int:
    try:
        location = _coerce_location_payload(getattr(args, "location_json", None), field="location-json")
        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)

        request: dict[str, Any] = {
            "method": "POST",
            "path": "/locations/v1/locations",
            "body": {"location": location},
        }
        selector = {"kind": "location", "operation": "create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="locations.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "location": location}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and re-read the created location",
                },
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "locations.create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.create",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else plan
        )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/locations/v1/locations",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_location = _extract_location(response, operation="locations.create")
        created_id = _extract_location_id(created_location, operation="locations.create")
        after_location = _get_location_by_id_optional(
            location_id=created_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        checks = [
            {"field": "response.location.id", "expected": created_id, "actual": created_location.get("id")},
        ]
        if after_location is None:
            checks.append({"field": "get-location.id", "expected": created_id, "actual": None})
            verification_ok = False
        else:
            checks.append({"field": "after.id", "expected": created_id, "actual": after_location.get("id")})
            verification_ok = after_location.get("id") == created_id

        verification = {
            "ok": bool(verification_ok),
            "type": "read-after-write",
            "path": f"/locations/v1/locations/{created_id}",
            "method": "GET",
            "before": {},
            "after": after_location,
            "checks": checks,
            "notes": "Create verification uses returned location.id and read-back get-location check.",
        }

        receipt = _build_receipt(
            method="locations.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "locations.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("locations.create.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "locations.create",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.create"})
        return 1


def cmd_locations_update(args, ctx) -> int:
    try:
        location_id = _coerce_text(getattr(args, "location_id", None), field="location-id")
        location = _coerce_location_payload(getattr(args, "location_json", None), field="location-json")
        payload_id = location.get("id")
        if payload_id is None:
            location["id"] = location_id
        elif str(payload_id).strip() != location_id:
            raise ValidationError("--location-json id does not match --location-id")

        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)
        before_state = _get_location_by_id(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        request: dict[str, Any] = {
            "method": "PUT",
            "path": f"/locations/v1/locations/{location_id}",
            "body": {"location": location},
        }
        selector = {"kind": "location", "operation": "update", "location_id": location_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="locations.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "location_id": location_id, "location": location}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Re-read location and verify all provided fields",
                },
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "locations.update",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.update",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else plan
        )
        _assert_plan_state_unchanged(plan=loaded_plan, current_state=before_state)

        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path=f"/locations/v1/locations/{location_id}",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _get_location_by_id(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        checks, fields_ok = _compare_expected_fields(expected=location, after=after_state)
        verification = {
            "ok": bool(fields_ok and after_state.get("id") == location_id),
            "type": "read-after-write",
            "path": f"/locations/v1/locations/{location_id}",
            "method": "GET",
            "before": before_state,
            "after": after_state,
            "checks": checks,
        }

        receipt = _build_receipt(
            method="locations.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "locations.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("locations.update.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "locations.update",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.update"})
        return 1


def cmd_locations_archive(args, ctx) -> int:
    try:
        location_id = _coerce_text(getattr(args, "location_id", None), field="location-id")
        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)

        before_state = _get_location_by_id(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        request: dict[str, Any] = {
            "method": "POST",
            "path": f"/locations/v1/locations/{location_id}/archive",
            "body": {},
        }
        selector = {"kind": "location", "operation": "archive", "location_id": location_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.archive",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="locations.archive",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "archive", "location_id": location_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Re-read location and verify archived=true",
                },
                requires_ack=True,
            )

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: locations.archive requires --ack-irreversible")

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "locations.archive",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.archive",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else plan
        )
        _assert_plan_state_unchanged(plan=loaded_plan, current_state=before_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/locations/v1/locations/{location_id}/archive",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _get_location_by_id_optional(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        archived_actual = False if after_state is None else bool(after_state.get("archived"))
        verification = {
            "ok": archived_actual is True,
            "type": "read-after-write",
            "path": f"/locations/v1/locations/{location_id}",
            "method": "GET",
            "before": before_state,
            "after": after_state,
            "checks": [{"field": "archived", "expected": True, "actual": after_state.get("archived") if isinstance(after_state, dict) else None}],
        }

        receipt = _build_receipt(
            method="locations.archive",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "locations.archive",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("locations.archive.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "locations.archive",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.archive"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.archive"})
        return 1


def cmd_locations_set_default(args, ctx) -> int:
    try:
        location_id = _coerce_text(getattr(args, "location_id", None), field="location-id")
        auth_headers, auth_mode = _resolve_locations_auth(ctx=ctx)

        before_state = _get_location_by_id(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        request: dict[str, Any] = {
            "method": "POST",
            "path": f"/locations/v1/locations/{location_id}/set-default",
            "body": {},
        }
        selector = {"kind": "location", "operation": "set-default", "location_id": location_id}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.set-default",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="locations.set-default",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "set-default", "location_id": location_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Re-read location and verify default=true",
                },
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "locations.set-default",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = (
            _load_plan(
                plan_in=str(plan_in),
                expected_method="locations.set-default",
                expected_selector=selector,
                ctx=ctx,
            )
            if plan_in
            else plan
        )
        _assert_plan_state_unchanged(plan=loaded_plan, current_state=before_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/locations/v1/locations/{location_id}/set-default",
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _get_location_by_id_optional(
            location_id=location_id,
            base_url=ctx["cfg"].base_url,
            auth_headers=auth_headers,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": bool(isinstance(after_state, dict) and bool(after_state.get("default")) is True),
            "type": "read-after-write",
            "path": f"/locations/v1/locations/{location_id}",
            "method": "GET",
            "before": before_state,
            "after": after_state,
            "checks": [{"field": "default", "expected": True, "actual": after_state.get("default") if isinstance(after_state, dict) else None}],
        }

        receipt = _build_receipt(
            method="locations.set-default",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "locations.set-default",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("locations.set-default.apply", {"receipt_out": out["receipt_out"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "locations.set-default",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "locations.set-default"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "locations.set-default"})
        return 1
