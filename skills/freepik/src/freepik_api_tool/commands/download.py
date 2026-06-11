from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..freepik_api import FreepikApi
from ..http import HttpClient
from ..inventory import append_inventory_row, now_utc_iso, read_inventory_index, sha256_file
from ..jsonpath import jsonpath_get


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Freepik licensed download has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _detail_data(detail: Any) -> dict[str, Any]:
    if not isinstance(detail, dict):
        raise RuntimeError("Refused: resource detail response is not a JSON object")
    data = detail.get("data")
    if isinstance(data, dict):
        return data
    return detail


def _pick_license_url_from_detail(detail: Any, *, jsonpath: str | None) -> str | None:
    if jsonpath:
        v = jsonpath_get(detail, jsonpath)
        if isinstance(v, str) and v.startswith("http"):
            return v
        raise RuntimeError(f"Refused: license JSONPath did not resolve to a URL: {jsonpath}")

    data = _detail_data(detail)
    v = data.get("license")
    if isinstance(v, str) and v.startswith("http"):
        return v

    licenses = data.get("licenses")
    if isinstance(licenses, list):
        for item in licenses:
            if isinstance(item, dict):
                u = item.get("url")
                if isinstance(u, str) and u.startswith("http"):
                    return u
    return None


def _extract_download_items(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise RuntimeError("Refused: download response is not a JSON object")
    data = payload.get("data", payload)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        items = [x for x in data if isinstance(x, dict)]
        if not items:
            raise RuntimeError("Refused: download response data list contained no objects")
        return items
    raise RuntimeError("Refused: download response did not contain a supported data shape")


def _derive_name_from_url(url: str, *, fallback: str) -> str:
    name = Path(urlparse(url).path).name
    return name or fallback


def _pick_download_targets(payload: Any, *, jsonpath: str | None, fallback: str) -> list[dict[str, str]]:
    if jsonpath:
        v = jsonpath_get(payload, jsonpath)
        if isinstance(v, str) and v.startswith("http"):
            return [{"url": v, "filename": _derive_name_from_url(v, fallback=fallback)}]
        if isinstance(v, list):
            targets: list[dict[str, str]] = []
            for item in v:
                if isinstance(item, str) and item.startswith("http"):
                    targets.append({"url": item, "filename": _derive_name_from_url(item, fallback=fallback)})
            if targets:
                return targets
        raise RuntimeError(f"Refused: download JSONPath did not resolve to a URL or URL list: {jsonpath}")

    items = _extract_download_items(payload)
    out: list[dict[str, str]] = []
    for item in items:
        u = item.get("url")
        if not (isinstance(u, str) and u.startswith("http")):
            raise RuntimeError("Refused: download response item missing url")
        fn = item.get("filename")
        if isinstance(fn, str) and fn.strip():
            out.append({"url": u, "filename": Path(fn).name})
        else:
            out.append({"url": u, "filename": _derive_name_from_url(u, fallback=fallback)})
    return out


def _irreversible_license_recovery_contract() -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "Licensed downloads and license records cannot be rolled back by this CLI. "
            "Local cleanup is manual."
        ),
    }


def _build_before_state_contract(
    *,
    resource_id: str,
    fmt: str,
    out_dir: Path,
    inventory: Path,
    image_size: str,
) -> dict[str, Any]:
    if image_size:
        endpoint = f"/resources/{resource_id}/download"
    else:
        endpoint = f"/resources/{resource_id}/download/{fmt}"
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "reason": (
            "Licensed downloads may create a Freepik account download/license record and local files. "
            "This source tool has no reliable before-state snapshot for those writes."
        ),
        "provider_write": {
            "method": "GET",
            "endpoint": endpoint,
            "may_create_license_or_download_record": True,
        },
        "local_state": {
            "downloads_dir": str(out_dir),
            "inventory_csv": str(inventory),
            "dedupe_key": {"resource_id": resource_id, "format": fmt},
        },
    }


def _build_after_apply_verification_plan() -> dict[str, Any]:
    return {
        "status": "best_effort_after_apply",
        "steps": [
            "Confirm the Freepik download/license endpoint returned a usable download URL.",
            "Confirm the binary download was saved locally.",
            "Confirm the destination file hash and inventory row were recorded.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def _missing_no_snapshot_approval_output(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": False,
        "dry_run": False,
        "refused": True,
        "refusal_type": "SafetyError",
        "reasons": [BEFORE_STATE_REFUSAL_REASON],
        "plan": plan,
        "verification_plan": _build_after_apply_verification_plan(),
        "recovery": _irreversible_license_recovery_contract(),
    }


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise RuntimeError(BEFORE_STATE_REFUSAL_REASON)


def run_download(args: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    cfg = ctx["cfg"]
    project_cfg = ctx.get("project_cfg") or {}
    project_dir = Path(str(ctx.get("project_dir") or Path.cwd())).expanduser().resolve()
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    apply = bool(ctx["apply"])
    rid = str(args.id)
    fmt = str(args.format).lstrip(".").lower()
    out_dir_str = (str(getattr(args, "out_dir", "") or "")).strip() or str(project_cfg.get("downloads_dir") or (project_dir / "downloads"))
    inv_path_str = (str(getattr(args, "inventory", "") or "")).strip() or str(project_cfg.get("inventory_csv") or (project_dir / "licensed-downloads-ledger.csv"))
    if not out_dir_str.strip():
        raise RuntimeError("Refused: missing --out-dir (or project config `downloads_dir`)")
    if not inv_path_str.strip():
        raise RuntimeError("Refused: missing --inventory (or project config `inventory_csv`)")
    out_dir = Path(out_dir_str)
    inv_path = Path(inv_path_str)
    force = bool(args.force)
    image_size = (str(args.image_size).strip() if getattr(args, "image_size", None) else "") or cfg.image_size
    post_slug = (str(getattr(args, "post_slug", "") or "")).strip()
    ghost_id = (str(getattr(args, "ghost_id", "") or "")).strip()
    usage_role = (str(getattr(args, "usage_role", "") or "")).strip()

    index = read_inventory_index(inv_path)
    if (rid, fmt) in index and not force:
        raise RuntimeError(
            f"Refused: resource already in inventory for id={rid} format={fmt}; pass --force to re-download"
        )

    detail = api.get_resource(rid)
    data = _detail_data(detail)

    # Fail-closed non-AI gate (required for this migration workflow).
    # Only proceed when the resource detail explicitly includes:
    # - is_ai_generated == False
    # - has_prompt == False
    if "is_ai_generated" not in data or "has_prompt" not in data:
        raise RuntimeError(
            "Refused: resource detail missing AI flags (is_ai_generated/has_prompt); "
            "treating as unknown per safety policy"
        )
    if data.get("is_ai_generated") is not False or data.get("has_prompt") is not False:
        raise RuntimeError(
            f"Refused: resource is AI/unknown per safety policy (is_ai_generated={data.get('is_ai_generated')}, "
            f"has_prompt={data.get('has_prompt')})"
        )

    download_url_jsonpath = args.download_url_jsonpath or cfg.download_url_jsonpath
    license_url_jsonpath = args.license_url_jsonpath or cfg.license_url_jsonpath
    license_url = _pick_license_url_from_detail(detail, jsonpath=license_url_jsonpath)

    plan = {
        "apply": apply,
        "resource_id": rid,
        "format": fmt,
        "license_url": license_url,
        "resource_url": data.get("url"),
        "preview_url": (data.get("preview") or {}).get("url") if isinstance(data.get("preview"), dict) else None,
        "name": data.get("name"),
        "author": (data.get("author") or {}).get("name") if isinstance(data.get("author"), dict) else None,
        "resource_type": data.get("type"),
        "is_ai_generated": data.get("is_ai_generated"),
        "has_prompt": data.get("has_prompt"),
        "image_size": image_size or "",
        "note": (
            "Dry-run does not call the Freepik download endpoint. "
            "Apply requires explicit no-snapshot approval because licensed downloads may create a provider record."
        ),
    }
    plan["before_state"] = _build_before_state_contract(
        resource_id=rid,
        fmt=fmt,
        out_dir=out_dir,
        inventory=inv_path,
        image_size=image_size or "",
    )
    plan["verification_plan"] = _build_after_apply_verification_plan()
    if not apply:
        return {
            "dry_run": True,
            "plan": plan,
            "recovery": _irreversible_license_recovery_contract(),
        }

    try:
        _require_no_snapshot_approval(ctx)
    except RuntimeError:
        ctx["audit"].write(
            "freepik.download.refused",
            {
                "resource_id": rid,
                "format": fmt,
                "reason": BEFORE_STATE_REFUSAL_REASON,
                "before_state": plan["before_state"],
            },
        )
        return _missing_no_snapshot_approval_output(plan)

    # Apply: call the download endpoint (may create a license record), then fetch the binary.
    out_dir.mkdir(parents=True, exist_ok=True)
    if image_size:
        # `image_size` is only supported on the /download endpoint (no-format).
        payload = api.download_by_id(rid, image_size=image_size)
        dl_mode = "by_id"
    else:
        try:
            payload = api.download_by_id_and_format(rid, fmt=fmt)
            dl_mode = "by_id_and_format"
        except Exception as e:  # noqa: BLE001
            # Fallback: some resource types/accounts may only support the non-format download endpoint.
            ctx["audit"].write(
                "freepik.download_mode_fallback",
                {"resource_id": rid, "format": fmt, "error": str(e)},
            )
            payload = api.download_by_id(rid)
            dl_mode = "by_id"

    try:
        targets = _pick_download_targets(payload, jsonpath=download_url_jsonpath, fallback=f"{rid}.{fmt}")
    except Exception as e:  # noqa: BLE001
        ctx["audit"].write(
            "freepik.download_response_unparsed",
            {
                "resource_id": rid,
                "format": fmt,
                "download_mode": dl_mode,
                "error": str(e),
                "response": payload,
            },
        )
        raise

    # If license URL wasn't present before download, try again after the download call.
    if not license_url:
        try:
            license_url = _pick_license_url_from_detail(api.get_resource(rid), jsonpath=license_url_jsonpath)
        except Exception:
            license_url = None

    if not license_url:
        raise RuntimeError(
            "Refused: could not find a license URL in the resource detail response; "
            "set FREEPIK_LICENSE_URL_JSONPATH or --license-url-jsonpath"
        )

    base_row: dict[str, Any] = {
        "downloaded_at_utc": now_utc_iso(),
        "resource_id": rid,
        "format": fmt,
        "license_url": license_url,
        "notes": "",
        "title": str(data.get("title") or data.get("name") or ""),
        "resource_type": str(data.get("type") or ""),
        "resource_url": str(data.get("url") or ""),
        "image_size": image_size or "",
        "post_slug": post_slug,
        "ghost_id": ghost_id,
        "usage_role": usage_role,
    }

    preview = data.get("preview")
    if isinstance(preview, dict) and isinstance(preview.get("url"), str):
        base_row["preview_url"] = preview["url"]

    tags = data.get("tags")
    if isinstance(tags, list):
        out_tags: list[str] = []
        for t in tags:
            if isinstance(t, dict):
                name = t.get("name") or t.get("slug")
                if name:
                    out_tags.append(str(name))
            elif t:
                out_tags.append(str(t))
        base_row["keywords"] = "; ".join(out_tags)

    author = data.get("author") or data.get("contributor")
    if isinstance(author, dict):
        base_row["author"] = str(author.get("name") or "")
    elif isinstance(author, str):
        base_row["author"] = author

    rows: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for i, t in enumerate(targets, start=1):
        download_url = t["url"]
        safe_remote = Path(t["filename"]).name or f"{rid}.{fmt}"
        file_name = f"{rid}--{safe_remote}"
        if file_name in used_names:
            file_name = f"{rid}--{i}--{safe_remote}"
        used_names.add(file_name)
        file_path = out_dir / file_name

        if file_path.exists() and not force:
            raise RuntimeError(f"Refused: destination already exists: {file_path}; pass --force to overwrite")

        http.download_to_path(download_url, file_path, retries=2)
        digest = sha256_file(file_path)

        row = dict(base_row)
        row["file_name"] = file_name
        row["file_path"] = str(file_path)
        row["sha256"] = digest
        row["download_url"] = download_url

        append_inventory_row(inv_path, row)
        rows.append(row)

    ctx["audit"].write(
        "freepik.download",
        {
            "resource_id": rid,
            "format": fmt,
            "file_paths": [r["file_path"] for r in rows],
            "license_url": license_url,
        },
    )
    return {
        "ok": True,
        "rows": rows,
        "before_state": plan["before_state"],
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for Freepik licensed downloads.",
        },
        "verification": {
            "ok": True,
            "mode": "download-and-inventory",
            "file_count": len(rows),
        },
        "recovery": _irreversible_license_recovery_contract(),
    }


def cmd_download(args: Any, ctx: dict[str, Any]) -> int:
    ctx["out"].emit(run_download(args, ctx))
    return 0
