from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from ..api import PinterestApi, resolve_access_token
from ..write_framework import require_write_allowed
from .write_safety import blocked_plan


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )


def _canonicalize_url(url: str, *, canonical_host: str, allowed_hosts: set[str]) -> str | None:
    """
    Canonicalize a URL for a specific site host.

    - Only canonicalizes when the input hostname is in `allowed_hosts`.
    - scheme: https
    - host: canonical_host
    - drop query + fragment
    - normalize trailing slash (best-effort)
    """
    s = (url or "").strip()
    if not s:
        return None
    try:
        u = urlparse(s)
    except Exception:
        return None
    if u.scheme not in {"http", "https"}:
        return None
    if u.hostname not in allowed_hosts:
        return None

    path = u.path or "/"
    # Best-effort trailing slash normalization for typical Ghost paths.
    if path and not path.endswith("/") and "." not in path.split("/")[-1]:
        path = f"{path}/"

    return urlunparse(("https", canonical_host, path, "", "", ""))


@dataclass(frozen=True)
class LinkFix:
    pin_id: str
    old_link: str
    new_link: str
    reason: str


def _load_pins_from_audit_json(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("pins.json must be a JSON object")
    items = obj.get("items")
    if not isinstance(items, list):
        raise RuntimeError("pins.json must contain an `items` array")
    out = [it for it in items if isinstance(it, dict)]
    return out


def cmd_pin_links_plan(args: Any, ctx: dict[str, Any]) -> int:
    pins_json = Path(str(args.pins_json)).expanduser().resolve()
    pins = _load_pins_from_audit_json(pins_json)

    project_cfg = ctx.get("project_cfg") or {}
    canonical_host = str(args.canonical_host or project_cfg.get("canonical_host") or "").strip().lower()
    if not canonical_host:
        raise RuntimeError("Refused: missing --canonical-host (or project config `canonical_host`)")
    allowed_hosts = {canonical_host, f"www.{canonical_host}"}
    for h in (args.allowed_host or []):
        s = str(h or "").strip().lower()
        if s:
            allowed_hosts.add(s)

    fixes: list[LinkFix] = []
    for p in pins:
        pid = str(p.get("id") or "").strip()
        if not pid:
            continue
        old = str(p.get("link") or "").strip()
        if not old:
            continue

        new = _canonicalize_url(old, canonical_host=canonical_host, allowed_hosts=allowed_hosts)
        if not new:
            continue
        if new == old:
            continue

        reason_parts: list[str] = []
        u = urlparse(old)
        if u.scheme == "http":
            reason_parts.append("http->https")
        if u.fragment:
            reason_parts.append("remove_fragment")
        if u.query:
            reason_parts.append("remove_query")
        if u.hostname == f"www.{canonical_host}":
            reason_parts.append("www->root")
        if not reason_parts:
            reason_parts.append("canonicalize")

        fixes.append(LinkFix(pin_id=pid, old_link=old, new_link=new, reason=",".join(reason_parts)))
        if args.max_actions is not None and int(args.max_actions) > 0 and len(fixes) >= int(args.max_actions):
            break

    plan = {
        "ok": True,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_pins_json": str(pins_json),
        "action": "pin_link_update",
        "canonical_host": canonical_host,
        "allowed_hosts": sorted(allowed_hosts),
        "count": len(fixes),
        "items": [
            {
                "pin_id": f.pin_id,
                "old_link": f.old_link,
                "new_link": f.new_link,
                "reason": f.reason,
            }
            for f in fixes
        ],
    }

    out_file = Path(str(args.out)).expanduser().resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ctx["audit"].write(
        "pins.links_plan",
        {"source_pins_json": str(pins_json), "out": str(out_file), "count": len(fixes)},
    )
    ctx["out"].emit({"ok": True, "out": str(out_file), "count": len(fixes)})
    return 0


def _load_plan(path: Path) -> list[LinkFix]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("Plan file must be a JSON object")
    items = obj.get("items")
    if not isinstance(items, list):
        raise RuntimeError("Plan file must contain an `items` array")
    fixes: list[LinkFix] = []
    for it in items:
        if not isinstance(it, dict):
            raise RuntimeError("Plan items must be objects")
        pid = str(it.get("pin_id") or "").strip()
        old = str(it.get("old_link") or "").strip()
        new = str(it.get("new_link") or "").strip()
        reason = str(it.get("reason") or "").strip()
        if not pid or not old or not new:
            raise RuntimeError("Plan items require pin_id, old_link, new_link")
        fixes.append(LinkFix(pin_id=pid, old_link=old, new_link=new, reason=reason or "canonicalize"))
    return fixes


def cmd_pin_links_apply(args: Any, ctx: dict[str, Any]) -> int:
    plan_file = Path(str(args.plan)).expanduser().resolve()
    fixes = _load_plan(plan_file)

    limit = int(args.limit) if getattr(args, "limit", None) else None
    if limit is not None and limit < 1:
        raise RuntimeError("--limit must be >= 1")
    to_apply = fixes[:limit] if limit is not None else fixes

    if ctx["apply"]:
        require_write_allowed(ctx)
    api = _api(ctx)

    dry_run = not bool(ctx["apply"])
    results: list[dict[str, Any]] = []

    for f in to_apply:
        # Verify current state before any write.
        current = api.get(f"/pins/{f.pin_id}")
        if not isinstance(current, dict):
            raise RuntimeError("Unexpected pin response (not an object)")
        current_link = str(current.get("link") or "").strip()
        if current_link != f.old_link and not bool(args.allow_mismatch):
            raise RuntimeError(
                f"Pin {f.pin_id} link mismatch; expected {f.old_link!r}, got {current_link!r}. "
                "Rebuild the plan or pass --allow-mismatch to proceed."
            )

        if dry_run:
            results.append(
                {
                    "pin_id": f.pin_id,
                    "ok": True,
                    "dry_run": True,
                    "old_link": current_link,
                    "new_link": f.new_link,
                    "reason": f.reason,
                }
            )
            continue

        # Apply the update.
        _ = api.patch(f"/pins/{f.pin_id}", json_body={"link": f.new_link})
        # Verify by read-back.
        after = api.get(f"/pins/{f.pin_id}")
        after_link = str(after.get("link") or "").strip()
        if after_link != f.new_link:
            raise RuntimeError(f"Verification failed for pin {f.pin_id}: link is {after_link!r} (expected {f.new_link!r})")

        results.append(
            {
                "pin_id": f.pin_id,
                "ok": True,
                "dry_run": False,
                "old_link": current_link,
                "new_link": f.new_link,
                "reason": f.reason,
            }
        )

    out = {
        "ok": True,
        "dry_run": dry_run,
        "plan": str(plan_file),
        "requested": len(to_apply),
        "results": results,
    }
    blocked = blocked_plan(
        action="pins.links.apply",
        operations=[{"method": "PATCH", "path": "/pins/{pin_id}"}],
        request={"plan": str(plan_file), "requested": len(to_apply)},
    )
    if dry_run:
        out["before_state"] = blocked["before_state"]
        out["verification_plan"] = blocked["verification_plan"]
        out["rollback"] = blocked["rollback"]
    else:
        reason = "No reliable before-state snapshot is available for this Pinterest pin-link batch write."
        out["before_state"] = blocked["before_state"]
        out["no_snapshot_approval"] = {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": reason,
        }
    ctx["audit"].write(
        "pins.links_apply",
        {"dry_run": dry_run, "plan": str(plan_file), "requested": len(to_apply), "applied": 0 if dry_run else len(to_apply)},
    )
    ctx["out"].emit(out)
    return 0
