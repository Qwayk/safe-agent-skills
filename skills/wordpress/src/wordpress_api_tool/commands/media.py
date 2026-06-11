from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..batchio import load_media_download_items, load_media_updates
from ..diffutil import caption_text_from_media, source_url_from_media, title_text_from_media
from ..http import HttpClient
from .. import v2 as v2util
from ..wp_api import WordPressApi


def _media_get(api: WordPressApi, media_id: int):
    media = api.media_by_id(int(media_id))
    return {
        "id": media.get("id"),
        "source_url": source_url_from_media(media),
        "title": title_text_from_media(media),
        "alt_text": media.get("alt_text") or "",
        "caption": caption_text_from_media(media),
        "raw": media,
    }


def _media_set(
    api: WordPressApi,
    *,
    media_id: int,
    caption: str | None,
    alt_text: str | None,
    title: str | None,
    apply: bool,
):
    if caption is None and alt_text is None and title is None:
        raise RuntimeError("Refused: no fields provided (use --caption/--alt-text/--title)")
    before = api.media_by_id(int(media_id))
    desired = {"caption": caption, "alt_text": alt_text, "title": title}
    before_norm = {
        "caption": caption_text_from_media(before),
        "alt_text": before.get("alt_text") or "",
        "title": title_text_from_media(before),
        "source_url": source_url_from_media(before),
    }

    would_change = {}
    for k, v in desired.items():
        if v is None:
            continue
        if v != before_norm[k]:
            would_change[k] = {"before": before_norm[k], "after": v}

    result = {
        "target": {"media_id": int(media_id), "source_url": before_norm["source_url"]},
        "apply": bool(apply),
        "changes": would_change,
    }

    if not would_change:
        result["changed"] = False
        return result

    if not apply:
        result["changed"] = True
        return result

    api.update_media(media_id=int(media_id), caption=caption, alt_text=alt_text, title=title)

    after = api.media_by_id(int(media_id))
    after_norm = {
        "caption": caption_text_from_media(after),
        "alt_text": after.get("alt_text") or "",
        "title": title_text_from_media(after),
    }

    verified = True
    mismatches = {}
    for k, v in desired.items():
        if v is None:
            continue
        if after_norm[k] != v:
            verified = False
            mismatches[k] = {"expected": v, "actual": after_norm[k]}

    result.update({"changed": True, "verified": verified, "mismatches": mismatches})
    return result


def _media_set_batch(
    api: WordPressApi,
    *,
    updates: list[dict[str, str | None]],
    apply: bool,
) -> dict[str, Any]:
    if not updates:
        raise RuntimeError("Refused: empty updates list")

    ids: list[int] = []
    for u in updates:
        raw = u.get("id")
        if raw is None or str(raw).strip() == "":
            raise RuntimeError("Refused: each update must include an 'id'")
        ids.append(int(raw))

    media_list = api.media_by_include(ids)
    by_id: dict[int, dict[str, Any]] = {}
    for m in media_list:
        if not isinstance(m, dict):
            continue
        mid = m.get("id")
        if isinstance(mid, int):
            by_id[mid] = m

    missing = [i for i in ids if i not in by_id]
    if missing:
        raise RuntimeError(f"Refused: some media ids were not found or not accessible: {missing}")

    results: list[dict[str, Any]] = []
    to_update: list[dict[str, Any]] = []

    for u in updates:
        raw_id = u.get("id")
        assert raw_id is not None
        media_id = int(raw_id)
        before = by_id.get(media_id) or {}
        desired = {"caption": u.get("caption"), "alt_text": u.get("alt_text"), "title": u.get("title")}
        if desired["caption"] is None and desired["alt_text"] is None and desired["title"] is None:
            raise RuntimeError(f"Refused: media id={media_id} has no fields set (caption/alt_text/title)")

        before_norm = {
            "caption": caption_text_from_media(before),
            "alt_text": before.get("alt_text") or "",
            "title": title_text_from_media(before),
            "source_url": source_url_from_media(before),
        }

        would_change: dict[str, Any] = {}
        for k, v in desired.items():
            if v is None:
                continue
            if v != before_norm[k]:
                would_change[k] = {"before": before_norm[k], "after": v}

        res: dict[str, Any] = {
            "target": {"media_id": media_id, "source_url": before_norm["source_url"]},
            "apply": bool(apply),
            "changes": would_change,
        }
        if not would_change:
            res["changed"] = False
            results.append(res)
            continue

        if not apply:
            res["changed"] = True
            results.append(res)
            continue

        to_update.append({"media_id": media_id, "desired": desired, "result": res})
        results.append(res)

    if not apply:
        return {"apply": False, "count": len(results), "errors": 0, "results": results}

    updated_ids: list[int] = []
    for item in to_update:
        mid = int(item["media_id"])
        desired = item["desired"]
        try:
            api.update_media(
                media_id=mid,
                caption=desired.get("caption"),
                alt_text=desired.get("alt_text"),
                title=desired.get("title"),
            )
            updated_ids.append(mid)
        except Exception as e:
            raise RuntimeError(f"Failed updating media id={mid}: {e}") from e

    after_by_id: dict[int, dict[str, Any]] = {}
    if updated_ids:
        after_list = api.media_by_include(updated_ids)
        for m in after_list:
            if not isinstance(m, dict):
                continue
            mid = m.get("id")
            if isinstance(mid, int):
                after_by_id[mid] = m

    errors = 0
    for item in to_update:
        mid = int(item["media_id"])
        desired = item["desired"]
        res = item["result"]
        after = after_by_id.get(mid)
        if not isinstance(after, dict):
            res["verified"] = False
            res["mismatches"] = {"_error": {"expected": "media item", "actual": "missing on read-back"}}
            errors += 1
            continue

        after_norm = {
            "caption": caption_text_from_media(after),
            "alt_text": after.get("alt_text") or "",
            "title": title_text_from_media(after),
        }
        verified = True
        mismatches: dict[str, Any] = {}
        for k, v in desired.items():
            if v is None:
                continue
            if after_norm[k] != v:
                verified = False
                mismatches[k] = {"expected": v, "actual": after_norm[k]}
        res["verified"] = verified
        res["mismatches"] = mismatches
        if not verified:
            errors += 1

    return {"apply": True, "count": len(results), "errors": errors, "results": results}


def cmd_media_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    ctx["out"].emit(_media_get(api, int(args.id)))
    return 0


def cmd_media_find(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    params: dict[str, Any] = {}
    if args.query:
        params["search"] = str(args.query)

    page = api.list_collection(
        "/media",
        params=params,
        context=str(args.context),
        limit=int(args.limit),
        per_page=None if args.per_page is None else int(args.per_page),
        max_pages=int(args.max_pages),
    )

    results = []
    for m in page["items"]:
        if not isinstance(m, dict):
            continue
        results.append(
            {
                "id": m.get("id"),
                "source_url": source_url_from_media(m),
                "title": title_text_from_media(m),
                "alt_text": m.get("alt_text") or "",
                "caption": caption_text_from_media(m),
                "mime_type": m.get("mime_type"),
                "media_type": m.get("media_type"),
                "link": m.get("link"),
            }
        )

    payload: dict[str, Any] = {
        "ok": True,
        "count": len(results),
        "limit": page["limit"],
        "truncated": page["truncated"],
        "results": results,
    }
    if page.get("truncated_reason"):
        payload["truncated_reason"] = page["truncated_reason"]
    if page.get("total") is not None:
        payload["total"] = page["total"]
    if page.get("total_pages") is not None:
        payload["total_pages"] = page["total_pages"]
    payload["pages_fetched"] = page["pages_fetched"]

    ctx["out"].emit(payload)
    return 0


def cmd_media_resolve(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    media = api.media_resolve_by_url(url=str(args.url))
    ctx["out"].emit(_media_get(api, int(media["id"])))
    return 0


def _safe_filename_from_url(url: str) -> str:
    name = (urlparse(url).path or "").split("/")[-1] or "download"
    # Remove any path traversal and control chars.
    name = name.replace("\\", "_").replace("/", "_").strip()
    if not name:
        name = "download"
    return name


def cmd_media_download(args, ctx) -> int:
    if bool(args.id) == bool(args.url):
        raise RuntimeError("Refused: provide exactly one selector: --id or --url")

    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"])
    api = WordPressApi.from_config(ctx["cfg"], http)

    if args.id is not None:
        media = api.media_by_id(int(args.id))
        url = source_url_from_media(media)
        if not url:
            raise RuntimeError("Media item is missing source_url")
    else:
        url = str(args.url)

    out_dir = Path(str(args.out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename_from_url(url)
    out_path = out_dir / filename

    try:
        meta = http.download_to_file(url, out_path=str(out_path))
    except Exception as e:
        raise RuntimeError(f"Download failed for {url}: {type(e).__name__}: {e}") from e

    ctx["out"].emit(
        {
            "url": url,
            "path": str(out_path),
            "bytes": os.path.getsize(out_path),
            "sha256": meta.get("sha256"),
            "content_type": meta.get("content_type"),
        }
    )
    return 0


_FILENAME_ALLOWED_RE = re.compile(r"[^A-Za-z0-9._ -]+")


def _sanitize_filename(name: str) -> str:
    raw = str(name or "").strip()
    if not raw:
        return "download"
    # Refuse if user attempted a path; we only allow bare filenames.
    if "/" in raw or "\\" in raw:
        raise RuntimeError("Refused: filename must not contain path separators")
    p = Path(raw)
    if p.is_absolute() or p.name != raw:
        raise RuntimeError("Refused: filename must be a simple name (no directories)")
    if raw in {".", ".."}:
        raise RuntimeError("Refused: filename is not allowed")
    cleaned = _FILENAME_ALLOWED_RE.sub("_", raw).strip(" .")
    if not cleaned:
        cleaned = "download"
    if cleaned in {".", ".."}:
        cleaned = "download"
    # Keep filenames reasonably short to avoid filesystem issues.
    if len(cleaned) > 200:
        root, ext = os.path.splitext(cleaned)
        cleaned = (root[: max(0, 200 - len(ext))] + ext)[:200]
    return cleaned


def _insert_suffix(filename: str, suffix: str) -> str:
    root, ext = os.path.splitext(filename)
    if not root:
        root = "download"
    return f"{root}{suffix}{ext}"


def _safe_join_out_dir(out_dir: Path, filename: str) -> Path:
    out_dir_resolved = out_dir.resolve()
    out_path = (out_dir / filename).resolve()
    if not out_path.is_relative_to(out_dir_resolved):
        raise RuntimeError("Refused: output path escapes --out-dir")
    return out_path


def media_download_batch_core(
    api: WordPressApi,
    http: HttpClient,
    *,
    items: list[dict[str, str | None]],
    out_dir: Path,
    skip_existing: bool,
    max_items: int,
    apply: bool,
) -> dict[str, Any]:
    if not items:
        raise RuntimeError("Refused: empty input file")

    hard_cap = 5000
    if max_items <= 0:
        raise RuntimeError("Refused: --max-items must be positive")
    if max_items > hard_cap:
        raise RuntimeError(f"Refused: --max-items exceeds hard cap ({hard_cap})")
    if len(items) > max_items:
        raise RuntimeError(f"Refused: input has {len(items)} items (> --max-items {max_items})")

    def _validate_url(url: str) -> str:
        u = str(url or "").strip()
        if not u:
            raise RuntimeError("Refused: empty url")
        parsed = urlparse(u)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError("Refused: url must be http(s)")
        return u

    results: list[dict[str, Any]] = []
    errors = 0
    used_filenames: dict[str, int] = {}
    out_dir_created = False

    def _choose_filename(item: dict[str, str | None], url: str) -> str:
        base = item.get("filename") or _safe_filename_from_url(url)
        filename = _sanitize_filename(base)
        n = used_filenames.get(filename, 0) + 1
        used_filenames[filename] = n
        if n == 1:
            return filename
        return _insert_suffix(filename, f"-{n}")

    for idx, item in enumerate(items, start=1):
        raw_id = None if item.get("id") is None else str(item.get("id") or "").strip()
        raw_url = None if item.get("url") is None else str(item.get("url") or "").strip()
        selector: dict[str, Any] = {}
        if raw_id:
            try:
                selector["id"] = int(raw_id)
            except Exception as e:
                errors += 1
                results.append({"row": idx, "input": item, "error": f"Invalid id: {e}"})
                break
        if raw_url:
            selector["url"] = raw_url
        if not selector:
            errors += 1
            results.append({"row": idx, "input": item, "error": "Missing both id and url"})
            break

        try:
            resolved_url: str
            if "id" in selector:
                media = api.media_by_id(int(selector["id"]))
                resolved_url = source_url_from_media(media)
                if not resolved_url:
                    raise RuntimeError("Media item is missing source_url")
                resolved_url = _validate_url(resolved_url)
                if "url" in selector:
                    provided = _validate_url(str(selector["url"]))
                    if provided != resolved_url:
                        raise RuntimeError("Provided url does not match source_url resolved from id")
            else:
                resolved_url = _validate_url(str(selector["url"]))

            filename = _choose_filename(item, resolved_url)
            out_path = _safe_join_out_dir(out_dir, filename)

            would_skip = bool(skip_existing and out_path.exists())
            action = "skip" if would_skip else "download"
            entry: dict[str, Any] = {
                "row": idx,
                "selector": selector,
                "url": resolved_url,
                "path": str(out_path),
                "action": action,
            }

            if not apply:
                results.append(entry)
                continue

            if would_skip:
                entry["ok"] = True
                entry["skipped_reason"] = "exists"
                results.append(entry)
                continue

            if not out_dir_created:
                out_dir.mkdir(parents=True, exist_ok=True)
                out_dir_created = True

            meta = http.download_to_file(resolved_url, out_path=str(out_path))
            size = os.path.getsize(out_path) if out_path.exists() else 0
            if size <= 0:
                raise RuntimeError("Downloaded file is empty")

            entry.update(
                {
                    "ok": True,
                    "bytes": int(meta.get("bytes") or size),
                    "sha256": meta.get("sha256"),
                    "content_type": meta.get("content_type"),
                }
            )
            results.append(entry)
        except Exception as e:
            errors += 1
            results.append({"row": idx, "selector": selector, "input": item, "error": str(e)})
            break

    return {
        "ok": errors == 0,
        "apply": bool(apply),
        "count": len(results),
        "errors": errors,
        "results": results,
    }


def cmd_media_download_batch(args, ctx) -> int:
    if ctx["apply"] and not ctx["yes"]:
        raise RuntimeError("Refused: batch media downloads require both --apply and --yes")

    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"])
    api = WordPressApi.from_config(ctx["cfg"], http)

    try:
        items = load_media_download_items(str(args.file))
    except Exception as e:
        raise RuntimeError(f"Failed to read --file {args.file!r}: {e}") from e

    out_dir = Path(str(args.out_dir))

    result = media_download_batch_core(
        api,
        http,
        items=items,
        out_dir=out_dir,
        skip_existing=bool(args.skip_existing),
        max_items=int(args.max_items),
        apply=bool(ctx["apply"]),
    )

    downloaded_count = 0
    skipped_count = 0
    if isinstance(result.get("results"), list):
        for r in result["results"]:
            if not isinstance(r, dict):
                continue
            if r.get("ok") is True and r.get("action") == "download":
                downloaded_count += 1
            if r.get("ok") is True and r.get("action") == "skip":
                skipped_count += 1

    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"file": str(args.file), "out_dir": str(out_dir)},
            "risk_level": "medium",
            "risk_reasons": ["Downloads many files to local disk (batch local writes)"],
            "preconditions": [
                "Review the plan (paths, filenames, and counts) before applying",
                "For apply, use --apply --yes (this command enforces both)",
            ],
            "proposed_changes": result.get("results") or [],
            "verification_plan": "After apply, verify each downloaded file exists and has size > 0.",
            "rollback": {"supported": True, "notes": "Delete the downloaded files from the output directory."},
        }
        result["dry_run"] = True
        result["risk_level"] = plan["risk_level"]
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        changed_any = downloaded_count > 0
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"file": str(args.file), "out_dir": str(out_dir)},
            "changed": changed_any,
            "verification": {
                "ok": bool(result.get("errors") == 0),
                "details": {
                    "errors": int(result.get("errors") or 0),
                    "downloaded": downloaded_count,
                    "skipped": skipped_count,
                },
            },
            "diff_applied": result.get("results") or [],
            "backups": None,
            "rollback_plan": None,
        }
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)

    ctx["audit"].write("media.download_batch", result)
    ctx["out"].emit(result)
    return 1 if int(result.get("errors") or 0) else 0


def cmd_media_set(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    before_media = api.media_by_id(int(args.id))
    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family="media.set",
        selector=f"id-{int(args.id)}",
        payload={"media": before_media},
    )

    result = _media_set(
        api,
        media_id=int(args.id),
        caption=args.caption,
        alt_text=args.alt_text,
        title=args.title,
        apply=bool(ctx["apply"]),
    )
    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("target") or {"media_id": int(args.id)},
            "risk_level": "medium",
            "risk_reasons": ["Edits existing Media Library metadata"],
            "preconditions": [
                "You have permission to edit this media item",
                "The media item exists and is accessible",
            ],
            "proposed_changes": result.get("changes") or {},
            "before_state": before_state,
            "verification_plan": (
                "After apply, re-fetch the media item and assert the edited fields match the requested values."
            ),
            "rollback": {
                "supported": True,
                "notes": before_state["restore_note"],
            },
        }
        result["dry_run"] = True
        result["risk_level"] = plan["risk_level"]
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        changed = bool(result.get("changed"))
        verified = bool(result.get("verified")) if changed else True
        fields = list((result.get("changes") or {}).keys())
        rollback_plan = None
        if changed:
            rollback_plan = (
                "To revert, re-run media set with the previous values from the `diff_applied` block "
                f"({', '.join(fields) or 'fields'})."
            )
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("target") or {"media_id": int(args.id)},
            "changed": changed,
            "verification": {
                "ok": verified,
                "details": {"verified_fields": fields} if changed and verified else (result.get("mismatches") or {}),
            },
            "diff_applied": result.get("changes") or {},
            "before_state": before_state,
            "backups": [before_state],
            "rollback_plan": rollback_plan or before_state["restore_note"],
        }
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)
    ctx["audit"].write("media.set", result)
    ctx["out"].emit(result)
    return 0


def cmd_media_set_batch(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    try:
        updates = load_media_updates(args.file)
    except Exception as e:
        raise RuntimeError(f"Failed to read --file {args.file!r}: {e}") from e

    ids: list[int] = []
    for u in updates:
        try:
            ids.append(int(u.get("id") or 0))
        except Exception:
            continue
    before_media = api.media_by_include(ids) if ids else []
    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family="media.set-batch",
        selector=f"count-{len(ids)}",
        payload={"media_ids": ids, "media": before_media},
    )

    result = _media_set_batch(api, updates=updates, apply=bool(ctx["apply"]))

    changed_any = False
    if isinstance(result.get("results"), list):
        for r in result["results"]:
            if isinstance(r, dict) and r.get("changed") is True:
                changed_any = True
                break

    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"media_ids": ids, "file": str(args.file)},
            "risk_level": "high",
            "risk_reasons": ["Batch edit of Media Library metadata"],
            "preconditions": [
                "Review the plan and proposed changes carefully before applying",
                "You have permission to edit every targeted media item",
            ],
            "proposed_changes": result.get("results") or [],
            "before_state": before_state,
            "verification_plan": (
                "After apply, re-fetch updated media items and assert the edited fields match the requested values."
            ),
            "rollback": {
                "supported": True,
                "notes": before_state["restore_note"],
            },
        }
        result["dry_run"] = True
        result["risk_level"] = plan["risk_level"]
        result["changed"] = changed_any
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        errors = int(result.get("errors") or 0)
        verified_ok = errors == 0
        if isinstance(result.get("results"), list):
            for r in result["results"]:
                if not isinstance(r, dict):
                    continue
                if r.get("changed") is True and r.get("verified") is False:
                    verified_ok = False
                    break

        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"media_ids": ids, "file": str(args.file)},
            "changed": changed_any,
            "verification": {"ok": verified_ok, "details": {"errors": errors}},
            "diff_applied": result.get("results") or [],
            "before_state": before_state,
            "backups": [before_state],
            "rollback_plan": before_state["restore_note"] if changed_any else None,
        }
        result["changed"] = changed_any
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)
    ctx["audit"].write("media.set_batch", result)
    ctx["out"].emit(result)
    return 0 if not result.get("errors") else 1


# Used by jobs runner.
media_set_core = _media_set
media_set_batch_core = _media_set_batch
