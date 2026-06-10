from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path
from typing import Any

from ..caption_policy import caption_matches_expected, guess_caption_policy
from ..content_lexical import (
    LexicalEditReport,
    ReplaceManyItemResult,
    audit_heading_bold,
    clear_heading_bold,
    convert_html_list_cards_to_native_lists,
    delete_linked_list_items_by_url_after_heading,
    delete_images_by_src,
    dump_lexical_field,
    fix_link_whitespace,
    fix_bullet_lists_split_by_html_ul_cards,
    fix_numbered_list_split_by_html_ol_after_heading,
    fix_numbered_paragraphs_to_list_after_heading,
    insert_image_after_heading,
    list_images,
    move_top_level_image_before_heading,
    parse_lexical_field,
    replace_first_image_after_heading,
    replace_image_src,
    replace_images_by_src_map,
    set_paid_rel_on_amazon_links,
    set_paid_rel_on_links,
    set_image_meta_by_src,
    sync_top_level_images_before_headings,
    insert_internal_links_section_before_heading,
    insert_link_paragraph_after_heading_section_end,
    unlink_links_by_url,
    unlink_links_by_url_after_heading,
    unlink_internal_links_in_image_captions,
    linkify_text_in_paragraph,
)
from ..post_patch import resolve_post
from ..runtime import get_api


def add_bodylex_commands(post_sub) -> None:
    bodylex = post_sub.add_parser("bodylex", help="Post body helpers (Lexical mode)")
    bodylex_sub = bodylex.add_subparsers(dest="bodylex_cmd", required=True)

    inspect = bodylex_sub.add_parser("inspect", help="List image nodes in Lexical")
    inspect.add_argument("--slug", default=None)
    inspect.add_argument("--id", default=None)
    inspect.set_defaults(func=cmd_bodylex_inspect)

    scaffold = bodylex_sub.add_parser(
        "scaffold",
        help="Generate editable helper files for Lexical workflows (no API writes)",
    )
    scaffold_sub = scaffold.add_subparsers(dest="bodylex_scaffold_cmd", required=True)

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
    captions_map.add_argument(
        "--all",
        action="store_true",
        help="Deprecated alias for --mode all (kept for compatibility).",
    )
    captions_map.add_argument(
        "--include-context",
        action="store_true",
        help="Include non-applying helper fields like _context_heading/_path/_kind_guess/_expected_suffix.",
    )
    captions_map.add_argument("--force", action="store_true", help="Overwrite output file if it exists")
    captions_map.set_defaults(func=cmd_bodylex_scaffold_captions_map)

    image = bodylex_sub.add_parser("image", help="Image operations (Lexical)")
    image_sub = image.add_subparsers(dest="bodylex_image_cmd", required=True)

    replace_src = image_sub.add_parser("replace-src", help="Replace an image src (by exact match)")
    replace_src.add_argument("--slug", default=None)
    replace_src.add_argument("--id", default=None)
    replace_src.add_argument("--old-src", required=True)
    replace_src.add_argument("--new-src", required=True)
    replace_src.add_argument("--alt", default=None)
    replace_src.add_argument("--caption", default=None)
    replace_src.add_argument("--title", default=None)
    replace_src.add_argument("--diff", action="store_true")
    replace_src.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    replace_src.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    replace_src.set_defaults(func=cmd_bodylex_image_replace_src)

    replace_many = image_sub.add_parser(
        "replace-many",
        help="Replace many image src values from a JSON mapping (single post update)",
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
    replace_many.set_defaults(func=cmd_bodylex_image_replace_many)

    replace_after = image_sub.add_parser(
        "replace-after-heading",
        help="Replace the Nth image after a top-level heading (root.children)",
    )
    replace_after.add_argument("--slug", default=None)
    replace_after.add_argument("--id", default=None)
    replace_after.add_argument("--heading", required=True)
    replace_after.add_argument(
        "--expect-old-src",
        default=None,
        help="Optional safety: refuse unless the targeted image currently has this exact src",
    )
    replace_after.add_argument("--new-src", required=True)
    replace_after.add_argument("--alt", default=None)
    replace_after.add_argument("--caption", default=None)
    replace_after.add_argument("--title", default=None)
    replace_after.add_argument("--nth-after-heading", type=int, default=1)
    replace_after.add_argument("--heading-occurrence", type=int, default=None)
    replace_after.add_argument("--diff", action="store_true")
    replace_after.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    replace_after.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    replace_after.set_defaults(func=cmd_bodylex_image_replace_after_heading)

    set_meta = image_sub.add_parser("set-meta", help="Update image alt/caption/title by src")
    set_meta.add_argument("--slug", default=None)
    set_meta.add_argument("--id", default=None)
    set_meta.add_argument("--src", required=True)
    set_meta.add_argument("--alt", default=None)
    set_meta.add_argument("--caption", default=None)
    set_meta.add_argument("--title", default=None)
    set_meta.add_argument("--diff", action="store_true")
    set_meta.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    set_meta.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    set_meta.set_defaults(func=cmd_bodylex_image_set_meta)

    insert_after = image_sub.add_parser(
        "insert-after-heading",
        help="Insert an image after a top-level heading by cloning a template image node",
    )
    insert_after.add_argument("--slug", default=None)
    insert_after.add_argument("--id", default=None)
    insert_after.add_argument("--heading", required=True)
    insert_after.add_argument("--src", required=True, help="New image src to insert")
    insert_after.add_argument("--alt", default=None)
    insert_after.add_argument("--caption", default=None)
    insert_after.add_argument("--title", default=None)
    insert_after.add_argument(
        "--template-src",
        required=True,
        help="Existing image src to clone for a safe node shape",
    )
    insert_after.add_argument("--heading-occurrence", type=int, default=None)
    insert_after.add_argument("--diff", action="store_true")
    insert_after.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    insert_after.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    insert_after.set_defaults(func=cmd_bodylex_image_insert_after_heading)

    delete_src = image_sub.add_parser("delete-by-src", help="Delete image nodes by exact src")
    delete_src.add_argument("--slug", default=None)
    delete_src.add_argument("--id", default=None)
    delete_src.add_argument("--src", required=True)
    delete_src.add_argument("--all", action="store_true", help="Allow deleting multiple matches")
    delete_src.add_argument("--diff", action="store_true")
    delete_src.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    delete_src.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    delete_src.set_defaults(func=cmd_bodylex_image_delete_by_src)

    move_before = image_sub.add_parser(
        "move-before-heading",
        help="Move an existing top-level image node to immediately before a heading",
    )
    move_before.add_argument("--slug", default=None)
    move_before.add_argument("--id", default=None)
    move_before.add_argument("--src", required=True)
    move_before.add_argument("--heading", required=True)
    move_before.add_argument("--heading-occurrence", type=int, default=None)
    move_before.add_argument("--diff", action="store_true")
    move_before.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    move_before.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    move_before.set_defaults(func=cmd_bodylex_image_move_before_heading)

    sync_before = image_sub.add_parser(
        "sync-before-headings",
        help="Remove all top-level images and insert new ones immediately before specified headings (single edit pass)",
    )
    sync_before.add_argument("--slug", default=None)
    sync_before.add_argument("--id", default=None)
    sync_before.add_argument(
        "--placements-file",
        required=True,
        help="JSON file: list of {heading, src, alt?, caption?, title?, heading_occurrence?}",
    )
    sync_before.add_argument(
        "--no-fix-split-numbered-lists",
        action="store_true",
        help="Disable auto-fixing split numbered lists (HTML <ol> cards) when detected",
    )
    sync_before.add_argument("--diff", action="store_true")
    sync_before.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    sync_before.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    sync_before.set_defaults(func=cmd_bodylex_image_sync_before_headings)

    fix_numbered = bodylex_sub.add_parser(
        "fix-numbered-list-after-heading",
        help="Fix numbered list steps split into HTML <ol> cards after a heading",
    )
    fix_numbered.add_argument("--slug", default=None)
    fix_numbered.add_argument("--id", default=None)
    fix_numbered.add_argument("--heading", required=True)
    fix_numbered.add_argument("--heading-occurrence", type=int, default=None)
    fix_numbered.add_argument("--diff", action="store_true")
    fix_numbered.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    fix_numbered.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    fix_numbered.set_defaults(func=cmd_bodylex_fix_numbered_list_after_heading)

    fix_numbered_paras = bodylex_sub.add_parser(
        "fix-numbered-paragraphs-after-heading",
        help='Convert numbered paragraphs ("1. ...") after a heading into a proper ordered list',
    )
    fix_numbered_paras.add_argument("--slug", default=None)
    fix_numbered_paras.add_argument("--id", default=None)
    fix_numbered_paras.add_argument("--heading", required=True)
    fix_numbered_paras.add_argument("--heading-occurrence", type=int, default=None)
    fix_numbered_paras.add_argument("--diff", action="store_true")
    fix_numbered_paras.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    fix_numbered_paras.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    fix_numbered_paras.set_defaults(func=cmd_bodylex_fix_numbered_paragraphs_after_heading)

    fix_bullets_split = bodylex_sub.add_parser(
        "fix-bullet-lists-split-html-cards",
        help="Fix bullet list items split into HTML <ul> cards (WordPress importer artifact)",
    )
    fix_bullets_split.add_argument("--slug", default=None)
    fix_bullets_split.add_argument("--id", default=None)
    fix_bullets_split.add_argument("--diff", action="store_true")
    fix_bullets_split.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    fix_bullets_split.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    fix_bullets_split.set_defaults(func=cmd_bodylex_fix_bullet_lists_split_html_cards)

    convert_html_lists = bodylex_sub.add_parser(
        "convert-html-list-cards",
        help="Convert WordPress-imported HTML <ul>/<ol> list cards into native Ghost list blocks",
    )
    convert_html_lists.add_argument("--slug", default=None)
    convert_html_lists.add_argument("--id", default=None)
    convert_html_lists.add_argument("--diff", action="store_true")
    convert_html_lists.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    convert_html_lists.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    convert_html_lists.set_defaults(func=cmd_bodylex_convert_html_list_cards)

    fix_link_ws = bodylex_sub.add_parser(
        "fix-link-whitespace",
        help="Fix link underline artifacts caused by leading/trailing whitespace inside a hyperlink",
    )
    fix_link_ws.add_argument("--slug", default=None)
    fix_link_ws.add_argument("--id", default=None)
    fix_link_ws.add_argument("--diff", action="store_true")
    fix_link_ws.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    fix_link_ws.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    fix_link_ws.set_defaults(func=cmd_bodylex_fix_link_whitespace)

    linkify = bodylex_sub.add_parser(
        "linkify",
        help="Insert a contextual internal link by wrapping anchor text inside a paragraph (Lexical)",
    )
    linkify.add_argument("--slug", default=None)
    linkify.add_argument("--id", default=None)
    linkify.add_argument(
        "--paragraph-contains",
        required=True,
        help="Select the paragraph by substring match (case-insensitive)",
    )
    linkify.add_argument(
        "--paragraph-occurrence",
        type=int,
        default=None,
        help="If multiple paragraphs match, choose 1-based occurrence",
    )
    linkify.add_argument(
        "--include-list-items",
        action="store_true",
        help="Also match list item nodes (default only matches paragraph nodes)",
    )
    linkify.add_argument("--anchor-text", required=True, help="Exact anchor text to linkify (no leading/trailing spaces)")
    linkify.add_argument(
        "--anchor-occurrence",
        type=int,
        default=None,
        help="If anchor text appears multiple times in the paragraph, choose 1-based occurrence",
    )
    linkify.add_argument("--url", required=True, help="Link URL")
    linkify.add_argument("--diff", action="store_true")
    linkify.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    linkify.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    linkify.set_defaults(func=cmd_bodylex_linkify)

    insert_link_para = bodylex_sub.add_parser(
        "insert-link-paragraph-after-heading-section-end",
        help="Insert a link-only paragraph at the end of a heading section (Lexical root.children only)",
    )
    insert_link_para.add_argument("--slug", default=None)
    insert_link_para.add_argument("--id", default=None)
    insert_link_para.add_argument("--heading", required=True, help="Section heading text (match is case/whitespace-insensitive)")
    insert_link_para.add_argument("--heading-occurrence", type=int, default=None)
    insert_link_para.add_argument("--link-text", required=True, help="Paragraph link text (no leading/trailing spaces)")
    insert_link_para.add_argument("--url", required=True, help="Link URL")
    insert_link_para.add_argument("--diff", action="store_true")
    insert_link_para.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    insert_link_para.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    insert_link_para.set_defaults(func=cmd_bodylex_insert_link_paragraph_after_heading_section_end)

    clear_heading_bold_cmd = bodylex_sub.add_parser(
        "clear-heading-bold",
        help="Remove bold formatting from all heading text nodes (Lexical headings only)",
    )
    clear_heading_bold_cmd.add_argument("--slug", default=None)
    clear_heading_bold_cmd.add_argument("--id", default=None)
    clear_heading_bold_cmd.add_argument("--diff", action="store_true")
    clear_heading_bold_cmd.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    clear_heading_bold_cmd.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    clear_heading_bold_cmd.set_defaults(func=cmd_bodylex_clear_heading_bold)

    amazon_rel = bodylex_sub.add_parser(
        "set-amazon-link-rel",
        help="Mark Amazon links as paid by ensuring rel includes: sponsored nofollow (Lexical link nodes only)",
    )
    amazon_rel.add_argument("--slug", default=None)
    amazon_rel.add_argument("--id", default=None)
    amazon_rel.add_argument("--diff", action="store_true")
    amazon_rel.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    amazon_rel.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    amazon_rel.set_defaults(func=cmd_bodylex_set_amazon_link_rel)

    paid_rel = bodylex_sub.add_parser(
        "set-paid-link-rel",
        help="Mark paid links by ensuring Lexical link rel includes required tokens (Lexical link nodes only)",
    )
    paid_rel.add_argument("--slug", default=None)
    paid_rel.add_argument("--id", default=None)
    paid_rel.add_argument("--diff", action="store_true")
    paid_rel.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    paid_rel.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    paid_rel.add_argument("--host", action="append", default=None, help="Match links to this host (repeatable)")
    paid_rel.add_argument(
        "--all-external",
        action="store_true",
        help="Match all external http(s) links (not internal hosts)",
    )
    paid_rel.add_argument(
        "--internal-host",
        action="append",
        default=None,
        help="Extra hostnames to treat as internal (repeatable; only meaningful with --all-external)",
    )
    paid_rel.add_argument(
        "--rel",
        default="noreferrer noopener sponsored nofollow",
        help='Required rel tokens to ensure (default: "noreferrer noopener sponsored nofollow")',
    )
    paid_rel.set_defaults(func=cmd_bodylex_set_paid_link_rel)

    unlink = bodylex_sub.add_parser(
        "unlink-by-url",
        help="Remove hyperlink(s) for exact URL match while keeping visible text (Lexical link nodes only)",
    )
    unlink.add_argument("--slug", default=None)
    unlink.add_argument("--id", default=None)
    unlink.add_argument("--url", action="append", default=None, help="URL to unlink (repeatable; exact match)")
    unlink.add_argument("--diff", action="store_true")
    unlink.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    unlink.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    unlink.set_defaults(func=cmd_bodylex_unlink_by_url)

    unlink_after_heading = bodylex_sub.add_parser(
        "unlink-by-url-after-heading",
        help="Unlink specific URLs only after a top-level H2 heading (Lexical root.children only)",
    )
    unlink_after_heading.add_argument("--slug", default=None)
    unlink_after_heading.add_argument("--id", default=None)
    unlink_after_heading.add_argument(
        "--after-heading",
        default="Conclusion",
        help='Start unlinking after this H2 heading (default: "Conclusion")',
    )
    unlink_after_heading.add_argument("--url", action="append", default=None, help="URL to unlink (repeatable; exact match)")
    unlink_after_heading.add_argument("--diff", action="store_true")
    unlink_after_heading.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    unlink_after_heading.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    unlink_after_heading.set_defaults(func=cmd_bodylex_unlink_by_url_after_heading)

    delete_link_items_after_heading = bodylex_sub.add_parser(
        "delete-link-items-by-url-after-heading",
        help="Delete list items (or whole blocks) containing specific link URLs, only after a top-level H2 heading",
    )
    delete_link_items_after_heading.add_argument("--slug", default=None)
    delete_link_items_after_heading.add_argument("--id", default=None)
    delete_link_items_after_heading.add_argument(
        "--after-heading",
        default="Conclusion",
        help='Start deleting after this H2 heading (default: "Conclusion")',
    )
    delete_link_items_after_heading.add_argument(
        "--url",
        action="append",
        default=None,
        help="URL to delete (repeatable; exact match; deletes the containing list item/block)",
    )
    delete_link_items_after_heading.add_argument("--diff", action="store_true")
    delete_link_items_after_heading.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    delete_link_items_after_heading.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    delete_link_items_after_heading.set_defaults(func=cmd_bodylex_delete_link_items_by_url_after_heading)

    unlink_caption_links = bodylex_sub.add_parser(
        "unlink-internal-caption-links",
        help="Remove internal hyperlinks from image captions (keeps caption text; Lexical image nodes only)",
    )
    unlink_caption_links.add_argument("--slug", default=None)
    unlink_caption_links.add_argument("--id", default=None)
    unlink_caption_links.add_argument("--diff", action="store_true")
    unlink_caption_links.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    unlink_caption_links.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    unlink_caption_links.add_argument(
        "--internal-host",
        action="append",
        default=None,
        help="Extra hostnames to treat as internal (repeatable; defaults to site.url host)",
    )
    unlink_caption_links.set_defaults(func=cmd_bodylex_unlink_internal_caption_links)

    insert_links_section = bodylex_sub.add_parser(
        "insert-links-section",
        help="Insert an H2 + paragraph + bullet list of links before a heading (Lexical root.children only)",
    )
    insert_links_section.add_argument("--slug", default=None)
    insert_links_section.add_argument("--id", default=None)
    insert_links_section.add_argument("--before-heading", default="Conclusion", help='Insert before this heading (default: "Conclusion")')
    insert_links_section.add_argument("--section-heading", required=True, help="Inserted section H2 text")
    insert_links_section.add_argument("--intro", required=True, help="Inserted intro paragraph text")
    insert_links_section.add_argument(
        "--link",
        action="append",
        default=None,
        help='Link item in the form "ANCHOR|URL" (repeatable)',
    )
    insert_links_section.add_argument(
        "--skip-url",
        default=None,
        help="Skip inserting a link whose URL exactly matches this (useful to avoid self-links)",
    )
    insert_links_section.add_argument("--diff", action="store_true")
    insert_links_section.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    insert_links_section.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    insert_links_section.set_defaults(func=cmd_bodylex_insert_links_section)


def _selector(slug: str | None, post_id: str | None) -> dict[str, str | None]:
    return {"slug": slug} if slug else {"id": post_id}


def _refuse_on_non_draft(before: dict[str, Any], *, allow_published: bool) -> list[str]:
    status = before.get("status")
    if status != "draft" and not allow_published:
        return [f"Refused: post status is {status}; pass --allow-published or use --require-current draft"]
    return []


def _get_lexical_obj(post: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    return parse_lexical_field(post.get("lexical"))


def cmd_bodylex_inspect(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="lexical")
    sel = _selector(args.slug, args.id)
    base = {"selector": sel, "post_id": str(post.get("id")), "status": post.get("status")}
    lexical_obj, reasons = _get_lexical_obj(post)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": reasons, "images": []})
        return 0
    imgs = list_images(lexical_obj)
    ctx["out"].print(
        {
            **base,
            "refused": False,
            "images": [dataclasses.asdict(i) for i in imgs],
        }
    )
    return 0


def cmd_bodylex_scaffold_captions_map(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="lexical")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(post.get("id")), "status": post.get("status")}

    lexical_obj, reasons = _get_lexical_obj(post)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    mode = "all" if bool(args.all) else str(args.mode)
    if bool(args.all) and str(args.mode) != "missing":
        ctx["out"].print({**base, "refused": True, "reasons": ["Refused: pass either --all or --mode (not both)"]})
        return 0

    mapping: dict[str, dict[str, Any]] = {}
    for img in list_images(lexical_obj):
        caption_text = img.caption_text or ""
        has_caption = bool(caption_text.strip())
        if mode == "missing" and has_caption:
            continue
        if mode == "nonconforming":
            exp = guess_caption_policy(img.src, alt=img.alt, title=img.title, caption_text=img.caption_text)
            if has_caption and caption_matches_expected(img.caption_text, expected_suffix=exp.expected_suffix):
                continue

        exp = guess_caption_policy(img.src, alt=img.alt, title=img.title, caption_text=img.caption_text)
        item: dict[str, Any] = {
            "new_src": img.src,
            "alt": img.alt or "",
            "caption": caption_text if mode != "missing" and has_caption else "",
        }
        if img.title and img.title.strip():
            item["title"] = img.title
        if bool(args.include_context):
            item.update(
                {
                    "_index": img.index,
                    "_path": img.path,
                    "_context_heading": img.context_heading,
                    "_kind_guess": exp.kind,
                    "_expected_suffix": exp.expected_suffix,
                    "_existing_alt": img.alt,
                    "_existing_caption": img.caption_text,
                    "_existing_title": img.title,
                }
            )
        mapping[img.src] = item

    if not mapping:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": ["No images matched (nothing to scaffold)"],
                "out": args.out,
            }
        )
        return 0

    out_path = Path(args.out)
    if out_path.exists() and not args.force:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: output file exists (pass --force): {args.out}"],
                "out": args.out,
            }
        )
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ctx["out"].print(
        {
            **base,
            "refused": False,
            "out": args.out,
            "image_count": len(mapping),
            "note": "Fill in caption/alt/title as needed, then apply with: post bodylex image replace-many",
        }
    )
    return 0


def _apply_lexical_update(
    *,
    api,
    before: dict[str, Any],
    new_lexical_obj: dict[str, Any],
    verify_transform,
    debug_ctx: str,
) -> dict[str, Any]:
    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError(f"{debug_ctx}: Post is missing updated_at; cannot safely update")
    lexical_str = dump_lexical_field(new_lexical_obj)
    api.posts_update(str(before["id"]), {"posts": [{"updated_at": updated_at, "lexical": lexical_str}]})

    after = resolve_post(api, slug=None, post_id=str(before["id"]), formats="html,lexical,mobiledoc")
    after_obj, reasons = parse_lexical_field(after.get("lexical"))
    if after_obj is None:
        raise RuntimeError(f"{debug_ctx}: Verification failed: cannot parse lexical after update: {reasons}")
    vrep, _ = verify_transform(after_obj)
    if vrep.refused:
        raise RuntimeError(f"{debug_ctx}: Verification refused after update: {vrep.reasons}")
    if vrep.changed:
        raise RuntimeError(f"{debug_ctx}: Verification failed: re-running the transform would still change the post")
    return after


def cmd_bodylex_image_replace_src(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = replace_image_src(
        lexical_obj,
        old_src=args.old_src,
        new_src=args.new_src,
        alt=args.alt,
        caption=args.caption,
        title=args.title,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return replace_image_src(
            obj,
            old_src=args.old_src,
            new_src=args.new_src,
            alt=args.alt,
            caption=args.caption,
            title=args.title,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.replace_src"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.replace_src",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "old_src": args.old_src, "new_src": args.new_src},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image replace-src selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.replace_src",
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
            action="post.bodylex.image.replace_src",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "old_src": args.old_src, "new_src": args.new_src},
        )
    ctx["audit"].write(
        "post.bodylex.image.replace_src",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "old_src": args.old_src,
            "new_src": args.new_src,
            "reasons": rep.reasons,
        },
    )
    ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons})
    return 0


def _as_dict_item(r: ReplaceManyItemResult) -> dict[str, Any]:
    return {
        "old_src": r.old_src,
        "new_src": r.new_src,
        "matched": r.matched,
        "changed": r.changed,
        "reasons": r.reasons,
    }


def cmd_bodylex_image_replace_many(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    with open(args.map, encoding="utf-8") as f:
        mapping = json.load(f)
    if not isinstance(mapping, dict) or not mapping:
        ctx["out"].print({**base, "refused": True, "reasons": ["--map must be a non-empty JSON object"]})
        return 0

    rep, new_obj, items = replace_images_by_src_map(lexical_obj, mapping=mapping, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": rep.reasons,
                "items": [_as_dict_item(i) for i in items],
            }
        )
        return 0
    if not rep.changed:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": False,
                "items": [_as_dict_item(i) for i in items],
            }
        )
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "diff": rep.diff,
                "items": [_as_dict_item(i) for i in items],
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        vrep, vobj, _ = replace_images_by_src_map(obj, mapping=mapping, include_diff=False)
        return vrep, vobj

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.replace_many"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.replace_many",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "map_file": args.map, "matched": rep.matched},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image replace-many selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.replace_many",
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
            action="post.bodylex.image.replace_many",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "map_file": args.map, "matched": rep.matched},
        )
    ctx["audit"].write(
        "post.bodylex.image.replace_many",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "map_file": args.map,
            "matched": rep.matched,
        },
    )
    ctx["out"].print(
        {**base, "refused": False, "matched": rep.matched, "changed": True, "items": [_as_dict_item(i) for i in items]}
    )
    return 0


def cmd_bodylex_image_replace_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = replace_first_image_after_heading(
        lexical_obj,
        heading=args.heading,
        new_src=args.new_src,
        expect_old_src=args.expect_old_src,
        alt=args.alt,
        caption=args.caption,
        title=args.title,
        nth_after_heading=int(args.nth_after_heading),
        heading_occurrence=args.heading_occurrence,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return replace_first_image_after_heading(
            obj,
            heading=args.heading,
            new_src=args.new_src,
            expect_old_src=args.expect_old_src,
            alt=args.alt,
            caption=args.caption,
            title=args.title,
            nth_after_heading=int(args.nth_after_heading),
            heading_occurrence=args.heading_occurrence,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.replace_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.replace_after_heading",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "heading": args.heading,
                "nth_after_heading": int(args.nth_after_heading),
                "expect_old_src": args.expect_old_src,
                "new_src": args.new_src,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image replace-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.replace_after_heading",
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
            action="post.bodylex.image.replace_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "heading": args.heading,
                "nth_after_heading": int(args.nth_after_heading),
                "expect_old_src": args.expect_old_src,
                "new_src": args.new_src,
            },
        )
    ctx["audit"].write(
        "post.bodylex.image.replace_after_heading",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "heading": args.heading,
            "nth_after_heading": int(args.nth_after_heading),
            "expect_old_src": args.expect_old_src,
            "new_src": args.new_src,
            "reasons": rep.reasons,
        },
    )
    ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons})
    return 0


def cmd_bodylex_image_set_meta(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = set_image_meta_by_src(
        lexical_obj,
        src=args.src,
        alt=args.alt,
        caption=args.caption,
        title=args.title,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return set_image_meta_by_src(
            obj,
            src=args.src,
            alt=args.alt,
            caption=args.caption,
            title=args.title,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.set_meta"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.set_meta",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "src": args.src,
                "alt": args.alt,
                "caption": args.caption,
                "title": args.title,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image set-meta selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.set_meta",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "selector": sel, "error": str(e), "src": args.src},
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodylex.image.set_meta",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "src": args.src,
                "alt": args.alt,
                "caption": args.caption,
                "title": args.title,
            },
        )
    ctx["audit"].write(
        "post.bodylex.image.set_meta",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "src": args.src,
            "reasons": rep.reasons,
        },
    )
    ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons})
    return 0


def cmd_bodylex_image_insert_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = insert_image_after_heading(
        lexical_obj,
        heading=args.heading,
        src=args.src,
        alt=args.alt,
        caption=args.caption,
        title=args.title,
        template_src=args.template_src,
        heading_occurrence=args.heading_occurrence,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return insert_image_after_heading(
            obj,
            heading=args.heading,
            src=args.src,
            alt=args.alt,
            caption=args.caption,
            title=args.title,
            template_src=args.template_src,
            heading_occurrence=args.heading_occurrence,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.insert_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.insert_after_heading",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "heading": args.heading,
                "src": args.src,
                "template_src": args.template_src,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image insert-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.insert_after_heading",
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
            action="post.bodylex.image.insert_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "heading": args.heading,
                "src": args.src,
                "template_src": args.template_src,
            },
        )
    ctx["audit"].write(
        "post.bodylex.image.insert_after_heading",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "heading": args.heading,
            "src": args.src,
            "template_src": args.template_src,
            "reasons": rep.reasons,
        },
    )
    ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons})
    return 0


def cmd_bodylex_image_delete_by_src(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = delete_images_by_src(
        lexical_obj,
        src=args.src,
        allow_multiple=bool(args.all),
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        vrep, vobj = delete_images_by_src(obj, src=args.src, allow_multiple=bool(args.all), include_diff=False)
        # Idempotence verification: after deleting, re-running the same delete should produce
        # "no match" (i.e. no further changes needed). Treat that as a successful verification.
        if vrep.refused and vrep.reasons == ["No image matched src"]:
            return LexicalEditReport(refused=False, reasons=[], matched=0, changed=False, diff=None), obj
        return vrep, vobj

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.delete_by_src"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.delete_by_src",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "src": args.src, "all": bool(args.all)},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image delete-by-src selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.delete_by_src",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "selector": sel, "error": str(e), "src": args.src},
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodylex.image.delete_by_src",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "src": args.src, "all": bool(args.all)},
        )
    ctx["audit"].write(
        "post.bodylex.image.delete_by_src",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "src": args.src, "all": bool(args.all)},
    )
    ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons})
    return 0


def cmd_bodylex_image_move_before_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = move_top_level_image_before_heading(
        lexical_obj,
        src=args.src,
        heading=args.heading,
        heading_occurrence=args.heading_occurrence,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff}
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return move_top_level_image_before_heading(
            obj,
            src=args.src,
            heading=args.heading,
            heading_occurrence=args.heading_occurrence,
            include_diff=False,
        )

    after = _apply_lexical_update(
        api=api,
        before=before,
        new_lexical_obj=new_obj,
        verify_transform=verify_transform,
        debug_ctx=f"post bodylex image move-before-heading selector={sel} post_id={before.get('id')}",
    )
    ctx["audit"].write(
        "post.bodylex.image.move_before_heading",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "src": args.src, "heading": args.heading},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_fix_bullet_lists_split_html_cards(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = fix_bullet_lists_split_by_html_ul_cards(lexical_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return fix_bullet_lists_split_by_html_ul_cards(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.fix_bullet_lists_split_html_cards"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.fix_bullet_lists_split_html_cards",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex fix-bullet-lists-split-html-cards selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.fix_bullet_lists_split_html_cards",
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
            action="post.bodylex.fix_bullet_lists_split_html_cards",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.fix_bullet_lists_split_html_cards",
        {"apply": True, "selector": sel, "post_id": str(before["id"])},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_convert_html_list_cards(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = convert_html_list_cards_to_native_lists(lexical_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return convert_html_list_cards_to_native_lists(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.convert_html_list_cards"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.convert_html_list_cards",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex convert-html-list-cards selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.convert_html_list_cards",
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
            action="post.bodylex.convert_html_list_cards",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.convert_html_list_cards",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_fix_link_whitespace(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = fix_link_whitespace(lexical_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return fix_link_whitespace(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.fix_link_whitespace"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.fix_link_whitespace",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex fix-link-whitespace selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.fix_link_whitespace",
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
            action="post.bodylex.fix_link_whitespace",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.fix_link_whitespace",
        {"apply": True, "selector": sel, "post_id": str(before["id"])},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_linkify(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = linkify_text_in_paragraph(
        lexical_obj,
        paragraph_contains=str(args.paragraph_contains),
        paragraph_occurrence=args.paragraph_occurrence,
        anchor_text=str(args.anchor_text),
        anchor_occurrence=args.anchor_occurrence,
        url=str(args.url),
        include_list_items=bool(args.include_list_items),
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return linkify_text_in_paragraph(
            obj,
            paragraph_contains=str(args.paragraph_contains),
            paragraph_occurrence=args.paragraph_occurrence,
            anchor_text=str(args.anchor_text),
            anchor_occurrence=args.anchor_occurrence,
            url=str(args.url),
            include_list_items=bool(args.include_list_items),
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.linkify"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.linkify",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "paragraph_contains": str(args.paragraph_contains),
                "paragraph_occurrence": args.paragraph_occurrence,
                "anchor_text": str(args.anchor_text),
                "anchor_occurrence": args.anchor_occurrence,
                "url": str(args.url),
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex linkify selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.linkify",
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
            action="post.bodylex.linkify",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.linkify",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "paragraph_contains": str(args.paragraph_contains),
            "paragraph_occurrence": args.paragraph_occurrence,
            "anchor_text": str(args.anchor_text),
            "anchor_occurrence": args.anchor_occurrence,
            "url": str(args.url),
        },
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_insert_link_paragraph_after_heading_section_end(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = insert_link_paragraph_after_heading_section_end(
        lexical_obj,
        heading=str(args.heading),
        heading_occurrence=args.heading_occurrence,
        link_text=str(args.link_text),
        url=str(args.url),
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return insert_link_paragraph_after_heading_section_end(
            obj,
            heading=str(args.heading),
            heading_occurrence=args.heading_occurrence,
            link_text=str(args.link_text),
            url=str(args.url),
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.insert_link_paragraph_after_heading_section_end"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.insert_link_paragraph_after_heading_section_end",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "heading": str(args.heading),
                "heading_occurrence": args.heading_occurrence,
                "link_text": str(args.link_text),
                "url": str(args.url),
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex insert-link-paragraph-after-heading-section-end selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.insert_link_paragraph_after_heading_section_end",
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
            action="post.bodylex.insert_link_paragraph_after_heading_section_end",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.insert_link_paragraph_after_heading_section_end",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "heading": str(args.heading),
            "heading_occurrence": args.heading_occurrence,
            "link_text": str(args.link_text),
            "url": str(args.url),
        },
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_clear_heading_bold(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    audit_before = audit_heading_bold(lexical_obj, max_examples=10)
    rep, new_obj = clear_heading_bold(lexical_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched, "audit_before": audit_before})
        return 0

    audit_after = audit_heading_bold(new_obj, max_examples=10)
    if not rep.changed:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": False,
                "audit_before": audit_before,
                "audit_after": audit_after,
            }
        )
        return 0

    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "audit_before": audit_before,
                "audit_after": audit_after,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return clear_heading_bold(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.clear_heading_bold"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.clear_heading_bold",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "audit_before": audit_before,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex clear-heading-bold selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.clear_heading_bold",
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
            action="post.bodylex.clear_heading_bold",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "audit_after": audit_heading_bold(parse_lexical_field(after.get("lexical"))[0] or {}, max_examples=10),
            },
        )
    ctx["audit"].write("post.bodylex.clear_heading_bold", {"apply": True, "selector": sel, "post_id": str(before["id"])})
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_unlink_by_url(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    urls = args.url or []
    rep, new_obj = unlink_links_by_url(lexical_obj, urls=urls, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return unlink_links_by_url(obj, urls=urls, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.unlink_by_url"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.unlink_by_url",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "urls": urls},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex unlink-by-url selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.unlink_by_url",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "selector": sel, "urls": urls, "error": str(e)},
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodylex.unlink_by_url",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel, "urls": urls},
        )
    ctx["audit"].write(
        "post.bodylex.unlink_by_url",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched, "urls": urls},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_unlink_by_url_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    urls = [str(u) for u in (args.url or []) if str(u or "").strip()]
    if not urls:
        ctx["out"].print({**base, "refused": True, "reasons": ["Provide at least one --url"]})
        return 0

    rep, new_obj = unlink_links_by_url_after_heading(
        lexical_obj,
        after_heading=str(args.after_heading or "Conclusion"),
        urls=urls,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return unlink_links_by_url_after_heading(
            obj,
            after_heading=str(args.after_heading or "Conclusion"),
            urls=urls,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.unlink_by_url_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.unlink_by_url_after_heading",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "after_heading": str(args.after_heading or "Conclusion"),
                "urls": urls,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex unlink-by-url-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.unlink_by_url_after_heading",
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "selector": sel,
                    "after_heading": str(args.after_heading or "Conclusion"),
                    "urls": urls,
                    "error": str(e),
                },
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodylex.unlink_by_url_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "after_heading": str(args.after_heading or "Conclusion"),
                "urls": urls,
            },
        )
    ctx["audit"].write(
        "post.bodylex.unlink_by_url_after_heading",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "matched": rep.matched,
            "after_heading": str(args.after_heading or "Conclusion"),
            "urls": urls,
        },
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_delete_link_items_by_url_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    urls = [str(u) for u in (args.url or []) if str(u or "").strip()]
    if not urls:
        ctx["out"].print({**base, "refused": True, "reasons": ["Provide at least one --url"]})
        return 0

    after_heading = str(args.after_heading or "Conclusion")
    rep, new_obj = delete_linked_list_items_by_url_after_heading(
        lexical_obj,
        after_heading=after_heading,
        urls=urls,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return delete_linked_list_items_by_url_after_heading(
            obj,
            after_heading=after_heading,
            urls=urls,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.delete_link_items_by_url_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.delete_link_items_by_url_after_heading",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "after_heading": after_heading,
                "urls": urls,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex delete-link-items-by-url-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.delete_link_items_by_url_after_heading",
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "selector": sel,
                    "after_heading": after_heading,
                    "urls": urls,
                    "error": str(e),
                },
            )
        raise
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.bodylex.delete_link_items_by_url_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "after_heading": after_heading,
                "urls": urls,
            },
        )
    ctx["audit"].write(
        "post.bodylex.delete_link_items_by_url_after_heading",
        {
            "apply": True,
            "selector": sel,
            "post_id": str(before["id"]),
            "matched": rep.matched,
            "after_heading": after_heading,
            "urls": urls,
        },
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_unlink_internal_caption_links(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    site = api.get_site().get("site") or {}
    site_url = site.get("url") if isinstance(site, dict) else None
    internal_hosts: set[str] = set()
    if isinstance(site_url, str) and site_url.strip():
        try:
            from urllib.parse import urlparse

            host = (urlparse(site_url.strip()).hostname or "").lower().strip()
            if host:
                internal_hosts.add(host)
        except Exception:
            internal_hosts = set()
    extra = [h.strip().lower() for h in (args.internal_host or []) if isinstance(h, str) and h.strip()]
    internal_hosts.update(extra)

    rep, new_obj = unlink_internal_links_in_image_captions(
        lexical_obj,
        internal_hosts=internal_hosts,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return unlink_internal_links_in_image_captions(obj, internal_hosts=internal_hosts, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.unlink_internal_caption_links"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.unlink_internal_caption_links",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "internal_hosts": sorted(internal_hosts)},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex unlink-internal-caption-links selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.unlink_internal_caption_links",
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
            action="post.bodylex.unlink_internal_caption_links",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.unlink_internal_caption_links",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched, "internal_hosts": sorted(internal_hosts)},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def _parse_anchor_url_pairs(raw_items: list[str] | None) -> tuple[list[tuple[str, str]], list[str]]:
    out: list[tuple[str, str]] = []
    reasons: list[str] = []
    for raw in raw_items or []:
        s = str(raw or "").strip()
        if not s:
            continue
        if "|" not in s:
            reasons.append(f'Refused: --link must be "ANCHOR|URL" (got: {s!r})')
            continue
        anchor, url = s.split("|", 1)
        anchor = anchor.strip()
        url = url.strip()
        if not anchor or not url:
            reasons.append(f"Refused: invalid --link (empty anchor or url): {s!r}")
            continue
        out.append((anchor, url))
    if not out and not reasons:
        reasons.append("Provide at least one --link")
    return out, reasons


def cmd_bodylex_insert_links_section(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    links, link_reasons = _parse_anchor_url_pairs(args.link)
    if link_reasons:
        ctx["out"].print({**base, "refused": True, "reasons": link_reasons})
        return 0

    rep, new_obj = insert_internal_links_section_before_heading(
        lexical_obj,
        before_heading=str(args.before_heading or "Conclusion"),
        section_heading=str(args.section_heading),
        intro_text=str(args.intro),
        links=links,
        skip_url=str(args.skip_url) if args.skip_url is not None else None,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return insert_internal_links_section_before_heading(
            obj,
            before_heading=str(args.before_heading or "Conclusion"),
            section_heading=str(args.section_heading),
            intro_text=str(args.intro),
            links=links,
            skip_url=str(args.skip_url) if args.skip_url is not None else None,
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.insert_links_section"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.insert_links_section",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex insert-links-section selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.insert_links_section",
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
            action="post.bodylex.insert_links_section",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.insert_links_section",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_set_amazon_link_rel(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = set_paid_rel_on_amazon_links(lexical_obj, include_diff=bool(args.diff))
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff})
        return 0

    def verify_transform(obj: dict[str, Any]):
        return set_paid_rel_on_amazon_links(obj, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.set_amazon_link_rel"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.set_amazon_link_rel",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex set-amazon-link-rel selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.set_amazon_link_rel",
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
            action="post.bodylex.set_amazon_link_rel",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write("post.bodylex.set_amazon_link_rel", {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched})
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_set_paid_link_rel(args, ctx) -> int:
    from urllib.parse import urlparse

    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    hosts: list[str] = []
    if args.host:
        for item in args.host:
            for h in str(item).split(","):
                h = h.strip().lower().lstrip(".")
                if h:
                    hosts.append(h)
    host_mode = bool(hosts)
    all_external_mode = bool(args.all_external)
    if host_mode == all_external_mode:
        ctx["out"].print(
            {**base, "refused": True, "reasons": ["Refused: provide exactly one mode: --host or --all-external"]}
        )
        return 0

    required_tokens = [t for t in str(args.rel or "").split() if t.strip()]
    if not required_tokens:
        ctx["out"].print({**base, "refused": True, "reasons": ["Refused: --rel must be non-empty"]})
        return 0

    internal_hosts: set[str] = set()
    if all_external_mode:
        site = api.get_site().get("site") or {}
        site_url = str(site.get("url") or "").strip()
        try:
            h = urlparse(site_url).hostname or ""
        except Exception:
            h = ""
        if h:
            h = h.lower()
            internal_hosts.add(h)
            if h.startswith("www."):
                internal_hosts.add(h[len("www.") :])
            else:
                internal_hosts.add("www." + h)
        if args.internal_host:
            for item in args.internal_host:
                for extra in str(item).split(","):
                    extra = extra.strip().lower().lstrip(".")
                    if extra:
                        internal_hosts.add(extra)

    def match_url(url: str) -> bool:
        u = (url or "").strip()
        if u.startswith("/"):
            return False
        try:
            p = urlparse(u)
        except Exception:
            return False
        if p.scheme not in ("http", "https"):
            return False
        host = (p.hostname or "").lower()
        if not host:
            return False
        if host_mode:
            for h in hosts:
                if host == h or host.endswith("." + h):
                    return True
            return False
        return host not in internal_hosts

    rep, new_obj = set_paid_rel_on_links(
        lexical_obj,
        match_url=match_url,
        required_tokens=required_tokens,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "matched": rep.matched,
                "changed": True,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return set_paid_rel_on_links(obj, match_url=match_url, required_tokens=required_tokens, include_diff=False)

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.set_paid_link_rel"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.set_paid_link_rel",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "mode": "all_external" if all_external_mode else "host",
                "hosts": hosts,
                "internal_hosts": sorted(internal_hosts),
                "required_tokens": required_tokens,
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex set-paid-link-rel selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.set_paid_link_rel",
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
            action="post.bodylex.set_paid_link_rel",
            before=None,
            after=after,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "selector": sel},
        )
    ctx["audit"].write(
        "post.bodylex.set_paid_link_rel",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "matched": rep.matched},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_image_sync_before_headings(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    placements_path = Path(args.placements_file)
    try:
        placements = json.loads(placements_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        ctx["out"].print({**base, "refused": True, "reasons": [f"Refused: failed to read placements file: {e}"]})
        return 0

    rep, new_obj = sync_top_level_images_before_headings(
        lexical_obj,
        placements=placements,
        fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff}
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        return sync_top_level_images_before_headings(
            obj,
            placements=placements,
            fix_split_numbered_lists=not bool(args.no_fix_split_numbered_lists),
            include_diff=False,
        )

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.image.sync_before_headings"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.image.sync_before_headings",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": sel,
                "placements_file": str(placements_path),
            },
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex image sync-before-headings selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.image.sync_before_headings",
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
            action="post.bodylex.image.sync_before_headings",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "placements_file": str(placements_path),
            },
        )
    ctx["audit"].write(
        "post.bodylex.image.sync_before_headings",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "placements_file": str(placements_path)},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_fix_numbered_list_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = fix_numbered_list_split_by_html_ol_after_heading(
        lexical_obj,
        heading=args.heading,
        heading_occurrence=args.heading_occurrence,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff}
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        vrep, vobj = fix_numbered_list_split_by_html_ol_after_heading(
            obj,
            heading=args.heading,
            heading_occurrence=args.heading_occurrence,
            include_diff=False,
        )
        # After fixing, the HTML cards are removed, so a strict re-run could refuse if it no longer
        # sees a split list. Treat that situation as idempotent success.
        if vrep.refused and vrep.reasons == ["Refused: expected a numbered list immediately after heading"]:
            return LexicalEditReport(refused=False, reasons=[], matched=0, changed=False, diff=None), obj
        return vrep, vobj

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.fix_numbered_list_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.fix_numbered_list_after_heading",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "heading": args.heading},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex fix-numbered-list-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.fix_numbered_list_after_heading",
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
            action="post.bodylex.fix_numbered_list_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "heading": args.heading,
            },
        )
    ctx["audit"].write(
        "post.bodylex.fix_numbered_list_after_heading",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "heading": args.heading},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0


def cmd_bodylex_fix_numbered_paragraphs_after_heading(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    sel = _selector(args.slug, args.id)
    base = {"apply": bool(ctx["apply"]), "selector": sel, "post_id": str(before.get("id")), "status": before.get("status")}

    if args.require_current and before.get("status") != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={before.get('status')}"],
            }
        )
        return 0

    reasons = _refuse_on_non_draft(before, allow_published=bool(args.allow_published)) if ctx["apply"] else []
    if reasons:
        ctx["out"].print({**base, "refused": True, "reasons": reasons})
        return 0

    lexical_obj, parse_reasons = _get_lexical_obj(before)
    if lexical_obj is None:
        ctx["out"].print({**base, "refused": True, "reasons": parse_reasons})
        return 0

    rep, new_obj = fix_numbered_paragraphs_to_list_after_heading(
        lexical_obj,
        heading=args.heading,
        heading_occurrence=args.heading_occurrence,
        include_diff=bool(args.diff),
    )
    if rep.refused:
        ctx["out"].print({**base, "refused": True, "reasons": rep.reasons, "matched": rep.matched})
        return 0
    if not rep.changed:
        ctx["out"].print({**base, "refused": False, "matched": rep.matched, "changed": False, "reasons": rep.reasons})
        return 0
    if not ctx["apply"]:
        ctx["out"].print(
            {**base, "refused": False, "matched": rep.matched, "changed": True, "reasons": rep.reasons, "diff": rep.diff}
        )
        return 0

    def verify_transform(obj: dict[str, Any]):
        vrep, vobj = fix_numbered_paragraphs_to_list_after_heading(
            obj,
            heading=args.heading,
            heading_occurrence=args.heading_occurrence,
            include_diff=False,
        )
        # After fixing, a re-run should be a no-op ("No numbered paragraphs after heading").
        if not vrep.refused and not vrep.changed and vrep.reasons == ["No numbered paragraphs after heading"]:
            return LexicalEditReport(refused=False, reasons=[], matched=0, changed=False, diff=None), obj
        return vrep, vobj

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.bodylex.fix_numbered_paragraphs_after_heading"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.bodylex.fix_numbered_paragraphs_after_heading",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": sel, "heading": args.heading},
        )
    try:
        after = _apply_lexical_update(
            api=api,
            before=before,
            new_lexical_obj=new_obj,
            verify_transform=verify_transform,
            debug_ctx=f"post bodylex fix-numbered-paragraphs-after-heading selector={sel} post_id={before.get('id')}",
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.bodylex.fix_numbered_paragraphs_after_heading",
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
            action="post.bodylex.fix_numbered_paragraphs_after_heading",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": sel,
                "heading": args.heading,
            },
        )
    ctx["audit"].write(
        "post.bodylex.fix_numbered_paragraphs_after_heading",
        {"apply": True, "selector": sel, "post_id": str(before["id"]), "heading": args.heading},
    )
    ctx["out"].print({**base, "refused": False, "changed": True, "matched": rep.matched, "after_id": str(after.get("id"))})
    return 0
