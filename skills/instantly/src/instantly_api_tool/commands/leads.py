from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plan_apply import load_apply_plan, request_from_plan, require_plan_in_on_apply
from ..plans import build_plan, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    if getattr(args, "campaign_id", None):
        params["campaign_id"] = str(args.campaign_id).strip()
    return params


def cmd_leads_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.post("/leads/list", json_body=_pagination_params(args))
    out = {"ok": True, "leads": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("leads.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_leads_get(args: Any, ctx: dict) -> int:
    lead_id = str(getattr(args, "lead_id", "") or "").strip()
    if not lead_id:
        raise ValidationError("Missing --lead-id")
    client = _client(ctx)
    res = client.get(f"/leads/{lead_id}")
    out = {"ok": True, "lead": res.data}
    ctx["audit"].write("leads.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def _read_csv_leads(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValidationError(f"CSV not found: {path}")
    leads: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            lead: dict[str, Any] = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
            if not str(lead.get("email") or "").strip():
                raise ValidationError("CSV must include an email column with non-empty values")
            leads.append(lead)
    return leads


def _read_json_leads(path: Path) -> list[dict[str, Any]]:
    obj = read_json_file(path)
    if not isinstance(obj, list):
        raise ValidationError("JSON leads file must be a list of objects")
    out: list[dict[str, Any]] = []
    for item in obj:
        if not isinstance(item, dict):
            raise ValidationError("JSON leads file must be a list of objects")
        if not str(item.get("email") or "").strip():
            raise ValidationError("Each lead must include a non-empty email")
        out.append(dict(item))
    return out


def _load_file_json_obj(file_path: str, *, label: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError(f"{label} JSON file must be a JSON object")
    return dict(body_any)


def _chunks(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    if size <= 0:
        raise ValidationError("Chunk size must be > 0")
    return [items[i : i + size] for i in range(0, len(items), size)]


def cmd_leads_add_bulk(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")

    csv_path = str(getattr(args, "csv", "") or "").strip()
    json_path = str(getattr(args, "json", "") or "").strip()
    if bool(csv_path) == bool(json_path):
        raise ValidationError("Provide exactly one of --csv or --json")

    chunk_size = int(getattr(args, "chunk_size", 1000) or 1000)
    if chunk_size > 1000:
        raise ValidationError("Chunk size must be <= 1000")

    if csv_path:
        leads = _read_csv_leads(Path(csv_path))
        selector_val = csv_path
    else:
        leads = _read_json_leads(Path(json_path))
        selector_val = json_path

    if not leads:
        raise ValidationError("No leads found in input")

    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: leads add-bulk requires --apply --yes (bulk lead injection)")

    leads_chunks = _chunks(leads, chunk_size)
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.add-bulk", "value": selector_val},
        risk_level="high",
        risk_reasons=["bulk-lead-injection"],
        request={
            "method": "POST",
            "path": "/leads/add",
            "body": {"campaign_id": campaign_id, "leads_count": len(leads), "chunk_size": chunk_size},
        },
        verification_plan={
            "type": "best-effort",
            "notes": "After apply, performs a lightweight leads list call to confirm API connectivity.",
        },
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "campaign_id": campaign_id, "leads_count": len(leads)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "leads_count": len(leads),
            "chunks": len(leads_chunks),
        }
        ctx["audit"].write("leads.add_bulk.plan", {"ok": True, "plan_out": plan_path, "leads_count": len(leads)})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    results: list[dict[str, Any]] = []
    for idx, chunk in enumerate(leads_chunks, start=1):
        body = {"campaign_id": campaign_id, "leads": chunk}
        res = client.post("/leads/add", json_body=body).data
        results.append({"chunk": idx, "sent": len(chunk), "result": res})

    verify = None
    try:
        verify = client.post("/leads/list", json_body={"campaign_id": campaign_id, "limit": 1}).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "leads.list", "campaign_id": campaign_id}},
        "result": {"chunks": results, "verify": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("leads.add_bulk.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_leads_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (lead JSON)")
    body = _load_file_json_obj(file_path, label="Lead create")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.create", "value": file_path},
        risk_level="medium",
        risk_reasons=["creates-lead"],
        request={"method": "POST", "path": "/leads", "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: no automatic read-back (lead ids may be generated)."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("leads.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post("/leads", json_body=body).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("leads.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_leads_patch(args: Any, ctx: dict) -> int:
    lead_id = str(getattr(args, "lead_id", "") or "").strip()
    if not lead_id:
        raise ValidationError("Missing --lead-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (lead patch JSON)")
    body = _load_file_json_obj(file_path, label="Lead patch")
    path = f"/leads/{lead_id}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.patch", "value": lead_id},
        risk_level="medium",
        risk_reasons=["patches-lead"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: GET lead by id after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "lead_id": lead_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("leads.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get(path).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "leads.get", "lead_id": lead_id}},
        "result": {"operation_result": result, "verified_lead": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("leads.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_leads_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="leads delete")
    if apply and not yes:
        raise SafetyError("Refused: leads delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    lead_id = str(getattr(args, "lead_id", "") or "").strip() or None
    if not lead_id and not apply:
        raise ValidationError("Missing --lead-id (or provide --plan-in with --apply)")

    file_path = str(getattr(args, "file", "") or "").strip() or None
    body = _load_file_json_obj(file_path, label="Lead delete") if file_path else {}
    path = f"/leads/{lead_id}" if lead_id else ""

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.delete", "value": lead_id or "<from-plan>"},
        risk_level="high",
        risk_reasons=["deletes-lead"],
        request={"method": "DELETE", "path": path or "/leads/<id>", "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: try GET lead after delete (should fail/404)."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "lead_id": lead_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None
    if not apply:
        ctx["audit"].write("leads.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="leads.delete")
    _, plan_path_val, body_from_plan = request_from_plan(plan_obj, expected_method="DELETE")
    if lead_id and plan_path_val != f"/leads/{lead_id}":
        raise SafetyError("Refused: plan path mismatch for leads delete")
    path = plan_path_val

    client = _client(ctx)
    result = client.delete(path, json_body=body_from_plan).data
    verify = None
    try:
        verify = client.get(path).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan_obj.get("selector"),
        "changed": True,
        "verification": {"ok": verify is None, "details": {"type": "leads.get", "lead_id": lead_id or "<from-plan>"}},
        "result": {"operation_result": result, "lead_after": verify},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("leads.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_leads_bulk_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="leads bulk-delete")
    if apply and not yes:
        raise SafetyError("Refused: leads bulk-delete requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    file_path = str(getattr(args, "file", "") or "").strip() or None
    if not file_path and not apply:
        raise ValidationError("Missing --file (or provide --plan-in with --apply)")

    body = _load_file_json_obj(file_path, label="Leads bulk delete") if file_path else {}
    path = "/leads"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.bulk-delete", "value": file_path or "<from-plan>"},
        risk_level="high",
        risk_reasons=["bulk-deletes-leads"],
        request={"method": "DELETE", "path": path, "body": body},
        verification_plan={"type": "best-effort", "notes": "Best-effort: response-only."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        ctx["audit"].write("leads.bulk_delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="leads.bulk-delete")
    _, plan_path_val, body_from_plan = request_from_plan(plan_obj, expected_method="DELETE")
    if plan_path_val != "/leads":
        raise SafetyError("Refused: plan path mismatch for leads bulk-delete")

    client = _client(ctx)
    result = client.delete("/leads", json_body=body_from_plan).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan_obj.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("leads.bulk_delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_leads_merge(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    require_plan_in_on_apply(apply=apply, plan_in=plan_in, reason="leads merge")
    if apply and not yes:
        raise SafetyError("Refused: leads merge requires --apply --yes")
    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")

    file_path = str(getattr(args, "file", "") or "").strip() or None
    if not file_path and not apply:
        raise ValidationError("Missing --file (or provide --plan-in with --apply)")

    body = _load_file_json_obj(file_path, label="Leads merge") if file_path else {}
    path = "/leads/merge"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "leads.merge", "value": file_path or "<from-plan>"},
        risk_level="high",
        risk_reasons=["merges-leads"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "response-only", "notes": "Response-only."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not apply) else None

    if not apply:
        ctx["audit"].write("leads.merge.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    assert plan_in is not None
    plan_obj = load_apply_plan(plan_in=plan_in, env_fingerprint=str(ctx["cfg"].base_url), kind="leads.merge")
    _, plan_path_val, body_from_plan = request_from_plan(plan_obj, expected_method="POST")
    if plan_path_val != "/leads/merge":
        raise SafetyError("Refused: plan path mismatch for leads merge")

    client = _client(ctx)
    result = client.post("/leads/merge", json_body=body_from_plan).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan_obj.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("leads.merge.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def _high_risk_post_with_yes(args: Any, ctx: dict, *, kind: str, path: str, label: str) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError(f"Missing --file ({label} JSON)")
    body = _load_file_json_obj(file_path, label=label)
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {kind} requires --apply --yes")

    audit_key = kind.replace("-", "_").replace(".", "_")
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": kind, "value": file_path},
        risk_level="high",
        risk_reasons=[kind],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "response-only", "notes": "Response-only."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write(f"{audit_key}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body=body).data
    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": True, "details": {"type": "response-only"}},
        "result": {"operation_result": result},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write(f"{audit_key}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_leads_update_interest_status(args: Any, ctx: dict) -> int:
    return _high_risk_post_with_yes(
        args,
        ctx,
        kind="leads.update-interest-status",
        path="/leads/update-interest-status",
        label="Update interest status",
    )


def cmd_leads_remove_from_subsequence(args: Any, ctx: dict) -> int:
    return _high_risk_post_with_yes(
        args,
        ctx,
        kind="leads.remove-from-subsequence",
        path="/leads/subsequence/remove",
        label="Remove lead from subsequence",
    )


def cmd_leads_bulk_assign(args: Any, ctx: dict) -> int:
    return _high_risk_post_with_yes(
        args,
        ctx,
        kind="leads.bulk-assign",
        path="/leads/bulk-assign",
        label="Bulk assign leads",
    )


def cmd_leads_move(args: Any, ctx: dict) -> int:
    return _high_risk_post_with_yes(
        args,
        ctx,
        kind="leads.move",
        path="/leads/move",
        label="Move leads",
    )


def cmd_leads_move_to_subsequence(args: Any, ctx: dict) -> int:
    return _high_risk_post_with_yes(
        args,
        ctx,
        kind="leads.move-to-subsequence",
        path="/leads/subsequence/move",
        label="Move lead to subsequence",
    )
