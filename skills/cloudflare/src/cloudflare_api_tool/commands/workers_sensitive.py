from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    resolve_safe_out_path,
    sha256_of_file,
    sha256_of_bytes,
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
        raise SafetyError("Refusing sensitive read: this command requires --apply and writes output to a file.")


def _base_plan(ctx: dict, *, selector: dict[str, Any], notes: list[str]) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": "high",
        "risk_reasons": [
            "This fetches sensitive content (code or KV values) and writes it to a local file.",
            "The tool will not print the content to stdout.",
        ],
        "preconditions": [
            "API token has least-privilege permissions needed for this action.",
            "The output path is under --project-dir and has been reviewed.",
        ],
        "proposed_changes": [],
        "verification_plan": [
            "Confirm the output file exists after apply and record its sha256.",
        ],
        "notes": list(notes),
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
        "changed": True,
        "verification": {"ok": False, "details": {}},
        "diff_applied": [],
        "notes": [],
    }


def cmd_workers_scripts_download(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not script_name:
        raise ValidationError("Missing --script-name")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"account_id": account_id, "script_name": script_name, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        notes=[
            "This uses the Workers script download endpoint.",
            "Content is written to a file and never printed to stdout.",
        ],
    )
    plan["proposed_changes"] = [
        {"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "workers_script_download"}
    ]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "workers.scripts.download", "plan": plan})
        return 0

    _require_apply(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    resp = ctx["cf"].request_raw(
        "GET",
        f"/accounts/{account_id}/workers/scripts/{script_name}",
        headers={"accept": "*/*"},
    )
    data = resp.body
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(data)
    digest = sha256_of_bytes(data)
    file_digest = sha256_of_file(safe.abs_path)
    ok = digest == file_digest and safe.abs_path.exists()

    receipt = _base_receipt(ctx, selector=selector)
    receipt["verification"] = {"ok": ok, "details": {"sha256": digest, "bytes_written": len(data)}}
    receipt["diff_applied"] = [
        {
            "resource": "local_file",
            "action": "written",
            "path": safe.rel_to_project,
            "abs_path": str(safe.abs_path),
            "sha256": digest,
            "bytes_written": len(data),
            "content_type": resp.headers.get("content-type"),
        }
    ]
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "workers.scripts.download", "receipt": receipt})
    return 0


def cmd_workers_scripts_content_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not script_name:
        raise ValidationError("Missing --script-name")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"account_id": account_id, "script_name": script_name, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        notes=[
            "This uses the Workers script content endpoint (/content/v2).",
            "Content is written to a file and never printed to stdout.",
        ],
    )
    plan["proposed_changes"] = [
        {"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "workers_script_content"}
    ]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "workers.scripts.content.get", "plan": plan})
        return 0

    _require_apply(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    resp = ctx["cf"].request_raw(
        "GET",
        f"/accounts/{account_id}/workers/scripts/{script_name}/content/v2",
        headers={"accept": "*/*"},
    )
    data = resp.body
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(data)
    digest = sha256_of_bytes(data)
    file_digest = sha256_of_file(safe.abs_path)
    ok = digest == file_digest and safe.abs_path.exists()

    receipt = _base_receipt(ctx, selector=selector)
    receipt["verification"] = {"ok": ok, "details": {"sha256": digest, "bytes_written": len(data)}}
    receipt["diff_applied"] = [
        {
            "resource": "local_file",
            "action": "written",
            "path": safe.rel_to_project,
            "abs_path": str(safe.abs_path),
            "sha256": digest,
            "bytes_written": len(data),
            "content_type": resp.headers.get("content-type"),
        }
    ]
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "workers.scripts.content.get", "receipt": receipt})
    return 0


def cmd_workers_kv_values_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    namespace_id = str(getattr(args, "namespace_id", "") or "").strip()
    key_name = str(getattr(args, "key_name", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not namespace_id:
        raise ValidationError("Missing --namespace-id")
    if not key_name:
        raise ValidationError("Missing --key-name")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"account_id": account_id, "namespace_id": namespace_id, "key_name": key_name, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        notes=[
            "This reads one KV value and writes it to a file.",
            "KV values may contain secrets; the tool will not print the value to stdout.",
        ],
    )
    plan["proposed_changes"] = [
        {"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "workers_kv_value"}
    ]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "workers.kv.values.get", "plan": plan})
        return 0

    _require_apply(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    resp = ctx["cf"].request_raw(
        "GET",
        f"/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key_name}",
        headers={"accept": "application/octet-stream"},
    )
    data = resp.body
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(data)
    digest = sha256_of_bytes(data)
    file_digest = sha256_of_file(safe.abs_path)
    ok = digest == file_digest and safe.abs_path.exists()

    receipt = _base_receipt(ctx, selector=selector)
    receipt["verification"] = {"ok": ok, "details": {"sha256": digest, "bytes_written": len(data)}}
    receipt["diff_applied"] = [
        {
            "resource": "local_file",
            "action": "written",
            "path": safe.rel_to_project,
            "abs_path": str(safe.abs_path),
            "sha256": digest,
            "bytes_written": len(data),
            "content_type": resp.headers.get("content-type") or "application/octet-stream",
        }
    ]
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "workers.kv.values.get", "receipt": receipt})
    return 0
