from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plans import build_plan, utc_now, validate_plan_env, validate_plan_kind
from ..redaction import sanitize


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
    return params


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)


def _extract_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("id", "custom_tag_id", "customTagId"):
            v = obj.get(k)
            if v:
                s = str(v).strip()
                if s:
                    return s
    return None


def cmd_custom_tags_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/custom-tags", params=_pagination_params(args))
    out = {"ok": True, "custom_tags": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("custom_tags.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_custom_tags_get(args: Any, ctx: dict) -> int:
    tag_id = str(getattr(args, "tag_id", "") or "").strip()
    if not tag_id:
        raise ValidationError("Missing --tag-id")
    client = _client(ctx)
    res = client.get(f"/custom-tags/{tag_id}")
    out = {"ok": True, "custom_tag": res.data}
    ctx["audit"].write("custom_tags.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_custom_tags_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (custom tag JSON)")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "custom-tags.create", "value": file_path},
        risk_level="medium",
        risk_reasons=["creates-custom-tag"],
        request={"method": "POST", "path": "/custom-tags", "body": sanitize(body)},
        verification_plan={"type": "read-back", "notes": "Best-effort: GET custom tag by returned id."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("custom_tags.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/custom-tags", json_body=body).data
    verify = None
    tag_id = _extract_id(created)
    if tag_id:
        try:
            verify = client.get(f"/custom-tags/{tag_id}").data
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
        "verification": {"ok": verify is not None, "details": {"type": "custom-tags.get", "tag_id": tag_id}},
        "result": {"created": sanitize(created), "verified_custom_tag": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("custom_tags.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_custom_tags_patch(args: Any, ctx: dict) -> int:
    tag_id = str(getattr(args, "tag_id", "") or "").strip()
    if not tag_id:
        raise ValidationError("Missing --tag-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (custom tag patch JSON)")
    body = _load_file_json(file_path)
    path = f"/custom-tags/{tag_id}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "custom-tags.patch", "value": tag_id},
        risk_level="medium",
        risk_reasons=["updates-custom-tag"],
        request={"method": "PATCH", "path": path, "body": sanitize(body)},
        verification_plan={"type": "read-back", "notes": "GET custom tag after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "tag_id": tag_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("custom_tags.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    changed = client.patch(path, json_body=body).data
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
        "verification": {"ok": verify is not None, "details": {"type": "custom-tags.get", "tag_id": tag_id}},
        "result": {"operation_result": sanitize(changed), "verified_custom_tag": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("custom_tags.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_custom_tags_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = ctx.get("plan_in")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")
    if apply:
        if not yes:
            raise SafetyError("Refused: custom-tags delete requires --apply --yes")
        if not plan_in:
            raise SafetyError("Refused: custom-tags delete on apply requires --plan-in (plan-file workflow)")

    if plan_in:
        plan_obj_any = read_json_file(plan_in)
        if not isinstance(plan_obj_any, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan_obj: dict[str, Any] = dict(plan_obj_any)
        validate_plan_env(plan_obj, env_fingerprint=str(ctx["cfg"].base_url))
        validate_plan_kind(plan_obj, kind="custom-tags.delete")
        baseline = plan_obj.get("baseline") or {}
        if not isinstance(baseline, dict):
            raise ValidationError("Plan baseline must be a JSON object")
        tag_id = str(baseline.get("tag_id") or "").strip()
        if not tag_id:
            raise ValidationError("Plan baseline missing tag_id")
    else:
        tag_id = str(getattr(args, "tag_id", "") or "").strip()
        if not tag_id:
            raise ValidationError("Missing --tag-id (or provide --plan-in)")

    path = f"/custom-tags/{tag_id}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "custom-tags.delete", "value": tag_id},
        risk_level="high",
        risk_reasons=["deletes-custom-tag"],
        request={"method": "DELETE", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: try GET custom tag after delete (should fail/404)."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "tag_id": tag_id},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("custom_tags.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.delete(path, json_body={}).data
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
        "verification": {"ok": verify is None, "details": {"type": "custom-tags.get", "tag_id": tag_id}},
        "result": {"operation_result": sanitize(result), "custom_tag_after": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("custom_tags.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_custom_tags_toggle_resource(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (toggle-resource JSON)")
    body = _load_file_json(file_path)

    apply = bool(ctx.get("apply"))
    if apply and not bool(ctx.get("yes")):
        raise SafetyError("Refused: custom-tags toggle-resource requires --apply --yes (mapping endpoint)")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "custom-tags.toggle-resource", "value": file_path},
        risk_level="high",
        risk_reasons=["tag-mapping-change"],
        request={"method": "POST", "path": "/custom-tags/toggle-resource", "body": sanitize(body)},
        verification_plan={"type": "read-back", "notes": "Best-effort: list custom tag mappings after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("custom_tags.toggle_resource.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.post("/custom-tags/toggle-resource", json_body=body).data
    verify = None
    try:
        verify = client.get("/custom-tag-mappings", params={"limit": 20}).data
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
        "verification": {"ok": verify is not None, "details": {"type": "custom-tag-mappings.list", "limit": 20}},
        "result": {"operation_result": sanitize(result), "custom_tag_mappings_after": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("custom_tags.toggle_resource.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0

