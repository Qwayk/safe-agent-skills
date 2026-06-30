from __future__ import annotations

import json
import re
import time
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


_DOMAIN_NAME_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
)
_VALID_RECORD_TYPES = {
    "A",
    "AAAA",
    "NS",
    "SOA",
    "CNAME",
    "MX",
    "TXT",
    "SPF",
    "SRV",
    "PTR",
    "NAPTR",
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _coerce_required_domain_name(raw: Any, *, field: str = "domain-name") -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")
    if value.startswith(".") or value.endswith("."):
        raise ValidationError(f"--{field} must not start or end with a dot")
    if not _DOMAIN_NAME_RE.fullmatch(value):
        raise ValidationError(f"--{field} must be a hostname with a TLD (for example, example.com)")
    return value


def _coerce_optional_bool(raw: Any, *, field: str) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be true or false")

    value = raw.strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValidationError(f"--{field} must be true or false")


def _parse_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if isinstance(raw, (dict, list)):
        return raw
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be valid JSON")
    text = raw.strip()
    if not text:
        raise ValidationError(f"Missing --{field}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"--{field} must be valid JSON") from exc


def _coerce_optional_json_array(raw: Any, *, field: str) -> list[dict[str, Any]] | None:
    if raw is None:
        return None
    parsed = _parse_json_arg(raw, field=field)
    if not isinstance(parsed, list):
        raise ValidationError(f"--{field} must be a JSON array")
    out: list[dict[str, Any]] = []
    for index, item in enumerate(parsed):
        out.append(_coerce_dns_record(item, field=f"{field}[{index}]"))
    return out


def _coerce_dns_record(raw: Any, *, field: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError(f"--{field} must contain JSON objects")

    record_type = str(raw.get("type") or "").strip().upper()
    if not record_type:
        raise ValidationError(f"{field}.type is required")
    if record_type == "UNKNOWN" or record_type not in _VALID_RECORD_TYPES:
        allowed = ", ".join(sorted(_VALID_RECORD_TYPES))
        raise ValidationError(f"{field}.type must be one of: {allowed}")

    host_name = raw.get("hostName")
    if not isinstance(host_name, str) or not host_name.strip():
        raise ValidationError(f"{field}.hostName is required")
    host_name_value = host_name.strip()
    if len(host_name_value) > 256:
        raise ValidationError(f"{field}.hostName must be 256 characters or fewer")

    values = raw.get("values")
    if not isinstance(values, list) or not values:
        raise ValidationError(f"{field}.values must be a non-empty JSON array")
    if len(values) > 50:
        raise ValidationError(f"{field}.values must contain at most 50 entries")

    normalized_values: list[str] = []
    for idx, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field}.values[{idx}] must be a non-empty string")
        candidate = value.strip()
        if len(candidate) > 1000:
            raise ValidationError(f"{field}.values[{idx}] must be 1000 characters or fewer")
        normalized_values.append(candidate)

    normalized: dict[str, Any] = {
        "type": record_type,
        "hostName": host_name_value,
        "values": normalized_values,
    }
    ttl = raw.get("ttl")
    if ttl is not None:
        if isinstance(ttl, bool) or not isinstance(ttl, int):
            raise ValidationError(f"{field}.ttl must be an integer")
        normalized["ttl"] = ttl
    return normalized


def _coerce_dns_zone_json(raw: Any) -> dict[str, Any]:
    parsed = _parse_json_arg(raw, field="dns-zone-json")
    if not isinstance(parsed, dict):
        raise ValidationError("--dns-zone-json must be a JSON object")

    domain_name = _coerce_required_domain_name(parsed.get("domainName"), field="dns-zone-json.domainName")
    records = parsed.get("records")
    if not isinstance(records, list):
        raise ValidationError("--dns-zone-json.records must be a JSON array")
    if len(records) < 2:
        raise ValidationError("--dns-zone-json.records must contain at least 2 records")
    if len(records) > 5000:
        raise ValidationError("--dns-zone-json.records must contain at most 5000 records")

    normalized_records = [
        _coerce_dns_record(item, field=f"dns-zone-json.records[{index}]") for index, item in enumerate(records)
    ]

    normalized: dict[str, Any] = {
        "domainName": domain_name,
        "records": normalized_records,
    }
    dnssec_enabled = parsed.get("dnssecEnabled")
    if dnssec_enabled is not None:
        if not isinstance(dnssec_enabled, bool):
            raise ValidationError("--dns-zone-json.dnssecEnabled must be true or false")
        normalized["dnssecEnabled"] = dnssec_enabled
    return normalized


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


def _resolve_domain_dns_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="domain-dns",
    )
    return auth["headers"], auth["mode"]


def _http_status_from_error(exc: RuntimeError) -> int | None:
    parts = str(exc).split()
    if len(parts) < 2 or parts[0] != "HTTP":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _extract_dns_zone(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    zone = payload.get("dnsZone")
    if not isinstance(zone, dict):
        raise ValidationError(f"{operation} response did not include a dnsZone object")
    return zone


def _build_get_request(path: str) -> dict[str, Any]:
    return {"method": "GET", "path": path}


def _build_selector(*, operation: str, domain_name: str) -> dict[str, Any]:
    return {"kind": "wix-domain-dns-zone", "operation": operation, "domain_name": domain_name}


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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool, command_label: str) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=command_label)


def _assert_reviewed_plan_gate(ctx: dict[str, Any], *, command_label: str) -> None:
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and bool(ctx.get("enforce_reviewed_plan")) and not ctx.get("plan_in"):
        raise SafetyError(
            f"Refused: {command_label} live apply requires a reviewed saved plan. "
            "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
        )


def _assert_live_ack(ctx: dict[str, Any], *, command_label: str) -> None:
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"Refused: {command_label} live apply requires --ack-irreversible")


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: Any,
    before_state_available: bool,
    risk_reasons: list[str],
    preconditions: list[str],
    state_capture_notes: str,
    proposed_changes: list[dict[str, Any]],
    verification_notes: str,
    recovery_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
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
        "state_capture": {
            "before_state_available": before_state_available,
            "notes": state_capture_notes,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "read-after-write",
            "notes": verification_notes,
        },
        "rollback": {
            "supported": False,
            "notes": recovery_notes,
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


def _assert_plan_state_matches(*, plan: dict[str, Any], current_state: Any, noun: str) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError(f"Refused: {noun} changed since the plan was created")


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
        "applied_at_utc": _utc_now(),
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


def _get_dns_zone_payload(*, domain_name: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/domains/v1/dns-zones/{domain_name}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _get_dns_zone_snapshot(
    *,
    domain_name: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
    allow_not_found: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, int | None]:
    try:
        payload = _get_dns_zone_payload(domain_name=domain_name, ctx=ctx, headers=headers)
        return payload, _extract_dns_zone(payload, operation="domain-dns.get-zone"), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if allow_not_found and status == 404:
            return None, None, 404
        raise


def _verify_zone_readback(
    *,
    domain_name: str,
    expected_dnssec_enabled: bool | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _get_dns_zone_payload(domain_name=domain_name, ctx=ctx, headers=headers)
    zone = _extract_dns_zone(payload, operation="domain-dns.verify")
    if str(zone.get("domainName") or "").strip() != domain_name:
        return {"ok": False, "reason": "Readback domainName did not match the target domain"}
    if expected_dnssec_enabled is not None and zone.get("dnssecEnabled") is not expected_dnssec_enabled:
        return {"ok": False, "reason": "Readback dnssecEnabled did not match the requested value"}
    return {
        "ok": True,
        "path": f"/domains/v1/dns-zones/{domain_name}",
        "response": payload,
    }


def _verify_zone_deleted(*, domain_name: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    _, _, status = _get_dns_zone_snapshot(
        domain_name=domain_name,
        ctx=ctx,
        headers=headers,
        allow_not_found=True,
    )
    if status == 404:
        return {
            "ok": True,
            "removed": True,
            "path": f"/domains/v1/dns-zones/{domain_name}",
            "notes": ["Readback returned 404 after delete."],
        }
    return {
        "ok": False,
        "removed": False,
        "reason": "DNS zone still exists after delete",
        "path": f"/domains/v1/dns-zones/{domain_name}",
    }


def cmd_domain_dns_get_zone(args, ctx) -> int:
    try:
        domain_name = _coerce_required_domain_name(getattr(args, "domain_name", None))
        headers, auth_mode = _resolve_domain_dns_auth(ctx=ctx)
        request_path = f"/domains/v1/dns-zones/{domain_name}"
        payload = _get_dns_zone_payload(domain_name=domain_name, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "domain-dns.get-zone",
            "auth_mode": auth_mode,
            "request": _build_get_request(request_path),
            "response": payload,
            "dnsZone": _extract_dns_zone(payload, operation="domain-dns.get-zone"),
        }
        ctx["audit"].write("domain-dns.get-zone", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_domain_dns_preview_zone(args, ctx) -> int:
    try:
        domain_name = _coerce_required_domain_name(getattr(args, "domain_name", None))
        headers, auth_mode = _resolve_domain_dns_auth(ctx=ctx)
        request_path = f"/domains/v1/dns-zones/{domain_name}/preview"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "domain-dns.preview-zone",
            "auth_mode": auth_mode,
            "request": _build_get_request(request_path),
            "response": payload,
            "dnsZone": _extract_dns_zone(payload, operation="domain-dns.preview-zone"),
        }
        ctx["audit"].write("domain-dns.preview-zone", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_domain_dns_create_zone(args, ctx) -> int:
    try:
        _assert_reviewed_plan_gate(ctx, command_label="domain-dns create-zone")
        dns_zone = _coerce_dns_zone_json(getattr(args, "dns_zone_json", None))
        domain_name = str(dns_zone["domainName"])
        headers, auth_mode = _resolve_domain_dns_auth(ctx=ctx)
        before_payload, before_zone, before_status = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=True,
        )

        request_body = {"dnsZone": dns_zone}
        selector = _build_selector(operation="create", domain_name=domain_name)
        request = {"method": "POST", "path": "/domains/v1/dns-zones", "body": request_body}
        replaces_existing_zone = before_zone is not None
        if before_status == 404:
            state_capture_notes = "No existing DNS zone was found before planning."
            recovery_notes = "No prior DNS zone snapshot exists. Recovery would require manual zone creation."
        else:
            state_capture_notes = "Captured the current DNS zone before planning the create-or-replace action."
            recovery_notes = "Rollback is not automated. Manual recovery would require recreating the prior DNS zone from the saved snapshot."
        risk_reasons = ["domain-dns-write", "account-level-api-key"]
        if replaces_existing_zone:
            risk_reasons.append("existing-zone-replaced")
            _assert_live_ack(ctx, command_label="domain-dns create-zone")
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="domain-dns.create-zone",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="domain-dns.create-zone",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=before_payload is not None,
                risk_reasons=risk_reasons,
                preconditions=[
                    "env_fingerprint must match",
                    "selector must match",
                    "live apply requires --plan-in --apply --yes",
                    "live apply also requires --ack-irreversible when replacing an existing DNS zone",
                ],
                state_capture_notes=state_capture_notes,
                proposed_changes=[{"operation": "create-zone", "domainName": domain_name}],
                verification_notes="Verify by rereading the DNS zone after apply.",
                recovery_notes=recovery_notes,
            )

        should_apply = _should_apply(
            ctx,
            requires_ack=replaces_existing_zone,
            command_label="domain-dns create-zone",
        )
        if not should_apply:
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "domain-dns.create-zone",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("domain-dns.create-zone.dry-run", out)
            ctx["out"].emit(out)
            return 0

        current_payload, _, _ = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=True,
        )
        _assert_plan_state_matches(plan=plan, current_state=current_payload, noun="DNS zone")
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/domains/v1/dns-zones",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_zone_readback(
            domain_name=domain_name,
            expected_dnssec_enabled=dns_zone.get("dnssecEnabled") if "dnssecEnabled" in dns_zone else None,
            ctx=ctx,
            headers=headers,
        )
        receipt = _build_receipt(
            method="domain-dns.create-zone",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "domain-dns.create-zone",
            "auth_mode": auth_mode,
            "response": response,
            "verification": verification,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("domain-dns.create-zone.apply", out)
        ctx["out"].emit(out)
        return 0
    except (SafetyError, ValidationError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_domain_dns_update_zone(args, ctx) -> int:
    try:
        _assert_reviewed_plan_gate(ctx, command_label="domain-dns update-zone")
        domain_name = _coerce_required_domain_name(getattr(args, "domain_name", None))
        additions = _coerce_optional_json_array(getattr(args, "additions_json", None), field="additions-json")
        deletions = _coerce_optional_json_array(getattr(args, "deletions_json", None), field="deletions-json")
        dnssec_enabled = _coerce_optional_bool(getattr(args, "dnssec_enabled", None), field="dnssec-enabled")
        if additions is None and deletions is None and dnssec_enabled is None:
            raise ValidationError(
                "At least one of --additions-json, --deletions-json, or --dnssec-enabled is required"
            )

        headers, auth_mode = _resolve_domain_dns_auth(ctx=ctx)
        if deletions:
            _assert_live_ack(ctx, command_label="domain-dns update-zone")
        before_payload, before_zone, _ = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=False,
        )
        _ = before_zone

        request_body: dict[str, Any] = {}
        if additions is not None:
            request_body["additions"] = additions
        if deletions is not None:
            request_body["deletions"] = deletions
        if dnssec_enabled is not None:
            request_body["dnssecEnabled"] = dnssec_enabled

        selector = _build_selector(operation="update", domain_name=domain_name)
        request = {
            "method": "PATCH",
            "path": f"/domains/v1/dns-zones/{domain_name}",
            "body": request_body,
        }
        has_deletions = bool(deletions)
        risk_reasons = ["domain-dns-write", "account-level-api-key"]
        if additions:
            risk_reasons.append("dns-record-additions")
        if has_deletions:
            risk_reasons.append("dns-record-deletions")
        if dnssec_enabled is not None:
            risk_reasons.append("dnssec-setting-change")
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="domain-dns.update-zone",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="domain-dns.update-zone",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                risk_reasons=risk_reasons,
                preconditions=[
                    "env_fingerprint must match",
                    "selector must match",
                    "live apply requires --plan-in --apply --yes",
                    "live apply also requires --ack-irreversible when DNS record deletions are requested",
                ],
                state_capture_notes="Captured the current DNS zone before planning DNS additions, deletions, or DNSSEC changes.",
                proposed_changes=[{"operation": "update-zone", "domainName": domain_name}],
                verification_notes="Verify by rereading the DNS zone after apply.",
                recovery_notes="Rollback is not automated. Manual recovery would require another explicit DNS zone update using the saved before-state snapshot.",
            )

        should_apply = _should_apply(
            ctx,
            requires_ack=has_deletions,
            command_label="domain-dns update-zone",
        )
        if not should_apply:
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "domain-dns.update-zone",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("domain-dns.update-zone.dry-run", out)
            ctx["out"].emit(out)
            return 0

        current_payload, _, _ = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=False,
        )
        _assert_plan_state_matches(plan=plan, current_state=current_payload, noun="DNS zone")
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/domains/v1/dns-zones/{domain_name}",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_zone_readback(
            domain_name=domain_name,
            expected_dnssec_enabled=dnssec_enabled,
            ctx=ctx,
            headers=headers,
        )
        receipt = _build_receipt(
            method="domain-dns.update-zone",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "domain-dns.update-zone",
            "auth_mode": auth_mode,
            "response": response,
            "verification": verification,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("domain-dns.update-zone.apply", out)
        ctx["out"].emit(out)
        return 0
    except (SafetyError, ValidationError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_domain_dns_delete_zone(args, ctx) -> int:
    try:
        _assert_reviewed_plan_gate(ctx, command_label="domain-dns delete-zone")
        _assert_live_ack(ctx, command_label="domain-dns delete-zone")
        domain_name = _coerce_required_domain_name(getattr(args, "domain_name", None))
        headers, auth_mode = _resolve_domain_dns_auth(ctx=ctx)
        before_payload, _, _ = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=False,
        )
        selector = _build_selector(operation="delete", domain_name=domain_name)
        request = {"method": "DELETE", "path": f"/domains/v1/dns-zones/{domain_name}"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="domain-dns.delete-zone",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="domain-dns.delete-zone",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                before_state_available=True,
                risk_reasons=["domain-dns-write", "account-level-api-key", "dns-zone-delete"],
                preconditions=[
                    "env_fingerprint must match",
                    "selector must match",
                    "live apply requires --plan-in --apply --yes --ack-irreversible",
                ],
                state_capture_notes="Captured the current DNS zone before planning deletion.",
                proposed_changes=[{"operation": "delete-zone", "domainName": domain_name}],
                verification_notes="Verify by rereading the DNS zone and expecting 404 after apply.",
                recovery_notes="Rollback is not automated. Manual recovery would require recreating the DNS zone from the saved snapshot.",
            )

        should_apply = _should_apply(
            ctx,
            requires_ack=True,
            command_label="domain-dns delete-zone",
        )
        if not should_apply:
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "domain-dns.delete-zone",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("domain-dns.delete-zone.dry-run", out)
            ctx["out"].emit(out)
            return 0

        current_payload, _, _ = _get_dns_zone_snapshot(
            domain_name=domain_name,
            ctx=ctx,
            headers=headers,
            allow_not_found=False,
        )
        _assert_plan_state_matches(plan=plan, current_state=current_payload, noun="DNS zone")
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/domains/v1/dns-zones/{domain_name}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_zone_deleted(domain_name=domain_name, ctx=ctx, headers=headers)
        receipt = _build_receipt(
            method="domain-dns.delete-zone",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "domain-dns.delete-zone",
            "auth_mode": auth_mode,
            "response": response,
            "verification": verification,
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("domain-dns.delete-zone.apply", out)
        ctx["out"].emit(out)
        return 0
    except (SafetyError, ValidationError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
