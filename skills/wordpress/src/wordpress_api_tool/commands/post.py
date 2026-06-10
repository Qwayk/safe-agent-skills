from __future__ import annotations

from collections.abc import Iterable
import difflib
import hashlib
from typing import Any

from ..batchio import load_caption_map
from ..diffutil import caption_text_from_media, source_url_from_media, title_text_from_media
from ..edit_content import update_gutenberg_image_captions
from ..extract import extract_attachment_ids_from_post_content, extract_img_srcs_from_html
from ..http import HttpClient
from .. import v2 as v2util
from ..wp_api import WordPressApi


def _dedupe_preserve_order_ints(values: Iterable[int]) -> list[int]:
    seen: set[int] = set()
    out: list[int] = []
    for v in values:
        iv = int(v)
        if iv in seen:
            continue
        seen.add(iv)
        out.append(iv)
    return out


def _sorted_unique_ints(values: Iterable[int]) -> list[int]:
    return sorted(set(int(v) for v in values))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _replace_exact(
    content_raw: str,
    *,
    from_text: str,
    to_text: str,
    expected_count: int,
    max_replacements: int,
) -> tuple[dict[str, Any], str]:
    if not isinstance(from_text, str) or not from_text:
        raise RuntimeError("Refused: --from must be a non-empty string")
    if not isinstance(to_text, str):
        raise RuntimeError("Refused: --to must be a string")
    expected_count = int(expected_count)
    if expected_count < 0:
        raise RuntimeError("Refused: --expected-count must be >= 0")
    max_replacements = int(max_replacements)
    if max_replacements < 0:
        raise RuntimeError("Refused: --max-replacements must be >= 0")

    before_count = content_raw.count(from_text)
    if before_count != expected_count:
        raise RuntimeError(
            f"Refused: source string occurrence count mismatch (expected {expected_count}, found {before_count})"
        )
    if expected_count == 0:
        return (
            {
                "before_count": before_count,
                "will_replace": 0,
                "after_count": before_count,
            },
            content_raw,
        )

    will_replace = min(before_count, max_replacements)
    new_raw = content_raw.replace(from_text, to_text, will_replace)
    after_count = new_raw.count(from_text)
    return (
        {
            "before_count": before_count,
            "will_replace": will_replace,
            "after_count": after_count,
        },
        new_raw,
    )


def _post_replace_in_content(
    api: WordPressApi,
    *,
    post_type: str,
    slug: str | None,
    post_id: int | None,
    from_text: str,
    to_text: str,
    expected_count: int,
    max_replacements: int,
    include_diff: bool,
    apply: bool,
) -> dict[str, Any]:
    if bool(slug) == bool(post_id):
        raise RuntimeError("Refused: provide exactly one selector: --slug or --id")

    if slug is not None:
        post = api.post_by_slug(post_type=post_type, slug=str(slug))
    else:
        assert post_id is not None
        post = api.post_by_id(post_type=post_type, post_id=int(post_id))

    resolved_id = post.get("id")
    if not isinstance(resolved_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    content_raw = (post.get("content") or {}).get("raw")
    if not isinstance(content_raw, str):
        raise RuntimeError("Missing content.raw (ensure auth has edit context).")

    if max_replacements is None:
        max_replacements = int(expected_count)

    change_meta, new_raw = _replace_exact(
        content_raw,
        from_text=from_text,
        to_text=to_text,
        expected_count=expected_count,
        max_replacements=int(max_replacements),
    )
    changed = new_raw != content_raw

    diff = None
    if include_diff and changed:
        diff = "\n".join(
            difflib.unified_diff(
                content_raw.splitlines(),
                new_raw.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )

    result: dict[str, Any] = {
        "post": {
            "id": resolved_id,
            "slug": post.get("slug") or slug,
            "post_type": str(post_type),
            "link": post.get("link"),
            "title": post.get("title", {}).get("rendered") if isinstance(post.get("title"), dict) else post.get("title"),
        },
        "apply": bool(apply),
        "changed": bool(changed),
        "changes": {
            "content_raw": {
                "from": {"text": from_text, "sha256": _sha256_text(from_text)},
                "to": {"text": to_text, "sha256": _sha256_text(to_text)},
                "match": change_meta,
                "before_sha256": _sha256_text(content_raw),
                "after_sha256": _sha256_text(new_raw),
                "diff": diff,
            }
        },
    }

    if not apply:
        return result

    if not changed:
        result["verified"] = True
        result["verify"] = {"note": "No changes needed"}
        return result

    api.update_post_content(post_type=post_type, post_id=resolved_id, content_raw=new_raw)
    after = api.post_by_id(post_type=post_type, post_id=resolved_id)
    after_raw = (after.get("content") or {}).get("raw")
    if not isinstance(after_raw, str):
        result["verified"] = False
        result["verify"] = {"error": "Missing content.raw on read-back"}
        return result

    remaining = after_raw.count(from_text)
    expected_remaining = int(change_meta.get("after_count") or 0)
    result["verified"] = remaining == expected_remaining
    result["verify"] = {
        "remaining_source_occurrences": remaining,
        "expected_remaining_source_occurrences": expected_remaining,
    }
    return result


def _post_set_image_captions(
    api: WordPressApi,
    *,
    post_type: str,
    slug: str,
    caption: str | None,
    caption_html: str | None,
    alt_text: str | None,
    captions_file: str | None,
    only_ids_csv: str | None,
    include_diff: bool,
    apply: bool,
):
    if caption is None and caption_html is None and alt_text is None and captions_file is None:
        raise RuntimeError(
            "Refused: no fields provided (use --caption or --caption-html or --captions-file and/or --alt-text)"
        )
    post = api.post_by_slug(post_type=post_type, slug=slug)
    post_id = post.get("id")
    if not isinstance(post_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    content_raw = (post.get("content") or {}).get("raw")
    if not isinstance(content_raw, str):
        raise RuntimeError("Missing content.raw (ensure auth has edit context).")

    if captions_file is not None and (caption is not None or caption_html is not None):
        raise RuntimeError("Provide only one of --caption/--caption-html or --captions-file")
    if caption is not None and caption_html is not None:
        raise RuntimeError("Provide only one of --caption or --caption-html")

    only_ids = None
    if only_ids_csv:
        only_ids = {int(x.strip()) for x in only_ids_csv.split(",") if x.strip()}

    caption_text_by_id = None
    if captions_file is not None:
        try:
            caption_text_by_id = load_caption_map(captions_file)
        except Exception as e:
            raise RuntimeError(f"Failed to read --captions-file {captions_file!r}: {e}") from e
        if not caption_text_by_id:
            raise RuntimeError(f"Refused: --captions-file {captions_file!r} contained no captions")

    report, new_raw = update_gutenberg_image_captions(
        content_raw,
        caption_text=caption,
        caption_html=caption_html,
        alt_text=alt_text,
        caption_text_by_id=caption_text_by_id,
        only_ids=only_ids,
        include_diff=include_diff,
    )

    result = {
        "post": {"id": post_id, "slug": slug, "post_type": post_type},
        "apply": bool(apply),
        "report": {
            "matched_blocks": report.matched_blocks,
            "updated_blocks": report.updated_blocks,
            "refused_blocks": report.refused_blocks,
            "reasons": report.reasons,
            "diff": report.diff,
        },
    }

    if not apply:
        return result

    if new_raw == content_raw:
        result["verified"] = True
        return result

    api.update_post_content(post_type=post_type, post_id=post_id, content_raw=new_raw)
    after = api.post_by_id(post_type=post_type, post_id=post_id)
    after_raw = (after.get("content") or {}).get("raw")
    if not isinstance(after_raw, str):
        result["verified"] = False
        result["verify"] = {"error": "Missing content.raw on read-back"}
        return result

    # Verification is semantic: if re-running the same edit produces no changes, we consider it verified.
    verify_report, _ = update_gutenberg_image_captions(
        after_raw,
        caption_text=caption,
        caption_html=caption_html,
        alt_text=alt_text,
        caption_text_by_id=caption_text_by_id,
        only_ids=only_ids,
        include_diff=False,
    )
    result["verified"] = verify_report.updated_blocks == 0
    result["verify"] = {
        "updated_blocks_remaining": verify_report.updated_blocks,
        "refused_blocks": verify_report.refused_blocks,
    }
    return result


_ALLOWED_POST_STATUSES = ("draft", "publish", "private", "pending", "future")


def _post_set_status(
    api: WordPressApi,
    *,
    post_type: str,
    slug: str | None,
    post_id: int | None,
    to_status: str,
    require_current: str | None,
    apply: bool,
):
    if bool(slug) == bool(post_id):
        raise RuntimeError("Refused: provide exactly one selector: --slug or --id")

    if to_status not in _ALLOWED_POST_STATUSES:
        allowed = ", ".join(_ALLOWED_POST_STATUSES)
        raise RuntimeError(f"Refused: unsupported status {to_status!r} (allowed: {allowed})")

    if slug is not None:
        post = api.post_by_slug(post_type=post_type, slug=str(slug))
    else:
        assert post_id is not None
        post = api.post_by_id(post_type=post_type, post_id=int(post_id))
    resolved_id = post.get("id")
    if not isinstance(resolved_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    current = post.get("status")
    if not isinstance(current, str) or not current:
        raise RuntimeError("Unexpected WordPress response: missing post status")

    result = {
        "post": {
            "id": resolved_id,
            "slug": post.get("slug"),
            "post_type": post_type,
            "link": post.get("link"),
        },
        "apply": bool(apply),
        "changes": {"status": {"before": current, "after": to_status}},
    }

    if require_current is not None and current != require_current:
        result["refused"] = True
        result["reason"] = f"Current status is {current!r}, expected {require_current!r}"
        return result

    if not apply:
        return result

    if current == to_status:
        result["verified"] = True
        return result

    api.update_post_status(post_type=post_type, post_id=resolved_id, status=to_status)
    after = api.post_by_id(post_type=post_type, post_id=resolved_id)
    after_status = after.get("status")
    result["verified"] = after_status == to_status
    result["verify"] = {"status": after_status}
    return result


def _term_summary(t: dict[str, Any]) -> dict[str, Any]:
    return {"id": t.get("id"), "name": t.get("name"), "slug": t.get("slug"), "taxonomy": t.get("taxonomy")}


def _term_summaries_by_include(api: WordPressApi, *, taxonomy: str, ids: list[int]) -> list[dict[str, Any]]:
    terms = api.terms_by_include(taxonomy=taxonomy, ids=ids)
    out: list[dict[str, Any]] = []
    for t in terms:
        if not isinstance(t, dict):
            continue
        out.append(_term_summary(t))
    return out


def _post_set_terms(
    api: WordPressApi,
    *,
    post_type: str,
    slug: str | None,
    post_id: int | None,
    set_mode: bool,
    category_ids: list[int] | None,
    category_slugs: list[str] | None,
    clear_categories: bool,
    tag_ids: list[int] | None,
    tag_slugs: list[str] | None,
    clear_tags: bool,
    apply: bool,
) -> dict[str, Any]:
    if not set_mode:
        raise RuntimeError("Refused: this command requires --set (explicit full replacement)")
    if bool(slug) == bool(post_id):
        raise RuntimeError("Refused: provide exactly one selector: --slug or --id")

    categories_specified = bool(clear_categories or category_ids or category_slugs)
    tags_specified = bool(clear_tags or tag_ids or tag_slugs)
    if not categories_specified and not tags_specified:
        raise RuntimeError(
            "Refused: provide at least one taxonomy to set "
            "(use --category-id/--category-slug/--clear-categories and/or --tag-id/--tag-slug/--clear-tags)"
        )

    if slug is not None:
        post = api.post_by_slug(post_type=post_type, slug=str(slug))
    else:
        assert post_id is not None
        post = api.post_by_id(post_type=post_type, post_id=int(post_id))

    resolved_id = post.get("id")
    if not isinstance(resolved_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    before_categories = _coerce_int_list(post.get("categories"))
    before_tags = _coerce_int_list(post.get("tags"))

    desired_categories: list[int] | None = None
    desired_tags: list[int] | None = None

    resolved_category_terms_by_slug: list[dict[str, Any]] = []
    resolved_tag_terms_by_slug: list[dict[str, Any]] = []

    if categories_specified:
        if clear_categories:
            desired_categories = []
        else:
            base = [int(x) for x in (category_ids or [])]
            for s in category_slugs or []:
                slug_v = str(s).strip()
                if not slug_v:
                    continue
                term = api.term_by_slug(taxonomy="categories", slug=slug_v, context="view")
                term_id = term.get("id")
                if not isinstance(term_id, int):
                    raise RuntimeError("Unexpected WordPress response: missing term id for category slug lookup")
                resolved_category_terms_by_slug.append(term)
                base.append(int(term_id))
            desired_categories = _dedupe_preserve_order_ints(base)

    if tags_specified:
        if clear_tags:
            desired_tags = []
        else:
            base = [int(x) for x in (tag_ids or [])]
            for s in tag_slugs or []:
                slug_v = str(s).strip()
                if not slug_v:
                    continue
                term = api.term_by_slug(taxonomy="tags", slug=slug_v, context="view")
                term_id = term.get("id")
                if not isinstance(term_id, int):
                    raise RuntimeError("Unexpected WordPress response: missing term id for tag slug lookup")
                resolved_tag_terms_by_slug.append(term)
                base.append(int(term_id))
            desired_tags = _dedupe_preserve_order_ints(base)

    after_categories = desired_categories if desired_categories is not None else before_categories
    after_tags = desired_tags if desired_tags is not None else before_tags

    update_payload: dict[str, Any] = {}
    if categories_specified:
        update_payload["categories"] = after_categories
    if tags_specified:
        update_payload["tags"] = after_tags

    changed = False
    if categories_specified and _sorted_unique_ints(before_categories) != _sorted_unique_ints(after_categories):
        changed = True
    if tags_specified and _sorted_unique_ints(before_tags) != _sorted_unique_ints(after_tags):
        changed = True

    # Provide helpful term summaries for review (names/slugs) when possible.
    changes: dict[str, Any] = {}
    if categories_specified:
        union = _sorted_unique_ints(before_categories + after_categories)
        union_terms = _term_summaries_by_include(api, taxonomy="categories", ids=union) if union else []
        changes["categories"] = {
            "before_ids": before_categories,
            "after_ids": after_categories,
            "terms_involved": union_terms,
            "resolved_by_slug": [_term_summary(t) for t in resolved_category_terms_by_slug],
            "mode": "set",
        }
    if tags_specified:
        union = _sorted_unique_ints(before_tags + after_tags)
        union_terms = _term_summaries_by_include(api, taxonomy="tags", ids=union) if union else []
        changes["tags"] = {
            "before_ids": before_tags,
            "after_ids": after_tags,
            "terms_involved": union_terms,
            "resolved_by_slug": [_term_summary(t) for t in resolved_tag_terms_by_slug],
            "mode": "set",
        }

    result: dict[str, Any] = {
        "post": {
            "id": resolved_id,
            "slug": post.get("slug"),
            "post_type": post_type,
            "link": post.get("link"),
        },
        "apply": bool(apply),
        "changed": changed,
        "changes": changes,
        "update_payload": update_payload,
    }

    if not apply:
        return result

    if not changed:
        result["verified"] = True
        return result

    api.update_post_terms(
        post_type=post_type,
        post_id=resolved_id,
        categories=after_categories if categories_specified else None,
        tags=after_tags if tags_specified else None,
    )
    after = api.post_by_id(post_type=post_type, post_id=resolved_id)
    after_cats = _coerce_int_list(after.get("categories"))
    after_tags_read = _coerce_int_list(after.get("tags"))

    verified = True
    if categories_specified and _sorted_unique_ints(after_cats) != _sorted_unique_ints(after_categories):
        verified = False
    if tags_specified and _sorted_unique_ints(after_tags_read) != _sorted_unique_ints(after_tags):
        verified = False

    result["verified"] = verified
    result["verify"] = {
        "expected": {
            "categories": _sorted_unique_ints(after_categories) if categories_specified else None,
            "tags": _sorted_unique_ints(after_tags) if tags_specified else None,
        },
        "actual": {
            "categories": _sorted_unique_ints(after_cats) if categories_specified else None,
            "tags": _sorted_unique_ints(after_tags_read) if tags_specified else None,
        },
        "note": "WordPress does not guarantee ordering for term ID arrays; verification uses set equality.",
    }
    return result


def cmd_post_find(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    posts = api.search_posts(post_type=args.post_type, query=args.query, limit=int(args.limit))
    out = []
    for p in posts[: int(args.limit)]:
        out.append(
            {
                "id": p.get("id"),
                "slug": p.get("slug"),
                "status": p.get("status"),
                "title": (p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered"),
                "link": p.get("link"),
            }
        )
    ctx["out"].emit({"count": len(out), "results": out})
    return 0


def cmd_post_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    post = api.post_by_slug(post_type=args.post_type, slug=args.slug)
    out = {
        "id": post.get("id"),
        "slug": post.get("slug"),
        "status": post.get("status"),
        "title": (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered"),
        "author": post.get("author"),
        "featured_media": post.get("featured_media"),
        "link": post.get("link"),
    }
    if args.include_raw:
        out["content_raw"] = (post.get("content") or {}).get("raw")
    ctx["out"].emit(out)
    return 0


def cmd_post_images(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    post = api.post_by_slug(post_type=args.post_type, slug=args.slug)
    content = post.get("content") or {}
    content_raw = content.get("raw") or content.get("rendered") or ""
    extracted = extract_attachment_ids_from_post_content(content_raw)
    ids = [e.attachment_id for e in extracted if isinstance(e.attachment_id, int)]
    featured = post.get("featured_media")
    if args.include_featured and isinstance(featured, int) and featured not in ids:
        ids.append(featured)

    media_items = {m.get("id"): m for m in api.media_by_include([int(i) for i in ids])}

    images = []
    for e in extracted:
        aid = e.attachment_id
        m = media_items.get(aid) if isinstance(aid, int) else None
        images.append(
            {
                "attachment_id": aid,
                "sources": list(e.sources),
                "is_featured": bool(isinstance(featured, int) and aid == featured),
                "media": None
                if not m
                else {
                    "source_url": source_url_from_media(m),
                    "title": title_text_from_media(m),
                    "alt_text": m.get("alt_text") or "",
                    "caption": caption_text_from_media(m),
                },
            }
        )

    ctx["out"].emit(
        {
            "post": {"id": post.get("id"), "slug": post.get("slug"), "featured_media": featured},
            "images": images,
        }
    )
    return 0


def _coerce_int_list(v: object) -> list[int]:
    if not isinstance(v, list):
        return []
    out: list[int] = []
    for x in v:
        if isinstance(x, int):
            out.append(x)
    return out


def _write_family(post_type: str, action: str) -> str:
    family = "post" if str(post_type) != "pages" else "page"
    return f"{family}.{action}"


def _term_names(terms: Iterable[dict[str, object]]) -> list[str]:
    out: list[str] = []
    for t in terms:
        name = t.get("name")
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out


def cmd_post_truth(args, ctx) -> int:
    if bool(args.slug) == bool(args.id):
        raise RuntimeError("Refused: provide exactly one selector: --slug or --id")

    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    if args.slug is not None:
        post = api.post_by_slug(post_type=args.post_type, slug=str(args.slug))
    else:
        post = api.post_by_id(post_type=args.post_type, post_id=int(args.id))

    post_id = post.get("id")
    if not isinstance(post_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    content = post.get("content") or {}
    raw = (content.get("raw") if isinstance(content, dict) else None) or ""
    rendered = (content.get("rendered") if isinstance(content, dict) else None) or ""

    featured_media = post.get("featured_media")
    featured: dict[str, object] | None = None
    if isinstance(featured_media, int) and featured_media > 0:
        fm = api.media_by_id(int(featured_media))
        featured = {
            "id": fm.get("id"),
            "source_url": source_url_from_media(fm),
            "title": title_text_from_media(fm),
            "alt_text": fm.get("alt_text") or "",
            "caption": caption_text_from_media(fm),
        }

    author_id = post.get("author")
    author: dict[str, object] | None = None
    if isinstance(author_id, int) and author_id > 0:
        try:
            u = api.user_by_id(int(author_id))
            author = {"id": u.get("id"), "name": u.get("name"), "slug": u.get("slug"), "email": u.get("email")}
        except Exception:
            author = {"id": author_id}

    tag_ids = _coerce_int_list(post.get("tags"))
    cat_ids = _coerce_int_list(post.get("categories"))
    tags = _term_names(api.terms_by_include(taxonomy="tags", ids=tag_ids)) if tag_ids else []
    categories = _term_names(api.terms_by_include(taxonomy="categories", ids=cat_ids)) if cat_ids else []

    extracted = extract_attachment_ids_from_post_content(raw if raw else rendered)
    attachment_ids = [e.attachment_id for e in extracted if isinstance(e.attachment_id, int)]

    img_srcs = extract_img_srcs_from_html(rendered) if rendered else []
    resolved_urls: dict[str, dict[str, object]] = {}
    unresolved_urls: list[dict[str, str]] = []
    if args.resolve_urls and img_srcs:
        for url in img_srcs[:50]:
            try:
                resolved_media = api.media_resolve_by_url(url=url)
                resolved_mid = resolved_media.get("id")
                if isinstance(resolved_mid, int):
                    resolved_urls[url] = {"id": resolved_mid}
                    if resolved_mid not in attachment_ids:
                        attachment_ids.append(resolved_mid)
            except Exception as err:
                unresolved_urls.append({"url": url, "error": str(err)})

    media_items: dict[int, dict[str, Any]] = {}
    if attachment_ids:
        for media_item in api.media_by_include(sorted(set(attachment_ids))):
            if not isinstance(media_item, dict):
                continue
            mid_obj = media_item.get("id")
            if isinstance(mid_obj, int):
                media_items[mid_obj] = media_item

    images = []
    for url in img_srcs:
        entry: dict[str, object] = {"src_url": url}
        res = resolved_urls.get(url)
        if res:
            mid_obj = res.get("id")
            if not isinstance(mid_obj, int):
                images.append(entry)
                continue
            mid = mid_obj
            entry["wp_media_id"] = mid
            media_obj: dict[str, Any] | None = media_items.get(mid)
            if isinstance(media_obj, dict):
                entry["media"] = {
                    "source_url": source_url_from_media(media_obj),
                    "title": title_text_from_media(media_obj),
                    "alt_text": media_obj.get("alt_text") or "",
                    "caption": caption_text_from_media(media_obj),
                }
        images.append(entry)

    # Attachments found via Gutenberg blocks/classes (often more reliable than HTML URLs).
    attachments = []
    for extracted_item in extracted:
        aid = extracted_item.attachment_id
        m = media_items.get(aid) if isinstance(aid, int) else None
        attachments.append(
            {
                "wp_media_id": aid,
                "sources": list(extracted_item.sources),
                "media": None
                if not m
                else {
                    "source_url": source_url_from_media(m),
                    "title": title_text_from_media(m),
                    "alt_text": m.get("alt_text") or "",
                    "caption": caption_text_from_media(m),
                },
            }
        )

    ctx["out"].emit(
        {
            "post": {
                "id": post_id,
                "slug": post.get("slug"),
                "status": post.get("status"),
                "title": (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered"),
                "link": post.get("link"),
            },
            "author": author,
            "terms": {"tags": tags, "categories": categories},
            "featured_media": featured,
            "body": {
                "img_srcs": images,
                "attachments": attachments,
                "unresolved_urls": unresolved_urls,
            },
        }
    )
    return 0


def cmd_post_set_image_captions(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    before_post = api.post_by_slug(post_type=args.post_type, slug=str(args.slug))
    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family=_write_family(str(args.post_type), "set-image-captions"),
        selector=f"slug-{args.slug}",
        payload={"post_type": str(args.post_type), "post": before_post},
    )
    result = _post_set_image_captions(
        api,
        post_type=args.post_type,
        slug=args.slug,
        caption=args.caption,
        caption_html=args.caption_html,
        alt_text=args.alt_text,
        captions_file=args.captions_file,
        only_ids_csv=args.only_ids,
        include_diff=bool(args.diff or not ctx["apply"]),
        apply=bool(ctx["apply"]),
    )
    report = result.get("report") if isinstance(result, dict) else None
    updated_blocks = 0
    if isinstance(report, dict):
        ub = report.get("updated_blocks")
        if isinstance(ub, int):
            updated_blocks = ub
    changed = updated_blocks > 0

    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": str(args.slug), "post_type": str(args.post_type)},
            "risk_level": "high",
            "risk_reasons": ["Edits existing post content (body captions/alt text)"],
            "preconditions": [
                "Review the proposed changes (diff) before applying",
                "Ensure the selector targets the intended post",
            ],
            "proposed_changes": report or {},
            "before_state": before_state,
            "verification_plan": (
                "After apply, re-fetch the post and verify by idempotence (re-running yields zero further changes)."
            ),
            "rollback": {
                "supported": True,
                "notes": before_state["restore_note"],
            },
        }
        result["dry_run"] = True
        result["changed"] = changed
        result["risk_level"] = plan["risk_level"]
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        verified = bool(result.get("verified")) if changed else True
        rollback_plan = None
        if changed:
            rollback_plan = "No automatic rollback for this command. Keep a manual backup of post raw content before apply to restore it."
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": str(args.slug), "post_type": str(args.post_type)},
            "changed": changed,
            "verification": {"ok": verified, "details": result.get("verify") or {}},
            "diff_applied": (report or {}).get("diff") if isinstance(report, dict) else None,
            "before_state": before_state,
            "backups": [before_state],
            "rollback_plan": rollback_plan or before_state["restore_note"],
        }
        result["changed"] = changed
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)
    ctx["audit"].write("post.set_image_captions", result)
    ctx["out"].emit(result)
    return 0


# Used by jobs runner and unit tests.
post_set_status_core = _post_set_status


def cmd_post_set_status(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    if args.slug is not None:
        before_post = api.post_by_slug(post_type=args.post_type, slug=str(args.slug))
        selector_name = f"slug-{args.slug}"
    else:
        before_post = api.post_by_id(post_type=args.post_type, post_id=int(args.id))
        selector_name = f"id-{args.id}"
    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family=_write_family(str(args.post_type), "set-status"),
        selector=selector_name,
        payload={"post_type": str(args.post_type), "post": before_post},
    )
    result = _post_set_status(
        api,
        post_type=args.post_type,
        slug=args.slug,
        post_id=args.id,
        to_status=args.to,
        require_current=args.require_current,
        apply=bool(ctx["apply"]),
    )
    changes = result.get("changes") if isinstance(result, dict) else None
    status_change = None
    if isinstance(changes, dict):
        status_change = changes.get("status")
    before = status_change.get("before") if isinstance(status_change, dict) else None
    after = status_change.get("after") if isinstance(status_change, dict) else None
    changed = bool(isinstance(before, str) and isinstance(after, str) and before != after)
    can_revert = changed and not bool(result.get("refused"))
    rollback_note = None
    if can_revert and isinstance(before, str):
        post_info = result.get("post") if isinstance(result.get("post"), dict) else {}
        selector = (
            f"--id {int(post_info.get('id'))}"
            if isinstance(post_info.get("id"), int)
            else f"--slug {args.slug}"
        )
        rollback_note = (
            f"To revert, re-run with the same selector and the previous status via --to {before!r}."
            f" Example: wordpress-api-tool --apply post set-status {selector} --to {before!r}."
        )

    if not ctx["apply"]:
        preconditions = ["Ensure the selector targets the intended post"]
        if args.require_current is not None:
            preconditions.append(f"Current status must be {args.require_current!r}")
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": args.slug, "id": args.id, "post_type": str(args.post_type)},
            "risk_level": "high",
            "risk_reasons": ["Post status change (may affect publication/visibility)"],
            "preconditions": preconditions,
            "proposed_changes": changes or {},
            "before_state": before_state,
            "verification_plan": "After apply, re-fetch the post and assert the status matches the requested value.",
            "rollback": {
                "supported": True,
                "notes": rollback_note or before_state["restore_note"],
            },
        }
        result["dry_run"] = True
        result["changed"] = changed
        result["risk_level"] = plan["risk_level"]
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        refused = bool(result.get("refused"))
        verified = bool(result.get("verified")) if changed and not refused else True
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": args.slug, "id": args.id, "post_type": str(args.post_type)},
            "changed": changed and not refused,
            "verification": {"ok": verified, "details": result.get("verify") or {"refused": refused}},
            "diff_applied": changes or {},
            "before_state": before_state,
            "backups": [before_state],
            "rollback_plan": rollback_note if changed and not refused else before_state["restore_note"],
        }
        result["changed"] = changed and not refused
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)
    ctx["audit"].write("post.set_status", result)
    ctx["out"].emit(result)
    return 0


def cmd_post_set_terms(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    if args.slug is not None:
        before_post = api.post_by_slug(post_type=args.post_type, slug=str(args.slug))
        selector_name = f"slug-{args.slug}"
    else:
        before_post = api.post_by_id(post_type=args.post_type, post_id=int(args.id))
        selector_name = f"id-{args.id}"
    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family="post.set-terms",
        selector=selector_name,
        payload={"post_type": str(args.post_type), "post": before_post},
    )
    result = _post_set_terms(
        api,
        post_type=args.post_type,
        slug=args.slug,
        post_id=args.id,
        set_mode=bool(args.set),
        category_ids=args.category_id,
        category_slugs=args.category_slug,
        clear_categories=bool(args.clear_categories),
        tag_ids=args.tag_id,
        tag_slugs=args.tag_slug,
        clear_tags=bool(args.clear_tags),
        apply=bool(ctx["apply"]),
    )

    changes = result.get("changes") if isinstance(result, dict) else None
    changed = bool(result.get("changed"))
    can_revert = bool(changed)
    rollback_note = None
    if can_revert:
        cat_note = None
        tag_note = None
        if isinstance(changes, dict) and changes.get("categories"):
            cat_before = changes["categories"].get("before_ids")
            if isinstance(cat_before, list):
                cat_note = f"categories.before_ids={cat_before}"
        if isinstance(changes, dict) and changes.get("tags"):
            tag_before = changes["tags"].get("before_ids")
            if isinstance(tag_before, list):
                tag_note = f"tags.before_ids={tag_before}"
        rollback_parts = [p for p in [cat_note, tag_note] if p]
        if rollback_parts:
            rollback_note = (
                "To revert, re-run with --set and the previous IDs from these fields: "
                + ", ".join(rollback_parts)
            )

    if not ctx["apply"]:
        update_payload = result.get("update_payload") if isinstance(result, dict) else None
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": args.slug, "id": args.id, "post_type": str(args.post_type)},
            "risk_level": "medium",
            "risk_reasons": ["Edits post taxonomy terms (categories/tags)"],
            "preconditions": [
                "Ensure the selector targets the intended post/page",
                "Ensure the term inputs are correct (IDs or slugs); slug inputs are resolved and may refuse on ambiguity",
            ],
            "proposed_changes": changes or {},
            "update_payload": update_payload or {},
            "before_state": before_state,
            "verification_plan": "After apply, re-fetch the post and verify the final terms match the requested set.",
            "rollback": {
                "supported": True,
                "notes": (
                    rollback_note if rollback_note is not None else before_state["restore_note"]
                ),
            },
        }
        result["dry_run"] = True
        result["risk_level"] = plan["risk_level"]
        result["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        verified = bool(result.get("verified")) if changed else True
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": result.get("post") or {"slug": args.slug, "id": args.id, "post_type": str(args.post_type)},
            "changed": changed,
            "verification": {"ok": verified, "details": result.get("verify") or {}},
            "diff_applied": changes or {},
            "before_state": before_state,
            "backups": [before_state],
            "rollback_plan": rollback_note if changed else before_state["restore_note"],
        }
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)

    ctx["audit"].write("post.set_terms", result)
    ctx["out"].emit(result)
    if ctx["apply"] and changed and not bool(result.get("verified")):
        return 1
    return 0


# Used by jobs runner.
post_set_image_captions_core = _post_set_image_captions


# Used by unit tests.
post_set_terms_core = _post_set_terms


# Used by unit tests.
post_replace_in_content_core = _post_replace_in_content


def cmd_post_replace_in_content(args, ctx) -> int:
    if ctx["apply"] and not getattr(args, "backup_out", None):
        raise RuntimeError("Refused: --backup-out is required with --apply for content edits")

    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    # Fetch once here so we can always snapshot before changes (even if the core refuses later).
    selector_slug = getattr(args, "slug", None)
    selector_id = getattr(args, "id", None)
    post_type = str(args.post_type)
    if bool(selector_slug) == bool(selector_id):
        raise RuntimeError("Refused: provide exactly one selector: --slug or --id")

    if selector_slug is not None:
        post = api.post_by_slug(post_type=post_type, slug=str(selector_slug))
    else:
        post = api.post_by_id(post_type=post_type, post_id=int(selector_id))

    resolved_id = post.get("id")
    if not isinstance(resolved_id, int):
        raise RuntimeError("Unexpected WordPress response: missing post id")

    content_raw = (post.get("content") or {}).get("raw")
    if not isinstance(content_raw, str):
        raise RuntimeError("Missing content.raw (ensure auth has edit context).")

    before_state = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family=_write_family(str(args.post_type), "replace-in-content"),
        selector=f"id-{resolved_id}",
        payload={"post_type": post_type, "post_id": resolved_id, "content_raw": content_raw},
    )

    backup_path = getattr(args, "backup_out", None)
    if backup_path:
        # Write the snapshot before running any transform/apply.
        from pathlib import Path

        p = Path(str(backup_path))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content_raw, encoding="utf-8")

    max_replacements = getattr(args, "max_replacements", None)
    if max_replacements is None:
        max_replacements = int(args.expected_count)

    result = _post_replace_in_content(
        api,
        post_type=post_type,
        slug=selector_slug,
        post_id=selector_id,
        from_text=str(args.from_text),
        to_text=str(args.to_text),
        expected_count=int(args.expected_count),
        max_replacements=int(max_replacements),
        include_diff=bool(args.diff),
        apply=bool(ctx["apply"]),
    )

    # Add v2 plan/receipt wrappers like other write-capable commands.
    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"slug": selector_slug, "id": selector_id, "post_type": post_type},
            "risk_level": "medium",
            "risk_reasons": ["Edits post/page body content.raw (exact string replacement)"],
            "preconditions": [
                "Ensure the selector targets the intended post/page",
                "Ensure --from and --to are exact and safe (HTML attributes are case-sensitive)",
                f"Ensure occurrence count matches exactly: expected {int(args.expected_count)}",
            ],
            "proposed_changes": result.get("changes") or {},
            "before_state": before_state,
            "backups": {"content_raw_snapshot_out": backup_path} if backup_path else None,
            "verification_plan": "After apply, re-fetch the post and verify the source string no longer occurs.",
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
        verified = bool(result.get("verified")) if bool(result.get("changed")) else True
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"slug": selector_slug, "id": selector_id, "post_type": post_type},
            "changed": bool(result.get("changed")),
            "verification": {"ok": verified, "details": result.get("verify") or {}},
            "diff_applied": (result.get("changes") or {}).get("content_raw", {}).get("diff"),
            "before_state": before_state,
            "backups": [before_state] + ([{"content_raw_snapshot_out": backup_path}] if backup_path else []),
            "rollback_plan": before_state["restore_note"],
        }
        result["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)

    ctx["audit"].write("post.replace_in_content", result)
    ctx["out"].emit(result)
    if ctx["apply"] and bool(result.get("changed")) and not bool(result.get("verified")):
        return 1
    return 0
