from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plans import build_plan, utc_now
from ..redaction import sanitize


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _load_file_json_obj(file_path: str, *, label: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError(f"{label} JSON file must be a JSON object")
    return dict(body_any)


def _require_yes_on_apply(ctx: dict, *, action: str) -> None:
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {action} requires --apply --yes")


def cmd_supersearch_enrichment_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (create enrichment JSON)")
    body = _load_file_json_obj(file_path, label="Create enrichment")
    _require_yes_on_apply(ctx, action="supersearch-enrichment create")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "supersearch-enrichment.create", "value": file_path},
        risk_level="high",
        risk_reasons=["supersearch-enrichment-create", "advanced-feature"],
        request={"method": "POST", "path": "/supersearch-enrichment", "body": body},
        verification_plan={"type": "response-only", "notes": "Response-only."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("supersearch_enrichment.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post("/supersearch-enrichment", json_body=body).data
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
    ctx["audit"].write("supersearch_enrichment.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_supersearch_enrichment_get(args: Any, ctx: dict) -> int:
    resource_id = str(getattr(args, "resource_id", "") or "").strip()
    if not resource_id:
        raise ValidationError("Missing --resource-id")
    client = _client(ctx)
    res = client.get(f"/supersearch-enrichment/{resource_id}")
    ctx["audit"].write("supersearch_enrichment.get", {"ok": True})
    ctx["out"].emit({"ok": True, "enrichment": res.data})
    return 0


def cmd_supersearch_enrichment_patch_settings(args: Any, ctx: dict) -> int:
    resource_id = str(getattr(args, "resource_id", "") or "").strip()
    if not resource_id:
        raise ValidationError("Missing --resource-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (settings patch JSON)")
    body = _load_file_json_obj(file_path, label="Patch settings")
    _require_yes_on_apply(ctx, action="supersearch-enrichment patch-settings")
    path = f"/supersearch-enrichment/{resource_id}/settings"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "supersearch-enrichment.patch-settings", "value": resource_id},
        risk_level="high",
        risk_reasons=["supersearch-enrichment-settings", "advanced-feature"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={
            "type": "best-effort",
            "notes": "Best-effort: GET /supersearch-enrichment/{resource_id} after apply.",
        },
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "resource_id": resource_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write("supersearch_enrichment.patch_settings.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get(f"/supersearch-enrichment/{resource_id}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "supersearch-enrichment.get", "resource_id": resource_id}},
        "result": {"operation_result": sanitize(result), "verified_enrichment": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    ctx["audit"].write("supersearch_enrichment.patch_settings.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_supersearch_enrichment_history(args: Any, ctx: dict) -> int:
    resource_id = str(getattr(args, "resource_id", "") or "").strip()
    if not resource_id:
        raise ValidationError("Missing --resource-id")
    client = _client(ctx)
    res = client.get(f"/supersearch-enrichment/history/{resource_id}")
    ctx["audit"].write("supersearch_enrichment.history", {"ok": True})
    ctx["out"].emit({"ok": True, "history": res.data})
    return 0


def _apply_gated_post_with_yes(args: Any, ctx: dict, *, kind: str, path: str, label: str) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError(f"Missing --file ({label} JSON)")
    body = _load_file_json_obj(file_path, label=label)
    _require_yes_on_apply(ctx, action=kind.replace(".", " "))

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": kind, "value": file_path},
        risk_level="high",
        risk_reasons=["supersearch-enrichment-advanced"],
        request={"method": "POST", "path": path, "body": body},
        verification_plan={"type": "response-only", "notes": "Response-only."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None
    if not bool(ctx.get("apply")):
        ctx["audit"].write(f"{kind.replace('-', '_').replace('.', '_')}.plan", {"ok": True, "plan_out": plan_path})
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
    ctx["audit"].write(f"{kind.replace('-', '_').replace('.', '_')}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_supersearch_enrichment_run(args: Any, ctx: dict) -> int:
    return _apply_gated_post_with_yes(
        args,
        ctx,
        kind="supersearch-enrichment.run",
        path="/supersearch-enrichment/run",
        label="Run enrichment",
    )


def cmd_supersearch_enrichment_enrich_leads(args: Any, ctx: dict) -> int:
    return _apply_gated_post_with_yes(
        args,
        ctx,
        kind="supersearch-enrichment.enrich-leads",
        path="/supersearch-enrichment/enrich-leads-from-supersearch",
        label="Enrich leads from supersearch",
    )


def cmd_supersearch_enrichment_ai(args: Any, ctx: dict) -> int:
    return _apply_gated_post_with_yes(
        args,
        ctx,
        kind="supersearch-enrichment.ai",
        path="/supersearch-enrichment/ai",
        label="AI enrichment",
    )


def cmd_supersearch_enrichment_count_leads(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (count leads JSON)")
    body = _load_file_json_obj(file_path, label="Count leads")
    client = _client(ctx)
    res = client.post("/supersearch-enrichment/count-leads-from-supersearch", json_body=body)
    ctx["audit"].write("supersearch_enrichment.count_leads", {"ok": True})
    ctx["out"].emit({"ok": True, "count": res.data})
    return 0


def cmd_supersearch_enrichment_preview_leads(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (preview leads JSON)")
    body = _load_file_json_obj(file_path, label="Preview leads")
    client = _client(ctx)
    res = client.post("/supersearch-enrichment/preview-leads-from-supersearch", json_body=body)
    ctx["audit"].write("supersearch_enrichment.preview_leads", {"ok": True})
    ctx["out"].emit({"ok": True, "preview": res.data})
    return 0
