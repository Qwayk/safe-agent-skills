from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
        raise SafetyError("Refusing to apply: this command is dry-run by default (pass --apply).")


def _require_yes(ctx) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing to apply: Cloudflare API writes require --yes.")


def _require_ack_irreversible(ctx) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refusing: this operation is high-risk/bulk and requires --ack-irreversible.")


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


def cmd_dns_records_list(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")

    params: dict[str, Any] = {}
    name = str(getattr(args, "name", "") or "").strip() or None
    rtype = str(getattr(args, "type", "") or "").strip() or None
    content = str(getattr(args, "content", "") or "").strip() or None
    if name:
        params["name"] = name
    if rtype:
        params["type"] = rtype
    if content:
        params["content"] = content

    page = int(getattr(args, "page", 1) or 1)
    per_page = int(getattr(args, "per_page", 50) or 50)
    params["page"] = page
    params["per_page"] = per_page

    res = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records", params=params)
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "dns.records.list",
            "zone_id": zone_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_dns_records_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    record_id = str(getattr(args, "record_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not record_id:
        raise ValidationError("Missing --record-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records/{record_id}")
    ctx["out"].emit({"ok": True, "command": "dns.records.get", "zone_id": zone_id, "record_id": record_id, "result": res.result})
    return 0


def _pick_unique_record(items: Any, *, name: str, rtype: str, content: str | None) -> dict[str, Any] | None:
    rows = items if isinstance(items, list) else ([items] if items else [])
    matches = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        if str(r.get("name") or "") != name:
            continue
        if str(r.get("type") or "") != rtype:
            continue
        if content is not None and str(r.get("content") or "") != content:
            continue
        matches.append(r)
    if not matches:
        return None
    if len(matches) > 1:
        raise SafetyError("Ambiguous DNS record selector: multiple records match. Refusing.")
    return matches[0]


def cmd_dns_records_ensure(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    name = str(getattr(args, "name", "") or "").strip()
    rtype = str(getattr(args, "type", "") or "").strip().upper()
    content = str(getattr(args, "content", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not name:
        raise ValidationError("Missing --name")
    if not rtype:
        raise ValidationError("Missing --type")
    if not content:
        raise ValidationError("Missing --content")

    ttl = getattr(args, "ttl", None)
    proxied = getattr(args, "proxied", None)
    comment = str(getattr(args, "comment", "") or "").strip() or None

    params = {"name": name, "type": rtype, "content": content, "page": 1, "per_page": 100}
    cur = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records", params=params).result
    existing = _pick_unique_record(cur, name=name, rtype=rtype, content=content)

    desired: dict[str, Any] = {"type": rtype, "name": name, "content": content}
    if ttl is not None:
        desired["ttl"] = int(ttl)
    if proxied is not None:
        desired["proxied"] = bool(proxied)
    if comment is not None:
        desired["comment"] = comment

    action = "create" if existing is None else "update"
    record_id = str(existing.get("id") or "").strip() if isinstance(existing, dict) else ""
    if existing is not None:
        differs = False
        for k, v in desired.items():
            if k not in existing:
                differs = True
                break
            if existing.get(k) != v:
                differs = True
                break
        if not differs:
            action = "no-op"

    selector = {"zone_id": zone_id, "name": name, "type": rtype, "content": content}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["DNS record changes can affect production traffic."],
    )
    if action == "create":
        plan["proposed_changes"] = [{"resource": "dns_record", "action": "create", "zone_id": zone_id, "record": desired}]
        plan["verification_plan"] = ["Re-list records with the same name/type/content and confirm exactly one exists."]
    elif action == "update":
        if not record_id:
            raise SafetyError("DNS record match is missing an id; refusing to update.")
        plan["proposed_changes"] = [
            {"resource": "dns_record", "action": "update", "zone_id": zone_id, "record_id": record_id, "record": desired}
        ]
        plan["verification_plan"] = ["Re-fetch the DNS record by id and confirm it matches the desired fields."]
    else:
        plan["proposed_changes"] = []
        plan["verification_plan"] = ["Confirm the existing record already matches the desired fields."]
        plan["notes"] = ["No changes needed."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.records.ensure", plan=plan, extra={"action": action})

    _require_apply(ctx)
    if action in {"create", "update"}:
        _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    if action == "create":
        ctx["audit"].write("apply", {"action": "dns_record_create", "zone_id": zone_id, "name": name, "type": rtype})
        created = ctx["cf"].post_json(f"/zones/{zone_id}/dns_records", json_body=desired).result or {}
        diff.append({"resource": "dns_record", "action": "created", "zone_id": zone_id, "record_id": (created or {}).get("id"), "record": desired})
        changed = True
        rid = str((created or {}).get("id") or "").strip()
        verification_ok = False
        verify_obj = None
        if rid:
            verify_obj = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records/{rid}").result
            if isinstance(verify_obj, dict) and str(verify_obj.get("name") or "") == name and str(verify_obj.get("type") or "") == rtype:
                verification_ok = True
        verification = {"ok": bool(verification_ok), "method": "read_back_get_by_id", "details": {"record_id": rid}}
    elif action == "update":
        assert record_id
        ctx["audit"].write("apply", {"action": "dns_record_update", "zone_id": zone_id, "record_id": record_id})
        _ = ctx["cf"].put_json(f"/zones/{zone_id}/dns_records/{record_id}", json_body=desired).result
        diff.append({"resource": "dns_record", "action": "updated", "zone_id": zone_id, "record_id": record_id, "record": desired})
        changed = True
        verify_obj = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records/{record_id}").result
        verification_ok = isinstance(verify_obj, dict) and all(verify_obj.get(k) == v for k, v in desired.items())
        verification = {"ok": bool(verification_ok), "method": "read_back_get_by_id", "details": {"record_id": record_id}}
    else:
        verification = {"ok": True, "method": "no_op", "details": {}}

    receipt = _base_receipt(ctx, selector=selector, changed=changed)
    receipt["diff_applied"] = diff
    receipt["verification"] = verification
    return _emit_receipt(ctx, command="dns.records.ensure", receipt=receipt, extra={"action": action})


def cmd_dns_records_ensure_absent(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    name = str(getattr(args, "name", "") or "").strip()
    rtype = str(getattr(args, "type", "") or "").strip().upper()
    content = str(getattr(args, "content", "") or "").strip() or None
    record_id = str(getattr(args, "record_id", "") or "").strip() or None
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if record_id:
        target_id = record_id
    else:
        if not name:
            raise ValidationError("Missing --name (or provide --record-id)")
        if not rtype:
            raise ValidationError("Missing --type (or provide --record-id)")
        params = {"name": name, "type": rtype, "page": 1, "per_page": 100}
        if content:
            params["content"] = content
        cur = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records", params=params).result
        existing = _pick_unique_record(cur, name=name, rtype=rtype, content=content if content else None)
        target_id = str(existing.get("id") or "").strip() if existing else ""

    selector = {"zone_id": zone_id, "record_id": target_id, "name": name or None, "type": rtype or None, "content": content}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Deleting DNS records can affect production traffic."],
    )
    if target_id:
        plan["proposed_changes"] = [{"resource": "dns_record", "action": "delete", "zone_id": zone_id, "record_id": target_id}]
        plan["verification_plan"] = ["Attempt to fetch the record by id; expect missing/not found."]
    else:
        plan["notes"] = ["No matching record found; no changes needed."]
        plan["verification_plan"] = ["No-op."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.records.ensure_absent", plan=plan, extra={"found": bool(target_id)})

    _require_apply(ctx)
    if target_id:
        _require_yes(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    changed = False
    diff: list[dict[str, Any]] = []
    verification: dict[str, Any]
    if target_id:
        ctx["audit"].write("apply", {"action": "dns_record_delete", "zone_id": zone_id, "record_id": target_id})
        _ = ctx["cf"].delete_json(f"/zones/{zone_id}/dns_records/{target_id}").result
        changed = True
        diff.append({"resource": "dns_record", "action": "deleted", "zone_id": zone_id, "record_id": target_id})
        # Best-effort verify (may 404).
        resp = ctx["cf"].request_raw_allow_errors("GET", f"/zones/{zone_id}/dns_records/{target_id}")
        verification = {"ok": int(resp.status) >= 400, "method": "read_back_get_expected_missing", "http_status": int(resp.status)}
    else:
        verification = {"ok": True, "method": "no_op", "details": {}}

    receipt = _base_receipt(ctx, selector=selector, changed=changed)
    receipt["diff_applied"] = diff
    receipt["verification"] = verification
    return _emit_receipt(ctx, command="dns.records.ensure_absent", receipt=receipt, extra={"found": bool(target_id)})


def cmd_dns_records_export(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: DNS export is a sensitive read. Provide --out.")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite) if out_path else None
    selector = {"zone_id": zone_id, "out": (safe.rel_to_project if safe else None)}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="medium",
        risk_reasons=["DNS export can reveal full zone records; output is file-only."],
    )
    if safe:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "dns_export"}]
    else:
        plan["notes"].append("Provide --out to write the export to a file (required on --apply).")
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.records.export", plan=plan)

    _require_apply(ctx)
    assert safe is not None
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "dns_export", "zone_id": zone_id, "out": safe.rel_to_project})
    resp = ctx["cf"].request_raw("GET", f"/zones/{zone_id}/dns_records/export", retries=3)
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(resp.body)

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dns_export", "action": "exported", "zone_id": zone_id, "output_file": safe.rel_to_project}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"sha256": sha256_of_file(safe.abs_path)}}
    receipt["output_file"] = {
        "out_path": str(safe.abs_path),
        "out_rel": safe.rel_to_project,
        "size_bytes": safe.abs_path.stat().st_size,
        "sha256": sha256_of_file(safe.abs_path),
        "http_status": int(resp.status),
    }
    return _emit_receipt(ctx, command="dns.records.export", receipt=receipt, extra={"file": receipt["output_file"]})


def cmd_dns_records_import(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    file_path = str(getattr(args, "file", "") or "").strip()
    proxied = getattr(args, "proxied", None)
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not file_path:
        raise ValidationError("Missing --file")
    p = Path(file_path)
    if not p.exists():
        raise ValidationError(f"Import file not found: {p}")

    selector = {"zone_id": zone_id, "file": str(p)}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["DNS import is a bulk write that can change many records."],
    )
    plan["proposed_changes"] = [{"resource": "dns_import", "action": "import", "zone_id": zone_id, "file": str(p)}]
    plan["verification_plan"] = ["Record API success response (no automatic read-back)."]
    plan["notes"] = ["High risk: review file content carefully before applying."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.records.import", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    _require_ack_irreversible(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    data: dict[str, Any] = {}
    if proxied is not None:
        data["proxied"] = "true" if bool(proxied) else "false"
    file_bytes = p.read_bytes()
    files = {"file": (p.name, file_bytes)}

    ctx["audit"].write("apply", {"action": "dns_import", "zone_id": zone_id, "file": str(p)})
    res = ctx["cf"].request_json("POST", f"/zones/{zone_id}/dns_records/import", data=data or None, files=files).result

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [
        {
            "resource": "dns_import",
            "action": "imported",
            "zone_id": zone_id,
            "file_sha256": sha256_of_bytes(file_bytes),
            "file_size_bytes": len(file_bytes),
        }
    ]
    receipt["verification"] = {"ok": True, "method": "api_response_success", "details": {}}
    receipt["result"] = res
    return _emit_receipt(ctx, command="dns.records.import", receipt=receipt)


def cmd_dns_scan_trigger(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")

    selector = {"zone_id": zone_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["DNS scan can propose bulk changes; trigger is a high-impact operation."],
    )
    plan["proposed_changes"] = [{"resource": "dns_scan", "action": "trigger", "zone_id": zone_id}]
    plan["verification_plan"] = ["Record API success response (no automatic read-back)."]
    plan["notes"] = ["High risk: prefer reviewing scan results before applying."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.scan.trigger", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    _require_ack_irreversible(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "dns_scan_trigger", "zone_id": zone_id})
    res = ctx["cf"].post_json(f"/zones/{zone_id}/dns_records/scan/trigger", json_body={}).result

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dns_scan", "action": "triggered", "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "api_response_success", "details": {}}
    receipt["result"] = res
    return _emit_receipt(ctx, command="dns.scan.trigger", receipt=receipt)


def cmd_dns_scan_review(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/dns_records/scan/review")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "dns.scan.review",
            "zone_id": zone_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_dns_scan_apply(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip() or None
    if not zone_id:
        raise ValidationError("Missing --zone-id")

    body = read_json_file(body_json_file) if body_json_file else {}
    selector = {"zone_id": zone_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8")) if body_json_file else None}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Applying DNS scan results is a bulk write and can change many records."],
    )
    plan["proposed_changes"] = [{"resource": "dns_scan", "action": "apply", "zone_id": zone_id}]
    plan["verification_plan"] = ["Record API success response (no automatic read-back)."]
    plan["notes"] = ["High risk: confirm the scan review output matches intent before applying."]

    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.scan.apply", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    _require_ack_irreversible(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "dns_scan_apply", "zone_id": zone_id})
    res = ctx["cf"].post_json(f"/zones/{zone_id}/dns_records/scan/review", json_body=body if isinstance(body, dict) else {}).result

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dns_scan", "action": "applied", "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "api_response_success", "details": {}}
    receipt["result"] = res
    return _emit_receipt(ctx, command="dns.scan.apply", receipt=receipt)


def cmd_dns_settings_zone_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/dns_settings")
    ctx["out"].emit({"ok": True, "command": "dns.settings.zone.get", "zone_id": zone_id, "result": res.result})
    return 0


def cmd_dns_settings_zone_update(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"zone_id": zone_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["DNS settings changes can affect production behavior."],
    )
    plan["proposed_changes"] = [{"resource": "dns_settings_zone", "action": "update", "zone_id": zone_id, "body_json_file": body_json_file}]
    plan["verification_plan"] = ["Re-fetch zone DNS settings and confirm the expected fields changed."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.settings.zone.update", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "dns_settings_zone_update", "zone_id": zone_id})
    _ = ctx["cf"].patch_json(f"/zones/{zone_id}/dns_settings", json_body=body if isinstance(body, dict) else {}).result
    verify = ctx["cf"].get_json(f"/zones/{zone_id}/dns_settings").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dns_settings_zone", "action": "updated", "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get", "details": {}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.settings.zone.update", receipt=receipt)


def cmd_dns_settings_account_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings")
    ctx["out"].emit({"ok": True, "command": "dns.settings.account.get", "account_id": account_id, "result": res.result})
    return 0


def cmd_dns_settings_account_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Account DNS settings changes can affect multiple zones."],
    )
    plan["proposed_changes"] = [
        {"resource": "dns_settings_account", "action": "update", "account_id": account_id, "body_json_file": body_json_file}
    ]
    plan["verification_plan"] = ["Re-fetch account DNS settings and confirm the expected fields changed."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.settings.account.update", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "dns_settings_account_update", "account_id": account_id})
    _ = ctx["cf"].patch_json(f"/accounts/{account_id}/dns_settings", json_body=body if isinstance(body, dict) else {}).result
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dns_settings_account", "action": "updated", "account_id": account_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get", "details": {}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.settings.account.update", receipt=receipt)


def cmd_dns_views_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings/views")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "dns.settings.views.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_dns_views_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    view_id = str(getattr(args, "view_id", "") or "").strip()
    if not view_id:
        raise ValidationError("Missing --view-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings/views/{view_id}")
    ctx["out"].emit(
        {"ok": True, "command": "dns.settings.views.get", "account_id": account_id, "view_id": view_id, "result": res.result}
    )
    return 0


def cmd_dns_views_create(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Internal DNS view changes can affect resolution behavior."],
    )
    plan["proposed_changes"] = [{"resource": "internal_dns_view", "action": "create", "account_id": account_id}]
    plan["verification_plan"] = ["Fetch created view by id (when available) and confirm it exists."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.settings.views.create", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "internal_dns_view_create", "account_id": account_id})
    created = ctx["cf"].post_json(f"/accounts/{account_id}/dns_settings/views", json_body=body if isinstance(body, dict) else {}).result or {}
    view_id = str((created or {}).get("id") or "").strip()
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings/views/{view_id}").result if view_id else None
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "internal_dns_view", "action": "created", "account_id": account_id, "view_id": view_id or None}]
    receipt["verification"] = {"ok": bool(view_id), "method": "read_back_get_by_id", "details": {"view_id": view_id or None}}
    receipt["result"] = verify if verify is not None else created
    return _emit_receipt(ctx, command="dns.settings.views.create", receipt=receipt)


def cmd_dns_views_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    view_id = str(getattr(args, "view_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not view_id:
        raise ValidationError("Missing --view-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "view_id": view_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Internal DNS view changes can affect resolution behavior."],
    )
    plan["proposed_changes"] = [{"resource": "internal_dns_view", "action": "update", "account_id": account_id, "view_id": view_id}]
    plan["verification_plan"] = ["Re-fetch view by id and confirm the expected fields changed."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.settings.views.update", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "internal_dns_view_update", "account_id": account_id, "view_id": view_id})
    _ = ctx["cf"].patch_json(
        f"/accounts/{account_id}/dns_settings/views/{view_id}",
        json_body=body if isinstance(body, dict) else {},
    ).result
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/dns_settings/views/{view_id}").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "internal_dns_view", "action": "updated", "account_id": account_id, "view_id": view_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get_by_id", "details": {"view_id": view_id}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.settings.views.update", receipt=receipt)


def cmd_dns_views_delete(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    view_id = str(getattr(args, "view_id", "") or "").strip()
    if not view_id:
        raise ValidationError("Missing --view-id")
    selector = {"account_id": account_id, "view_id": view_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Deleting internal DNS views can affect resolution behavior."],
    )
    plan["proposed_changes"] = [{"resource": "internal_dns_view", "action": "delete", "account_id": account_id, "view_id": view_id}]
    plan["verification_plan"] = ["Attempt to fetch view by id; expect missing/not found."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.settings.views.delete", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "internal_dns_view_delete", "account_id": account_id, "view_id": view_id})
    _ = ctx["cf"].delete_json(f"/accounts/{account_id}/dns_settings/views/{view_id}").result
    resp = ctx["cf"].request_raw_allow_errors("GET", f"/accounts/{account_id}/dns_settings/views/{view_id}")
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "internal_dns_view", "action": "deleted", "account_id": account_id, "view_id": view_id}]
    receipt["verification"] = {"ok": int(resp.status) >= 400, "method": "read_back_get_expected_missing", "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.settings.views.delete", receipt=receipt)


def cmd_dnssec_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/dnssec")
    ctx["out"].emit({"ok": True, "command": "dns.dnssec.get", "zone_id": zone_id, "result": res.result})
    return 0


def cmd_dnssec_set(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"zone_id": zone_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["DNSSEC changes can impact domain validation and resolution."],
    )
    plan["proposed_changes"] = [{"resource": "dnssec", "action": "set", "zone_id": zone_id}]
    plan["verification_plan"] = ["Re-fetch DNSSEC and confirm the status matches intent."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.dnssec.set", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "dnssec_set", "zone_id": zone_id})
    _ = ctx["cf"].patch_json(f"/zones/{zone_id}/dnssec", json_body=body if isinstance(body, dict) else {}).result
    verify = ctx["cf"].get_json(f"/zones/{zone_id}/dnssec").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dnssec", "action": "set", "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get", "details": {}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.dnssec.set", receipt=receipt)


def cmd_dnssec_delete(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    selector = {"zone_id": zone_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Deleting DNSSEC records can impact domain validation and resolution."],
    )
    plan["proposed_changes"] = [{"resource": "dnssec", "action": "delete", "zone_id": zone_id}]
    plan["verification_plan"] = ["Re-fetch DNSSEC and confirm records/status reflect the deletion."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.dnssec.delete", plan=plan)

    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "dnssec_delete", "zone_id": zone_id})
    _ = ctx["cf"].delete_json(f"/zones/{zone_id}/dnssec").result
    verify = ctx["cf"].get_json(f"/zones/{zone_id}/dnssec").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "dnssec", "action": "deleted", "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get", "details": {}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.dnssec.delete", receipt=receipt)


def _account_id_from_args(args, ctx) -> str:
    return _resolve_account_id(args, ctx)


def cmd_secondary_acls_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/acls")
    items = res.result or []
    ctx["out"].emit(
        {"ok": True, "command": "dns.secondary.account.acls.list", "account_id": account_id, "count": len(items) if isinstance(items, list) else None, "result": items, "result_info": res.result_info}
    )
    return 0


def cmd_secondary_acls_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    acl_id = str(getattr(args, "acl_id", "") or "").strip()
    if not acl_id:
        raise ValidationError("Missing --acl-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/acls/{acl_id}")
    ctx["out"].emit({"ok": True, "command": "dns.secondary.account.acls.get", "account_id": account_id, "acl_id": acl_id, "result": res.result})
    return 0


def cmd_secondary_acls_create(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS ACL changes can affect transfer security."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_acl", "action": "create", "account_id": account_id}]
    plan["verification_plan"] = ["Fetch created ACL by id (when available)."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.acls.create", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_acl_create", "account_id": account_id})
    created = ctx["cf"].post_json(f"/accounts/{account_id}/secondary_dns/acls", json_body=body if isinstance(body, dict) else {}).result or {}
    acl_id = str((created or {}).get("id") or "").strip()
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/acls/{acl_id}").result if acl_id else None
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_acl", "action": "created", "account_id": account_id, "acl_id": acl_id or None}]
    receipt["verification"] = {"ok": bool(acl_id), "method": "read_back_get_by_id", "details": {"acl_id": acl_id or None}}
    receipt["result"] = verify if verify is not None else created
    return _emit_receipt(ctx, command="dns.secondary.account.acls.create", receipt=receipt)


def cmd_secondary_acls_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    acl_id = str(getattr(args, "acl_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not acl_id:
        raise ValidationError("Missing --acl-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "acl_id": acl_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS ACL changes can affect transfer security."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_acl", "action": "update", "account_id": account_id, "acl_id": acl_id}]
    plan["verification_plan"] = ["Re-fetch ACL by id and confirm the expected fields changed."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.acls.update", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_acl_update", "account_id": account_id, "acl_id": acl_id})
    _ = ctx["cf"].put_json(f"/accounts/{account_id}/secondary_dns/acls/{acl_id}", json_body=body if isinstance(body, dict) else {}).result
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/acls/{acl_id}").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_acl", "action": "updated", "account_id": account_id, "acl_id": acl_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get_by_id", "details": {"acl_id": acl_id}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.secondary.account.acls.update", receipt=receipt)


def cmd_secondary_acls_delete(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    acl_id = str(getattr(args, "acl_id", "") or "").strip()
    if not acl_id:
        raise ValidationError("Missing --acl-id")
    selector = {"account_id": account_id, "acl_id": acl_id}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS ACL deletion can affect transfer security."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_acl", "action": "delete", "account_id": account_id, "acl_id": acl_id}]
    plan["verification_plan"] = ["Attempt to fetch ACL by id; expect missing/not found."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.acls.delete", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_acl_delete", "account_id": account_id, "acl_id": acl_id})
    _ = ctx["cf"].delete_json(f"/accounts/{account_id}/secondary_dns/acls/{acl_id}").result
    resp = ctx["cf"].request_raw_allow_errors("GET", f"/accounts/{account_id}/secondary_dns/acls/{acl_id}")
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_acl", "action": "deleted", "account_id": account_id, "acl_id": acl_id}]
    receipt["verification"] = {"ok": int(resp.status) >= 400, "method": "read_back_get_expected_missing", "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.acls.delete", receipt=receipt)


def cmd_secondary_peers_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/peers")
    items = res.result or []
    ctx["out"].emit(
        {"ok": True, "command": "dns.secondary.account.peers.list", "account_id": account_id, "count": len(items) if isinstance(items, list) else None, "result": items, "result_info": res.result_info}
    )
    return 0


def cmd_secondary_peers_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    peer_id = str(getattr(args, "peer_id", "") or "").strip()
    if not peer_id:
        raise ValidationError("Missing --peer-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/peers/{peer_id}")
    ctx["out"].emit({"ok": True, "command": "dns.secondary.account.peers.get", "account_id": account_id, "peer_id": peer_id, "result": res.result})
    return 0


def cmd_secondary_peers_create(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS peer changes can affect transfer behavior."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_peer", "action": "create", "account_id": account_id}]
    plan["verification_plan"] = ["Fetch created peer by id (when available)."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.peers.create", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_peer_create", "account_id": account_id})
    created = ctx["cf"].post_json(f"/accounts/{account_id}/secondary_dns/peers", json_body=body if isinstance(body, dict) else {}).result or {}
    peer_id = str((created or {}).get("id") or "").strip()
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/peers/{peer_id}").result if peer_id else None
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_peer", "action": "created", "account_id": account_id, "peer_id": peer_id or None}]
    receipt["verification"] = {"ok": bool(peer_id), "method": "read_back_get_by_id", "details": {"peer_id": peer_id or None}}
    receipt["result"] = verify if verify is not None else created
    return _emit_receipt(ctx, command="dns.secondary.account.peers.create", receipt=receipt)


def cmd_secondary_peers_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    peer_id = str(getattr(args, "peer_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not peer_id:
        raise ValidationError("Missing --peer-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    selector = {"account_id": account_id, "peer_id": peer_id, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS peer changes can affect transfer behavior."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_peer", "action": "update", "account_id": account_id, "peer_id": peer_id}]
    plan["verification_plan"] = ["Re-fetch peer by id and confirm the expected fields changed."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.peers.update", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_peer_update", "account_id": account_id, "peer_id": peer_id})
    _ = ctx["cf"].put_json(f"/accounts/{account_id}/secondary_dns/peers/{peer_id}", json_body=body if isinstance(body, dict) else {}).result
    verify = ctx["cf"].get_json(f"/accounts/{account_id}/secondary_dns/peers/{peer_id}").result
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_peer", "action": "updated", "account_id": account_id, "peer_id": peer_id}]
    receipt["verification"] = {"ok": True, "method": "read_back_get_by_id", "details": {"peer_id": peer_id}}
    receipt["result"] = verify
    return _emit_receipt(ctx, command="dns.secondary.account.peers.update", receipt=receipt)


def cmd_secondary_peers_delete(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    peer_id = str(getattr(args, "peer_id", "") or "").strip()
    if not peer_id:
        raise ValidationError("Missing --peer-id")
    selector = {"account_id": account_id, "peer_id": peer_id}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Secondary DNS peer deletion can affect transfer behavior."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_peer", "action": "delete", "account_id": account_id, "peer_id": peer_id}]
    plan["verification_plan"] = ["Attempt to fetch peer by id; expect missing/not found."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.peers.delete", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_peer_delete", "account_id": account_id, "peer_id": peer_id})
    _ = ctx["cf"].delete_json(f"/accounts/{account_id}/secondary_dns/peers/{peer_id}").result
    resp = ctx["cf"].request_raw_allow_errors("GET", f"/accounts/{account_id}/secondary_dns/peers/{peer_id}")
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_peer", "action": "deleted", "account_id": account_id, "peer_id": peer_id}]
    receipt["verification"] = {"ok": int(resp.status) >= 400, "method": "read_back_get_expected_missing", "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.peers.delete", receipt=receipt)


def _tsig_safe_out(args, ctx) -> Any:
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: this endpoint is a sensitive read/write-result. Provide --out.")
    return resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite) if out_path else None


def cmd_secondary_tsigs_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    safe = _tsig_safe_out(args, ctx)
    selector = {"account_id": account_id, "out": (safe.rel_to_project if safe else None)}
    plan = _base_plan(ctx, selector=selector, risk_level="medium", risk_reasons=["TSIG details can include secrets; output is file-only."])
    if safe:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "secondary_dns_tsig_list"}]
    else:
        plan["notes"].append("Provide --out to write the response to a file (required on --apply).")
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.tsigs.list", plan=plan)
    _require_apply(ctx)
    assert safe is not None
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_tsig_list", "account_id": account_id, "out": safe.rel_to_project})
    resp = ctx["cf"].request_raw("GET", f"/accounts/{account_id}/secondary_dns/tsigs")
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(resp.body)
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_tsig", "action": "listed", "account_id": account_id}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {}}
    receipt["output_file"] = {"out_path": str(safe.abs_path), "out_rel": safe.rel_to_project, "size_bytes": len(resp.body), "sha256": sha256_of_bytes(resp.body), "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.tsigs.list", receipt=receipt, extra={"file": receipt["output_file"]})


def cmd_secondary_tsigs_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    tsig_id = str(getattr(args, "tsig_id", "") or "").strip()
    if not tsig_id:
        raise ValidationError("Missing --tsig-id")
    safe = _tsig_safe_out(args, ctx)
    selector = {"account_id": account_id, "tsig_id": tsig_id, "out": (safe.rel_to_project if safe else None)}
    plan = _base_plan(ctx, selector=selector, risk_level="medium", risk_reasons=["TSIG details can include secrets; output is file-only."])
    if safe:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "secondary_dns_tsig_get"}]
    else:
        plan["notes"].append("Provide --out to write the response to a file (required on --apply).")
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.tsigs.get", plan=plan)
    _require_apply(ctx)
    assert safe is not None
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_tsig_get", "account_id": account_id, "tsig_id": tsig_id, "out": safe.rel_to_project})
    resp = ctx["cf"].request_raw("GET", f"/accounts/{account_id}/secondary_dns/tsigs/{tsig_id}")
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(resp.body)
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_tsig", "action": "fetched", "account_id": account_id, "tsig_id": tsig_id}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {}}
    receipt["output_file"] = {"out_path": str(safe.abs_path), "out_rel": safe.rel_to_project, "size_bytes": len(resp.body), "sha256": sha256_of_bytes(resp.body), "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.tsigs.get", receipt=receipt, extra={"file": receipt["output_file"]})


def cmd_secondary_tsigs_create(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    safe = _tsig_safe_out(args, ctx)
    selector = {"account_id": account_id, "out": (safe.rel_to_project if safe else None), "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="irreversible", risk_reasons=["TSIG create can return a secret shown once; output is file-only."])
    if safe:
        plan["proposed_changes"] = [{"resource": "secondary_dns_tsig", "action": "create", "account_id": account_id, "output_file": safe.rel_to_project}]
    else:
        plan["notes"].append("Provide --out to write the secret-bearing response to a file (required on --apply).")
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.tsigs.create", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    _require_ack_irreversible(ctx)
    assert safe is not None
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_tsig_create", "account_id": account_id, "out": safe.rel_to_project})
    resp = ctx["cf"].request_raw("POST", f"/accounts/{account_id}/secondary_dns/tsigs", json_body=body if isinstance(body, dict) else {})
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(resp.body)
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_tsig", "action": "created", "account_id": account_id}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {}}
    receipt["output_file"] = {"out_path": str(safe.abs_path), "out_rel": safe.rel_to_project, "size_bytes": len(resp.body), "sha256": sha256_of_bytes(resp.body), "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.tsigs.create", receipt=receipt, extra={"file": receipt["output_file"]})


def cmd_secondary_tsigs_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    tsig_id = str(getattr(args, "tsig_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not tsig_id:
        raise ValidationError("Missing --tsig-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    body = read_json_file(body_json_file)
    safe = _tsig_safe_out(args, ctx)
    selector = {"account_id": account_id, "tsig_id": tsig_id, "out": (safe.rel_to_project if safe else None), "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))}
    plan = _base_plan(ctx, selector=selector, risk_level="irreversible", risk_reasons=["TSIG update can return a secret; output is file-only."])
    if safe:
        plan["proposed_changes"] = [{"resource": "secondary_dns_tsig", "action": "update", "account_id": account_id, "tsig_id": tsig_id, "output_file": safe.rel_to_project}]
    else:
        plan["notes"].append("Provide --out to write the secret-bearing response to a file (required on --apply).")
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.tsigs.update", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    _require_ack_irreversible(ctx)
    assert safe is not None
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_tsig_update", "account_id": account_id, "tsig_id": tsig_id, "out": safe.rel_to_project})
    resp = ctx["cf"].request_raw("PUT", f"/accounts/{account_id}/secondary_dns/tsigs/{tsig_id}", json_body=body if isinstance(body, dict) else {})
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(resp.body)
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_tsig", "action": "updated", "account_id": account_id, "tsig_id": tsig_id}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {}}
    receipt["output_file"] = {"out_path": str(safe.abs_path), "out_rel": safe.rel_to_project, "size_bytes": len(resp.body), "sha256": sha256_of_bytes(resp.body), "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.tsigs.update", receipt=receipt, extra={"file": receipt["output_file"]})


def cmd_secondary_tsigs_delete(args, ctx) -> int:
    _require_token(ctx)
    account_id = _account_id_from_args(args, ctx)
    tsig_id = str(getattr(args, "tsig_id", "") or "").strip()
    if not tsig_id:
        raise ValidationError("Missing --tsig-id")
    selector = {"account_id": account_id, "tsig_id": tsig_id}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["TSIG deletion can affect DNS transfer security."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_tsig", "action": "delete", "account_id": account_id, "tsig_id": tsig_id}]
    plan["verification_plan"] = ["Attempt to fetch TSIG by id; expect missing/not found."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command="dns.secondary.account.tsigs.delete", plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": "secondary_tsig_delete", "account_id": account_id, "tsig_id": tsig_id})
    _ = ctx["cf"].delete_json(f"/accounts/{account_id}/secondary_dns/tsigs/{tsig_id}", json_body={}).result
    resp = ctx["cf"].request_raw_allow_errors("GET", f"/accounts/{account_id}/secondary_dns/tsigs/{tsig_id}")
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_tsig", "action": "deleted", "account_id": account_id, "tsig_id": tsig_id}]
    receipt["verification"] = {"ok": int(resp.status) >= 400, "method": "read_back_get_expected_missing", "http_status": int(resp.status)}
    return _emit_receipt(ctx, command="dns.secondary.account.tsigs.delete", receipt=receipt)


def cmd_secondary_zone_incoming_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/secondary_dns/incoming")
    ctx["out"].emit({"ok": True, "command": "dns.secondary.zone.incoming.get", "zone_id": zone_id, "result": res.result})
    return 0


def _zone_secondary_write(ctx, *, command: str, zone_id: str, action: str, method: str, path: str, body_json_file: str | None = None) -> int:
    body = read_json_file(body_json_file) if body_json_file else {}
    selector = {"zone_id": zone_id, "action": action, "body_sha256": sha256_of_bytes(json.dumps(body, sort_keys=True).encode("utf-8")) if body_json_file else None}
    plan = _base_plan(ctx, selector=selector, risk_level="high", risk_reasons=["Zone transfer changes can affect DNS availability and transfers."])
    plan["proposed_changes"] = [{"resource": "secondary_dns_zone", "action": action, "zone_id": zone_id}]
    plan["verification_plan"] = ["Best-effort: re-fetch the config/status endpoint when available."]
    if not bool(ctx.get("apply")):
        return _emit_plan(ctx, command=command, plan=plan)
    _require_apply(ctx)
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
    ctx["audit"].write("apply", {"action": action, "zone_id": zone_id})
    if method == "POST":
        res = ctx["cf"].post_json(path, json_body=body if isinstance(body, dict) else {}).result
    elif method == "PUT":
        res = ctx["cf"].put_json(path, json_body=body if isinstance(body, dict) else {}).result
    elif method == "DELETE":
        res = ctx["cf"].delete_json(path, json_body=body if isinstance(body, dict) else {}).result
    else:
        raise ValidationError(f"Unsupported method: {method}")
    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "secondary_dns_zone", "action": action, "zone_id": zone_id}]
    receipt["verification"] = {"ok": True, "method": "api_response_success", "details": {}}
    receipt["result"] = res
    return _emit_receipt(ctx, command=command, receipt=receipt)


def cmd_secondary_zone_incoming_create(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.incoming.create",
        zone_id=zone_id,
        action="incoming_create",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/incoming",
        body_json_file=body_json_file,
    )


def cmd_secondary_zone_incoming_update(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.incoming.update",
        zone_id=zone_id,
        action="incoming_update",
        method="PUT",
        path=f"/zones/{zone_id}/secondary_dns/incoming",
        body_json_file=body_json_file,
    )


def cmd_secondary_zone_incoming_delete(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.incoming.delete",
        zone_id=zone_id,
        action="incoming_delete",
        method="DELETE",
        path=f"/zones/{zone_id}/secondary_dns/incoming",
    )


def cmd_secondary_zone_outgoing_get(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/secondary_dns/outgoing")
    ctx["out"].emit({"ok": True, "command": "dns.secondary.zone.outgoing.get", "zone_id": zone_id, "result": res.result})
    return 0


def cmd_secondary_zone_outgoing_create(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.create",
        zone_id=zone_id,
        action="outgoing_create",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/outgoing",
        body_json_file=body_json_file,
    )


def cmd_secondary_zone_outgoing_update(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.update",
        zone_id=zone_id,
        action="outgoing_update",
        method="PUT",
        path=f"/zones/{zone_id}/secondary_dns/outgoing",
        body_json_file=body_json_file,
    )


def cmd_secondary_zone_outgoing_delete(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.delete",
        zone_id=zone_id,
        action="outgoing_delete",
        method="DELETE",
        path=f"/zones/{zone_id}/secondary_dns/outgoing",
    )


def cmd_secondary_zone_outgoing_status(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/secondary_dns/outgoing/status")
    ctx["out"].emit({"ok": True, "command": "dns.secondary.zone.outgoing.status", "zone_id": zone_id, "result": res.result})
    return 0


def cmd_secondary_zone_outgoing_enable(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.enable",
        zone_id=zone_id,
        action="outgoing_enable",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/outgoing/enable",
    )


def cmd_secondary_zone_outgoing_disable(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.disable",
        zone_id=zone_id,
        action="outgoing_disable",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/outgoing/disable",
    )


def cmd_secondary_zone_outgoing_force_notify(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.outgoing.force_notify",
        zone_id=zone_id,
        action="outgoing_force_notify",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/outgoing/force_notify",
    )


def cmd_secondary_zone_force_axfr(args, ctx) -> int:
    _require_token(ctx)
    zone_id = str(getattr(args, "zone_id", "") or "").strip()
    if not zone_id:
        raise ValidationError("Missing --zone-id")
    return _zone_secondary_write(
        ctx,
        command="dns.secondary.zone.force_axfr",
        zone_id=zone_id,
        action="force_axfr",
        method="POST",
        path=f"/zones/{zone_id}/secondary_dns/force_axfr",
    )
