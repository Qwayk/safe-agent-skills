from __future__ import annotations

import time
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


def _coerce_required_connected_domain_id(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --connected-domain-id")
    if not isinstance(raw, str):
        raise ValidationError("--connected-domain-id must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("--connected-domain-id cannot be empty")
    if "." not in value:
        raise ValidationError("--connected-domain-id must include a TLD (for example, example.com)")
    if value.startswith(".") or value.endswith("."):
        raise ValidationError("--connected-domain-id must not start or end with a dot")
    return value


def _coerce_required_domain(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --domain")
    if not isinstance(raw, str):
        raise ValidationError("--domain must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("Missing --domain")
    if "." not in value:
        raise ValidationError("--domain must include a TLD (for example, example.com)")
    if value.startswith(".") or value.endswith("."):
        raise ValidationError("--domain must not start or end with a dot")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")
    return value


def _coerce_optional_connection_type(raw: Any) -> str | None:
    value = _coerce_optional_text(raw, field="connection-type")
    if value is None:
        return None
    normalized = value.upper()
    if normalized not in {"POINTING", "NAMESERVERS", "HIDDEN"}:
        raise ValidationError("--connection-type must be POINTING, NAMESERVERS, or HIDDEN")
    return normalized


def _coerce_optional_assignment_type(raw: Any) -> str | None:
    value = _coerce_optional_text(raw, field="assignment-type")
    if value is None:
        return None
    normalized = value.upper()
    if normalized not in {"PRIMARY", "REDIRECT"}:
        raise ValidationError("--assignment-type must be PRIMARY or REDIRECT")
    return normalized


def _coerce_int_in_range(raw: Any, *, field: str, minimum: int, maximum: int) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise ValidationError(f"--{field} must be an integer")
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValidationError(f"--{field} must be an integer")
        try:
            value = int(text)
        except ValueError as exc:
            raise ValidationError(f"--{field} must be an integer") from exc
    else:
        raise ValidationError(f"--{field} must be an integer")
    if value < minimum or value > maximum:
        raise ValidationError(f"--{field} must be between {minimum} and {maximum}")
    return value


def _build_list_params(*, cursor: str | None, limit: int | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = int(limit)
    return params


def _build_site_query_body(*, site_id: str) -> dict[str, Any]:
    return {"query": {"filter": {"id": site_id}, "cursorPaging": {"limit": 1}}}


def _http_status_from_error(exc: RuntimeError) -> int | None:
    parts = str(exc).split()
    if len(parts) < 2 or parts[0] != "HTTP":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


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


def _query_site_snapshot(*, site_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/site-list/v2/sites/query",
        headers=headers,
        params=None,
        json_body=_build_site_query_body(site_id=site_id),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    sites = payload.get("sites")
    if not isinstance(sites, list):
        raise ValidationError("Site preflight returned invalid payload")
    for item in sites:
        if not isinstance(item, dict):
            continue
        candidate = str(item.get("id") or "").strip()
        if candidate == site_id:
            return item
    raise SafetyError(f"Refused: target site not found: {site_id}")


def _get_connected_domain_payload(
    *,
    connected_domain_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/domains/v1/connected-domains/{connected_domain_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _get_connected_domain_snapshot(
    *,
    connected_domain_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
    allow_not_found: bool,
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        payload = _get_connected_domain_payload(connected_domain_id=connected_domain_id, ctx=ctx, headers=headers)
        connected_domain = payload.get("connectedDomain")
        if not isinstance(connected_domain, dict):
            raise ValidationError("Connected domain readback returned no connectedDomain object")
        return connected_domain, None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if allow_not_found and status == 404:
            return None, 404
        raise


def _build_create_body(
    *,
    domain: str,
    connection_type: str | None,
    assignment_type: str | None,
    suppress_notifications: bool,
) -> dict[str, Any]:
    connected_domain: dict[str, Any] = {"domain": domain}
    if connection_type is not None:
        connected_domain["connectionType"] = connection_type
    if assignment_type is not None:
        connected_domain["siteInfo"] = {"assignmentType": assignment_type}
    if suppress_notifications:
        connected_domain["suppressNotifications"] = True
    return {"connectedDomain": connected_domain}


def _build_selector_create(*, domain: str, site_id: str) -> dict[str, Any]:
    return {"kind": "wix-connected-domain", "operation": "create", "domain": domain, "site_id": site_id}


def _build_selector_delete(*, connected_domain_id: str) -> dict[str, Any]:
    return {"kind": "wix-connected-domain", "operation": "delete", "connected_domain_id": connected_domain_id}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    baseline: dict[str, Any],
    risk_reasons: list[str],
    preconditions: list[str],
    verification_notes: str,
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
        "baseline": baseline,
        "proposed_changes": [selector],
        "verification_plan": {"type": "read-after-write", "notes": verification_notes},
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="connected-domains")


def _assert_no_connected_domain_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if before_state != current_state:
        raise SafetyError("Refused: connected domain changed since plan was created")


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


def _verify_create(
    *,
    domain: str,
    site_id: str,
    assignment_type: str | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _get_connected_domain_payload(connected_domain_id=domain, ctx=ctx, headers=headers)
    connected_domain = payload.get("connectedDomain")
    if not isinstance(connected_domain, dict):
        return {"ok": False, "reason": "Readback returned no connectedDomain object"}
    if str(connected_domain.get("id") or "") != domain and str(connected_domain.get("domain") or "") != domain:
        return {"ok": False, "reason": "Readback did not match the requested domain"}
    site_info = connected_domain.get("siteInfo")
    if isinstance(site_info, dict):
        returned_site_id = str(site_info.get("id") or "").strip()
        if returned_site_id and returned_site_id != site_id:
            return {"ok": False, "reason": "Readback siteInfo.id did not match --site-id"}
        returned_assignment_type = str(site_info.get("assignmentType") or "").strip().upper()
        if assignment_type is not None and returned_assignment_type and returned_assignment_type != assignment_type:
            return {"ok": False, "reason": "Readback assignmentType did not match the requested assignmentType"}
    return {
        "ok": True,
        "path": f"/domains/v1/connected-domains/{domain}",
        "response": payload,
        "notes": [
            "Readback confirms the connectedDomain object exists.",
            "This does not prove DNS propagation is complete; Wix docs say changes can take up to 48 hours.",
        ],
    }


def _verify_delete(*, connected_domain_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    _, status = _get_connected_domain_snapshot(
        connected_domain_id=connected_domain_id,
        ctx=ctx,
        headers=headers,
        allow_not_found=True,
    )
    if status == 404:
        return {
            "ok": True,
            "removed": True,
            "path": f"/domains/v1/connected-domains/{connected_domain_id}",
            "notes": [
                "Readback returned 404 after delete.",
                "Wix docs also note that deleting a PRIMARY domain can make the site fall back to its free Wix URL.",
            ],
        }
    return {
        "ok": False,
        "removed": False,
        "reason": "Connected domain still exists after delete",
        "path": f"/domains/v1/connected-domains/{connected_domain_id}",
    }


def cmd_connected_domains_list(args, ctx) -> int:
    try:
        cursor = _coerce_optional_text(getattr(args, "cursor", None), field="cursor")
        limit = _coerce_int_in_range(getattr(args, "limit", None), field="limit", minimum=1, maximum=100)

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="connected-domains",
        )

        params = _build_list_params(cursor=cursor, limit=limit)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/domains/v1/connected-domains",
            headers=auth["headers"],
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "connected_domains.list",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": "/domains/v1/connected-domains",
                "params": params,
            },
            "response": payload,
        }
        ctx["audit"].write("connected_domains.list", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_connected_domains_get(args, ctx) -> int:
    try:
        connected_domain_id = _coerce_required_connected_domain_id(getattr(args, "connected_domain_id", None))

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="connected-domains",
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/domains/v1/connected-domains/{connected_domain_id}",
            headers=auth["headers"],
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "connected_domains.get",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": f"/domains/v1/connected-domains/{connected_domain_id}",
            },
            "response": payload,
        }
        ctx["audit"].write("connected_domains.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_connected_domains_get_setup_info(args, ctx) -> int:
    try:
        connected_domain_id = _coerce_required_connected_domain_id(getattr(args, "connected_domain_id", None))

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="connected-domains",
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/domains/v1/connected-domain-setup-info/{connected_domain_id}",
            headers=auth["headers"],
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "connected_domains.get_setup_info",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": f"/domains/v1/connected-domain-setup-info/{connected_domain_id}",
            },
            "response": payload,
        }
        ctx["audit"].write("connected_domains.get_setup_info", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_connected_domains_create(args, ctx) -> int:
    try:
        domain = _coerce_required_domain(getattr(args, "domain", None))
        site_id = _coerce_required_text(getattr(args, "site_id", None), field="site-id")
        connection_type = _coerce_optional_connection_type(getattr(args, "connection_type", None))
        assignment_type = _coerce_optional_assignment_type(getattr(args, "assignment_type", None))
        suppress_notifications = bool(getattr(args, "suppress_notifications", False))

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="connected-domains",
        )
        auth_headers = auth["headers"]
        auth_mode = auth["mode"]

        site_snapshot = _query_site_snapshot(site_id=site_id, ctx=ctx, headers=auth_headers)
        existing_connected_domain, existing_status = _get_connected_domain_snapshot(
            connected_domain_id=domain,
            ctx=ctx,
            headers=auth_headers,
            allow_not_found=True,
        )
        if existing_status != 404:
            raise SafetyError(f"Refused: connected domain already exists: {domain}")

        body = _build_create_body(
            domain=domain,
            connection_type=connection_type,
            assignment_type=assignment_type,
            suppress_notifications=suppress_notifications,
        )
        request = {"method": "POST", "path": "/domains/v1/connected-domains", "body": body}
        selector = _build_selector_create(domain=domain, site_id=site_id)
        baseline = {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "site_snapshot": site_snapshot,
            "before_state": existing_connected_domain,
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="connected_domains.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="connected_domains.create",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline=baseline,
                risk_reasons=["connected-domain-create", "dns-side-effects"],
                preconditions=[
                    "env_fingerprint must match",
                    "selector must match",
                    "target site must exist",
                    "connected domain must not already exist",
                    "apply requires --apply and --yes",
                    "this tool requires --site-id and sends wix-site-id for deterministic targeting",
                    "external domains only; Wix docs say DNS propagation can take up to 48 hours",
                ],
                verification_notes=(
                    "Verify by reading the connected domain back. Readback confirms object creation, not completed DNS propagation."
                ),
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "connected_domains.create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = plan
        if plan_in:
            loaded_plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="connected_domains.create",
                expected_selector=selector,
                ctx=ctx,
            )
            live_site_snapshot = _query_site_snapshot(site_id=site_id, ctx=ctx, headers=auth_headers)
            live_connected_domain, live_status = _get_connected_domain_snapshot(
                connected_domain_id=domain,
                ctx=ctx,
                headers=auth_headers,
                allow_not_found=True,
            )
            if live_status != 404:
                raise SafetyError(f"Refused: connected domain already exists: {domain}")
            baseline = loaded_plan.get("baseline")
            if not isinstance(baseline, dict):
                raise SafetyError("Refused: plan baseline missing")
            if baseline.get("site_snapshot") != live_site_snapshot:
                raise SafetyError("Refused: target site changed since plan was created")
            if baseline.get("before_state") != live_connected_domain:
                raise SafetyError("Refused: connected domain state changed since plan was created")

        write_headers = dict(auth_headers)
        write_headers["wix-site-id"] = site_id
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/domains/v1/connected-domains",
            headers=write_headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_create(
            domain=domain,
            site_id=site_id,
            assignment_type=assignment_type,
            ctx=ctx,
            headers=auth_headers,
        )
        receipt = _build_receipt(
            method="connected_domains.create",
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
            "method": "connected_domains.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("connected_domains.create.apply", {"ok": out["ok"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not (bool(ctx.get("apply")) and bool(ctx.get("yes"))),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "connected_domains.create",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "connected_domains.create"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "connected_domains.create",
        }
        ctx["out"].emit(out)
        return 1


def cmd_connected_domains_delete(args, ctx) -> int:
    try:
        connected_domain_id = _coerce_required_connected_domain_id(getattr(args, "connected_domain_id", None))
        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: live connected domain delete requires --ack-irreversible")
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="connected-domains",
        )
        auth_headers = auth["headers"]
        auth_mode = auth["mode"]

        before_state, _ = _get_connected_domain_snapshot(
            connected_domain_id=connected_domain_id,
            ctx=ctx,
            headers=auth_headers,
            allow_not_found=False,
        )
        if before_state is None:
            raise SafetyError(f"Refused: connected domain not found: {connected_domain_id}")

        request = {"method": "DELETE", "path": f"/domains/v1/connected-domains/{connected_domain_id}"}
        selector = _build_selector_delete(connected_domain_id=connected_domain_id)
        baseline = {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="connected_domains.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="connected_domains.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline=baseline,
                risk_reasons=["connected-domain-delete", "dns-side-effects", "irreversible"],
                preconditions=[
                    "env_fingerprint must match",
                    "selector must match",
                    "connected domain must exist",
                    "apply requires --apply, --yes, and --ack-irreversible",
                    "deleting PRIMARY can make the site fall back to its free Wix URL",
                    "deleting a subdomain removes its CNAME from Google's Cloud DNS",
                ],
                verification_notes="Verify by reading the connected domain back and expecting 404.",
            )

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "connected_domains.delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = plan
        if plan_in:
            loaded_plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="connected_domains.delete",
                expected_selector=selector,
                ctx=ctx,
            )
            live_before_state, _ = _get_connected_domain_snapshot(
                connected_domain_id=connected_domain_id,
                ctx=ctx,
                headers=auth_headers,
                allow_not_found=False,
            )
            if live_before_state is None:
                raise SafetyError(f"Refused: connected domain not found: {connected_domain_id}")
            _assert_no_connected_domain_drift(plan=loaded_plan, current_state=live_before_state)

        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/domains/v1/connected-domains/{connected_domain_id}",
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_delete(connected_domain_id=connected_domain_id, ctx=ctx, headers=auth_headers)
        receipt = _build_receipt(
            method="connected_domains.delete",
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
            "method": "connected_domains.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("connected_domains.delete.apply", {"ok": out["ok"]})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not (bool(ctx.get("apply")) and bool(ctx.get("yes"))),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "connected_domains.delete",
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "connected_domains.delete"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "connected_domains.delete",
        }
        ctx["out"].emit(out)
        return 1
