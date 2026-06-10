from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..content_lexical import list_images as list_lexical_images
from ..content_lexical import parse_lexical_field
from ..runtime import get_api


@dataclass(frozen=True)
class LedgerRow:
    image_url: str
    image_kind: str  # featured|body
    post_id: str
    post_slug: str
    post_title: str
    post_status: str
    primary_tag_slug: str
    tags_slugs: str
    alt: str
    caption: str
    context_heading: str
    image_index: str


def add_post_images_commands(post_sub) -> None:
    post_images = post_sub.add_parser("images", help="Post image export helpers (read-only)")
    images_sub = post_images.add_subparsers(dest="post_images_cmd", required=True)

    export = images_sub.add_parser(
        "export-ledger",
        help="Export a CSV ledger of featured + body image URLs from Lexical posts",
    )
    export.add_argument("--out", required=True, help="Output CSV path")
    export.add_argument("--filter", default=None, help="Ghost filter string (same syntax as Ghost Admin API)")
    export.add_argument("--limit", type=int, default=25, help="Posts per page (API limit)")
    export.add_argument("--max-pages", type=int, default=None, help="Optional max page count (for testing)")
    export.add_argument("--include", default="tags", help="Comma-separated include list (default: tags)")
    export.add_argument("--order", default=None, help='Order string, e.g. "published_at desc"')
    export.set_defaults(func=cmd_post_images_export_ledger)


def _tag_slugs(tags: Any) -> list[str]:
    out: list[str] = []
    if isinstance(tags, list):
        for t in tags:
            if isinstance(t, dict):
                slug = t.get("slug")
                if isinstance(slug, str) and slug.strip():
                    out.append(slug.strip())
            elif isinstance(t, str) and t.strip():
                out.append(t.strip())
    return out


def _primary_tag_slug(post: dict[str, Any]) -> str:
    pt = post.get("primary_tag")
    if isinstance(pt, dict):
        slug = pt.get("slug")
        if isinstance(slug, str):
            return slug
    if isinstance(pt, str):
        return pt
    return ""


def _coerce_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _ledger_rows_for_post(post: dict[str, Any]) -> tuple[list[LedgerRow], list[str]]:
    rows: list[LedgerRow] = []
    warnings: list[str] = []

    post_id = str(post.get("id") or "")
    slug = _coerce_str(post.get("slug"))
    title = _coerce_str(post.get("title"))
    status = _coerce_str(post.get("status"))

    tags = post.get("tags")
    tag_slugs = _tag_slugs(tags)
    primary_tag_slug = _primary_tag_slug(post)
    tags_joined = "|".join(tag_slugs)

    feature_image = _coerce_str(post.get("feature_image"))
    if feature_image.strip():
        rows.append(
            LedgerRow(
                image_url=feature_image.strip(),
                image_kind="featured",
                post_id=post_id,
                post_slug=slug,
                post_title=title,
                post_status=status,
                primary_tag_slug=primary_tag_slug,
                tags_slugs=tags_joined,
                alt=_coerce_str(post.get("feature_image_alt")).strip(),
                caption=_coerce_str(post.get("feature_image_caption")).strip(),
                context_heading="",
                image_index="",
            )
        )

    lexical_obj, reasons = parse_lexical_field(post.get("lexical"))
    if lexical_obj is None:
        # Still include featured image; record warning for body parsing.
        if reasons:
            warnings.extend(reasons)
        return rows, warnings

    imgs = list_lexical_images(lexical_obj)
    for img in imgs:
        if not img.src:
            continue
        rows.append(
            LedgerRow(
                image_url=img.src,
                image_kind="body",
                post_id=post_id,
                post_slug=slug,
                post_title=title,
                post_status=status,
                primary_tag_slug=primary_tag_slug,
                tags_slugs=tags_joined,
                alt=(img.alt or "").strip(),
                caption=(img.caption_text or "").strip(),
                context_heading=(img.context_heading or "").strip(),
                image_index=str(img.index),
            )
        )

    return rows, warnings


def cmd_post_images_export_ledger(args, ctx) -> int:
    api = get_api(ctx)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    include = [s.strip() for s in str(args.include or "").split(",") if s.strip()]
    params: dict[str, Any] = {"limit": int(args.limit)}
    if args.filter:
        params["filter"] = str(args.filter)
    if include:
        params["include"] = ",".join(include)
    if args.order:
        params["order"] = str(args.order)

    header = [
        "image_url",
        "image_kind",
        "post_id",
        "post_slug",
        "post_title",
        "post_status",
        "primary_tag_slug",
        "tags_slugs",
        "alt",
        "caption",
        "context_heading",
        "image_index",
    ]

    pages_fetched = 0
    posts_seen = 0
    featured_rows = 0
    body_rows = 0
    posts_with_body_images = 0
    parse_warnings: dict[str, list[str]] = {}

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()

        page = 1
        while True:
            if args.max_pages is not None and pages_fetched >= int(args.max_pages):
                break
            res = api.posts_browse(params={**params, "page": page})
            pages_fetched += 1
            posts = res.get("posts")
            if not isinstance(posts, list):
                raise RuntimeError("Unexpected Ghost response: missing posts list")

            for post in posts:
                if not isinstance(post, dict):
                    continue
                posts_seen += 1
                rows, warnings = _ledger_rows_for_post(post)
                if warnings:
                    parse_warnings[str(post.get("id") or post.get("slug") or f"row{posts_seen}")] = warnings
                has_body = False
                for row in rows:
                    w.writerow(
                        {
                            "image_url": row.image_url,
                            "image_kind": row.image_kind,
                            "post_id": row.post_id,
                            "post_slug": row.post_slug,
                            "post_title": row.post_title,
                            "post_status": row.post_status,
                            "primary_tag_slug": row.primary_tag_slug,
                            "tags_slugs": row.tags_slugs,
                            "alt": row.alt,
                            "caption": row.caption,
                            "context_heading": row.context_heading,
                            "image_index": row.image_index,
                        }
                    )
                    if row.image_kind == "featured":
                        featured_rows += 1
                    elif row.image_kind == "body":
                        body_rows += 1
                        has_body = True
                if has_body:
                    posts_with_body_images += 1

            meta = res.get("meta") or {}
            pagination = meta.get("pagination") if isinstance(meta, dict) else None
            if not isinstance(pagination, dict):
                break
            next_page = pagination.get("next")
            if not next_page:
                break
            page = int(next_page)

    ctx["out"].print(
        {
            "out_csv": str(out_path),
            "filter": params.get("filter"),
            "include": params.get("include"),
            "order": params.get("order"),
            "pages_fetched": pages_fetched,
            "posts_seen": posts_seen,
            "rows_featured": featured_rows,
            "rows_body": body_rows,
            "posts_with_body_images": posts_with_body_images,
            "posts_with_parse_warnings": len(parse_warnings),
            "parse_warnings": parse_warnings if parse_warnings else None,
        }
    )
    return 0

