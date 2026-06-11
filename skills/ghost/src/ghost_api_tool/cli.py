from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .backup_snapshots import SnapshotWriter, domain_from_admin_api_url
from .errors import SafetyError, ToolError, ValidationError
from .commands import auth as auth_cmd
from .commands import image as image_cmd
from .commands import jobs as jobs_cmd
from .commands import member as member_cmd
from .commands import newsletter as newsletter_cmd
from .commands import onboarding as onboarding_cmd
from .commands import content as content_cmd
from .commands import page as page_cmd
from .commands import post as post_cmd
from .commands import tag as tag_cmd
from .commands import tier as tier_cmd
from .commands import offer as offer_cmd
from .commands import theme as theme_cmd
from .commands import webhook as webhook_cmd
from .config import load_config, load_content_config
from .json_files import read_json_file, write_json_file
from .output import Output
from .project_config import load_project_config
from .runs import (
    RunContext,
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
)
from .webhooks_ledger import iter_webhook_rows, webhooks_index_path_for_env_file


class _HelpRequested(SystemExit):
    """
    Internal: raised to short-circuit argparse help in JSON mode so we can emit a single JSON object to stdout.
    """

    def __init__(self, *, help_text: str, code: int = 0):
        super().__init__(code)
        self.help_text = help_text


def _argv_wants_json(argv: list[str]) -> bool:
    for tok in argv:
        s = str(tok)
        if s.startswith("--output="):
            return s.split("=", 1)[1].strip().lower() == "json"
    for i, tok in enumerate(argv):
        if str(tok) == "--output" and i + 1 < len(argv):
            return str(argv[i + 1]).strip().lower() == "json"
    return True  # default


def _peek_output_mode(argv: list[str]) -> str:
    return "json" if _argv_wants_json(argv) else "text"


def _safe_argv(argv: list[str]) -> list[str]:
    """
    Redact likely PII (like emails) from argv before writing to artifacts/audit.

    This keeps proof artifacts shareable without leaking member emails.
    """
    out: list[str] = []
    for tok in argv:
        s = str(tok)
        if "@" in s and "://" not in s:
            out.append("<redacted>")
        else:
            out.append(s)
    return out


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical_sha256(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()


def _sanitize_artifact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if (
                lk in {"authorization", "password", "secret", "token", "api_key", "admin_api_key", "email"}
                or lk.endswith("_token")
                or lk.endswith("_secret")
                or lk.endswith("_api_key")
                or lk.endswith("_password")
                or lk.endswith("_email")
            ):
                out[k] = "***REDACTED***"
            else:
                out[k] = _sanitize_artifact(v)
        return out
    if isinstance(obj, list):
        return [_sanitize_artifact(x) for x in obj]
    return obj


def _strip_provenance(obj: Any) -> Any:
    """
    Remove volatile, local-only provenance pointers before hashing for drift detection.

    These fields are useful in stdout, but must not affect plan hashes.
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if k in {"run_id", "artifacts_dir", "runs_index", "audit_log", "audit_log_global"}:
                continue
            out[k] = _strip_provenance(v)
        return out
    if isinstance(obj, list):
        return [_strip_provenance(x) for x in obj]
    return obj


def _normalize_output_obj(obj: Any) -> Any:
    """
    Apply the same v2-friendly defaults regardless of whether the output was captured or printed.
    """
    if not isinstance(obj, dict):
        return obj
    out = dict(obj)
    if "ok" not in out:
        out["ok"] = True
    if "apply" in out and "dry_run" not in out and isinstance(out.get("apply"), bool):
        out["dry_run"] = not bool(out.get("apply"))
    return out


def _extract_selector(args: argparse.Namespace) -> dict[str, Any]:
    selector: dict[str, Any] = {}
    for k in ("id", "slug", "from_slug", "to_slug", "tag_id", "member_id", "newsletter_id", "file", "csv"):
        if hasattr(args, k):
            v = getattr(args, k)
            if v is not None and str(v).strip():
                selector[k] = v
    return selector


def _risk_level_from_argv(argv: list[str]) -> tuple[str, list[str]]:
    toks = " ".join(argv).lower()
    reasons: list[str] = []
    if "theme activate" in toks:
        reasons.append("theme_activation")
        return "high", reasons
    if "webhook" in toks and ("create" in toks or "update" in toks):
        reasons.append("unverifiable_webhook_write")
        return "high", reasons
    if "delete" in toks or "merge" in toks or "set-status" in toks or "jobs run" in toks:
        reasons.append("destructive_or_batch_or_status_change")
        return "high", reasons
    if "import" in toks:
        reasons.append("bulk_write")
        return "high", reasons
    if "publish" in toks or "--newsletter" in toks:
        reasons.append("may_trigger_email_delivery")
        return "irreversible", reasons
    if (
        "create" in toks
        or "copy" in toks
        or "patch" in toks
        or "update" in toks
        or "upload" in toks
        or "replace" in toks
        or "convert" in toks
    ):
        reasons.append("write_operation")
        return "medium", reasons
    return "low", reasons


def _is_write_capable(args: argparse.Namespace) -> bool:
    cmd = str(getattr(args, "cmd", "") or "")
    if cmd in {"runs"}:
        return False
    if cmd in {"content"}:
        return False

    if cmd == "jobs":
        return True
    if cmd == "image":
        return True
    if cmd == "tag":
        return str(getattr(args, "tag_cmd", "") or "") not in {"list", "audit"}
    if cmd == "tier":
        return str(getattr(args, "tier_cmd", "") or "") not in {"list", "get"}
    if cmd == "offer":
        return str(getattr(args, "offer_cmd", "") or "") not in {"list", "get"}
    if cmd == "theme":
        return True
    if cmd == "webhook":
        return True
    if cmd == "newsletter":
        return str(getattr(args, "newsletter_cmd", "") or "") not in {"list", "get"}
    if cmd == "member":
        return str(getattr(args, "member_cmd", "") or "") not in {"list", "count", "get", "export-engagement"}
    if cmd == "page":
        return str(getattr(args, "page_cmd", "") or "") not in {"get", "find"}
    if cmd == "post":
        ro = {
            "get",
            "id",
            "find",
            "audit",
            "email-stats-export",
            "authors",
            "images",
            "links",
            "scaffold",
        }
        return str(getattr(args, "post_cmd", "") or "") not in ro
    return False


class _NoopAudit:
    def bind_context(self, _context: dict[str, Any]) -> None:
        return

    def write(self, _event: str, _payload: dict[str, Any]) -> None:
        return

    def close(self) -> None:
        return


class _CaptureOutput:
    def __init__(self) -> None:
        self.items: list[Any] = []

    def emit(self, obj: Any) -> None:
        self.items.append(obj)

    def print(self, obj: Any) -> None:
        self.emit(obj)

    def one(self) -> Any:
        if len(self.items) != 1:
            raise RuntimeError(f"Internal error: expected exactly 1 output object, got {len(self.items)}")
        return self.items[0]


def _command_variant(args: argparse.Namespace) -> str:
    cmd = str(getattr(args, "cmd", "") or "")
    if cmd == "post":
        post_cmd = str(getattr(args, "post_cmd", "") or "")
        if post_cmd == "body":
            body_cmd = str(getattr(args, "body_cmd", "") or "")
            return f"post.body.{body_cmd}" if body_cmd else "post.body"
        if post_cmd == "freepik":
            freepik_cmd = str(getattr(args, "post_freepik_cmd", "") or "")
            return f"post.freepik.{freepik_cmd}" if freepik_cmd else "post.freepik"
        if post_cmd == "bodylex":
            bodylex_cmd = str(getattr(args, "bodylex_cmd", "") or "")
            bodylex_image_cmd = str(getattr(args, "bodylex_image_cmd", "") or "")
            bodylex_scaffold_cmd = str(getattr(args, "bodylex_scaffold_cmd", "") or "")
            if bodylex_cmd == "image" and bodylex_image_cmd:
                return f"post.bodylex.image.{bodylex_image_cmd}"
            if bodylex_cmd == "scaffold" and bodylex_scaffold_cmd:
                return f"post.bodylex.scaffold.{bodylex_scaffold_cmd}"
            return f"post.bodylex.{bodylex_cmd}" if bodylex_cmd else "post.bodylex"
        if post_cmd == "bodymob":
            bodymob_cmd = str(getattr(args, "bodymob_cmd", "") or "")
            bodymob_image_cmd = str(getattr(args, "bodymob_image_cmd", "") or "")
            if bodymob_cmd == "image" and bodymob_image_cmd:
                return f"post.bodymob.image.{bodymob_image_cmd}"
            return f"post.bodymob.{bodymob_cmd}" if bodymob_cmd else "post.bodymob"
        return f"post.{post_cmd}" if post_cmd else "post"
    if cmd == "page":
        page_cmd = str(getattr(args, "page_cmd", "") or "")
        return f"page.{page_cmd}" if page_cmd else "page"
    if cmd == "member":
        member_cmd = str(getattr(args, "member_cmd", "") or "")
        return f"member.{member_cmd}" if member_cmd else "member"
    if cmd == "newsletter":
        newsletter_cmd = str(getattr(args, "newsletter_cmd", "") or "")
        return f"newsletter.{newsletter_cmd}" if newsletter_cmd else "newsletter"
    if cmd == "tag":
        tag_cmd = str(getattr(args, "tag_cmd", "") or "")
        return f"tag.{tag_cmd}" if tag_cmd else "tag"
    if cmd == "tier":
        tier_cmd = str(getattr(args, "tier_cmd", "") or "")
        return f"tier.{tier_cmd}" if tier_cmd else "tier"
    if cmd == "offer":
        offer_cmd = str(getattr(args, "offer_cmd", "") or "")
        return f"offer.{offer_cmd}" if offer_cmd else "offer"
    if cmd == "theme":
        theme_cmd = str(getattr(args, "theme_cmd", "") or "")
        return f"theme.{theme_cmd}" if theme_cmd else "theme"
    if cmd == "webhook":
        webhook_cmd = str(getattr(args, "webhook_cmd", "") or "")
        return f"webhook.{webhook_cmd}" if webhook_cmd else "webhook"
    if cmd == "image":
        image_cmd = str(getattr(args, "image_cmd", "") or "")
        return f"image.{image_cmd}" if image_cmd else "image"
    if cmd == "jobs":
        jobs_cmd = str(getattr(args, "jobs_cmd", "") or "")
        return f"jobs.{jobs_cmd}" if jobs_cmd else "jobs"
    return cmd


def _webhook_ledger_rows(*, env_file: str, run_id: str | None) -> list[dict[str, Any]]:
    if not env_file:
        return []
    ledger_path = webhooks_index_path_for_env_file(env_file)
    rows = iter_webhook_rows(ledger_path)
    if not run_id:
        return rows[-3:]
    return [row for row in rows if str(row.get("run_id") or "") == str(run_id)][-3:]


def _snapshot_restore_recovery(*, backup_root: str | None, snapshot_records: list[dict[str, Any]], for_apply: bool) -> dict[str, Any]:
    backups = [{"type": "snapshot_dir", "path": backup_root}] if backup_root else []
    rollback_plan: dict[str, Any] = {
        "type": "manual_restore_from_snapshot",
        "notes": "Use the saved __before.json snapshot together with the matching __meta.json file to rebuild the prior state with a new reviewed write command.",
    }
    if backup_root:
        rollback_plan["artifacts_dir"] = backup_root
    if for_apply and snapshot_records:
        rollback_plan["meta_paths"] = [row.get("meta") for row in snapshot_records if row.get("meta")]
    else:
        rollback_plan["artifacts_expected_on_apply"] = ["__before.json", "__after.json", "__meta.json"]
    return {
        "end_state": "snapshot_plus_restore",
        "strategy": "restore_from_local_snapshots",
        "rollback_ready": bool(snapshot_records) if for_apply else False,
        "rollback_plan": rollback_plan,
        "backups": backups,
        "snapshots": snapshot_records,
        "restore_note": "This write family keeps local snapshot files under backup-snapshots/ so you can restore from the saved before-state after apply.",
    }


def _irreversible_recovery(*, reason: str) -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "rollback_plan": None,
        "backups": [],
        "snapshots": [],
        "restore_note": reason,
    }


def _webhook_recovery(*, env_file: str, run_id: str | None, for_apply: bool) -> dict[str, Any]:
    ledger_path = str(webhooks_index_path_for_env_file(env_file)) if env_file else None
    recovery = {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "ledger_only_proof",
        "rollback_ready": False,
        "rollback_plan": None,
        "backups": [],
        "snapshots": [],
        "restore_note": "Ghost has no webhook get/list endpoint. This tool stores a local ledger row for proof, but it does not create a restorable snapshot or direct undo path for webhook writes.",
        "ledger_path": ledger_path,
    }
    if for_apply and env_file:
        recovery["ledger_rows"] = _webhook_ledger_rows(env_file=env_file, run_id=run_id)
    return recovery


def _live_apply_before_state_block_reason(*, args: argparse.Namespace, raw_plan: dict[str, Any] | None = None) -> str | None:
    if bool(getattr(args, "apply", False)) and bool(getattr(args, "ack_no_snapshot", False)):
        return None
    variant = _command_variant(args)
    blocked_variants = {
        "webhook.create",
        "webhook.update",
        "webhook.delete",
        "theme.upload",
        "theme.activate",
        "jobs.run",
        "image.upload",
        "post.create",
        "post.copy",
        "page.create",
        "page.copy",
        "member.create",
        "member.import",
        "newsletter.create",
        "tag.create",
        "tier.create",
        "offer.create",
    }
    if variant in blocked_variants:
        return (
            f"{variant} has no saved before-state snapshot. Review the dry-run plan and pass "
            "--ack-no-snapshot only when the approved change should continue without an automatic restore point."
        )

    if variant == "page.sync-md":
        actions = raw_plan.get("actions") if isinstance(raw_plan, dict) else None
        if isinstance(actions, list):
            action_names = {str(row.get('action')) for row in actions if isinstance(row, dict)}
            if "create" in action_names and "delete" not in action_names:
                return (
                    "page.sync-md would create a brand-new page, so there is no current page state to save. "
                    "Review the dry-run plan and pass --ack-no-snapshot only when the approved change should "
                    "continue without an automatic restore point."
                )

    return None


def _annotate_before_state_apply_gate(*, args: argparse.Namespace, raw_plan: Any) -> tuple[Any, str | None]:
    if not isinstance(raw_plan, dict):
        return raw_plan, None
    reason = _live_apply_before_state_block_reason(args=args, raw_plan=raw_plan)
    if not reason:
        return raw_plan, None
    annotated = dict(raw_plan)
    annotated["before_state_apply_gate"] = {"blocked": True, "reason": reason}
    return annotated, reason


def _is_irreversible_write_family(args: argparse.Namespace) -> tuple[bool, str | None]:
    variant = _command_variant(args)
    if variant.startswith("webhook."):
        return True, "Webhook writes are proof-only here: Ghost does not expose a read-back endpoint and this tool does not keep restorable snapshots for them."
    if variant in {"theme.upload", "theme.activate"}:
        return True, "Theme writes are clearly labeled as high-impact, but this tool does not keep enough before-state to offer a direct restore path for them."
    if variant == "jobs.run":
        return True, "Batch jobs can mix many write rows, including publish-like actions, so the wrapper run stays clearly labeled instead of promising one generic rollback path."
    if variant == "image.upload":
        return True, "Image uploads create new storage objects and this tool does not offer a direct undo or restore flow for them."
    if variant in {"post.create", "post.copy", "page.create", "page.copy"}:
        return True, "Create and copy flows in this CLI do not expose a direct inverse action or a full restore path."
    if variant in {"member.create", "member.import", "newsletter.create", "tag.create", "tier.create", "offer.create"}:
        return True, "This write family can change or create resources, but this CLI does not expose a direct inverse action or a full restore path for it."
    if variant == "post.set-status" and (bool(getattr(args, "newsletter", None)) or bool(getattr(args, "email_only", False))):
        return True, "Publishing with newsletter delivery can trigger email sends, so this write family stays clearly labeled as irreversible here."
    if variant == "post.freepik.apply-one" and bool(getattr(args, "publish", False)):
        return True, "Publishing as part of the Freepik apply flow can make the change public immediately, so this path stays clearly labeled as irreversible here."
    return False, None


def _recovery_contract_for_command(
    *,
    args: argparse.Namespace,
    backup_root: str | None,
    env_file: str,
    run_id: str | None,
    backup: SnapshotWriter | None,
    for_apply: bool,
) -> dict[str, Any]:
    variant = _command_variant(args)
    if variant.startswith("webhook."):
        return _webhook_recovery(env_file=env_file, run_id=run_id, for_apply=for_apply)

    irreversible, reason = _is_irreversible_write_family(args)
    if irreversible:
        return _irreversible_recovery(reason=reason or "This write family is intentionally labeled as irreversible in this CLI.")

    snapshot_records = backup.records() if backup is not None else []
    return _snapshot_restore_recovery(
        backup_root=backup_root,
        snapshot_records=snapshot_records,
        for_apply=for_apply,
    )


def _inject_recovery_fields(obj: dict[str, Any], *, recovery: dict[str, Any], for_apply: bool) -> dict[str, Any]:
    merged = dict(obj)
    merged.setdefault("recovery", recovery)
    if for_apply:
        merged.setdefault("backups", recovery.get("backups", []))
        merged.setdefault("rollback_plan", recovery.get("rollback_plan"))
    target_key = "receipt" if for_apply else "plan"
    nested = merged.get(target_key)
    if isinstance(nested, dict):
        nested_out = dict(nested)
        nested_out.setdefault("recovery", recovery)
        if for_apply:
            nested_out.setdefault("backups", recovery.get("backups", []))
            nested_out.setdefault("rollback_plan", recovery.get("rollback_plan"))
        merged[target_key] = nested_out
    return merged


def _build_live_output_postprocess(
    *,
    args: argparse.Namespace,
    backup_root: str | None,
    env_file: str,
    run_id: str | None,
    backup: SnapshotWriter | None,
) -> Any:
    def _postprocess(obj: dict[str, Any]) -> dict[str, Any]:
        apply_flag = bool(obj.get("apply")) if isinstance(obj.get("apply"), bool) else False
        for_apply = bool(obj.get("applied")) or apply_flag or isinstance(obj.get("receipt"), dict)
        recovery = _recovery_contract_for_command(
            args=args,
            backup_root=backup_root,
            env_file=env_file,
            run_id=run_id,
            backup=backup,
            for_apply=for_apply,
        )
        return _inject_recovery_fields(obj, recovery=recovery, for_apply=for_apply)

    return _postprocess


def _build_plan(
    *,
    raw_plan: Any,
    tool: str,
    version: str,
    command: str,
    env_fingerprint: str,
    selector: dict[str, Any],
    risk_level: str,
    risk_reasons: list[str],
    recovery: dict[str, Any],
) -> dict[str, Any]:
    raw_with_recovery = (
        _inject_recovery_fields(raw_plan, recovery=recovery, for_apply=False) if isinstance(raw_plan, dict) else raw_plan
    )
    raw_sanitized = _normalize_output_obj(_sanitize_artifact(raw_with_recovery))
    raw_sha = _canonical_sha256(_strip_provenance(raw_sanitized))
    proposed = None
    if isinstance(raw_sanitized, dict):
        proposed = raw_sanitized.get("changes") or raw_sanitized.get("planned") or raw_sanitized.get("to_delete")
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "raw_plan_sha256 must match recomputed plan for apply"],
        "baseline": {"env_fingerprint": env_fingerprint, "selector": selector, "raw_plan_sha256": raw_sha},
        "proposed_changes": proposed,
        "verification_plan": {
            "type": "read_back_or_idempotence",
            "notes": "This tool verifies writes and raises on mismatch; see receipt.verification.",
        },
        "recovery": recovery,
        "rollback": {
            "supported": str(recovery.get("end_state") or "") == "snapshot_plus_restore",
            "notes": recovery.get("restore_note"),
        },
        "raw_plan": raw_sanitized,
    }


def _build_receipt(
    *,
    raw_receipt: Any,
    tool: str,
    version: str,
    command: str,
    env_fingerprint: str,
    selector: dict[str, Any],
    plan_sha256: str | None,
    recovery: dict[str, Any],
) -> dict[str, Any]:
    raw_with_recovery = (
        _inject_recovery_fields(raw_receipt, recovery=recovery, for_apply=True)
        if isinstance(raw_receipt, dict)
        else raw_receipt
    )
    raw_sanitized = _sanitize_artifact(raw_with_recovery)
    changed = None
    if isinstance(raw_sanitized, dict):
        if isinstance(raw_sanitized.get("changed"), bool):
            changed = bool(raw_sanitized.get("changed"))
        elif isinstance(raw_sanitized.get("changes"), list):
            changed = len(raw_sanitized.get("changes") or []) > 0
    return {
        "tool": tool,
        "version": version,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "selector": selector,
        "changed": changed,
        "verification": {
            "ok": True,
            "details": {
                "type": "read_back_or_idempotence",
                "notes": "Command completed without verification errors.",
            },
        },
        "diff_applied": None,
        "backups": recovery.get("backups", []),
        "rollback_plan": recovery.get("rollback_plan"),
        "recovery": recovery,
        "plan_raw_sha256": plan_sha256,
        "raw_receipt": raw_sanitized,
    }


def _write_artifacts(
    *,
    artifacts_dir: Path | None,
    plan_obj: dict[str, Any] | None,
    receipt_obj: dict[str, Any] | None,
    plan_out: str | None,
    receipt_out: str | None,
) -> tuple[str | None, str | None]:
    plan_path = None
    receipt_path = None

    if plan_obj is not None:
        if artifacts_dir is not None:
            plan_path = write_json_file(artifacts_dir / "plan.json", plan_obj)
        if plan_out:
            plan_path = write_json_file(plan_out, plan_obj)

    if receipt_obj is not None:
        if artifacts_dir is not None:
            receipt_path = write_json_file(artifacts_dir / "receipt.json", receipt_obj)
        if receipt_out:
            receipt_path = write_json_file(receipt_out, receipt_obj)

    return plan_path, receipt_path


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str | None,
    env_fingerprint: str | None,
    output_obj: dict[str, Any] | None,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
    apply: bool | None,
    yes: bool | None,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return

    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    plan_path = str(plan_file) if plan_file.exists() else None
    receipt_path = str(receipt_file) if receipt_file.exists() else None

    summary_lines = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=plan_path,
        receipt_path=receipt_path,
        audit_log_path=audit_log_path,
        audit_log_global_path=audit_log_global_path,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary_lines)

    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": tool,
            "version": version,
            "command": command,
            "env_fingerprint": env_fingerprint,
            "dry_run": bool(output_obj.get("dry_run")) if isinstance(output_obj, dict) else None,
            "apply": apply,
            "yes": yes,
            "ok": bool(output_obj.get("ok")) if isinstance(output_obj, dict) else None,
            "refused": bool(output_obj.get("refused")) if isinstance(output_obj, dict) else False,
            "plan_path": plan_path,
            "receipt_path": receipt_path,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )


def _cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary = None
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = (Path(ad) / "summary.md")
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def build_parser() -> argparse.ArgumentParser:
    class _JsonAwareParser(argparse.ArgumentParser):
        def parse_args(self, args=None, namespace=None):  # type: ignore[override]
            self._raw_args = list(args) if args is not None else sys.argv[1:]
            self._help_text = None
            return super().parse_args(args=args, namespace=namespace)

        def print_help(self, file=None) -> None:  # type: ignore[override]
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)):
                # Capture instead of printing (we emit JSON in main()).
                self._help_text = self.format_help()
                return
            return super().print_help(file=file)

        def exit(self, status=0, message=None) -> None:  # type: ignore[override]
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)) and getattr(self, "_help_text", None):
                raise _HelpRequested(help_text=str(getattr(self, "_help_text") or ""), code=int(status) if isinstance(status, int) else 0)
            return super().exit(status=status, message=message)

        def error(self, message: str) -> None:  # type: ignore[override]
            # In json mode: emit a single JSON error object via the normal exception handler.
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)):
                raise ValidationError(message)
            super().error(message)

    p = _JsonAwareParser(prog="ghost-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument(
        "--config",
        default=None,
        help="Optional non-secret project config JSON (paths/defaults). Use for customer projects; do not store API keys here.",
    )
    p.add_argument(
        "--project-dir",
        default=None,
        help="Optional project root dir for outputs. If omitted and --config is provided, defaults to the config file's directory; otherwise defaults to the current working directory.",
    )
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument(
        "--output",
        choices=("json", "text"),
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/status-change/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write computed plan JSON to a file (v2)")
    p.add_argument("--plan-in", default=None, help="Apply only if recomputed plan matches this file (v2)")
    p.add_argument("--receipt-out", default=None, help="Write receipt JSON to a file after apply (v2)")
    p.add_argument("--ack-irreversible", action="store_true", help="Additional acknowledgement for irreversible actions (v2)")
    p.add_argument("--ack-theme-change", action="store_true", help="Additional acknowledgement for theme activation (v2)")
    p.add_argument("--ack-no-verify", action="store_true", help="Acknowledge that verification may not be possible (v2)")
    p.add_argument("--run-id", default=None, help="Override run id for artifacts/history (v2)")
    p.add_argument("--artifacts-dir", default=None, help="Override artifacts dir (v2)")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing run artifacts/history (v2)")

    sub = p.add_subparsers(dest="cmd", parser_class=_JsonAwareParser)

    runs = sub.add_parser("runs", help="Local run history helpers")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_JsonAwareParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs (local)")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to list (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list)
    runs_show = runs_sub.add_parser("show", help="Show one run (local)")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--api-url",
        default=None,
        help='Optional: paste the non-secret "API URL" value from Ghost Integrations (example: https://your-site.ghost.io)',
    )
    onboarding.add_argument(
        "--accept-version",
        default="v5.0",
        help="Accept-Version to write into the env file (default: v5.0)",
    )
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding)

    content = sub.add_parser("content", help="Read-only Ghost Content API operations")
    content_sub = content.add_subparsers(dest="content_cmd", required=True, parser_class=_JsonAwareParser)
    content_cmd.add_content_commands(content_sub, parser_class=_JsonAwareParser)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_JsonAwareParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials (/admin/posts?limit=1)")
    auth_check.add_argument(
        "--full-site",
        action="store_true",
        help="Print full /site payload (may include extra fields)",
    )
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    post = sub.add_parser("post", help="Post operations")
    post_sub = post.add_subparsers(dest="post_cmd", required=True, parser_class=_JsonAwareParser)
    post_cmd.add_post_commands(post_sub)

    page = sub.add_parser("page", help="Page operations")
    page_sub = page.add_subparsers(dest="page_cmd", required=True, parser_class=_JsonAwareParser)
    page_cmd.add_page_commands(page_sub)

    image = sub.add_parser("image", help="Image upload operations")
    image_sub = image.add_subparsers(dest="image_cmd", required=True, parser_class=_JsonAwareParser)
    image_cmd.add_image_commands(image_sub)

    tag = sub.add_parser("tag", help="Tag operations")
    tag_sub = tag.add_subparsers(dest="tag_cmd", required=True, parser_class=_JsonAwareParser)
    tag_cmd.add_tag_commands(tag_sub)

    tier = sub.add_parser("tier", help="Tier operations")
    tier_sub = tier.add_subparsers(dest="tier_cmd", required=True, parser_class=_JsonAwareParser)
    tier_cmd.add_tier_commands(tier_sub)

    offer = sub.add_parser("offer", help="Offer operations")
    offer_sub = offer.add_subparsers(dest="offer_cmd", required=True, parser_class=_JsonAwareParser)
    offer_cmd.add_offer_commands(offer_sub)

    theme = sub.add_parser("theme", help="Theme operations")
    theme_sub = theme.add_subparsers(dest="theme_cmd", required=True, parser_class=_JsonAwareParser)
    theme_cmd.add_theme_commands(theme_sub)

    webhook = sub.add_parser("webhook", help="Webhook operations")
    webhook_sub = webhook.add_subparsers(dest="webhook_cmd", required=True, parser_class=_JsonAwareParser)
    webhook_cmd.add_webhook_commands(webhook_sub)

    newsletter = sub.add_parser("newsletter", help="Newsletter operations")
    newsletter_sub = newsletter.add_subparsers(dest="newsletter_cmd", required=True, parser_class=_JsonAwareParser)
    newsletter_cmd.add_newsletter_commands(newsletter_sub)

    member = sub.add_parser("member", help="Member operations")
    member_sub = member.add_subparsers(dest="member_cmd", required=True, parser_class=_JsonAwareParser)
    member_cmd.add_member_commands(member_sub)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_JsonAwareParser)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (dry-run by default)")
    jobs_run.add_argument("--file", required=True, help="Path to job file (.csv)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of job rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_peek_output_mode(argv))
    audit: Any = AuditLogger(path=None, enabled=False)
    run_ctx: RunContext = RunContext(enabled=False, run_id=None, artifacts_dir=None, runs_index_path=None, audit_log_path=None)
    run_audit_log_path: str | None = None
    global_audit_log_path: str | None = None
    runs_index_path: Any = None
    args: Any = argparse.Namespace(
        output=_peek_output_mode(argv),
        debug=False,
        apply=False,
        yes=False,
        plan_out=None,
        receipt_out=None,
    )

    try:
        try:
            args = parser.parse_args(argv)
        except _HelpRequested as e:
            if _peek_output_mode(argv) == "json":
                out.emit({"ok": True, "kind": "help", "help": str(e.help_text or "")})
            else:
                sys.stdout.write(str(e.help_text or ""))
                if not str(e.help_text or "").endswith("\n"):
                    sys.stdout.write("\n")
            return 0
        except SystemExit as e:
            # argparse already printed help/usage to stderr.
            return int(e.code) if isinstance(e.code, int) else 1

        runs_index_path = runs_index_path_for_env_file(str(args.env_file))
        write_capable = _is_write_capable(args)
        run_ctx = init_run_context(
            env_file=str(args.env_file),
            enabled=write_capable,
            run_id=str(args.run_id) if args.run_id else None,
            artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
            no_artifacts=bool(args.no_artifacts),
        )
        run_audit_log_path = str(run_ctx.audit_log_path) if (run_ctx.enabled and run_ctx.audit_log_path) else None
        global_audit_log_path = str(args.log_file) if args.log_file else None

        loggers: list[AuditLogger] = []
        if run_audit_log_path:
            loggers.append(AuditLogger(path=run_audit_log_path, enabled=True))
        if global_audit_log_path:
            loggers.append(AuditLogger(path=global_audit_log_path, enabled=True))
        audit = (
            CompositeAuditLogger(loggers)
            if len(loggers) > 1
            else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))
        )

        # `runs` is local-only and should not create a run context.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            run_ctx = RunContext(
                enabled=False,
                run_id=None,
                artifacts_dir=None,
                runs_index_path=runs_index_path,
                audit_log_path=None,
            )

        out.set_provenance(
            {
                "run_id": run_ctx.run_id,
                "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
                "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
                "audit_log": run_audit_log_path or global_audit_log_path,
                "audit_log_global": global_audit_log_path,
            }
        )

        if bool(args.version):
            payload = {"ok": True, "tool": "ghost-api-tool", "version": __version__}
            if str(getattr(args, "output", "json")) == "json":
                out.emit(payload)
            else:
                print(f"ghost-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        safe_argv = _safe_argv(argv)
        command_str = "ghost-api-tool " + " ".join(safe_argv)

        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
            project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
            if not str(getattr(args, "project_dir", "") or "").strip():
                project_dir = cfg_base_dir or Path.cwd()
            project_dir = project_dir.resolve()
            ctx = {
                "cfg": None,
                "content_cfg": None,
                "out": out,
                "audit": audit,
                "tool": "ghost-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "env_file": str(args.env_file),
                "runs_index_path": runs_index_path,
                "project_cfg": project_cfg,
                "project_dir": str(project_dir),
            }
            return int(args.func(args, ctx))

        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()

        def _domain_from_api_url(api_url: str) -> str | None:
            try:
                from urllib.parse import urlsplit

                return urlsplit(str(api_url or "")).hostname
            except Exception:
                return None

        cmd = str(getattr(args, "cmd", "") or "")
        cfg = None
        content_cfg = None
        backup_root = Path(args.env_file).resolve().parent / "backup-snapshots"
        backup = None
        env_fingerprint = None
        timeout_s = 30.0

        if cmd == "content":
            content_cfg = load_content_config(args.env_file)
            timeout_s = float(args.timeout_s) if args.timeout_s is not None else content_cfg.timeout_s
            env_fingerprint = _domain_from_api_url(content_cfg.content_api_url)
        else:
            cfg = load_config(args.env_file)
            timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
            backup = SnapshotWriter(
                root_dir=backup_root,
                domain=domain_from_admin_api_url(cfg.admin_api_url),
                enabled=bool(write_capable),
            )
            env_fingerprint = domain_from_admin_api_url(cfg.admin_api_url)

        selector = _extract_selector(args)
        risk_level, risk_reasons = _risk_level_from_argv(argv)

        plan_out = args.plan_out
        receipt_out = args.receipt_out

        out.set_provenance(
            {
                "run_id": run_ctx.run_id,
                "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
                "runs_index": str(run_ctx.runs_index_path or runs_index_path) if (run_ctx.runs_index_path or runs_index_path) else None,
                "audit_log": run_audit_log_path or global_audit_log_path,
                "audit_log_global": global_audit_log_path,
                "_postprocess": (
                    _build_live_output_postprocess(
                        args=args,
                        backup_root=str(backup_root),
                        env_file=str(args.env_file),
                        run_id=run_ctx.run_id,
                        backup=backup,
                    )
                    if write_capable
                    else None
                ),
            }
        )

        ctx = {
            "cfg": cfg,
            "content_cfg": content_cfg,
            "out": out,
            "audit": audit,
            "backup": backup,
            "backup_root": str(backup_root),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "plan_out": plan_out,
            "plan_in": args.plan_in,
            "receipt_out": receipt_out,
            "ack_irreversible": bool(args.ack_irreversible),
            "ack_theme_change": bool(getattr(args, "ack_theme_change", False)),
            "ack_no_verify": bool(getattr(args, "ack_no_verify", False)),
            "tool": "ghost-api-tool",
            "tool_version": __version__,
            "command_str": command_str,
            "env_fingerprint": env_fingerprint,
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index_path": run_ctx.runs_index_path or runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
        }

        audit.bind_context(
            {
                "tool": "ghost-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": env_fingerprint,
                "run_id": run_ctx.run_id,
            }
        )

        plan_obj: dict[str, Any] | None = None
        plan_sha: str | None = None

        if write_capable:
            audit.write(
                "run.start",
                {
                    "risk_level": risk_level,
                    "risk_reasons": risk_reasons,
                    "selector": selector,
                    "apply": bool(args.apply),
                    "yes": bool(args.yes),
                    "ack_no_snapshot": bool(args.ack_no_snapshot),
                    "plan_in": bool(args.plan_in),
                    "ack_irreversible": bool(args.ack_irreversible),
                },
            )

        if write_capable and bool(args.apply):
            # Apply path: compute a dry-run plan first (for proof + drift detection).
            preflight_out = _CaptureOutput()
            preflight_ctx = dict(ctx)
            preflight_ctx["apply"] = False
            preflight_ctx["out"] = preflight_out
            preflight_ctx["audit"] = _NoopAudit()
            preflight_ctx["backup"] = SnapshotWriter(
                root_dir=backup_root,
                domain=domain_from_admin_api_url(cfg.admin_api_url),
                enabled=True,
            )
            _ = int(args.func(args, preflight_ctx))
            raw_plan = preflight_out.one()
            raw_plan, blocked_before_state_reason = _annotate_before_state_apply_gate(args=args, raw_plan=raw_plan)
            plan_recovery = _recovery_contract_for_command(
                args=args,
                backup_root=str(backup_root),
                env_file=str(args.env_file),
                run_id=run_ctx.run_id,
                backup=preflight_ctx.get("backup"),
                for_apply=False,
            )
            plan_obj = _build_plan(
                raw_plan=raw_plan,
                tool="ghost-api-tool",
                version=__version__,
                command=command_str,
                env_fingerprint=env_fingerprint,
                selector=selector,
                risk_level=risk_level,
                risk_reasons=risk_reasons,
                recovery=plan_recovery,
            )
            plan_sha = (plan_obj.get("baseline") or {}).get("raw_plan_sha256")

            # High/irreversible applies require explicit confirmations and a saved plan.
            if risk_level in {"high", "irreversible"}:
                if not bool(args.yes):
                    out.emit(
                        {
                            "ok": True,
                            "dry_run": False,
                            "refused": True,
                            "reasons": [f"Refused: {risk_level} risk apply requires --yes"],
                            "refusal_type": "SafetyError",
                            "risk_level": risk_level,
                        }
                    )
                    if run_ctx.enabled:
                        _write_artifacts(
                            artifacts_dir=run_ctx.artifacts_dir,
                            plan_obj=plan_obj,
                            receipt_obj=None,
                            plan_out=plan_out,
                            receipt_out=None,
                        )
                        _finalize_run_artifacts(
                            run_ctx=run_ctx,
                            tool="ghost-api-tool",
                            version=__version__,
                            command=command_str,
                            env_fingerprint=env_fingerprint,
                            output_obj=out.last if isinstance(out.last, dict) else None,
                            audit_log_path=run_audit_log_path or global_audit_log_path,
                            audit_log_global_path=global_audit_log_path,
                            apply=bool(args.apply),
                            yes=bool(args.yes),
                        )
                    audit.write("run.end", {"ok": True, "refused": True})
                    return 0

                if not args.plan_in:
                    out.emit(
                        {
                            "ok": True,
                            "dry_run": False,
                            "refused": True,
                            "reasons": [f"Refused: {risk_level} risk apply requires --plan-in (apply a reviewed plan)"],
                            "refusal_type": "SafetyError",
                            "risk_level": risk_level,
                        }
                    )
                    if run_ctx.enabled:
                        _write_artifacts(
                            artifacts_dir=run_ctx.artifacts_dir,
                            plan_obj=plan_obj,
                            receipt_obj=None,
                            plan_out=plan_out,
                            receipt_out=None,
                        )
                        _finalize_run_artifacts(
                            run_ctx=run_ctx,
                            tool="ghost-api-tool",
                            version=__version__,
                            command=command_str,
                            env_fingerprint=env_fingerprint,
                            output_obj=out.last if isinstance(out.last, dict) else None,
                            audit_log_path=run_audit_log_path or global_audit_log_path,
                            audit_log_global_path=global_audit_log_path,
                            apply=bool(args.apply),
                            yes=bool(args.yes),
                        )
                    audit.write("run.end", {"ok": True, "refused": True})
                    return 0

                if risk_level == "irreversible" and not bool(args.ack_irreversible):
                    out.emit(
                        {
                            "ok": True,
                            "dry_run": False,
                            "refused": True,
                            "reasons": ["Refused: irreversible action requires --ack-irreversible"],
                            "refusal_type": "SafetyError",
                            "risk_level": risk_level,
                        }
                    )
                    if run_ctx.enabled:
                        _write_artifacts(
                            artifacts_dir=run_ctx.artifacts_dir,
                            plan_obj=plan_obj,
                            receipt_obj=None,
                            plan_out=plan_out,
                            receipt_out=None,
                        )
                        _finalize_run_artifacts(
                            run_ctx=run_ctx,
                            tool="ghost-api-tool",
                            version=__version__,
                            command=command_str,
                            env_fingerprint=env_fingerprint,
                            output_obj=out.last if isinstance(out.last, dict) else None,
                            audit_log_path=run_audit_log_path or global_audit_log_path,
                            audit_log_global_path=global_audit_log_path,
                            apply=bool(args.apply),
                            yes=bool(args.yes),
                        )
                    audit.write("run.end", {"ok": True, "refused": True})
                    return 0

            if args.plan_in:
                plan_in_obj = read_json_file(args.plan_in)
                if not isinstance(plan_in_obj, dict):
                    raise ValidationError("Plan file must be a JSON object")
                baseline = plan_in_obj.get("baseline")
                expected_sha = baseline.get("raw_plan_sha256") if isinstance(baseline, dict) else None
                if not expected_sha:
                    expected_sha = _canonical_sha256(_sanitize_artifact(plan_in_obj))
                if str(expected_sha) != str(plan_sha):
                    out.emit(
                        {
                            "ok": True,
                            "refused": True,
                            "reasons": [
                                "Refused: plan drift detected (recomputed plan does not match --plan-in). Re-run without --apply to generate a fresh plan.",
                            ],
                            "refusal_type": "SafetyError",
                            "expected_raw_plan_sha256": expected_sha,
                            "actual_raw_plan_sha256": plan_sha,
                        }
                    )
                    if run_ctx.enabled:
                        _write_artifacts(
                            artifacts_dir=run_ctx.artifacts_dir,
                            plan_obj=plan_obj,
                            receipt_obj=None,
                            plan_out=plan_out,
                            receipt_out=None,
                        )
                        _finalize_run_artifacts(
                            run_ctx=run_ctx,
                            tool="ghost-api-tool",
                            version=__version__,
                            command=command_str,
                            env_fingerprint=env_fingerprint,
                            output_obj=out.last if isinstance(out.last, dict) else None,
                            audit_log_path=run_audit_log_path or global_audit_log_path,
                            audit_log_global_path=global_audit_log_path,
                            apply=bool(args.apply),
                            yes=bool(args.yes),
                        )
                    return 0

            # Always write the plan proof for write-capable apply attempts.
            _write_artifacts(
                artifacts_dir=run_ctx.artifacts_dir if run_ctx.enabled else None,
                plan_obj=plan_obj,
                receipt_obj=None,
                plan_out=plan_out,
                receipt_out=None,
            )

            if blocked_before_state_reason:
                out.emit(
                    {
                        "ok": True,
                        "refused": True,
                        "reasons": [f"Refused: {blocked_before_state_reason}"],
                        "refusal_type": "SafetyError",
                    }
                )
                if run_ctx.enabled:
                    _finalize_run_artifacts(
                        run_ctx=run_ctx,
                        tool="ghost-api-tool",
                        version=__version__,
                        command=command_str,
                        env_fingerprint=env_fingerprint,
                        output_obj=out.last if isinstance(out.last, dict) else None,
                        audit_log_path=run_audit_log_path or global_audit_log_path,
                        audit_log_global_path=global_audit_log_path,
                        apply=bool(args.apply),
                        yes=bool(args.yes),
                    )
                audit.write("run.end", {"ok": True, "refused": True})
                return 0

        rc = int(args.func(args, ctx))

        # Dry-run path: write plan proof based on the actual command output.
        if write_capable and not bool(args.apply):
            raw_plan = out.last
            raw_plan, _ = _annotate_before_state_apply_gate(args=args, raw_plan=raw_plan)
            if raw_plan is not out.last and isinstance(out.last, dict):
                out.last.clear()
                out.last.update(raw_plan)
            plan_recovery = _recovery_contract_for_command(
                args=args,
                backup_root=str(backup_root),
                env_file=str(args.env_file),
                run_id=run_ctx.run_id,
                backup=ctx.get("backup"),
                for_apply=False,
            )
            plan_obj = _build_plan(
                raw_plan=raw_plan,
                tool="ghost-api-tool",
                version=__version__,
                command=command_str,
                env_fingerprint=env_fingerprint,
                selector=selector,
                risk_level=risk_level,
                risk_reasons=risk_reasons,
                recovery=plan_recovery,
            )
            plan_sha = (plan_obj.get("baseline") or {}).get("raw_plan_sha256")
            _write_artifacts(
                artifacts_dir=run_ctx.artifacts_dir if run_ctx.enabled else None,
                plan_obj=plan_obj,
                receipt_obj=None,
                plan_out=plan_out,
                receipt_out=None,
            )

        if write_capable and bool(args.apply):
            receipt_recovery = _recovery_contract_for_command(
                args=args,
                backup_root=str(backup_root),
                env_file=str(args.env_file),
                run_id=run_ctx.run_id,
                backup=ctx.get("backup"),
                for_apply=True,
            )
            receipt_obj = _build_receipt(
                raw_receipt=out.last,
                tool="ghost-api-tool",
                version=__version__,
                command=command_str,
                env_fingerprint=env_fingerprint,
                selector=selector,
                plan_sha256=plan_sha,
                recovery=receipt_recovery,
            )
            _write_artifacts(
                artifacts_dir=run_ctx.artifacts_dir if run_ctx.enabled else None,
                plan_obj=None,
                receipt_obj=receipt_obj,
                plan_out=None,
                receipt_out=receipt_out,
            )

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="ghost-api-tool",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )

        if write_capable:
            audit.write(
                "run.end",
                {
                    "ok": bool(out.last.get("ok")) if isinstance(out.last, dict) else None,
                    "refused": bool(out.last.get("refused")) if isinstance(out.last, dict) else False,
                },
            )

        return rc
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except SafetyError as e:
        audit.write("refused", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="ghost-api-tool",
            version=__version__,
            command="ghost-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
        )
        audit.write("run.end", {"ok": True, "refused": True})
        return 0
    except ToolError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="ghost-api-tool",
            version=__version__,
            command="ghost-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
        )
        audit.write("run.end", {"ok": False, "error_type": type(e).__name__})
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(getattr(args, "debug", False)):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="ghost-api-tool",
            version=__version__,
            command="ghost-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
        )
        audit.write("run.end", {"ok": False, "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()
