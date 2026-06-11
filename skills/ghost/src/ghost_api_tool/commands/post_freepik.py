from __future__ import annotations

import csv
import dataclasses
import json
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError, VerificationError
from ..content_lexical import (
    LexicalEditReport,
    dump_lexical_field,
    fix_numbered_paragraphs_to_list_after_heading,
    list_images as list_lexical_images,
    parse_lexical_field,
    sync_top_level_images_before_headings,
)
from ..post_patch import apply_post_patch, resolve_post
from ..runtime import get_api


_CAPTION_SUFFIX = "(stock image; for illustration only)."


@dataclasses.dataclass(frozen=True)
class ApplyOnePlan:
    selector: dict[str, str]
    post_id: str
    slug: str
    status: str
    snapshot_path: str | None
    remove_images_changed: bool
    removed_reasons: list[str]
    removed_matched: int
    detected_split_numbered_lists: int
    detected_numbered_paragraphs_instructions: int
    fixed_numbered_paragraphs_instructions: bool
    warnings: list[str]
    lexical_changed: bool
    would_upload: dict[str, Any] | None
    would_patch_fields: dict[str, Any]
    would_publish: bool
    tracking_csv: str | None


def _selector(slug: str | None, post_id: str | None) -> dict[str, str]:
    if bool(slug) == bool(post_id):
        raise ValidationError("Provide exactly one selector: --slug or --id")
    return {"slug": slug} if slug else {"id": str(post_id)}


def _require_caption_suffix(caption: str) -> None:
    cap = caption.strip()
    if not cap.endswith(_CAPTION_SUFFIX):
        raise ValidationError(f"Caption must end with: {_CAPTION_SUFFIX}")


def _write_json_snapshot(*, out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_local_path(path_str: str, *, project_dir: Path) -> Path:
    """
    Resolve a local path in a customer-ready way:

    - Absolute stays absolute.
    - Relative prefers the current working directory if it exists there.
    - Otherwise falls back to resolving relative to `project_dir`.
    """
    p = Path(str(path_str)).expanduser()
    if p.is_absolute():
        return p
    cwd_p = (Path.cwd() / p).resolve()
    if cwd_p.exists():
        return cwd_p
    return (project_dir / p).resolve()


def _default_snapshot_path(*, slug: str, post_id: str, snapshots_dir: str | None, project_dir: Path) -> Path | None:
    if not snapshots_dir or not str(snapshots_dir).strip():
        return None
    base = _resolve_local_path(str(snapshots_dir), project_dir=project_dir)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    name = f"{slug or post_id}.pre_apply.{ts}.json"
    return base / name


def _read_tracking_row(
    *, tracking_csv: Path, ghost_id: str, ghost_slug: str | None
) -> tuple[list[dict[str, str]], list[str], dict[str, str] | None]:
    rows: list[dict[str, str]] = []
    reasons: list[str] = []
    found: dict[str, str] | None = None
    with tracking_csv.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
            if row.get("ghost_id") == ghost_id:
                found = row
            elif ghost_slug and row.get("ghost_slug_final") == ghost_slug and found is None:
                found = row
    if not rows:
        reasons.append("tracking.csv is empty")
    return rows, reasons, found


_TRACKING_APPEND_FIELDS = {"freepik_apply_notes", "notes"}


def _update_tracking_csv(
    *,
    tracking_csv: Path,
    ghost_id: str,
    ghost_slug: str,
    updates: dict[str, str],
    project_dir: Path,
) -> None:
    tracking_csv = _resolve_local_path(str(tracking_csv), project_dir=project_dir)
    if not tracking_csv.exists():
        raise ValidationError(f"Tracking CSV not found: {tracking_csv}")
    rows, reasons, _found = _read_tracking_row(tracking_csv=tracking_csv, ghost_id=ghost_id, ghost_slug=ghost_slug)
    if reasons:
        raise ValidationError("; ".join(reasons))
    if not rows:
        raise ValidationError("tracking.csv is empty")
    fieldnames = list(rows[0].keys())
    updated = False
    for row in rows:
        if row.get("ghost_id") == ghost_id or row.get("ghost_slug_final") == ghost_slug:
            for k, v in updates.items():
                if k not in row:
                    raise ValidationError(f"tracking.csv missing expected column: {k}")
                if k in _TRACKING_APPEND_FIELDS:
                    cur = (row.get(k) or "").strip()
                    v2 = (v or "").strip()
                    if not v2:
                        continue
                    row[k] = (cur + ("\n" if cur else "") + v2)
                else:
                    row[k] = v
            updated = True
            break
    if not updated:
        raise ValidationError(f"Could not find tracking row for ghost_id={ghost_id} slug={ghost_slug}")
    with tracking_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _ghost_edit_url_from_admin_api_url(*, admin_api_url: str, post_id: str) -> str:
    base = admin_api_url.rstrip("/")
    marker = "/ghost/api/admin"
    if marker not in base:
        raise ValidationError("Cannot derive Ghost editor URL from GHOST_ADMIN_API_URL (missing /ghost/api/admin/)")
    site_base = base.split(marker, 1)[0]
    return f"{site_base}/ghost/#/editor/post/{post_id}"


def _resolve_featured_from_inventory(*, inventory_csv: Path, resource_id: str, post_slug: str) -> Path:
    inv = inventory_csv.expanduser().resolve()
    if not inv.exists():
        raise ValidationError(f"Inventory CSV not found: {inv}")

    matches: list[dict[str, str]] = []
    with inv.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if not isinstance(row, dict):
                continue
            rid = str(row.get("resource_id") or "").strip()
            if rid != resource_id:
                continue
            row_slug = str(row.get("post_slug") or row.get("ghost_slug") or "").strip()
            if row_slug and post_slug and row_slug != post_slug:
                continue
            matches.append({str(k): str(v) for k, v in row.items()})

    if not matches:
        raise ValidationError(f"Inventory does not contain resource_id={resource_id} (post_slug={post_slug}): {inv}")

    preferred = [m for m in matches if str(m.get("usage_role") or "").strip().lower() == "featured"]
    chosen = preferred[0] if len(preferred) == 1 else matches[0]

    file_path = str(chosen.get("file_path") or "").strip()
    if not file_path:
        raise ValidationError(f"Inventory row missing file_path for resource_id={resource_id}: {inv}")
    p = Path(file_path)
    if not p.is_absolute():
        p = inv.parent / p
    p = p.resolve()
    if not p.exists():
        raise ValidationError(f"Inventory file_path does not exist: {p}")
    return p


def _resolve_featured_from_downloads_root(*, downloads_root: Path, resource_id: str, post_slug: str) -> Path:
    root = downloads_root.expanduser().resolve()
    if not root.exists():
        raise ValidationError(f"Downloads root not found: {root}")
    by_post = root / "by-post" / post_slug
    if not by_post.exists():
        raise ValidationError(f"Downloads folder not found for post_slug={post_slug}: {by_post}")
    matches = sorted(by_post.glob(f"{resource_id}--*.jpg"))
    if not matches:
        matches = sorted(by_post.glob(f"{resource_id}--*.jpeg"))
    if len(matches) != 1:
        raise ValidationError(f"Expected exactly 1 downloaded file for {resource_id} under {by_post}, got {len(matches)}")
    return matches[0].resolve()


def _resolve_featured_file(
    *,
    featured_file: str | None,
    featured_freepik_id: str | None,
    post_slug: str,
    freepik_inventory_csv: str | None,
    freepik_downloads_root: str | None,
    project_dir: Path,
) -> str:
    if featured_file and featured_file.strip():
        p = _resolve_local_path(str(featured_file), project_dir=project_dir)
        if not p.exists():
            raise ValidationError(f"Featured file not found: {p}")
        return str(p)

    if not (featured_freepik_id and featured_freepik_id.strip()):
        raise ValidationError("Pass --featured-file or --freepik-featured-id (to auto-resolve file path)")
    rid = featured_freepik_id.strip()

    if freepik_inventory_csv and str(freepik_inventory_csv).strip():
        inv = _resolve_local_path(str(freepik_inventory_csv), project_dir=project_dir)
        return str(_resolve_featured_from_inventory(inventory_csv=inv, resource_id=rid, post_slug=post_slug))

    if freepik_downloads_root and str(freepik_downloads_root).strip():
        root = _resolve_local_path(str(freepik_downloads_root), project_dir=project_dir)
        return str(_resolve_featured_from_downloads_root(downloads_root=root, resource_id=rid, post_slug=post_slug))

    raise ValidationError(
        "Pass --featured-file, or pass --freepik-featured-id with either --freepik-inventory-csv or --freepik-downloads-root (so the tool can resolve the local file path)"
    )


def cmd_post_freepik_apply_one(args, ctx) -> int:
    api = get_api(ctx)
    project_cfg = ctx.get("project_cfg") or {}
    project_dir = Path(str(ctx.get("project_dir") or Path.cwd())).expanduser().resolve()
    sel = _selector(args.slug, args.id)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical")
    post_id = str(before.get("id"))
    slug = str(before.get("slug") or "")
    status = str(before.get("status") or "")
    edit_url = _ghost_edit_url_from_admin_api_url(admin_api_url=api._cfg.admin_api_url, post_id=post_id)  # noqa: SLF001

    if args.require_current and status != args.require_current:
        ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: require-current={args.require_current} but status={status}"]})
        return 0

    if not isinstance(args.featured_alt, str) or not args.featured_alt.strip():
        raise ValidationError("--featured-alt is required")
    if not isinstance(args.featured_caption, str) or not args.featured_caption.strip():
        raise ValidationError("--featured-caption is required")
    _require_caption_suffix(args.featured_caption)

    snapshots_dir = args.snapshots_dir
    if snapshots_dir is None:
        snapshots_dir = project_cfg.get("snapshots_dir") or str(project_dir / "snapshots")
    snapshot_path = _default_snapshot_path(slug=slug, post_id=post_id, snapshots_dir=str(snapshots_dir), project_dir=project_dir)
    if bool(ctx["apply"]) and snapshot_path is not None:
        _write_json_snapshot(out_path=snapshot_path, payload=before)

    lexical_obj, parse_reasons = parse_lexical_field(before.get("lexical"))
    if lexical_obj is None:
        ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": parse_reasons})
        return 0

    warnings: list[str] = []
    detected_numbered_paragraphs_instructions = 0
    fixed_numbered_paragraphs_instructions = False
    try:
        drep, dobj = fix_numbered_paragraphs_to_list_after_heading(
            lexical_obj,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        if drep.refused:
            warnings.append("Nonstandard Instructions list detected but auto-fix refused: " + "; ".join(drep.reasons))
        elif drep.changed:
            detected_numbered_paragraphs_instructions = int(drep.matched or 0)
            if not bool(args.no_fix_numbered_paragraphs):
                lexical_obj = dobj
                fixed_numbered_paragraphs_instructions = True
            else:
                warnings.append('Instructions uses numbered paragraphs; pass without --no-fix-numbered-paragraphs to normalize to an ordered list.')
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Failed to detect/fix numbered paragraph Instructions list: {e}")

    if bool(ctx["apply"]) and bool(args.publish) and detected_numbered_paragraphs_instructions and bool(args.no_fix_numbered_paragraphs):
        ctx["out"].print(
            {
                "apply": True,
                "refused": True,
                "selector": sel,
                "post_id": post_id,
                "reasons": [
                    "Refused: Instructions list is numbered paragraphs (non-standard spacing); run `post bodylex fix-numbered-paragraphs-after-heading --heading Instructions` or omit --no-fix-numbered-paragraphs.",
                ],
            }
        )
        return 0

    # Body images: remove all existing top-level images and safe standalone HTML <img> cards.
    rep: LexicalEditReport
    new_obj: dict[str, Any]
    detected_split_numbered_lists = 0

    if args.placements_file and args.body_images_json:
        ctx["out"].print(
            {
                "apply": bool(ctx["apply"]),
                "refused": True,
                "selector": sel,
                "post_id": post_id,
                "reasons": ["Refused: pass either --placements-file or --body-images-json (not both)"],
            }
        )
        return 0

    # placements: either a direct placements file (with src URLs), or a local-file upload plan that we will convert to placements.
    placements: list[dict[str, Any]] = []
    if args.placements_file:
        try:
            placements = json.loads(_resolve_local_path(args.placements_file, project_dir=project_dir).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            ctx["out"].print(
                {"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: failed to read placements file: {e}"]}
            )
            return 0

    body_upload_plan: list[dict[str, Any]] = []
    if args.body_images_json:
        try:
            body_upload_plan = json.loads(_resolve_local_path(args.body_images_json, project_dir=project_dir).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            ctx["out"].print(
                {"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: failed to read body images JSON: {e}"]}
            )
            return 0
        if not isinstance(body_upload_plan, list):
            ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": ["Refused: body images JSON must be a list"]})
            return 0
        for i, item in enumerate(body_upload_plan):
            if not isinstance(item, dict):
                ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: body image #{i+1} is not an object"]})
                return 0
            if not (isinstance(item.get("file"), str) and item["file"].strip()):
                ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: body image #{i+1} missing file"]})
                return 0
            file_path = _resolve_local_path(str(item["file"]), project_dir=project_dir)
            if not file_path.exists():
                ctx["out"].print(
                    {
                        "apply": bool(ctx["apply"]),
                        "refused": True,
                        "selector": sel,
                        "post_id": post_id,
                        "reasons": [f"Refused: body image #{i+1} file not found: {file_path}"],
                    }
                )
                return 0
            if not (isinstance(item.get("heading"), str) and item["heading"].strip()):
                ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: body image #{i+1} missing heading"]})
                return 0
            if not (isinstance(item.get("alt"), str) and item["alt"].strip()):
                ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: body image #{i+1} missing alt"]})
                return 0
            if not (isinstance(item.get("caption"), str) and item["caption"].strip()):
                ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": [f"Refused: body image #{i+1} missing caption"]})
                return 0
            _require_caption_suffix(str(item["caption"]))

    # Detect split numbered lists (best-effort): numbered list immediately after "Instructions" plus an HTML <ol> card.
    try:
        root_children = lexical_obj.get("root", {}).get("children", [])
        if isinstance(root_children, list):
            for i, node in enumerate(root_children):
                if isinstance(node, dict) and node.get("type") == "extended-heading":
                    txt = "".join(
                        c.get("text", "") for c in (node.get("children") or []) if isinstance(c, dict) and isinstance(c.get("text"), str)
                    ).strip()
                    if txt.lower() == "instructions":
                        # Find next non-empty node
                        j = i + 1
                        while j < len(root_children):
                            n = root_children[j]
                            if isinstance(n, dict) and n.get("type") == "paragraph":
                                # empty paragraph?
                                t = "".join(
                                    c.get("text", "") for c in (n.get("children") or []) if isinstance(c, dict) and isinstance(c.get("text"), str)
                                ).strip()
                                if not t:
                                    j += 1
                                    continue
                            break
                        if j + 1 < len(root_children):
                            first = root_children[j]
                            nxt = root_children[j + 1]
                            if (
                                isinstance(first, dict)
                                and first.get("type") == "list"
                                and first.get("listType") == "number"
                                and isinstance(nxt, dict)
                                and nxt.get("type") == "html"
                                and isinstance(nxt.get("html"), str)
                                and "<ol" in nxt["html"].lower()
                            ):
                                detected_split_numbered_lists += 1
                        break
    except Exception:
        detected_split_numbered_lists = detected_split_numbered_lists

    rep, new_obj = sync_top_level_images_before_headings(
        lexical_obj,
        placements=placements,
        fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": rep.reasons, "matched": rep.matched})
        return 0

    # Verify lexical idempotence locally (re-running the same transform yields no further changes).
    vrep, _vobj = sync_top_level_images_before_headings(
        new_obj,
        placements=placements,
        fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
        include_diff=False,
    )
    if vrep.refused:
        ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": ["Refused: verification transform refused", *vrep.reasons]})
        return 0
    if vrep.changed:
        ctx["out"].print({"apply": bool(ctx["apply"]), "refused": True, "selector": sel, "post_id": post_id, "reasons": ["Refused: verification transform was not idempotent (would change content again)"]})
        return 0

    if fixed_numbered_paragraphs_instructions:
        v2rep, _v2obj = fix_numbered_paragraphs_to_list_after_heading(
            new_obj,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        if v2rep.refused:
            ctx["out"].print(
                {
                    "apply": bool(ctx["apply"]),
                    "refused": True,
                    "selector": sel,
                    "post_id": post_id,
                    "reasons": ["Refused: numbered-paragraph list verification refused", *v2rep.reasons],
                }
            )
            return 0
        if v2rep.changed:
            ctx["out"].print(
                {
                    "apply": bool(ctx["apply"]),
                    "refused": True,
                    "selector": sel,
                    "post_id": post_id,
                    "reasons": ["Refused: numbered-paragraph list verification was not idempotent (would change content again)"],
                }
            )
            return 0

    tracking_csv = args.tracking_csv
    if tracking_csv is None:
        tracking_csv = project_cfg.get("tracking_csv")
    if isinstance(tracking_csv, str) and not tracking_csv.strip():
        tracking_csv = None

    freepik_inventory_csv = args.freepik_inventory_csv or project_cfg.get("freepik_inventory_csv")
    freepik_downloads_root = args.freepik_downloads_root or project_cfg.get("freepik_downloads_root")

    featured_freepik_id = (args.freepik_featured_id or "").strip() or None
    featured_file = _resolve_featured_file(
        featured_file=args.featured_file,
        featured_freepik_id=featured_freepik_id,
        post_slug=slug,
        freepik_inventory_csv=str(freepik_inventory_csv) if freepik_inventory_csv else None,
        freepik_downloads_root=str(freepik_downloads_root) if freepik_downloads_root else None,
        project_dir=project_dir,
    )
    upload_name = args.featured_upload_name or f"{slug}-featured.jpg"

    plan = ApplyOnePlan(
        selector=sel,
        post_id=post_id,
        slug=slug,
        status=status,
        snapshot_path=str(snapshot_path) if snapshot_path else None,
        remove_images_changed=bool(rep.changed),
        removed_reasons=list(rep.reasons or []),
        removed_matched=int(rep.matched or 0),
        detected_split_numbered_lists=detected_split_numbered_lists,
        detected_numbered_paragraphs_instructions=detected_numbered_paragraphs_instructions,
        fixed_numbered_paragraphs_instructions=fixed_numbered_paragraphs_instructions,
        warnings=list(warnings),
        lexical_changed=bool(rep.changed) or fixed_numbered_paragraphs_instructions,
        would_upload={"file": featured_file, "upload_name": upload_name, "purpose": "image"},
        would_patch_fields={
            "lexical": "<updated>" if (rep.changed or fixed_numbered_paragraphs_instructions) else "<unchanged>",
            "feature_image": "<uploaded-url>",
            "feature_image_alt": args.featured_alt.strip(),
            "feature_image_caption": args.featured_caption.strip(),
        },
        would_publish=bool(args.publish),
        tracking_csv=str(tracking_csv) if tracking_csv else None,
    )

    if not ctx["apply"]:
        ctx["out"].print(
            dataclasses.asdict(plan)
            | {"apply": False, "refused": False, "diff": rep.diff if bool(args.diff) else None, "ghost_edit_url": edit_url}
        )
        return 0

    # If requested, upload body images first, convert to placements with Ghost URLs, then re-run the body sync in-memory.
    applied_body_ids: list[str] = []
    if body_upload_plan:
        # Re-fetch the post again? Not needed; we already have lexical template nodes in lexical_obj.
        placements = []
        for item in body_upload_plan:
            file_path = str(_resolve_local_path(str(item["file"]), project_dir=project_dir))
            upload_name_body = item.get("upload_name")
            upload_body = api.upload_image(file_path=file_path, purpose="image", ref=file_path, upload_name=upload_name_body)
            imgs_body = upload_body.get("images") or []
            if not imgs_body or not imgs_body[0].get("url"):
                raise RuntimeError(f"Body image upload did not return an image url: {upload_body}")
            url_body = imgs_body[0]["url"]
            placements.append(
                {
                    "heading": item["heading"],
                    "heading_occurrence": item.get("heading_occurrence"),
                    "src": url_body,
                    "alt": item.get("alt"),
                    "caption": item.get("caption"),
                    "title": item.get("title"),
                }
            )
            if isinstance(item.get("freepik_id"), str) and item["freepik_id"].strip():
                applied_body_ids.append(item["freepik_id"].strip())

        rep2, new_obj2 = sync_top_level_images_before_headings(
            lexical_obj,
            placements=placements,
            fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
            include_diff=False,
        )
        if rep2.refused:
            raise SafetyError("Refused: body placement sync refused: " + "; ".join(rep2.reasons))
        vrep2, _ = sync_top_level_images_before_headings(
            new_obj2,
            placements=placements,
            fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
            include_diff=False,
        )
        if vrep2.refused or vrep2.changed:
            raise SafetyError("Refused: body placement sync was not idempotent")
        rep, new_obj = rep2, new_obj2

    # Apply: upload image and patch post (keep as draft for verification), then optionally publish.
    upload = api.upload_image(file_path=featured_file, purpose="image", ref=featured_file, upload_name=upload_name)
    imgs = upload.get("images") or []
    if not imgs or not imgs[0].get("url"):
        raise RuntimeError(f"Upload did not return an image url: {upload}")
    feature_url = imgs[0]["url"]

    patch: dict[str, Any] = {
        "feature_image": feature_url,
        "feature_image_alt": args.featured_alt.strip(),
        "feature_image_caption": args.featured_caption.strip(),
    }
    if rep.changed:
        patch["lexical"] = dump_lexical_field(new_obj)

    # Step 1: apply content changes while draft.
    plan1 = apply_post_patch(
        api,
        slug=args.slug,
        post_id=args.id,
        patch=patch,
        apply=True,
        require_current=args.require_current,
        snapshot=ctx.get("backup"),
        snapshot_action="post.freepik.apply_one",
        snapshot_meta={
            "featured": {"file": featured_file, "upload_name": upload_name, "url": feature_url},
            "placements_file": args.placements_file,
        },
    )

    # Verify: no Lexical images remain in body (post-wide).
    after_lex_obj, after_parse_reasons = parse_lexical_field(plan1.after.get("lexical"))
    if after_lex_obj is None:
        raise VerificationError("Verification failed: cannot parse post.lexical after update: " + "; ".join(after_parse_reasons))
    after_imgs = list_lexical_images(after_lex_obj)
    desired_srcs = [str(p.get("src")) for p in placements if isinstance(p, dict) and isinstance(p.get("src"), str)]
    if desired_srcs:
        got_srcs = [i.src for i in after_imgs]
        if len(got_srcs) != len(desired_srcs):
            raise VerificationError(f"Verification failed: expected {len(desired_srcs)} body image(s), got {len(got_srcs)}")
        extra = [s for s in got_srcs if s not in desired_srcs]
        missing = [s for s in desired_srcs if s not in got_srcs]
        if extra or missing:
            raise VerificationError(f"Verification failed: body image src mismatch (extra={extra}, missing={missing})")
        # Verify placement: each desired src is immediately before the intended heading occurrence.
        root_children = after_lex_obj.get("root", {}).get("children", [])
        if not isinstance(root_children, list):
            raise VerificationError("Verification failed: invalid lexical root.children after update")
        # Build heading positions by normalized text (exact match required by sync helper).
        def _heading_text(node: Any) -> str | None:
            if not (isinstance(node, dict) and node.get("type") == "extended-heading"):
                return None
            parts = []
            for c in node.get("children") or []:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    parts.append(c["text"])
            return "".join(parts).strip()

        heading_positions: dict[str, list[int]] = {}
        for idx, node in enumerate(root_children):
            t = _heading_text(node)
            if t is None:
                continue
            heading_positions.setdefault(t, []).append(idx)

        for p in placements:
            if not isinstance(p, dict):
                continue
            heading = p.get("heading")
            src = p.get("src")
            occ = p.get("heading_occurrence") or 1
            if not (isinstance(heading, str) and isinstance(src, str)):
                continue
            idxs = heading_positions.get(heading, [])
            if not idxs or occ < 1 or occ > len(idxs):
                raise VerificationError(f"Verification failed: heading not found for placement: {heading} occurrence {occ}")
            h_idx = idxs[occ - 1]
            if h_idx < 1:
                raise VerificationError(f"Verification failed: heading is first node; cannot have image before heading: {heading}")
            prev = root_children[h_idx - 1]
            if not (isinstance(prev, dict) and prev.get("type") == "image" and prev.get("src") == src):
                raise VerificationError(f"Verification failed: expected image src immediately before heading {heading}: {src}")
    else:
        if after_imgs:
            raise VerificationError("Verification failed: body still contains Lexical image node(s) after removal")

    published = False
    plan2 = None
    if bool(args.publish):
        if not bool(ctx.get("yes")):
            ctx["out"].print(
                {
                    "apply": True,
                    "refused": True,
                    "reasons": ["Refused: publishing requires --yes"],
                    "selector": sel,
                    "post_id": post_id,
                    "edit_url": edit_url,
                }
            )
            return 0
        plan2 = apply_post_patch(
            api,
            slug=args.slug,
            post_id=args.id,
            patch={"status": "published"},
            apply=True,
            require_current="draft",
            snapshot=ctx.get("backup"),
            snapshot_action="post.freepik.publish",
            snapshot_meta={"from_status": "draft"},
        )
        published = True

    # Update tracking.csv (mechanical).
    tracking_updated = False
    if tracking_csv:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        notes_bits: list[str] = []
        if rep.changed and rep.reasons:
            notes_bits.append("; ".join(rep.reasons))
        if fixed_numbered_paragraphs_instructions:
            notes_bits.append("Normalized Instructions numbered paragraphs to ordered list")
        if detected_split_numbered_lists and not bool(args.no_fix_split_numbered_lists):
            notes_bits.append("Fixed split numbered list under Instructions")
        if warnings:
            notes_bits.append("Warnings: " + "; ".join(warnings))
        notes_bits.append("Set featured image alt/caption")
        notes_bits.append(f"Verified {len(applied_body_ids)} body images")
        if published:
            notes_bits.append("Published")
        updates = {
            "ghost_status": "published" if published else str(plan1.after.get("status") or ""),
            "ghost_edit_url": edit_url,
            "freepik_apply_status": "completed" if published else "applied",
            "freepik_applied_featured_id": str(featured_freepik_id or ""),
            "freepik_applied_body_ids": "|".join(applied_body_ids),
            "freepik_applied_at": ts,
            "freepik_apply_notes": f"{ts}: " + ". ".join(notes_bits).strip() + ".",
        }
        _update_tracking_csv(
            tracking_csv=Path(str(tracking_csv)),
            ghost_id=post_id,
            ghost_slug=slug,
            updates=updates,
            project_dir=project_dir,
        )
        tracking_updated = True

    ctx["out"].print(
        {
            "apply": True,
            "refused": False,
            "selector": sel,
            "post_id": post_id,
            "slug": slug,
            "ghost_edit_url": edit_url,
            "snapshot_path": str(snapshot_path) if snapshot_path else None,
            "removed_body_images": rep.reasons,
            "feature_image": feature_url,
            "published": published,
            "tracking_updated": tracking_updated,
            "tracking_csv": str(tracking_csv) if tracking_csv else None,
            "after_status": (plan2.after.get("status") if plan2 else plan1.after.get("status")),
        }
    )
    return 0
