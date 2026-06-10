from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)
from ..state import get_default_account_id


def _resolve_account_id(args, ctx) -> str:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if account_id:
        return account_id
    default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
    if default:
        return default
    raise ValidationError(
        "Missing --account-id and no default is set. "
        "Run: cloudflare-api-tool accounts set-default --account-id <id>"
    )


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _require_apply(ctx) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError("Refusing to write: this command requires --apply (dry-run is the default).")


def _require_yes(ctx) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing to apply: Cloudflare API writes require --yes.")


def _base_plan(ctx: dict, *, selector: dict[str, Any], risk_level: str, risk_reasons: list[str]) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": list(risk_reasons),
        "preconditions": [
            "API token has least-privilege permissions needed for this action.",
            "Target identifiers are correct (account_id/zone_id/resource ids).",
            "Dry-run plan has been reviewed before applying.",
        ],
        "proposed_changes": [],
        "verification_plan": [],
        "notes": [],
    }


def _base_receipt(ctx: dict, *, selector: dict[str, Any]) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": False,
        "verification": {"ok": False, "details": {}},
        "diff_applied": [],
        "rollback_plan": {"supported": False, "notes": "Not implemented."},
        "notes": [],
    }


def _emit_plan(ctx: dict, *, command: str, plan: dict, extra: dict[str, Any] | None = None) -> int:
    _ = write_plan_if_requested(ctx, plan)
    ctx["audit"].write("plan", {"command": command, "selector": plan.get("selector"), "proposed_changes": plan.get("proposed_changes")})
    out = {"ok": True, "dry_run": True, "command": command, "plan": plan}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def _emit_receipt(ctx: dict, *, command: str, receipt: dict, extra: dict[str, Any] | None = None) -> int:
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write(
        "receipt",
        {
            "command": command,
            "selector": receipt.get("selector"),
            "changed": bool(receipt.get("changed")),
            "verification_ok": bool((receipt.get("verification") or {}).get("ok")),
        },
    )
    out = {"ok": True, "dry_run": False, "command": command, "changed": bool(receipt.get("changed")), "receipt": receipt}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def cmd_workers_routes_ensure(args, ctx) -> int:
    """
    Ensure a Workers route exists for a pattern -> script mapping.
    """
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    pattern = str(getattr(args, "pattern", "") or "").strip()
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not pattern:
        raise ValidationError("Missing --pattern")
    if not script_name:
        raise ValidationError("Missing --script-name")

    current = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes").result or []
    routes = current if isinstance(current, list) else [current]
    matches = [r for r in routes if isinstance(r, dict) and str(r.get("pattern") or "") == pattern]
    if len(matches) > 1:
        raise SafetyError(f"Ambiguous routes: multiple routes match pattern={pattern!r}. Refusing.")
    existing = matches[0] if matches else None

    action: str
    route_id: str | None = None
    if not existing:
        action = "create"
    else:
        route_id = str(existing.get("id") or "").strip() or None
        existing_script = str(existing.get("script") or "").strip()
        if existing_script == script_name:
            action = "no-op"
        else:
            if not route_id:
                raise SafetyError("Route match is missing an id; refusing to update.")
            action = "update"

    selector = {"zone_id": zone_id, "pattern": pattern, "script_name": script_name}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Worker routes can affect production traffic."],
    )
    if action == "create":
        plan["proposed_changes"] = [
            {
                "resource": "workers_route",
                "action": "create",
                "zone_id": zone_id,
                "pattern": pattern,
                "script_name": script_name,
            }
        ]
        plan["verification_plan"] = [
            "Re-fetch routes list and confirm a route exists with the same pattern and expected script_name.",
        ]
    elif action == "update":
        plan["proposed_changes"] = [
            {
                "resource": "workers_route",
                "action": "update",
                "zone_id": zone_id,
                "route_id": route_id,
                "pattern": pattern,
                "script_name": script_name,
            }
        ]
        plan["verification_plan"] = [
            "Re-fetch routes list and confirm the route for this pattern now points to the expected script_name.",
        ]
    else:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Confirm the existing route already matches the desired mapping."]
        plan["notes"] = ["No changes needed."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.routes.ensure", plan=plan, extra={"action": action})

    _require_apply(ctx)
    if action in {"create", "update"}:
        _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if action == "create":
        ctx["audit"].write("apply", {"action": "create_route", "zone_id": zone_id, "pattern": pattern})
        res = ctx["cf"].post_json(f"/zones/{zone_id}/workers/routes", json_body={"pattern": pattern, "script": script_name})
        created = res.result if isinstance(res.result, dict) else {}
        created_id = str(created.get("id") or "").strip() or None
        diff.append(
            {
                "resource": "workers_route",
                "action": "created",
                "zone_id": zone_id,
                "route_id": created_id,
                "pattern": pattern,
                "script_name": script_name,
            }
        )
        changed = True
    elif action == "update":
        assert route_id is not None
        ctx["audit"].write("apply", {"action": "update_route", "zone_id": zone_id, "route_id": route_id})
        _ = ctx["cf"].put_json(
            f"/zones/{zone_id}/workers/routes/{route_id}",
            json_body={"pattern": pattern, "script": script_name},
        )
        diff.append(
            {
                "resource": "workers_route",
                "action": "updated",
                "zone_id": zone_id,
                "route_id": route_id,
                "pattern": pattern,
                "script_name": script_name,
            }
        )
        changed = True

    verify_current = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes").result or []
    verify_routes = verify_current if isinstance(verify_current, list) else [verify_current]
    verify_matches = [r for r in verify_routes if isinstance(r, dict) and str(r.get("pattern") or "") == pattern]
    ok = len(verify_matches) == 1 and str((verify_matches[0] or {}).get("script") or "").strip() == script_name

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = changed
    receipt["diff_applied"] = diff
    receipt["verification"] = {"ok": ok, "details": {"routes_checked": True, "matches": len(verify_matches)}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by updating the route to the previous script mapping (not automatically captured in this phase).",
    }
    return _emit_receipt(ctx, command="workers.routes.ensure", receipt=receipt, extra={"action": action})


def cmd_workers_routes_ensure_absent(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    pattern = str(getattr(args, "pattern", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not pattern:
        raise ValidationError("Missing --pattern")

    current = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes").result or []
    routes = current if isinstance(current, list) else [current]
    matches = [r for r in routes if isinstance(r, dict) and str(r.get("pattern") or "") == pattern]
    if len(matches) > 1:
        raise SafetyError(f"Ambiguous routes: multiple routes match pattern={pattern!r}. Refusing.")
    existing = matches[0] if matches else None
    route_id = str(existing.get("id") or "").strip() if isinstance(existing, dict) else ""
    route_id = route_id or None

    selector = {"zone_id": zone_id, "pattern": pattern}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["Deleting a route can impact traffic routing."],
    )
    if existing and route_id:
        plan["proposed_changes"] = [
            {"resource": "workers_route", "action": "delete", "zone_id": zone_id, "route_id": route_id, "pattern": pattern}
        ]
        plan["verification_plan"] = ["Re-fetch routes list and confirm there is no route with the same pattern."]
    else:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Confirm no route exists for this pattern."]
        plan["notes"] = ["No changes needed."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.routes.ensure_absent", plan=plan, extra={"found": bool(existing and route_id)})

    _require_apply(ctx)
    if existing and route_id:
        _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if existing and route_id:
        ctx["audit"].write("apply", {"action": "delete_route", "zone_id": zone_id, "route_id": route_id})
        _ = ctx["cf"].delete_json(f"/zones/{zone_id}/workers/routes/{route_id}")
        diff.append({"resource": "workers_route", "action": "deleted", "zone_id": zone_id, "route_id": route_id, "pattern": pattern})
        changed = True

    verify_current = ctx["cf"].get_json(f"/zones/{zone_id}/workers/routes").result or []
    verify_routes = verify_current if isinstance(verify_current, list) else [verify_current]
    verify_matches = [r for r in verify_routes if isinstance(r, dict) and str(r.get("pattern") or "") == pattern]
    ok = len(verify_matches) == 0

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = changed
    receipt["diff_applied"] = diff
    receipt["verification"] = {"ok": ok, "details": {"routes_checked": True, "matches": len(verify_matches)}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by re-creating the route mapping (requires the original script_name).",
    }
    return _emit_receipt(ctx, command="workers.routes.ensure_absent", receipt=receipt, extra={"found": bool(existing and route_id)})


def cmd_workers_subdomain_ensure(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    subdomain = str(getattr(args, "subdomain", "") or "").strip()
    if not subdomain:
        raise ValidationError("Missing --subdomain")

    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/subdomain")
    cur = res.result
    cur_val: str | None = None
    if isinstance(cur, dict):
        cur_val = str(cur.get("subdomain") or "").strip() or None
    elif isinstance(cur, str):
        cur_val = cur.strip() or None

    selector = {"account_id": account_id, "subdomain": subdomain}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["Changing the Workers subdomain can affect how Workers are addressed."],
    )
    if cur_val == subdomain:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Confirm the current subdomain already matches the desired value."]
        plan["notes"] = ["No changes needed."]
        action = "no-op"
    else:
        plan["proposed_changes"] = [
            {"resource": "workers_subdomain", "action": "set", "account_id": account_id, "subdomain": subdomain}
        ]
        plan["verification_plan"] = ["Re-fetch subdomain and confirm it matches the desired value."]
        action = "set"

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.subdomain.ensure", plan=plan, extra={"action": action, "current_subdomain": cur_val})

    _require_apply(ctx)
    if cur_val != subdomain:
        _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if cur_val != subdomain:
        ctx["audit"].write("apply", {"action": "set_subdomain", "account_id": account_id})
        _ = ctx["cf"].put_json(f"/accounts/{account_id}/workers/subdomain", json_body={"subdomain": subdomain})
        diff.append({"resource": "workers_subdomain", "action": "set", "account_id": account_id, "subdomain": subdomain})
        changed = True

    verify = ctx["cf"].get_json(f"/accounts/{account_id}/workers/subdomain").result
    verify_val: str | None = None
    if isinstance(verify, dict):
        verify_val = str(verify.get("subdomain") or "").strip() or None
    elif isinstance(verify, str):
        verify_val = verify.strip() or None
    ok = verify_val == subdomain

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = changed
    receipt["diff_applied"] = diff
    receipt["verification"] = {"ok": ok, "details": {"subdomain_checked": True}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by setting the previous subdomain value (not automatically captured in this phase).",
    }
    return _emit_receipt(ctx, command="workers.subdomain.ensure", receipt=receipt, extra={"action": action, "current_subdomain": verify_val})


def cmd_workers_subdomain_ensure_absent(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)

    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/subdomain")
    cur = res.result
    cur_val: str | None = None
    if isinstance(cur, dict):
        cur_val = str(cur.get("subdomain") or "").strip() or None
    elif isinstance(cur, str):
        cur_val = cur.strip() or None

    selector = {"account_id": account_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["Deleting the Workers subdomain can affect how Workers are addressed."],
    )
    if not cur_val:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Confirm there is no configured subdomain."]
        plan["notes"] = ["No changes needed."]
    else:
        plan["proposed_changes"] = [{"resource": "workers_subdomain", "action": "delete", "account_id": account_id}]
        plan["verification_plan"] = ["Re-fetch subdomain and confirm it is not set."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.subdomain.ensure_absent", plan=plan, extra={"current_subdomain": cur_val})

    _require_apply(ctx)
    if cur_val:
        _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if cur_val:
        ctx["audit"].write("apply", {"action": "delete_subdomain", "account_id": account_id})
        _ = ctx["cf"].request_json("DELETE", f"/accounts/{account_id}/workers/subdomain")
        diff.append({"resource": "workers_subdomain", "action": "deleted", "account_id": account_id})
        changed = True

    verify = ctx["cf"].get_json(f"/accounts/{account_id}/workers/subdomain").result
    verify_val: str | None = None
    if isinstance(verify, dict):
        verify_val = str(verify.get("subdomain") or "").strip() or None
    elif isinstance(verify, str):
        verify_val = verify.strip() or None
    ok = not verify_val

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = changed
    receipt["diff_applied"] = diff
    receipt["verification"] = {"ok": ok, "details": {"subdomain_checked": True}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by re-creating the subdomain (requires knowing the desired subdomain name).",
    }
    return _emit_receipt(ctx, command="workers.subdomain.ensure_absent", receipt=receipt, extra={"current_subdomain": verify_val})


def cmd_workers_domains_attach(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    hostname = str(getattr(args, "hostname", "") or "").strip()
    service = str(getattr(args, "service", "") or "").strip()
    environment = str(getattr(args, "environment", "") or "").strip() or None
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not hostname:
        raise ValidationError("Missing --hostname")
    if not service:
        raise ValidationError("Missing --service")

    current = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains").result or []
    domains = current if isinstance(current, list) else [current]
    existing = None
    for d in domains:
        if not isinstance(d, dict):
            continue
        if str(d.get("hostname") or "").strip() == hostname:
            existing = d
            break

    selector = {"account_id": account_id, "zone_id": zone_id, "hostname": hostname, "service": service, "environment": environment}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["Attaching a domain can affect routing to a Workers service."],
    )

    if existing:
        ex_service = str(existing.get("service") or "").strip() or None
        ex_zone_id = str(existing.get("zone_id") or "").strip() or None
        ex_env = str(existing.get("environment") or "").strip() or None
        if ex_service == service and ex_zone_id == zone_id and (environment is None or ex_env == environment):
            plan["proposed_changes"] = []
            plan["verification_plan"] = ["Confirm the domain is already attached with the desired configuration."]
            plan["notes"] = ["No changes needed."]
            action = "no-op"
        else:
            raise SafetyError(
                "Domain hostname already exists but does not match the requested configuration. "
                "Refusing. Detach the existing domain first, then attach again."
            )
    else:
        body: dict[str, Any] = {"zone_id": zone_id, "hostname": hostname, "service": service}
        if environment:
            body["environment"] = environment
        plan["proposed_changes"] = [
            {"resource": "workers_domain", "action": "attach", "account_id": account_id, **body}
        ]
        plan["verification_plan"] = ["Re-fetch domains list and confirm the hostname is present with the expected configuration."]
        action = "attach"

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.domains.attach", plan=plan, extra={"action": action})

    _require_apply(ctx)
    if not existing:
        _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if not existing:
        body = {"zone_id": zone_id, "hostname": hostname, "service": service}
        if environment:
            body["environment"] = environment
        ctx["audit"].write("apply", {"action": "attach_domain", "account_id": account_id, "hostname": hostname})
        res = ctx["cf"].put_json(f"/accounts/{account_id}/workers/domains", json_body=body)
        out_obj = res.result if isinstance(res.result, dict) else {}
        domain_id = str(out_obj.get("id") or "").strip() or None
        diff.append({"resource": "workers_domain", "action": "attached", "account_id": account_id, "domain_id": domain_id, **body})
        changed = True

    verify_current = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains").result or []
    verify_domains = verify_current if isinstance(verify_current, list) else [verify_current]
    verify = None
    for d in verify_domains:
        if isinstance(d, dict) and str(d.get("hostname") or "").strip() == hostname:
            verify = d
            break
    ok = bool(verify)

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = changed
    receipt["diff_applied"] = diff
    receipt["verification"] = {"ok": ok, "details": {"domains_checked": True}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by detaching the domain (requires domain_id).",
    }
    return _emit_receipt(ctx, command="workers.domains.attach", receipt=receipt, extra={"action": action})


def cmd_workers_domains_detach(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    domain_id = str(getattr(args, "domain_id", "") or "").strip()
    if not domain_id:
        raise ValidationError("Missing --domain-id")

    # Pre-read for plan context (best-effort).
    existing_obj: dict[str, Any] | None = None
    try:
        res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains/{domain_id}")
        if isinstance(res.result, dict):
            existing_obj = res.result
    except Exception:
        existing_obj = None

    selector = {"account_id": account_id, "domain_id": domain_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["Detaching a domain can break routing to a Workers service."],
    )
    plan["proposed_changes"] = [{"resource": "workers_domain", "action": "detach", "account_id": account_id, "domain_id": domain_id}]
    plan["verification_plan"] = ["Re-fetch domains list and confirm the domain id is not present."]
    if existing_obj:
        plan["notes"] = [f"Existing hostname: {existing_obj.get('hostname')}"]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="workers.domains.detach", plan=plan, extra={"domain": existing_obj})

    _require_apply(ctx)
    _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "detach_domain", "account_id": account_id, "domain_id": domain_id})
    _ = ctx["cf"].request_json("DELETE", f"/accounts/{account_id}/workers/domains/{domain_id}")

    verify_current = ctx["cf"].get_json(f"/accounts/{account_id}/workers/domains").result or []
    verify_domains = verify_current if isinstance(verify_current, list) else [verify_current]
    still = [d for d in verify_domains if isinstance(d, dict) and str(d.get("id") or "").strip() == domain_id]
    ok = len(still) == 0

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = True
    receipt["diff_applied"] = [{"resource": "workers_domain", "action": "detached", "account_id": account_id, "domain_id": domain_id}]
    receipt["verification"] = {"ok": ok, "details": {"domains_checked": True, "matches": len(still)}}
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by re-attaching the domain with the previous configuration (zone_id/hostname/service).",
    }
    return _emit_receipt(ctx, command="workers.domains.detach", receipt=receipt, extra={"domain": existing_obj})


def _get_script_settings(ctx: dict, *, account_id: str, script_name: str) -> dict[str, Any]:
    res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts/{script_name}/script-settings")
    if isinstance(res.result, dict):
        return dict(res.result)
    return {}


def _observability_from_settings(settings: dict[str, Any]) -> Any:
    if not isinstance(settings, dict):
        return None
    obs = settings.get("observability")
    return obs if isinstance(obs, dict) else None


def cmd_workers_observability_status(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")

    settings = _get_script_settings(ctx, account_id=account_id, script_name=script_name)
    obs = _observability_from_settings(settings)
    enabled = bool(obs.get("enabled")) if isinstance(obs, dict) and "enabled" in obs else False
    head_sampling_rate = obs.get("head_sampling_rate") if isinstance(obs, dict) else None

    ctx["out"].emit(
        {
            "ok": True,
            "command": "workers.observability.status",
            "account_id": account_id,
            "script_name": script_name,
            "enabled": enabled,
            "head_sampling_rate": head_sampling_rate,
            "observability": obs,
        }
    )
    return 0


def _validate_sampling_rate(v: float | None) -> None:
    if v is None:
        return
    try:
        f = float(v)
    except Exception:
        raise ValidationError("--head-sampling-rate must be a number") from None
    if not (0.0 <= f <= 1.0):
        raise ValidationError("--head-sampling-rate must be in the range [0.0, 1.0]")


def _cmd_workers_observability_set(args, ctx, *, enabled: bool) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    if not script_name:
        raise ValidationError("Missing --script-name")

    head_sampling_rate = getattr(args, "head_sampling_rate", None)
    head_sampling_rate = float(head_sampling_rate) if head_sampling_rate is not None else None
    _validate_sampling_rate(head_sampling_rate)

    current_settings = _get_script_settings(ctx, account_id=account_id, script_name=script_name)
    current_obs = _observability_from_settings(current_settings) or {}
    current_enabled = bool(current_obs.get("enabled")) if "enabled" in current_obs else False
    current_rate = current_obs.get("head_sampling_rate") if isinstance(current_obs, dict) else None

    needs_change = current_enabled != bool(enabled)
    if head_sampling_rate is not None:
        if current_rate is None:
            needs_change = True
        else:
            try:
                needs_change = needs_change or (float(current_rate) != float(head_sampling_rate))
            except Exception:
                needs_change = True

    desired_obs: dict[str, Any] = dict(current_obs) if isinstance(current_obs, dict) else {}
    desired_obs["enabled"] = bool(enabled)
    if head_sampling_rate is not None:
        desired_obs["head_sampling_rate"] = float(head_sampling_rate)

    selector = {
        "account_id": account_id,
        "script_name": script_name,
        "enabled": bool(enabled),
        "head_sampling_rate": head_sampling_rate,
    }
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["This is a Cloudflare API write (PATCH Workers script-settings)."],
    )
    if needs_change:
        plan["proposed_changes"] = [
            {
                "resource": "workers_script_settings",
                "action": "patch_observability",
                "account_id": account_id,
                "script_name": script_name,
                "body": {"observability": desired_obs},
            }
        ]
        plan["verification_plan"] = [
            "Read-back GET /script-settings and confirm `observability.enabled` (and head_sampling_rate if set) matches the requested state.",
        ]
    else:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Read-back GET /script-settings and confirm the desired state is already present."]
        plan["notes"] = ["No changes needed."]

    if not bool(ctx.get("apply")):
        return _emit_plan(
            ctx,
            command="workers.observability.enable" if enabled else "workers.observability.disable",
            plan=plan,
            extra={"current_observability": current_obs, "proposed_observability": desired_obs},
        )

    _require_apply(ctx)
    _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    diff: list[dict[str, Any]] = []
    if needs_change:
        ctx["audit"].write(
            "apply",
            {
                "action": "patch_workers_script_settings_observability",
                "account_id": account_id,
                "script_name": script_name,
            },
        )
        _ = ctx["cf"].patch_json(
            f"/accounts/{account_id}/workers/scripts/{script_name}/script-settings",
            json_body={"observability": desired_obs},
        )
        diff.append(
            {
                "resource": "workers_script_settings",
                "action": "patched_observability",
                "account_id": account_id,
                "script_name": script_name,
            }
        )

    verify_settings = _get_script_settings(ctx, account_id=account_id, script_name=script_name)
    verify_obs = _observability_from_settings(verify_settings) or {}
    verify_enabled = bool(verify_obs.get("enabled")) if "enabled" in verify_obs else False
    verify_rate = verify_obs.get("head_sampling_rate") if isinstance(verify_obs, dict) else None

    ok = verify_enabled == bool(enabled)
    if ok and head_sampling_rate is not None:
        try:
            ok = (verify_rate is not None) and float(verify_rate) == float(head_sampling_rate)
        except Exception:
            ok = False

    receipt = _base_receipt(ctx, selector=selector)
    receipt["changed"] = bool(needs_change)
    receipt["diff_applied"] = diff
    receipt["verification"] = {
        "ok": bool(ok),
        "details": {
            "expected": {"enabled": bool(enabled), "head_sampling_rate": head_sampling_rate},
            "actual": {"enabled": verify_enabled, "head_sampling_rate": verify_rate},
        },
    }
    receipt["rollback_plan"] = {
        "supported": True,
        "notes": "Rollback by applying the opposite state (enable/disable) and verifying via read-back.",
    }
    return _emit_receipt(
        ctx,
        command="workers.observability.enable" if enabled else "workers.observability.disable",
        receipt=receipt,
        extra={"observability": verify_obs},
    )


def cmd_workers_observability_enable(args, ctx) -> int:
    return _cmd_workers_observability_set(args, ctx, enabled=True)


def cmd_workers_observability_disable(args, ctx) -> int:
    return _cmd_workers_observability_set(args, ctx, enabled=False)
