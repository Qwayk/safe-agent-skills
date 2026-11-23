from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..freepik_api import FreepikApi
from ..http import HttpClient
from ..inventory import append_inventory_row, now_utc_iso, read_inventory_index, sha256_file
from ..jsonpath import jsonpath_get
from ..shortlist import best_preview_url

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
    v = data.get("license_url") or data.get("licenseUrl") or data.get("license")
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


def _pick_download_targets(payload: Any, *, jsonpath: str | None, fallback: str) -> list[dict[str, Any]]:
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
    out: list[dict[str, Any]] = []
    for item in items:
        u = item.get("url")
        if not (isinstance(u, str) and u.startswith("http")):
            raise RuntimeError("Refused: download response item missing url")
        fn = item.get("filename")
        name = Path(fn).name if isinstance(fn, str) and fn.strip() else _derive_name_from_url(u, fallback=fallback)
        out.append({"url": u, "filename": name, "metadata": item})
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


def save_plan(path: str | None, plan: dict[str, Any]) -> str | None:
    if not path:
        return None
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(plan, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return str(target)


def require_reviewed_plan(
    ctx: dict[str, Any], *, kind: str, requests: list[dict[str, Any]]
) -> None:
    path = ctx.get("plan_in")
    if not path:
        raise RuntimeError("Save and review a preview with --plan-out, then apply it with --plan-in.")
    saved = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(saved, dict) or saved.get("kind") != kind:
        raise RuntimeError("Choose the saved Freepik preview for this operation.")
    plans = saved.get("plans") if kind == "batch-download" else [saved]
    if not isinstance(plans, list) or any(not isinstance(plan, dict) for plan in plans):
        raise RuntimeError("The saved preview does not contain a complete download request.")
    if [plan.get("request") for plan in plans] != requests:
        raise RuntimeError("The download request changed. Save and review a new preview.")


def _asset_client(ctx: dict[str, Any]) -> tuple[FreepikApi, HttpClient]:
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    return FreepikApi(cfg=ctx["cfg"], http=http), http


def download_request(args: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    cfg = ctx["cfg"]
    project_cfg = ctx.get("project_cfg") or {}
    project_dir = Path(ctx.get("project_dir") or Path.cwd()).expanduser().resolve()
    rid = str(args.id).strip()
    fmt = str(args.format).strip().lstrip(".").lower()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", rid) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", fmt):
        raise RuntimeError("Choose a valid Freepik resource ID and format.")
    out_dir = Path(args.out_dir or project_cfg.get("downloads_dir") or project_dir / "downloads").expanduser().resolve()
    inventory = Path(args.inventory or project_cfg.get("inventory_csv") or project_dir / "licensed-downloads-ledger.csv").expanduser().resolve()
    image_size = str(getattr(args, "image_size", "") or "").strip() or cfg.image_size or ""
    connection = urlparse(cfg.base_url)
    fingerprint = sha256(json.dumps([
        cfg.base_url, cfg.auth_header, cfg.auth_prefix, cfg.api_key,
    ]).encode("utf-8")).hexdigest()
    return {
        "resource_id": rid,
        "format": fmt,
        "image_size": image_size,
        "connection": connection._replace(netloc=connection.netloc.rsplit("@", 1)[-1], query="", fragment="").geturl(),
        "connection_fingerprint": fingerprint,
        "accept_language": cfg.accept_language,
        "downloads_dir": str(out_dir),
        "inventory_csv": str(inventory),
        "force": bool(args.force),
        "post_slug": str(getattr(args, "post_slug", "") or "").strip(),
        "ghost_id": str(getattr(args, "ghost_id", "") or "").strip(),
        "usage_role": str(getattr(args, "usage_role", "") or "").strip(),
        "download_url_jsonpath": args.download_url_jsonpath or cfg.download_url_jsonpath,
        "license_url_jsonpath": args.license_url_jsonpath or cfg.license_url_jsonpath,
    }


def _check_local_targets(request: dict[str, Any]) -> None:
    out_dir = Path(request["downloads_dir"])
    inventory = Path(request["inventory_csv"])
    if (out_dir.exists() and not out_dir.is_dir()) or inventory.is_dir():
        raise RuntimeError("Choose a download folder and an inventory CSV file.")
    key = (request["resource_id"], request["format"])
    if key in read_inventory_index(inventory) and not request["force"]:
        raise RuntimeError(
            f"Resource {key[0]} is already in the inventory for {key[1]}. Use --force if you intend to download it again."
        )


def prepare_download(request: dict[str, Any], ctx: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    _check_local_targets(request)
    api, _ = _asset_client(ctx)
    rid = request["resource_id"]
    detail = api.get_resource(rid)
    data = _detail_data(detail)
    if data.get("id") is not None and str(data["id"]) != rid:
        raise RuntimeError("Freepik returned details for a different resource ID.")
    if data.get("is_ai_generated") is not False or data.get("has_prompt") is not False:
        raise RuntimeError("Freepik did not confirm both non-AI fields for this asset.")
    license_url = _pick_license_url_from_detail(data, jsonpath=None) if not request["license_url_jsonpath"] else None
    plan = {
        "kind": "download",
        "apply": False,
        "request": request,
        "resource_id": rid,
        "format": request["format"],
        "image_size": request["image_size"],
        "license_url": license_url,
        "resource_url": data.get("url"),
        "preview_url": best_preview_url(data),
        "name": data.get("name") or data.get("title"),
        "author": (data.get("author") or {}).get("name") if isinstance(data.get("author"), dict) else None,
        "resource_type": data.get("type"),
        "is_ai_generated": data["is_ai_generated"],
        "has_prompt": data["has_prompt"],
        "before_state": _build_before_state_contract(
            resource_id=rid,
            fmt=request["format"],
            out_dir=Path(request["downloads_dir"]),
            inventory=Path(request["inventory_csv"]),
            image_size=request["image_size"],
        ),
        "verification_plan": _build_after_apply_verification_plan(),
    }
    if request["license_url_jsonpath"]:
        try:
            plan["license_url"] = _pick_license_url_from_detail(detail, jsonpath=request["license_url_jsonpath"])
        except (RuntimeError, KeyError, IndexError, ValueError, TypeError):
            pass
    return plan, data


def _returned_fields(payload: Any) -> tuple[str | None, str]:
    if not isinstance(payload, dict):
        return None, ""
    link = payload.get("license_url") or payload.get("licenseUrl") or _pick_license_url_from_detail(payload, jsonpath=None)
    if not isinstance(link, str) or urlparse(link).scheme not in {"http", "https"}:
        link = None
    return link, str(payload.get("download_id") or payload.get("downloadId") or "")


def _receipt_row(data: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    req = plan["request"]
    author = data.get("author") or data.get("contributor")
    tags = data.get("tags")
    keywords = []
    if isinstance(tags, list):
        for tag in tags:
            value = (tag.get("name") or tag.get("slug")) if isinstance(tag, dict) else tag
            if value:
                keywords.append(str(value))
    return {
        **{k: req[k] for k in ("resource_id", "image_size", "post_slug", "ghost_id", "usage_role")},
        "downloaded_at_utc": now_utc_iso(),
        "title": plan["name"] or "",
        "resource_type": plan["resource_type"] or "",
        "resource_url": plan["resource_url"] or "",
        "preview_url": plan["preview_url"] or "",
        "keywords": "; ".join(keywords),
        "author": author.get("name") or "" if isinstance(author, dict) else str(author or ""),
    }


def _file_format(path: Path) -> str:
    with path.open("rb") as stream:
        prefix = stream.read(16)
    if prefix.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if prefix.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return "zip"
    if prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP":
        return "webp"
    return path.suffix.lstrip(".").lower()


def apply_download(plan: dict[str, Any], data: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    req = plan["request"]
    _check_local_targets(req)
    rid, fmt = req["resource_id"], req["format"]
    out_dir = Path(req["downloads_dir"])
    inventory = Path(req["inventory_csv"])
    api, http = _asset_client(ctx)
    rows: list[dict[str, Any]] = []
    paths: list[str] = []
    result = {
        "ok": False,
        "resource_id": rid,
        "requested_format": fmt,
        "rows": rows,
        "file_paths": paths,
        "inventory_csv": str(inventory),
        "before_state": plan["before_state"],
        "no_snapshot_approval": {"acknowledged": True, "flag": "--ack-no-snapshot"},
        "recovery": _irreversible_license_recovery_contract(),
        "provider_status": "outcome_unknown",
    }

    try:
        if req["image_size"]:
            payload = api.download_by_id(rid, image_size=req["image_size"])
        else:
            payload = api.download_by_id_and_format(rid, fmt=fmt)
    except (RuntimeError, ValueError):
        result["error"] = (
            "Freepik's download outcome is unclear. Check Stock downloads in your account before trying again."
        )
        ctx["audit"].write("freepik.download.incomplete", result)
        return result

    result["provider_status"] = "replied"
    step = "read the download response"
    try:
        receipt_link, download_id = _returned_fields(payload)
        if isinstance(payload, dict):
            data_link, data_id = _returned_fields(payload.get("data"))
            receipt_link, download_id = data_link or receipt_link, data_id or download_id
        if req["license_url_jsonpath"]:
            try:
                receipt_link = _pick_license_url_from_detail(payload, jsonpath=req["license_url_jsonpath"])
            except (RuntimeError, KeyError, IndexError, ValueError, TypeError):
                pass
        result.update(license_url=receipt_link or plan["license_url"], download_id=download_id)
        targets = _pick_download_targets(payload, jsonpath=req["download_url_jsonpath"], fallback=f"{rid}.{fmt}")
        shared_license = receipt_link or plan["license_url"]
        target_links = [_returned_fields(target.get("metadata")) for target in targets]
        result.update(license_url=shared_license, download_id=download_id)
        step = "find the license link"
        if not shared_license and any(not link for link, _ in target_links):
            try:
                detail = api.get_resource(rid)
                shared_license = _pick_license_url_from_detail(detail, jsonpath=req["license_url_jsonpath"])
            except (RuntimeError, KeyError, IndexError, ValueError, TypeError):
                shared_license = None
        if not shared_license and any(not link for link, _ in target_links):
            raise RuntimeError("Freepik replied to the download request without a usable license link.")

        result.update(license_url=shared_license, download_id=download_id)
        base_row = _receipt_row(data, plan)
        step = "check the destination files"
        used_names: set[str] = set()
        outputs = []
        for index, (target, (target_license, target_id)) in enumerate(zip(targets, target_links, strict=True), 1):
            remote_name = Path(target["filename"]).name or "download"
            name = f"{rid}--{remote_name}"
            while name in used_names:
                name = f"{rid}--{index}--{name}"
            used_names.add(name)
            file_path = out_dir / name
            if file_path.exists() and not req["force"]:
                raise RuntimeError(f"A file already exists here: {file_path}")
            outputs.append((target, file_path, target_license or shared_license, target_id or download_id))
        for target, file_path, license_url, file_download_id in outputs:
            step = "save the downloaded file"
            http.download_to_path(target["url"], file_path, retries=2, overwrite=req["force"])
            paths.append(str(file_path))
            actual_format = _file_format(file_path)
            row = {
                **base_row,
                "file_name": file_path.name,
                "file_path": str(file_path),
                "sha256": sha256_file(file_path),
                "download_url": target["url"],
                "download_id": file_download_id,
                "license_url": license_url,
                "format": actual_format,
                "notes": f"requested_format={fmt}" if actual_format != fmt else "",
            }
            step = "write the inventory row"
            append_inventory_row(inventory, row)
            rows.append(row)
    except (RuntimeError, OSError, ValueError, KeyError, IndexError, TypeError):
        result["error"] = (
            f"Freepik replied, but the tool could not {step}. "
            "Check Stock downloads and the listed local files before trying again."
        )
        ctx["audit"].write("freepik.download.incomplete", result)
        return result

    result["ok"] = True
    result["verification"] = {"ok": True, "mode": "download-and-inventory", "file_count": len(rows)}
    ctx["audit"].write("freepik.download", result)
    return result


def run_download(args: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    request = download_request(args, ctx)
    apply = bool(ctx["apply"])
    if apply and ctx.get("ack_no_snapshot"):
        require_reviewed_plan(ctx, kind="download", requests=[request])
    plan, data = prepare_download(request, ctx)
    if not apply:
        return {
            "dry_run": True,
            "plan": plan,
            "plan_out": save_plan(ctx.get("plan_out"), plan),
            "recovery": _irreversible_license_recovery_contract(),
        }
    if not ctx.get("ack_no_snapshot"):
        return _missing_no_snapshot_approval_output(plan)
    return apply_download(plan, data, ctx)


def cmd_download(args: Any, ctx: dict[str, Any]) -> int:
    result = run_download(args, ctx)
    ctx["out"].emit(result)
    return 1 if result.get("ok") is False else 0
