from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    resolve_safe_out_path,
    sha256_of_bytes,
    sha256_of_file,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _require_apply(ctx) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError("Refusing to apply: this command is dry-run by default (pass --apply).")


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
        "risk_level": str(risk_level),
        "risk_reasons": list(risk_reasons),
        "preconditions": [
            "API token has least-privilege permissions needed for this action.",
            "Review the plan output before applying.",
        ],
        "proposed_changes": [],
        "verification_plan": [],
        "notes": [],
    }


def _base_receipt(ctx: dict, *, selector: dict[str, Any], changed: bool) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed),
        "verification": {"ok": False, "details": {}},
        "diff_applied": [],
        "notes": [],
    }


def _emit_plan(ctx: dict, *, command: str, plan: dict, extra: dict[str, Any] | None = None) -> int:
    _ = write_plan_if_requested(ctx, plan)
    ctx["audit"].write(
        "plan",
        {"command": command, "selector": plan.get("selector"), "proposed_changes": plan.get("proposed_changes")},
    )
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


def _emit_refused(ctx: dict, *, command: str, reasons: list[str], extra: dict[str, Any] | None = None) -> int:
    out = {"ok": True, "refused": True, "command": command, "reasons": list(reasons)}
    if extra:
        out.update(extra)
    ctx["out"].emit(out)
    return 0


def _resolve_zone_or_account(args) -> tuple[Literal["zone", "account"], str]:
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if zone_id and account_id:
        raise ValidationError("Provide only one of --zone-id or --account-id")
    if zone_id:
        return ("zone", zone_id)
    if account_id:
        return ("account", account_id)
    raise ValidationError("Missing --zone-id or --account-id")


def cmd_waf_rulesets_list(args, ctx) -> int:
    _require_token(ctx)
    scope, ident = _resolve_zone_or_account(args)
    path = f"/zones/{ident}/rulesets" if scope == "zone" else f"/accounts/{ident}/rulesets"
    res = ctx["cf"].get_json(path)
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.rulesets.list",
            "scope": scope,
            f"{scope}_id": ident,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_waf_rulesets_get(args, ctx) -> int:
    _require_token(ctx)
    scope, ident = _resolve_zone_or_account(args)
    ruleset_id = str(getattr(args, "ruleset_id", "") or "").strip()
    if not ruleset_id:
        raise ValidationError("Missing --ruleset-id")
    path = (
        f"/zones/{ident}/rulesets/{ruleset_id}"
        if scope == "zone"
        else f"/accounts/{ident}/rulesets/{ruleset_id}"
    )
    res = ctx["cf"].get_json(path)
    ctx["out"].emit({"ok": True, "command": "waf.rulesets.get", "scope": scope, f"{scope}_id": ident, "result": res.result})
    return 0


def cmd_waf_rulesets_entrypoint_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    ruleset_phase = str(getattr(args, "ruleset_phase", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not ruleset_phase:
        raise ValidationError("Missing --ruleset-phase")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/rulesets/phases/{ruleset_phase}/entrypoint")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.rulesets.entrypoint.get",
            "zone_id": zone_id,
            "ruleset_phase": ruleset_phase,
            "result": res.result,
        }
    )
    return 0


def cmd_waf_rulesets_entrypoint_update(args, ctx) -> int:
    _require_token(ctx)
    scope, ident = _resolve_zone_or_account(args)
    ruleset_phase = str(getattr(args, "ruleset_phase", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not ruleset_phase:
        raise ValidationError("Missing --ruleset-phase")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")

    body_obj = read_json_file(body_json_file)
    body_sha = sha256_of_file(Path(body_json_file))
    path = f"/zones/{ident}/rulesets/phases/{ruleset_phase}/entrypoint" if scope == "zone" else f"/accounts/{ident}/rulesets/phases/{ruleset_phase}/entrypoint"

    selector = {
        "scope": scope,
        f"{scope}_id": ident,
        "ruleset_phase": ruleset_phase,
        "path": "/{scope}/{id}/rulesets/phases/{ruleset_phase}/entrypoint",
        "body_json_sha256": body_sha,
    }
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Rulesets entrypoint updates can change caching/redirect/transform/origin behavior at the zone/account level."],
    )
    plan["proposed_changes"] = [
        {
            "resource": "rulesets_entrypoint",
            "action": "update",
            "scope": scope,
            f"{scope}_id": ident,
            "ruleset_phase": ruleset_phase,
            "path": path,
            "body_json_sha256": body_sha,
            "body_json": body_obj,
        }
    ]
    plan["verification_plan"] = ["GET the entrypoint back and confirm the expected ruleset is reflected in the response."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="waf.rulesets.entrypoint.update", plan=plan)

    if not bool(ctx.get("yes")):
        return _emit_refused(ctx, command="waf.rulesets.entrypoint.update", reasons=["Cloudflare API writes require --yes."])

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "rulesets_entrypoint_update", "scope": scope, f"{scope}_id": ident, "ruleset_phase": ruleset_phase})
    put_res = ctx["cf"].put_json(path, json_body=body_obj).result

    verified = ctx["cf"].get_json(path).result
    ok = verified is not None

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {
            "resource": "rulesets_entrypoint",
            "action": "updated",
            "scope": scope,
            f"{scope}_id": ident,
            "ruleset_phase": ruleset_phase,
            "path": path,
            "body_json_sha256": body_sha,
        }
    ]
    receipt["verification"] = {"ok": bool(ok), "method": "read_back_get", "details": {"path": path, "result": verified}}
    receipt["notes"] = ["PUT result is included separately for convenience; verification uses the read-back GET result."]
    return _emit_receipt(ctx, command="waf.rulesets.entrypoint.update", receipt=receipt, extra={"put_result": put_res})


def cmd_waf_rulesets_versions_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    ruleset_id = str(getattr(args, "ruleset_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not ruleset_id:
        raise ValidationError("Missing --ruleset-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/rulesets/{ruleset_id}/versions")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.rulesets.versions.list",
            "zone_id": zone_id,
            "ruleset_id": ruleset_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def _resolve_firewall_scope(args) -> tuple[Literal["zone", "account", "user"], str | None]:
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    account_id = str(getattr(args, "account_id", "") or "").strip()
    user = bool(getattr(args, "user", False))
    provided = sum([1 if zone_id else 0, 1 if account_id else 0, 1 if user else 0])
    if provided != 1:
        raise ValidationError("Select exactly one scope: --zone-id, --account-id, or --user")
    if zone_id:
        return ("zone", zone_id)
    if account_id:
        return ("account", account_id)
    return ("user", None)


def cmd_waf_firewall_access_rules_list(args, ctx) -> int:
    _require_token(ctx)
    scope, ident = _resolve_firewall_scope(args)
    if scope == "zone":
        path = f"/zones/{ident}/firewall/access_rules/rules"
    elif scope == "account":
        path = f"/accounts/{ident}/firewall/access_rules/rules"
    else:
        path = "/user/firewall/access_rules/rules"
    res = ctx["cf"].get_json(path)
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.firewall.access_rules.list",
            "scope": scope,
            f"{scope}_id": ident,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_waf_firewall_access_rules_get(args, ctx) -> int:
    _require_token(ctx)
    scope, ident = _resolve_firewall_scope(args)
    rule_id = str(getattr(args, "rule_id", "") or "").strip()
    if not rule_id:
        raise ValidationError("Missing --rule-id")
    if scope == "zone":
        path = f"/zones/{ident}/firewall/access_rules/rules/{rule_id}"
    elif scope == "account":
        path = f"/accounts/{ident}/firewall/access_rules/rules/{rule_id}"
    else:
        path = f"/user/firewall/access_rules/rules/{rule_id}"
    res = ctx["cf"].get_json(path)
    ctx["out"].emit({"ok": True, "command": "waf.firewall.access_rules.get", "scope": scope, f"{scope}_id": ident, "result": res.result})
    return 0


def cmd_waf_rate_limits_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/rate_limits")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.rate_limits.list",
            "zone_id": zone_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_waf_rate_limits_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    rate_limit_id = str(getattr(args, "rate_limit_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not rate_limit_id:
        raise ValidationError("Missing --rate-limit-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/rate_limits/{rate_limit_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.rate_limits.get",
            "zone_id": zone_id,
            "rate_limit_id": rate_limit_id,
            "result": res.result,
        }
    )
    return 0


def cmd_waf_snippets_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/snippets")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.snippets.list",
            "zone_id": zone_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_waf_snippets_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    snippet_name = str(getattr(args, "snippet_name", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not snippet_name:
        raise ValidationError("Missing --snippet-name")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/snippets/{snippet_name}")
    ctx["out"].emit(
        {"ok": True, "command": "waf.snippets.get", "zone_id": zone_id, "snippet_name": snippet_name, "result": res.result}
    )
    return 0


def cmd_waf_snippets_content_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    snippet_name = str(getattr(args, "snippet_name", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not snippet_name:
        raise ValidationError("Missing --snippet-name")
    if not out_path:
        return _emit_refused(ctx, command="waf.snippets.content.get", reasons=["Missing --out (required; content is file-only)."])

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"zone_id": zone_id, "snippet_name": snippet_name, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "This fetches snippet content (potentially sensitive) and writes it to a local file.",
            "The tool will not print the content to stdout.",
        ],
    )
    plan["proposed_changes"] = [
        {"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "waf_snippet_content"}
    ]
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="waf.snippets.content.get", plan=plan)

    _require_apply(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    resp = ctx["cf"].request_raw(
        "GET",
        f"/zones/{zone_id}/snippets/{snippet_name}/content",
        headers={"accept": "*/*"},
    )
    data = resp.body
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(data)
    digest = sha256_of_bytes(data)
    ok = safe.abs_path.exists() and sha256_of_file(safe.abs_path) == digest

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["verification"] = {"ok": ok, "details": {"bytes_written": len(data), "sha256": digest, "http_status": int(resp.status)}}
    receipt["diff_applied"] = [
        {
            "resource": "local_file",
            "action": "written",
            "path": safe.rel_to_project,
            "abs_path": str(safe.abs_path),
            "bytes_written": len(data),
            "sha256": digest,
            "content_type": resp.headers.get("content-type"),
        }
    ]
    return _emit_receipt(ctx, command="waf.snippets.content.get", receipt=receipt)


def cmd_waf_page_rules_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/pagerules")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.page_rules.list",
            "zone_id": zone_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_waf_page_rules_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    pagerule_id = str(getattr(args, "pagerule_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not pagerule_id:
        raise ValidationError("Missing --pagerule-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/pagerules/{pagerule_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "waf.page_rules.get",
            "zone_id": zone_id,
            "pagerule_id": pagerule_id,
            "result": res.result,
        }
    )
    return 0


def cmd_waf_managed_transforms_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/managed_headers")
    ctx["out"].emit({"ok": True, "command": "waf.managed_transforms.get", "zone_id": zone_id, "result": res.result})
    return 0


def cmd_waf_managed_transforms_update(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")

    body = read_json_file(body_json_file)
    body_bytes = json.dumps(body, sort_keys=True).encode("utf-8")
    selector = {"zone_id": zone_id, "body_json_file": body_json_file, "body_sha256": sha256_of_bytes(body_bytes)}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "Managed transforms can affect production request/response headers.",
            "A misconfiguration can break applications or security posture.",
        ],
    )
    plan["proposed_changes"] = [{"resource": "managed_transforms", "action": "update", "zone_id": zone_id}]
    plan["verification_plan"] = ["Re-fetch managed transforms and confirm the GET call succeeds after the update."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="waf.managed_transforms.update", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "managed_transforms_update", "zone_id": zone_id, "body_sha256": selector["body_sha256"]})
    patch_res = ctx["cf"].patch_json(f"/zones/{zone_id}/managed_headers", json_body=body).result
    verify_res = ctx["cf"].get_json(f"/zones/{zone_id}/managed_headers").result

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {"resource": "managed_transforms", "action": "updated", "zone_id": zone_id, "body_sha256": selector["body_sha256"]}
    ]
    receipt["verification"] = {"ok": True, "details": {"read_back_ok": True}}
    receipt["result"] = {"patch": patch_res, "read_back": verify_res}
    return _emit_receipt(ctx, command="waf.managed_transforms.update", receipt=receipt)
