from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests

from ..errors import SafetyError, ToolError, ValidationError
from ..http import HttpStatusError
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
    no_inverse_recovery_contract,
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


def _download_target(dest: Path | None, overwrite: bool) -> None:
    if dest is None:
        return
    if dest.exists() and not dest.is_file():
        raise SafetyError("Choose a file path for --dest.")
    if dest.exists() and not overwrite:
        raise SafetyError("The destination already exists. Choose a new path or preview an overwrite.")
    for parent in dest.parents:
        if parent.exists():
            if not parent.is_dir():
                raise SafetyError(f"Choose a destination inside a folder. {parent} is not a folder.")
            break


def _photo_links(client: UnsplashClient, photo_id: str) -> dict[str, Any]:
    photo = client.get(f"/photos/{photo_id}")
    if not isinstance(photo, dict) or photo.get("id") != photo_id:
        raise ValidationError("Unsplash did not return the requested photo.")
    links = photo.get("links")
    if not isinstance(links, dict):
        raise ValidationError("Unsplash did not return links for this photo.")
    location = links.get("download_location")
    if not isinstance(location, str) or not location:
        raise ValidationError("Unsplash did not return a download tracking link.")
    user = photo.get("user")
    if not isinstance(user, dict):
        user = {}
    profile = user.get("links")
    if not isinstance(profile, dict):
        profile = {}
    return {
        "tracking_url": client.validate_tracking_url(photo_id, location),
        "urls": photo.get("urls") if isinstance(photo.get("urls"), dict) else {},
        "photo_url": links.get("html"),
        "photographer": {"name": user.get("name"), "profile_url": profile.get("html")},
    }


def _full_image_url(photo: dict[str, Any]) -> str:
    urls = photo.get("urls")
    full = urls.get("full") if isinstance(urls, dict) else None
    if isinstance(full, str):
        parsed = urlsplit(full)
        if parsed.scheme == "https" and parsed.hostname and parsed.username is None:
            return full
    raise ValidationError("Unsplash did not return a usable full-size image URL.")


def _build_download_plan(request: dict[str, Any], photo: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    photo_id, dest, overwrite = request["photo_id"], request["dest"], request["overwrite"]
    return {
        "kind": "unsplash-photo-download",
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "generated_at_utc": _utc_now(),
        "env_fingerprint": request["connection"],
        "command": ctx["command_str"],
        "selector": {"kind": "photo", "value": photo_id},
        "risk_level": "medium",
        "risk_reasons": ["Unsplash records the download when you apply this preview."],
        "preconditions": ["The photo, connection, destination, and overwrite choice must match."],
        "baseline": request,
        "photo": photo,
        "proposed_changes": [
            {"action": "record a download", "endpoint": photo["tracking_url"]},
            *([{"action": "save a file", "path": dest, "overwrite": overwrite}] if dest else []),
        ],
        "before_state": before_state_contract(
            reason="The tool cannot save or restore Unsplash's earlier download count.",
            provider_write={"method": "GET", "endpoint": f"/photos/{photo_id}/download", "tracks_download": True},
            local_state={"dest": dest, "overwrite": overwrite},
        ),
        "verification_plan": {
            "steps": ["Record the tracking result. If a file is requested, check its size and record its hash."],
            "approval_required": "--ack-no-snapshot",
        },
        "recovery": no_inverse_recovery_contract(
            restore_note="The tool cannot undo Unsplash's download count. Remove an unwanted local copy manually."
        ),
    }


def _refuse_download(ctx: dict[str, Any], reason: str, plan: dict[str, Any] | None = None) -> int:
    out = (
        before_state_refusal_output(plan, reason=reason)
        if plan is not None
        else {"dry_run": False, "refused": True, "reasons": [reason], "refusal_type": "SafetyError"}
    )
    out.update(ok=False, tracking_status="not_sent")
    ctx["audit"].write("photos.download.refused", out)
    ctx["out"].emit(out)
    return 1


def cmd_photos_download(args: Any, ctx: dict[str, Any]) -> int:
    photo_id = validate_photo_id(args.id)
    dest = Path(args.dest).expanduser().resolve() if args.dest else None
    overwrite = args.overwrite
    apply = bool(ctx.get("apply"))
    plan_in = str(ctx.get("plan_in") or "")
    receipt_out = ctx.get("receipt_out")
    if apply and not plan_in:
        return _refuse_download(ctx, "Save and review a preview with --plan-out, then apply it with --plan-in.")
    if apply and overwrite and not ctx.get("yes"):
        return _refuse_download(ctx, "Applying an overwrite also needs --yes.")
    if overwrite and dest is None:
        return _refuse_download(ctx, "Choose a --dest before asking to overwrite a file.")
    if dest is not None and any(
        name and Path(name).expanduser().resolve() == dest
        for name in (plan_in, ctx.get("plan_out"), receipt_out)
    ):
        return _refuse_download(ctx, "Choose separate paths for the photo, preview, and receipt.")
    if plan_in and receipt_out and Path(plan_in).expanduser().resolve() == Path(receipt_out).expanduser().resolve():
        return _refuse_download(ctx, "Choose a receipt path different from the saved preview.")
    try:
        _download_target(dest, overwrite)
    except SafetyError as exc:
        return _refuse_download(ctx, str(exc))

    client: UnsplashClient = ctx["client"]
    request = {
        "connection": client.connection_fingerprint(), "photo_id": photo_id,
        "dest": str(dest) if dest else None, "overwrite": overwrite,
    }
    if not apply:
        photo = _photo_links(client, photo_id)
        if dest:
            _full_image_url(photo)
        plan = _build_download_plan(request, photo, ctx)
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("photos.download.plan", {"id": photo_id, "dest": request["dest"], "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "tracking_status": "not_sent", "plan": plan, "plan_out": plan_path})
        return 0

    saved = read_json_file(Path(plan_in).expanduser())
    if (
        not isinstance(saved, dict) or saved.get("kind") != "unsplash-photo-download"
        or saved.get("baseline") != request or not isinstance(saved.get("photo"), dict)
    ):
        return _refuse_download(ctx, "The saved preview does not match this download. Save and review a new one.")
    photo = saved["photo"]
    tracking_url = photo.get("tracking_url")
    if not isinstance(tracking_url, str):
        return _refuse_download(ctx, "The saved preview has no tracking link. Save a new preview.")
    client.validate_tracking_url(photo_id, tracking_url)
    image_url = _full_image_url(photo) if dest else None
    plan = _build_download_plan(request, photo, ctx)
    if not ctx.get("ack_no_snapshot"):
        return _refuse_download(ctx, "Approve recording the download without a restore point with --ack-no-snapshot.", plan)
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)

    tracking = None
    file_info = None
    tracking_status = "unknown"
    error = None
    try:
        tracking = client.download_tracking(photo_id, tracking_url)
        tracking_status = "recorded"
    except HttpStatusError as exc:
        if 400 <= exc.status < 500 and exc.status != 408:
            tracking_status = "failed"
            error = f"Unsplash declined the tracking request (HTTP {exc.status})."
        else:
            error = f"Unsplash replied with HTTP {exc.status}. The download count may have changed."
    except (RuntimeError, ToolError, ValueError):
        error = "The tracking outcome is unclear. Check before recording the download again."

    if tracking_status == "recorded" and dest and image_url:
        try:
            file_info = client.download_file(image_url, dest=dest, overwrite=overwrite)
        except (OSError, RuntimeError, ToolError, requests.RequestException):
            error = "Unsplash recorded the download, but the photo could not be saved. The destination was not replaced."

    receipt = {
        "tool": ctx["tool"], "version": ctx["tool_version"], "applied_at_utc": _utc_now(),
        "env_fingerprint": request["connection"], "command": ctx["command_str"],
        "selector": plan["selector"], "before_state": plan["before_state"],
        "no_snapshot_approval": {"acknowledged": True, "flag": "--ack-no-snapshot"},
        "tracking_status": tracking_status, "changed": {"recorded": True, "failed": False}.get(tracking_status),
        "photo": photo, "provider_response": tracking, "file": file_info,
        "verification": {
            "ok": error is None, "mode": "provider-response-and-optional-file",
            "details": {"download_tracking_response": tracking is not None, "file_written": file_info is not None},
        },
        "recovery": plan["recovery"],
    }
    receipt_path = None
    if receipt_out:
        try:
            receipt_path = write_json_file(receipt_out, receipt)
        except OSError:
            error = (error + " " if error else "") + "The local receipt could not be saved. Use the result shown here."

    try:
        ctx["audit"].write("photos.download.apply", {"id": photo_id, "tracking_status": tracking_status, "file": file_info, "receipt_out": receipt_path})
    except OSError:
        error = (error + " " if error else "") + "The audit log could not be saved. Use the result shown here."
    out = {"ok": error is None, "dry_run": False, "tracking_status": tracking_status, "receipt": receipt, "receipt_out": receipt_path}
    if error:
        out["error"] = error
    ctx["out"].emit(out)
    return int(error is not None)
