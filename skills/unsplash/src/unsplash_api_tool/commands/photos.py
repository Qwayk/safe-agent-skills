from __future__ import annotations

import time
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..pagination import validate_page, validate_per_page
from ..unsplash_client import (
    UnsplashClient,
    validate_photo_id,
    validate_positive_int,
)
from .write_safety import (
    before_state_contract,
    before_state_refusal_output,
    before_state_refusal_verification_plan,
    no_inverse_recovery_contract,
)


PHOTO_DOWNLOAD_REFUSAL_REASON = (
    "Refused: this Unsplash photo download has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cmd_photos_list(args: Any, ctx: dict[str, Any]) -> int:
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "latest", "oldest", "popular"}:
        raise ValidationError("--order-by must be one of: latest, oldest, popular")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        "/photos",
        params={k: v for k, v in {"page": page, "per_page": per_page, "order_by": order_by}.items() if v is not None},
    )
    out = {"ok": True, "endpoint": "GET /photos", "params": {"page": page, "per_page": per_page, "order_by": order_by}, "data": data}
    ctx["audit"].write("photos.list", {"page": page, "per_page": per_page, "order_by": order_by})
    ctx["out"].emit(out)
    return 0


def cmd_photos_get(args: Any, ctx: dict[str, Any]) -> int:
    photo_id = validate_photo_id(str(getattr(args, "id", "") or ""))
    client: UnsplashClient = ctx["client"]
    data = client.get(f"/photos/{photo_id}")
    out = {"ok": True, "endpoint": "GET /photos/:id", "id": photo_id, "data": data}
    ctx["audit"].write("photos.get", {"id": photo_id})
    ctx["out"].emit(out)
    return 0


def cmd_photos_random(args: Any, ctx: dict[str, Any]) -> int:
    count = None if getattr(args, "count", None) is None else validate_positive_int(getattr(args, "count", None), field="--count")
    if count is not None and (count < 1 or count > 30):
        raise ValidationError("--count must be between 1 and 30")

    query = str(getattr(args, "query", "") or "").strip() or None
    username = str(getattr(args, "username", "") or "").strip() or None
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")
    content_filter = str(getattr(args, "content_filter", "") or "").strip() or None
    if content_filter not in {None, "low", "high"}:
        raise ValidationError("--content-filter must be one of: low, high")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        "/photos/random",
        params={
            k: v
            for k, v in {
                "count": count,
                "query": query,
                "username": username,
                "orientation": orientation,
                "content_filter": content_filter,
            }.items()
            if v is not None
        },
    )
    out = {"ok": True, "endpoint": "GET /photos/random", "params": {"count": count, "query": query, "username": username, "orientation": orientation, "content_filter": content_filter}, "data": data}
    ctx["audit"].write("photos.random", out["params"])
    ctx["out"].emit(out)
    return 0


def cmd_photos_search(args: Any, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "query", "") or "").strip()
    if not query:
        raise ValidationError("Missing --query")
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "relevant", "latest"}:
        raise ValidationError("--order-by must be one of: relevant, latest")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        "/search/photos",
        params={"query": query, "page": page, "per_page": per_page, **({} if order_by is None else {"order_by": order_by})},
    )
    out = {"ok": True, "endpoint": "GET /search/photos", "params": {"query": query, "page": page, "per_page": per_page, "order_by": order_by}, "data": data}
    ctx["audit"].write("photos.search", {"query": query, "page": page, "per_page": per_page, "order_by": order_by})
    ctx["out"].emit(out)
    return 0


def cmd_photos_stats(args: Any, ctx: dict[str, Any]) -> int:
    photo_id = validate_photo_id(str(getattr(args, "id", "") or ""))
    resolution = str(getattr(args, "resolution", "") or "").strip() or None
    quantity = str(getattr(args, "quantity", "") or "").strip() or None

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/photos/{photo_id}/statistics",
        params={k: v for k, v in {"resolution": resolution, "quantity": quantity}.items() if v is not None},
    )
    out = {"ok": True, "endpoint": "GET /photos/:id/statistics", "id": photo_id, "params": {"resolution": resolution, "quantity": quantity}, "data": data}
    ctx["audit"].write("photos.stats", {"id": photo_id, "resolution": resolution, "quantity": quantity})
    ctx["out"].emit(out)
    return 0


def _build_download_plan(*, photo_id: str, dest: str | None, overwrite: bool, ctx: dict[str, Any]) -> dict[str, Any]:
    env_fingerprint = ctx["cfg"].base_url
    selector = {"kind": "photo", "value": photo_id}
    restore_note = (
        "Unsplash download tracking cannot be rolled back by this CLI. "
        "If the optional file download ran, delete the local destination file manually."
    )
    proposed_changes: list[dict[str, Any]] = [
        {"action": "GET /photos/:id/download", "notes": "Unsplash download tracking endpoint (required for compliance)"},
    ]
    risk_reasons = ["Triggers Unsplash download tracking endpoint"]
    if dest:
        proposed_changes.append(
            {
                "action": "write file",
                "path": dest,
                "overwrite": overwrite,
                "notes": "Download the binary file from the returned `url` and write it to disk.",
            }
        )
        risk_reasons.append("May write a file to disk")
    return {
        "tool": ctx.get("tool") or "unsplash-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": "medium",
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "photo id must match"],
        "baseline": {"env_fingerprint": env_fingerprint, "photo_id": photo_id, "dest": dest, "overwrite": overwrite},
        "proposed_changes": proposed_changes,
        "before_state": before_state_contract(
            reason=(
                "Unsplash download tracking is a provider-side write-like event. "
                "This source tool has no reliable before-state snapshot for that endpoint."
            ),
            provider_write={
                "method": "GET",
                "endpoint": f"/photos/{photo_id}/download",
                "tracks_download": True,
            },
            local_state={"dest": dest, "overwrite": overwrite},
        ),
        "verification_plan": before_state_refusal_verification_plan(),
        "recovery": no_inverse_recovery_contract(restore_note=restore_note),
    }


def _ensure_download_safety_contract(
    plan: dict[str, Any],
    *,
    photo_id: str,
    dest: str | None,
    overwrite: bool,
) -> dict[str, Any]:
    restore_note = (
        "Unsplash download tracking cannot be rolled back by this CLI. "
        "If the optional file download ran, delete the local destination file manually."
    )
    plan["before_state"] = before_state_contract(
        reason=(
            "Unsplash download tracking is a provider-side write-like event. "
            "This source tool has no reliable before-state snapshot for that endpoint."
        ),
        provider_write={"method": "GET", "endpoint": f"/photos/{photo_id}/download", "tracks_download": True},
        local_state={"dest": dest, "overwrite": overwrite},
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["recovery"] = no_inverse_recovery_contract(restore_note=restore_note)
    return plan


def _validate_plan_for_apply(plan: dict[str, Any], *, photo_id: str, dest: str | None, overwrite: bool, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(baseline.get("photo_id") or "") != str(photo_id):
        raise SafetyError("Refused: plan photo_id does not match current selector")
    if (baseline.get("dest") if baseline.get("dest") is not None else None) != dest:
        raise SafetyError("Refused: plan baseline dest does not match current --dest")
    if bool(baseline.get("overwrite")) != bool(overwrite):
        raise SafetyError("Refused: plan baseline overwrite does not match current --overwrite")


def cmd_photos_download(args: Any, ctx: dict[str, Any]) -> int:
    photo_id = validate_photo_id(str(getattr(args, "id", "") or ""))
    dest = str(getattr(args, "dest", "") or "").strip() or None
    overwrite = bool(getattr(args, "overwrite", False))
    if overwrite and not (bool(ctx.get("apply")) and bool(ctx.get("yes"))):
        raise SafetyError("Refused: --overwrite requires --apply --yes")

    if ctx.get("plan_in"):
        plan_obj = read_json_file(ctx["plan_in"])
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
    else:
        plan = _build_download_plan(photo_id=photo_id, dest=dest, overwrite=overwrite, ctx=ctx)
    plan = _ensure_download_safety_contract(plan, photo_id=photo_id, dest=dest, overwrite=overwrite)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("photos.download.plan", {"id": photo_id, "dest": dest, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    try:
        _validate_plan_for_apply(plan, photo_id=photo_id, dest=dest, overwrite=overwrite, ctx=ctx)
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"}
        ctx["audit"].write("photos.download.refused", out)
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("ack_no_snapshot")):
        out = before_state_refusal_output(plan, reason=PHOTO_DOWNLOAD_REFUSAL_REASON)
        ctx["audit"].write("photos.download.refused", out)
        ctx["out"].emit(out)
        return 0

    client: UnsplashClient = ctx["client"]
    tracking = client.download_tracking(photo_id)
    file_info = None
    if dest:
        download_url = str(tracking.get("url") or "").strip()
        if not download_url:
            raise SafetyError("Refused: Unsplash download tracking response did not include a file URL")
        file_info = client.download_file(download_url, dest=Path(dest), overwrite=overwrite)

    receipt = {
        "tool": ctx.get("tool") or "unsplash-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "photo", "value": photo_id},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for Unsplash download tracking.",
        },
        "changed": True,
        "provider_response": tracking,
        "file": file_info,
        "verification": {
            "ok": True,
            "mode": "provider-response-and-optional-file",
            "details": {"download_tracking_response": bool(tracking), "file_written": file_info is not None},
        },
        "recovery": plan.get("recovery"),
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("photos.download.apply", {"id": photo_id, "dest": dest, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0
