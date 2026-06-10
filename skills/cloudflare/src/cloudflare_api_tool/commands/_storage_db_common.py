from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
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


def require_token(ctx: dict) -> None:
    cfg = ctx.get("cfg")
    token = getattr(cfg, "token", None) if cfg else None
    if not token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def require_apply(ctx: dict) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError("Refusing to apply: this command is dry-run by default (pass --apply).")


def require_yes(ctx: dict) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing to apply: Cloudflare API writes require --yes.")


def require_ack_irreversible(ctx: dict) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refusing: this operation can return or create a secret/token and requires --ack-irreversible.")


def resolve_account_id(args, ctx) -> str:
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


def base_plan(ctx: dict, *, selector: dict[str, Any], risk_level: str, risk_reasons: list[str]) -> dict[str, Any]:
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": str(risk_level),
        "risk_reasons": list(risk_reasons),
        "preconditions": [
            "API token has least-privilege permissions needed for this operation.",
            "Review this plan before applying.",
        ],
        "request": {},
        "proposed_changes": [],
        "verification_plan": [],
        "notes": [],
    }


def base_receipt(ctx: dict, *, selector: dict[str, Any], changed: bool) -> dict[str, Any]:
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed),
        "diff_applied": [],
        "verification": {"ok": True, "method": "api_response_success", "details": {}},
        "output_file": None,
        "notes": [],
    }


def emit_plan(ctx: dict, *, command: str, plan: dict[str, Any], extra: dict[str, Any] | None = None) -> int:
    _ = write_plan_if_requested(ctx, plan)
    out_obj: dict[str, Any] = {"ok": True, "dry_run": True, "command": command, "plan": plan}
    if extra:
        out_obj.update(extra)
    ctx["audit"].write("plan", {"command": command, "selector": plan.get("selector")})
    ctx["out"].emit(out_obj)
    return 0


def emit_receipt(ctx: dict, *, command: str, receipt: dict[str, Any], extra: dict[str, Any] | None = None) -> int:
    _ = write_receipt_if_requested(ctx, receipt)
    out_obj: dict[str, Any] = {"ok": True, "dry_run": False, "command": command, "changed": bool(receipt.get("changed")), "receipt": receipt}
    if extra:
        out_obj.update(extra)
    ctx["audit"].write(
        "receipt",
        {"command": command, "changed": bool(receipt.get("changed")), "output_file": (receipt.get("output_file") or {}).get("out_rel")},
    )
    ctx["out"].emit(out_obj)
    return 0


def verify_and_require_plan(ctx: dict, *, plan: dict[str, Any]) -> None:
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)


def build_json_body_meta(obj: Any, *, source: str) -> dict[str, Any]:
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return {"body_kind": "json", "sha256": sha256_of_bytes(raw), "size_bytes": len(raw), "source": str(source)}


def write_raw_response_to_file(
    *,
    ctx: dict,
    out_path: str,
    overwrite: bool,
    method: str,
    http_status: int,
    body: bytes,
) -> dict[str, Any]:
    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_bytes(body)
    return {
        "out_path": str(safe.abs_path),
        "out_rel": safe.rel_to_project,
        "size_bytes": safe.abs_path.stat().st_size,
        "sha256": sha256_of_file(safe.abs_path),
        "http_status": int(http_status),
        "method": str(method).upper(),
    }
