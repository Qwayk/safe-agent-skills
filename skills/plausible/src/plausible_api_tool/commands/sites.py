from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .. import __version__
from ..plausible import PlausibleClient
from ..output import write_json_file
from ..recovery import build_inverse_recovery, build_irreversible_recovery


def _default_site_id(cfg, site_id: str | None) -> str:
    sid = (site_id or getattr(cfg, "site_id", "") or "").strip()
    if not sid:
        raise RuntimeError("Missing site id (provide --site-id or set PLAUSIBLE_SITE_ID)")
    return sid


def _now_utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _env_fingerprint(cfg) -> dict[str, str]:
    return {"base_url": str(getattr(cfg, "base_url", "")), "site_id": str(getattr(cfg, "site_id", ""))}


def _state_root(ctx: dict[str, Any]) -> Path | None:
    env_file = ctx.get("env_file")
    if not isinstance(env_file, str) or not env_file.strip():
        return None
    return Path(env_file).expanduser().resolve().parent / ".state" / "plausible"


def _capture_before_state(
    ctx: dict[str, Any],
    *,
    command: str,
    selector: dict[str, Any],
    before_state: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if before_state is None:
        return None, None
    record: dict[str, Any] = {
        "command": command,
        "captured_at_utc": _now_utc_iso(),
        "selector": selector,
        "before_state": before_state,
    }
    root = _state_root(ctx)
    if root is None:
        return record, None
    filename = f"before_state_{command.replace('.', '_')}_{time.time_ns()}.json"
    return record, write_json_file(str(root / filename), record)


def _write_plan_if_requested(ctx, plan: dict[str, Any]) -> str | None:
    if not ctx.get("plan_out"):
        return None
    return write_json_file(str(ctx["plan_out"]), plan)


def _write_receipt_if_requested(ctx, receipt: dict[str, Any]) -> str | None:
    if not ctx.get("receipt_out"):
        return None
    return write_json_file(str(ctx["receipt_out"]), receipt)


def _emit_validation_error(ctx, message: str) -> int:
    ctx["out"].emit({"ok": False, "error": message, "error_type": "ValidationError"})
    return 1


def _load_json_object_from_args(*, json_str: str | None, file_path: str | None, what: str) -> dict[str, Any] | None:
    if json_str and file_path:
        raise RuntimeError(f"Provide only one of: --{what} or --{what}-file")
    if file_path:
        raw = Path(str(file_path)).read_text(encoding="utf-8")
        obj = json.loads(raw)
    elif json_str:
        obj = json.loads(str(json_str))
    else:
        return None
    if not isinstance(obj, dict):
        raise RuntimeError(f"{what} must be a JSON object")
    return obj


def cmd_site_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.sites_list(
        after=getattr(args, "after", None),
        before=getattr(args, "before", None),
        limit=int(args.limit) if getattr(args, "limit", None) is not None else None,
        team_id=getattr(args, "team_id", None),
    )
    out = {"ok": True, "response": resp}
    ctx["audit"].write("site.list", {"after": getattr(args, "after", None), "before": getattr(args, "before", None)})
    ctx["out"].emit(out)
    return 0


def cmd_site_get(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    resp = client.site_get(site_id)
    out = {"ok": True, "site_id": site_id, "response": resp}
    ctx["audit"].write("site.get", {"site_id": site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_teams_list(_args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.sites_teams_list()
    out = {"ok": True, "response": resp}
    ctx["audit"].write("site.teams_list", {})
    ctx["out"].emit(out)
    return 0


def cmd_site_goals_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    resp = client.site_goals_list(
        site_id=site_id,
        after=getattr(args, "after", None),
        before=getattr(args, "before", None),
        limit=int(args.limit) if getattr(args, "limit", None) is not None else None,
    )
    out = {"ok": True, "site_id": site_id, "response": resp}
    ctx["audit"].write("site.goals_list", {"site_id": site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_custom_props_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    resp = client.site_custom_props_list(site_id=site_id)
    out = {"ok": True, "site_id": site_id, "response": resp}
    ctx["audit"].write("site.custom_props_list", {"site_id": site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_guests_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    resp = client.site_guests_list(
        site_id=site_id,
        after=getattr(args, "after", None),
        before=getattr(args, "before", None),
        limit=int(args.limit) if getattr(args, "limit", None) is not None else None,
    )
    out = {"ok": True, "site_id": site_id, "response": resp}
    ctx["audit"].write("site.guests_list", {"site_id": site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_create(args, ctx) -> int:
    cfg = ctx["cfg"]
    domain = str(args.domain or "").strip()
    if not domain:
        return _emit_validation_error(ctx, "--domain is required")

    tracker_cfg = _load_json_object_from_args(
        json_str=getattr(args, "tracker_config", None),
        file_path=getattr(args, "tracker_config_file", None),
        what="tracker-config",
    )

    payload: dict[str, Any] = {"domain": domain}
    if getattr(args, "timezone", None):
        payload["timezone"] = str(args.timezone)
    if getattr(args, "team_id", None):
        payload["team_id"] = str(args.team_id)
    if tracker_cfg is not None:
        payload["tracker_script_configuration"] = tracker_cfg

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"domain": domain}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            resp = pre_client.site_get(domain)
            before_snapshot = {"resource": "site", "present": True, "entry": resp}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "site", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.create",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site create",
        "selector": selector,
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the site settings are correct"],
        "proposed_changes": [{"action": "plausible.sites.create", "payload": payload}],
        "verification_plan": "GET /api/v1/sites/:site_id (site domain) and confirm fields match.",
        "rollback": {"supported": False, "notes": "Not supported: site deletion is destructive and irreversible."},
        "recovery": build_irreversible_recovery(),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path

    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes to create a site."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.create_refused", {"domain": domain})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to create a site without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_create(payload)

    verification: dict[str, Any]
    try:
        got = client.site_get(domain)
        verification = {"ok": True, "site_id": domain, "response": got}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "site_id": domain, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site create",
        "selector": {"domain": domain},
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.create", "created": {"domain": domain}}],
        "recovery": build_irreversible_recovery(),
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.create", {"domain": domain})
    ctx["out"].emit(out)
    return 0


def cmd_site_update(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    new_domain = (getattr(args, "domain", None) or "").strip() or None
    tracker_cfg = _load_json_object_from_args(
        json_str=getattr(args, "tracker_config", None),
        file_path=getattr(args, "tracker_config_file", None),
        what="tracker-config",
    )
    if new_domain is None and tracker_cfg is None:
        return _emit_validation_error(ctx, "Provide at least one change: --domain and/or --tracker-config/--tracker-config-file")

    payload: dict[str, Any] = {}
    if new_domain is not None:
        payload["domain"] = new_domain
    if tracker_cfg is not None:
        payload["tracker_script_configuration"] = tracker_cfg

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            before = pre_client.site_get(site_id)
            before_snapshot = {"resource": "site", "present": True, "entry": before}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "site", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.update",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site update",
        "selector": selector,
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the update is correct"],
        "proposed_changes": [{"action": "plausible.sites.update", "target": {"site_id": site_id}, "payload": payload}],
        "verification_plan": "GET /api/v1/sites/:site_id (new domain if changed) and confirm fields match.",
        "rollback": {"supported": False, "notes": "Not supported: some changes are not easily reversible."},
        "recovery": build_irreversible_recovery(),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes to update a site."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.update_refused", {"site_id": site_id})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to update a site without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_update(site_id, payload)
    verify_site_id = new_domain or site_id
    verification: dict[str, Any]
    try:
        got = client.site_get(verify_site_id)
        verification = {"ok": True, "site_id": verify_site_id, "response": got}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "site_id": verify_site_id, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site update",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.update", "updated": {"site_id": site_id, "new_domain": new_domain}}],
        "recovery": build_irreversible_recovery(),
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.update", {"site_id": site_id, "verify_site_id": verify_site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_delete(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            before = pre_client.site_get(site_id)
            before_snapshot = {"resource": "site", "present": True, "entry": before}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "site", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.delete",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site delete",
        "selector": selector,
        "risk_level": "irreversible",
        "risk_reasons": ["Deletes the site and all its data; Plausible deletion is permanent and may take time to complete."],
        "preconditions": ["Reviewed this plan and confirmed the site should be deleted", "Acknowledged the action is irreversible"],
        "proposed_changes": [{"action": "plausible.sites.delete", "target": {"site_id": site_id}}],
        "verification_plan": "Best-effort: list sites and confirm the site is absent.",
        "rollback": {"supported": False, "notes": "Not supported: site deletion is irreversible."},
        "recovery": build_irreversible_recovery(),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "risk_level": "irreversible",
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes --ack-irreversible to delete a site.", "Deletion is irreversible."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.delete_refused", {"site_id": site_id})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "Refusing to delete a site without --yes (this is destructive).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    if not bool(ctx.get("ack_irreversible", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "Refusing irreversible action without --ack-irreversible (site deletion cannot be undone).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_delete(site_id)
    verification: dict[str, Any]
    try:
        listed = client.sites_list(limit=100)
        domains = []
        sites = listed.get("sites") if isinstance(listed, dict) else None
        if isinstance(sites, list):
            for row in sites:
                if isinstance(row, dict) and isinstance(row.get("domain"), str):
                    domains.append(row["domain"])
        verification = {"ok": site_id not in set(domains), "check": "sites_list_absent", "site_id": site_id, "domains_sample": domains[:20]}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site delete",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.delete", "deleted": {"site_id": site_id}}],
        "recovery": build_irreversible_recovery(),
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "risk_level": "irreversible",
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.delete", {"site_id": site_id})
    ctx["out"].emit(out)
    return 0


def cmd_site_shared_links_ensure(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    name = str(getattr(args, "name", "") or "").strip()
    if not name:
        return _emit_validation_error(ctx, "--name is required")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "name": name}
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site shared-links ensure",
        "selector": selector,
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the shared link name is correct"],
        "proposed_changes": [{"action": "plausible.sites.shared_links.ensure", "payload": {"site_id": site_id, "name": name}}],
        "verification_plan": "Repeat the same idempotent PUT request and confirm response matches.",
        "rollback": {"supported": False, "notes": "Not supported via API: shared links are managed server-side."},
        "recovery": build_irreversible_recovery(),
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "reason": "Plausible shared-link ensure has no API read path for a restorable before-state snapshot.",
        },
    }
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes --ack-no-snapshot to create/ensure a shared link."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.shared_links.ensure_refused", {"site_id": site_id, "name": name})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to ensure a shared link without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1
    if not bool(ctx.get("ack_no_snapshot", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refused: shared-link ensure has no saved before-state snapshot. Review the dry-run plan and pass --ack-no-snapshot only when the approved change should continue without an automatic restore point.",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_shared_links_ensure(site_id=site_id, name=name)
    verification: dict[str, Any]
    try:
        again = client.site_shared_links_ensure(site_id=site_id, name=name)
        verification = {"ok": True, "idempotent": True, "second_response": again}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site shared-links ensure",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.shared_links.ensure", "ensured": selector}],
        "recovery": build_irreversible_recovery(),
        "before_state": plan["before_state"],
        "no_snapshot_approval": {
            "approved": bool(ctx.get("ack_no_snapshot")),
            "reason": "No saved before-state snapshot was available for this Plausible shared-link write.",
        },
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.shared_links.ensure", selector)
    ctx["out"].emit(out)
    return 0


def cmd_site_goals_ensure(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    goal_type = str(getattr(args, "goal_type", "") or "").strip()
    if goal_type not in ("event", "page"):
        return _emit_validation_error(ctx, "--goal-type must be one of: event, page")

    event_name = (getattr(args, "event_name", None) or "").strip() or None
    page_path = (getattr(args, "page_path", None) or "").strip() or None
    display_name = (getattr(args, "display_name", None) or "").strip() or None

    if goal_type == "event" and not event_name:
        return _emit_validation_error(ctx, "--event-name is required when --goal-type=event")
    if goal_type == "page" and not page_path:
        return _emit_validation_error(ctx, "--page-path is required when --goal-type=page")

    payload: dict[str, Any] = {"site_id": site_id, "goal_type": goal_type}
    if display_name is not None:
        payload["display_name"] = display_name
    if event_name is not None:
        payload["event_name"] = event_name
    if page_path is not None:
        payload["page_path"] = page_path

    env_fingerprint = _env_fingerprint(cfg)
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site goals ensure",
        "selector": {"site_id": site_id, "goal_type": goal_type, "display_name": display_name},
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the goal details are correct"],
        "proposed_changes": [{"action": "plausible.sites.goals.ensure", "payload": payload}],
        "verification_plan": f"GET /api/v1/sites/goals?site_id={site_id} and confirm the goal exists.",
        "rollback": {"supported": True, "notes": "Rollback requires deleting the goal by ID."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.goals.delete",
            rollback_ready=False,
            rollback_plan={"action": "plausible.sites.goals.delete", "target": {"site_id": site_id}},
        ),
    }
    selector = {"site_id": site_id, "goal_type": goal_type, "display_name": display_name, "event_name": event_name, "page_path": page_path}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_goals_list(site_id=site_id, limit=100)
            goals = listed.get("goals") if isinstance(listed, dict) else None
            matched: dict[str, Any] | None = None
            if isinstance(goals, list):
                for row in goals:
                    if not isinstance(row, dict):
                        continue
                    if str(row.get("goal_type") or "") != goal_type:
                        continue
                    if event_name and str(row.get("event_name") or "") == str(event_name):
                        matched = row
                        break
                    if page_path and str(row.get("page_path") or "") == str(page_path):
                        matched = row
                        break
                    if display_name and str(row.get("display_name") or "") == str(display_name):
                        matched = row
                        break
            before_snapshot = {"resource": "goal", "present": matched is not None, "entry": matched}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "goal", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.goals.ensure",
            selector=selector,
            before_state=before_snapshot,
        )
    plan["selector"] = selector
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes to create/ensure a goal."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.goals.ensure_refused", {"site_id": site_id, "goal_type": goal_type})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to ensure a goal without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_goal_ensure(
        site_id=site_id, goal_type=goal_type, event_name=event_name, page_path=page_path, display_name=display_name
    )
    verification: dict[str, Any]
    try:
        listed = client.site_goals_list(site_id=site_id, limit=100)
        goals = listed.get("goals") if isinstance(listed, dict) else None
        found = False
        if isinstance(goals, list):
            for row in goals:
                if not isinstance(row, dict):
                    continue
                if isinstance(resp, dict) and row.get("id") == resp.get("id"):
                    found = True
                    break
                if display_name and row.get("display_name") == display_name:
                    found = True
                    break
        verification = {"ok": found, "check": "goals_list_contains", "goal_id": resp.get("id") if isinstance(resp, dict) else None}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site goals ensure",
        "selector": {"site_id": site_id},
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.goals.ensure", "ensured": payload}],
        "rollback_plan": {"supported": True, "notes": "Delete the goal by ID if needed."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.goals.delete",
            rollback_ready=True,
            rollback_plan={
                "action": "plausible.sites.goals.delete",
                "target": {"site_id": site_id, "goal_id": (resp.get("id") if isinstance(resp, dict) else None)},
            },
        ),
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.goals.ensure", {"site_id": site_id, "goal_type": goal_type})
    ctx["out"].emit(out)
    return 0


def cmd_site_goals_delete(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    goal_id = str(getattr(args, "goal_id", "") or "").strip()
    if not goal_id:
        return _emit_validation_error(ctx, "--goal-id is required")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "goal_id": goal_id}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_goals_list(site_id=site_id, limit=100)
            goals = listed.get("goals") if isinstance(listed, dict) else None
            match: dict[str, Any] | None = None
            if isinstance(goals, list):
                for row in goals:
                    if not isinstance(row, dict):
                        continue
                    if str(row.get("id", "")) == str(goal_id):
                        match = row
                        break
            before_snapshot = {"resource": "goal", "present": match is not None, "entry": match}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "goal", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.goals.delete",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site goals delete",
        "selector": selector,
        "risk_level": "destructive",
        "preconditions": ["Reviewed this plan and confirmed the goal should be deleted", "Acknowledged the action is destructive"],
        "proposed_changes": [{"action": "plausible.sites.goals.delete", "target": selector}],
        "verification_plan": "Best-effort: list goals and confirm the goal id is absent.",
        "rollback": {"supported": False, "notes": "Not supported: goal deletion removes configuration; you can re-create it, but the ID will differ."},
        "recovery": build_irreversible_recovery(),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "risk_level": "destructive",
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes --ack-irreversible to delete a goal."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.goals.delete_refused", selector)
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing to delete a goal without --yes (this is destructive).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1
    if not bool(ctx.get("ack_irreversible", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing destructive action without --ack-irreversible.",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_goal_delete(goal_id=goal_id, site_id=site_id)
    verification: dict[str, Any]
    try:
        listed = client.site_goals_list(site_id=site_id, limit=100)
        goals = listed.get("goals") if isinstance(listed, dict) else None
        still_there = False
        if isinstance(goals, list):
            for row in goals:
                if isinstance(row, dict) and str(row.get("id", "")) == goal_id:
                    still_there = True
                    break
        verification = {"ok": not still_there, "check": "goals_list_absent", "goal_id": goal_id}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site goals delete",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.goals.delete", "deleted": selector}],
        "recovery": build_irreversible_recovery(),
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "risk_level": "destructive",
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.goals.delete", selector)
    ctx["out"].emit(out)
    return 0


def cmd_site_custom_props_ensure(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    prop_key = str(getattr(args, "property", "") or "").strip()
    if not prop_key:
        return _emit_validation_error(ctx, "--property is required")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "property": prop_key}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_custom_props_list(site_id=site_id)
            props = listed.get("custom_properties") if isinstance(listed, dict) else None
            match: dict[str, Any] | None = None
            if isinstance(props, list):
                for row in props:
                    if isinstance(row, dict) and row.get("property") == prop_key:
                        match = row
                        break
            before_snapshot = {"resource": "custom_prop", "present": match is not None, "entry": match}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "custom_prop", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.custom-props.ensure",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site custom-props ensure",
        "selector": selector,
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the custom property is correct"],
        "proposed_changes": [{"action": "plausible.sites.custom_props.ensure", "payload": selector}],
        "verification_plan": f"GET /api/v1/sites/custom-props?site_id={site_id} and confirm property exists.",
        "rollback": {"supported": True, "notes": "Rollback requires deleting the custom property by name."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.custom_props.delete",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.custom_props.delete", "target": selector},
        ),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes to create/ensure a custom property."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.custom_props.ensure_refused", selector)
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to ensure a custom property without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_custom_prop_ensure(site_id=site_id, prop_key=prop_key)
    verification: dict[str, Any]
    try:
        listed = client.site_custom_props_list(site_id=site_id)
        props = listed.get("custom_properties") if isinstance(listed, dict) else None
        found = False
        if isinstance(props, list):
            for row in props:
                if isinstance(row, dict) and row.get("property") == prop_key:
                    found = True
                    break
        verification = {"ok": found, "check": "custom_props_list_contains", "property": prop_key}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site custom-props ensure",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.custom_props.ensure", "ensured": selector}],
        "rollback_plan": {"supported": True, "notes": "Delete the custom property by name if needed."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.custom_props.delete",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.custom_props.delete", "target": selector},
        ),
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.custom_props.ensure", selector)
    ctx["out"].emit(out)
    return 0


def cmd_site_custom_props_delete(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    prop_key = str(getattr(args, "property", "") or "").strip()
    if not prop_key:
        return _emit_validation_error(ctx, "--property is required")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "property": prop_key}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_custom_props_list(site_id=site_id)
            props = listed.get("custom_properties") if isinstance(listed, dict) else None
            match: dict[str, Any] | None = None
            if isinstance(props, list):
                for row in props:
                    if isinstance(row, dict) and row.get("property") == prop_key:
                        match = row
                        break
            before_snapshot = {"resource": "custom_prop", "present": match is not None, "entry": match}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "custom_prop", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.custom-props.delete",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site custom-props delete",
        "selector": selector,
        "risk_level": "destructive",
        "preconditions": ["Reviewed this plan and confirmed the property should be deleted", "Acknowledged the action is destructive"],
        "proposed_changes": [{"action": "plausible.sites.custom_props.delete", "target": selector}],
        "verification_plan": "Best-effort: list custom properties and confirm property is absent.",
        "rollback": {"supported": True, "notes": "Rollback requires re-creating the custom property (idempotent)."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.custom_props.ensure",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.custom_props.ensure", "payload": selector},
        ),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "risk_level": "destructive",
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes --ack-irreversible to delete a custom property."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.custom_props.delete_refused", selector)
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing to delete a custom property without --yes (this is destructive).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1
    if not bool(ctx.get("ack_irreversible", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing destructive action without --ack-irreversible.",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_custom_prop_delete(site_id=site_id, prop_key=prop_key)
    verification: dict[str, Any]
    try:
        listed = client.site_custom_props_list(site_id=site_id)
        props = listed.get("custom_properties") if isinstance(listed, dict) else None
        still_there = False
        if isinstance(props, list):
            for row in props:
                if isinstance(row, dict) and row.get("property") == prop_key:
                    still_there = True
                    break
        verification = {"ok": not still_there, "check": "custom_props_list_absent", "property": prop_key}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site custom-props delete",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.custom_props.delete", "deleted": selector}],
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.custom_props.ensure",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.custom_props.ensure", "payload": selector},
        ),
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "risk_level": "destructive",
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.custom_props.delete", selector)
    ctx["out"].emit(out)
    return 0


def cmd_site_guests_ensure(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    email = str(getattr(args, "email", "") or "").strip()
    role = str(getattr(args, "role", "") or "").strip()
    if not email:
        return _emit_validation_error(ctx, "--email is required")
    if role not in ("viewer", "editor"):
        return _emit_validation_error(ctx, "--role must be one of: viewer, editor")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "email": email, "role": role}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_guests_list(site_id=site_id, limit=100)
            guests = listed.get("guests") if isinstance(listed, dict) else None
            match: dict[str, Any] | None = None
            if isinstance(guests, list):
                for row in guests:
                    if isinstance(row, dict) and str(row.get("email") or "") == email:
                        match = row
                        break
            before_snapshot = {"resource": "guest", "present": match is not None, "entry": match}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "guest", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.guests.ensure",
            selector=selector,
            before_state=before_snapshot,
        )
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site guests ensure",
        "selector": selector,
        "risk_level": "write",
        "preconditions": ["Reviewed this plan and confirmed the guest email/role are correct"],
        "proposed_changes": [{"action": "plausible.sites.guests.ensure", "payload": selector}],
        "verification_plan": f"GET /api/v1/sites/guests?site_id={site_id} and confirm email exists.",
        "rollback": {"supported": True, "notes": "Rollback requires deleting the guest membership (destructive)."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.guests.delete",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.guests.delete", "target": {"site_id": site_id, "email": email}},
        ),
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes to invite/ensure a guest."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.guests.ensure_refused", selector)
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "error": "Refusing to ensure a guest without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_guest_ensure(site_id=site_id, email=email, role=role)
    verification: dict[str, Any]
    try:
        listed = client.site_guests_list(site_id=site_id, limit=100)
        guests = listed.get("guests") if isinstance(listed, dict) else None
        found = False
        if isinstance(guests, list):
            for row in guests:
                if isinstance(row, dict) and row.get("email") == email:
                    found = True
                    break
        verification = {"ok": found, "check": "guests_list_contains", "email": email}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site guests ensure",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.guests.ensure", "ensured": selector}],
        "rollback_plan": {"supported": True, "notes": "Delete the guest by email if needed."},
        "recovery": build_inverse_recovery(
            strategy="plausible.sites.guests.delete",
            rollback_ready=True,
            rollback_plan={"action": "plausible.sites.guests.delete", "target": {"site_id": site_id, "email": email}},
        ),
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.guests.ensure", selector)
    ctx["out"].emit(out)
    return 0


def cmd_site_guests_delete(args, ctx) -> int:
    cfg = ctx["cfg"]
    site_id = _default_site_id(cfg, getattr(args, "site_id", None))
    email = str(getattr(args, "email", "") or "").strip()
    if not email:
        return _emit_validation_error(ctx, "--email is required")

    env_fingerprint = _env_fingerprint(cfg)
    selector = {"site_id": site_id, "email": email}
    before_state: dict[str, Any] | None = None
    before_state_path: str | None = None
    if ctx.get("http") is not None:
        pre_client = PlausibleClient(cfg=cfg, http=ctx["http"])
        before_snapshot: dict[str, Any]
        try:
            listed = pre_client.site_guests_list(site_id=site_id, limit=100)
            guests = listed.get("guests") if isinstance(listed, dict) else None
            match: dict[str, Any] | None = None
            if isinstance(guests, list):
                for row in guests:
                    if isinstance(row, dict) and str(row.get("email") or "") == email:
                        match = row
                        break
            before_snapshot = {"resource": "guest", "present": match is not None, "entry": match}
        except Exception as e:  # noqa: BLE001
            before_snapshot = {"resource": "guest", "present": False, "error_type": type(e).__name__, "error": str(e)}
        before_state, before_state_path = _capture_before_state(
            ctx,
            command="site.guests.delete",
            selector=selector,
            before_state=before_snapshot,
        )
    recovery = build_irreversible_recovery()
    rollback = {
        "supported": False,
        "notes": "Not supported: this command does not capture the guest's previous role, so it cannot build an exact inverse action.",
    }
    if before_state is not None:
        prev = before_state.get("before_state", {})
        if isinstance(prev, dict):
            entry = prev.get("entry")
            role = str((entry or {}).get("role") or "").strip() if isinstance(entry, dict) else ""
            if role in ("viewer", "editor"):
                recovery = build_inverse_recovery(
                    strategy="plausible.sites.guests.ensure",
                    rollback_ready=True,
                    rollback_plan={"action": "plausible.sites.guests.ensure", "target": {"site_id": site_id, "email": email, "role": role}},
                )
                rollback = {"supported": True, "notes": "Rollback uses the captured previous role via site_guest_ensure."}
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site guests delete",
        "selector": selector,
        "risk_level": "destructive",
        "preconditions": ["Reviewed this plan and confirmed the guest should be removed", "Acknowledged the action is destructive"],
        "proposed_changes": [{"action": "plausible.sites.guests.delete", "target": selector}],
        "verification_plan": "Best-effort: list guests and confirm email is absent.",
        "rollback": rollback,
        "recovery": recovery,
    }
    if before_state is not None:
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
    plan_path = _write_plan_if_requested(ctx, plan)

    if not ctx["apply"]:
        out: dict[str, Any] = {
            "ok": True,
            "dry_run": True,
            "risk_level": "destructive",
            "refused": True,
            "reasons": ["Write disabled: pass --apply --yes --ack-irreversible to delete a guest membership/invite."],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("site.guests.delete_refused", selector)
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing to delete a guest membership/invite without --yes (this is destructive).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1
    if not bool(ctx.get("ack_irreversible", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "destructive",
                "error": "Refusing destructive action without --ack-irreversible.",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.site_guest_delete(email=email)
    verification: dict[str, Any]
    try:
        listed = client.site_guests_list(site_id=site_id, limit=100)
        guests = listed.get("guests") if isinstance(listed, dict) else None
        still_there = False
        if isinstance(guests, list):
            for row in guests:
                if isinstance(row, dict) and row.get("email") == email:
                    still_there = True
                    break
        verification = {"ok": not still_there, "check": "guests_list_absent", "email": email}
    except Exception as e:  # noqa: BLE001
        verification = {"ok": False, "error": str(e), "error_type": type(e).__name__}
    verified = bool(verification.get("ok"))

    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": _now_utc_iso(),
        "env_fingerprint": env_fingerprint,
        "command": "site guests delete",
        "selector": selector,
        "changed": True,
        "verification": verification,
        "diff_applied": [{"action": "plausible.sites.guests.delete", "deleted": selector}],
        "recovery": recovery,
        "rollback_plan": None,
    }
    if before_state is not None:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "risk_level": "destructive",
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("site.guests.delete", selector)
    ctx["out"].emit(out)
    return 0
