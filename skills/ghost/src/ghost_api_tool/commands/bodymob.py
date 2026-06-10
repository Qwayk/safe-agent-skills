from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path
from typing import Any

from ..caption_policy import caption_matches_expected, guess_caption_policy
from ..content_mobiledoc import (
    dedupe_image_cards,
    dump_mobiledoc_field,
    parse_mobiledoc_field,
    replace_images_by_src_map,
)
from ..post_patch import resolve_post
from ..runtime import get_api


def add_bodymob_commands(post_sub) -> None:
    bodymob = post_sub.add_parser("bodymob", help="Post body helpers (Mobiledoc mode)")
    bodymob_sub = bodymob.add_subparsers(dest="bodymob_cmd", required=True)

    inspect = bodymob_sub.add_parser("inspect", help="List image cards in mobiledoc")
    inspect.add_argument("--slug", default=None)
    inspect.add_argument("--id", default=None)
    inspect.set_defaults(func=cmd_bodymob_inspect)

    scaffold = bodymob_sub.add_parser("scaffold", help="Generate editable helper files (no API writes)")
    scaffold_sub = scaffold.add_subparsers(dest="bodymob_scaffold_cmd", required=True)

    captions_map = scaffold_sub.add_parser(
        "captions-map",
        help="Write a replace-many mapping for image captions/alts (fill in manually)",
    )
    captions_map.add_argument("--slug", default=None)
    captions_map.add_argument("--id", default=None)
    captions_map.add_argument("--out", required=True, help="Output JSON path")
    captions_map.add_argument(
        "--mode",
        choices=["missing", "all", "nonconforming"],
        default="missing",
        help="missing: only images missing captions; all: include every image; nonconforming: missing or caption-policy mismatch",
    )
    captions_map.add_argument("--all", action="store_true", help="Deprecated alias for --mode all (kept for compatibility).")
    captions_map.add_argument(
        "--include-context",
        action="store_true",
        help="Include non-applying helper fields like _card_index/_kind_guess/_expected_suffix.",
    )
    captions_map.add_argument("--force", action="store_true", help="Overwrite output file if it exists")
    captions_map.set_defaults(func=cmd_bodymob_scaffold_captions_map)

    image = bodymob_sub.add_parser("image", help="Image operations (mobiledoc image cards)")
    image_sub = image.add_subparsers(dest="bodymob_image_cmd", required=True)

    replace_many = image_sub.add_parser(
        "replace-many",
        help="Replace many mobiledoc image src values from a JSON mapping (single post update)",
    )
    replace_many.add_argument("--slug", default=None)
    replace_many.add_argument("--id", default=None)
    replace_many.add_argument("--map", required=True, help="JSON file mapping old_src -> new_src or object")
    replace_many.add_argument("--diff", action="store_true")
    replace_many.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    replace_many.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    replace_many.set_defaults(func=cmd_bodymob_image_replace_many)

    dedupe = image_sub.add_parser(
        "dedupe",
        help="Remove duplicate mobiledoc image cards by src (keeps first occurrence)",
    )
    dedupe.add_argument("--slug", default=None)
    dedupe.add_argument("--id", default=None)
    dedupe.add_argument("--diff", action="store_true")
    dedupe.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    dedupe.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    dedupe.set_defaults(func=cmd_bodymob_image_dedupe)


def _selector(slug: str | None, post_id: str | None) -> dict[str, str | None]:
    return {"slug": slug} if slug else {"id": post_id}


def _refuse_on_non_draft(before: dict[str, Any], *, allow_published: bool) -> list[str]:
    status = before.get("status")
    if status != "draft" and not allow_published:
        return [f"Refused: post status is {status}; pass --allow-published or use --require-current draft"]
    return []


def cmd_bodymob_inspect(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"selector": sel, "post_id": str(post.get("id")), "status": post.get("status")}

    mob_obj, reasons = parse_mobiledoc_field(post.get("mobiledoc"))
    if mob_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": reasons, "images": []})
        return 0

    from ..content_mobiledoc import list_images as list_mobiledoc_images

    imgs, reasons = list_mobiledoc_images(mob_obj)
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons, "images": []})
        return 0
    ctx["out"].print({**base, "refused": False, "images": [dataclasses.asdict(i) for i in imgs]})
    return 0


def cmd_bodymob_scaffold_captions_map(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(post.get("id")), "status": post.get("status")}

    mob_obj, reasons = parse_mobiledoc_field(post.get("mobiledoc"))
    if mob_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    from ..content_mobiledoc import list_images as list_mobiledoc_images

    mode = "all" if bool(args.all) else str(args.mode)
    if bool(args.all) and str(args.mode) != "missing":
        ctx["out"].print({**base, "refused": True, "reasons": ["Refused: pass either --all or --mode (not both)"]})
        return 0

    imgs, reasons = list_mobiledoc_images(mob_obj)
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    mapping: dict[str, dict[str, Any]] = {}
    for img in imgs:
        cap = img.caption or ""
        has_cap = bool(cap.strip())
        if mode == "missing" and has_cap:
            continue
        exp = guess_caption_policy(img.src, alt=img.alt, title=img.title, caption_text=img.caption)
        if mode == "nonconforming" and has_cap and caption_matches_expected(img.caption, expected_suffix=exp.expected_suffix):
            continue

        item: dict[str, Any] = {"new_src": img.src, "alt": img.alt or "", "caption": cap if mode != "missing" and has_cap else ""}
        if img.title and img.title.strip():
            item["title"] = img.title
        if bool(args.include_context):
            item.update(
                {
                    "_index": img.index,
                    "_card_index": img.card_index,
                    "_kind_guess": exp.kind,
                    "_expected_suffix": exp.expected_suffix,
                    "_existing_alt": img.alt,
                    "_existing_caption": img.caption,
                    "_existing_title": img.title,
                }
            )
        mapping[img.src] = item

    if not mapping:
        ctx["out"].print({**base, "refused": True, "reasons": ["No images matched (nothing to scaffold)"], "out": args.out})
        return 0

    out_path = Path(args.out)
    if out_path.exists() and not args.force:
        ctx["out"].print({**base, "refused": True, "reasons": [f"Refused: output file exists (pass --force): {args.out}"], "out": args.out})
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ctx["out"].print({**base, "refused": False, "out": args.out, "image_count": len(mapping)})
    return 0


def _apply_mobiledoc_update(
    *,
    api,
    before: dict[str, Any],
    new_mobiledoc_obj: dict[str, Any],
    verify_transform,
    debug_ctx: str,
) -> dict[str, Any]:
    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError(f"{debug_ctx}: Post is missing updated_at; cannot safely update")
    mob_str = dump_mobiledoc_field(new_mobiledoc_obj)
    api.posts_update(str(before["id"]), {"posts": [{"updated_at": updated_at, "mobiledoc": mob_str}]})

    after = resolve_post(api, slug=None, post_id=str(before["id"]), formats="html,lexical,mobiledoc")
    after_obj, reasons = parse_mobiledoc_field(after.get("mobiledoc"))
    if after_obj is None:
        raise RuntimeError(f"{debug_ctx}: Verification failed: cannot parse mobiledoc after update: {reasons}")
    vrep, _new, _items = verify_transform(after_obj)
    if vrep.refused:
        raise RuntimeError(f"{debug_ctx}: Verification refused after update: {vrep.reasons}")
    if vrep.changed:
        raise RuntimeError(f"{debug_ctx}: Verification failed: re-running the transform would still change the post")
    return after


def cmd_bodymob_image_replace_many(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print({**base, "refused": True, "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"]})
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    with open(args.map, encoding="utf-8") as f:
        mapping = json.load(f)

    mob_obj, parse_reasons = parse_mobiledoc_field(before.get("mobiledoc"))
    if mob_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj, items = replace_images_by_src_map(mob_obj, mapping=mapping, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "items": [dataclasses.asdict(i) for i in items]})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "changed": False, "matched": rep.matched, "items": [dataclasses.asdict(i) for i in items]})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "diff": rep.diff, "items": [dataclasses.asdict(i) for i in items]})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return replace_images_by_src_map(obj, mapping=mapping, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodymob.image.replace_many"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodymob.image.replace_many",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "map_file": args.map, "matched": rep.matched},
        )
    try:
        after = _apply_mobiledoc_update(
            api=api, before=before, new_mobiledoc_obj=new_obj, verify_transform=verify_transform, debug_ctx="bodymob.replace_many"
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodymob.image.replace_many",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "selector": sel, "error": str(e), "map_file": args.map},
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodymob.image.replace_many",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "map_file": args.map, "matched": rep.matched},
        )

    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "items": [dataclasses.asdict(i) for i in items]})
    return 0


def cmd_bodymob_image_dedupe(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print({**base, "refused": True, "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"]})
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    mob_obj, parse_reasons = parse_mobiledoc_field(before.get("mobiledoc"))
    if mob_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj, result = dedupe_image_cards(mob_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "changed": False, "removed": result.removed, "duplicates": result.duplicates})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "changed": True,
                "removed": result.removed,
                "duplicates": result.duplicates,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return dedupe_image_cards(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodymob.image.dedupe"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodymob.image.dedupe",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "removed": result.removed, "duplicates": result.duplicates},
        )
    try:
        after = _apply_mobiledoc_update(api=api, before=before, new_mobiledoc_obj=new_obj, verify_transform=verify_transform, debug_ctx="bodymob.dedupe")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodymob.image.dedupe",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "selector": sel, "error": str(e)},
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodymob.image.dedupe",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "removed": result.removed, "duplicates": result.duplicates},
        )

    ctx["out"].print({**base, "refused": False, "changed": True, "removed": result.removed, "duplicates": result.duplicates})
    return 0
