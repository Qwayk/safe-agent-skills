from __future__ import annotations

import json
import time
import csv
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..content_html_card import list_images_in_html_card, set_figcaptions_by_src
from ..content_lexical import list_images as list_lexical_images
from ..content_lexical import parse_lexical_field
from ..post_audit import audit_post
from ..post_patch import apply_post_patch, resolve_post
from ..runtime import get_api
from .bodylex import add_bodylex_commands
from .bodymob import add_bodymob_commands
from .post_authors import add_post_authors_commands
from .post_images import add_post_images_commands
from .post_links import add_post_links_commands
from .post_freepik import cmd_post_freepik_apply_one


def add_post_commands(post_sub) -> None:
    post_get = post_sub.add_parser("get", help="Fetch post by slug or id")
    post_get.add_argument("--slug", default=None)
    post_get.add_argument("--id", default=None)
    post_get.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,lexical)")
    post_get.set_defaults(func=cmd_post_get)

    post_id = post_sub.add_parser("id", help="Resolve and print post id (by slug or id)")
    post_id.add_argument("--slug", default=None)
    post_id.add_argument("--id", default=None)
    post_id.set_defaults(func=cmd_post_id)

    post_find = post_sub.add_parser("find", help="Browse posts with filter/limit/order")
    post_find.add_argument("--filter", default=None)
    post_find.add_argument("--limit", type=int, default=15)
    post_find.add_argument("--page", type=int, default=None)
    post_find.add_argument("--order", default=None)
    post_find.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,lexical)")
    post_find.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    post_find.add_argument("--include", default=None, help="Comma-separated include list (API include param)")
    post_find.set_defaults(func=cmd_post_find)

    post_email_export = post_sub.add_parser("email-stats-export", help="Export email delivery stats for posts to CSV")
    post_email_export.add_argument("--out", required=True, help="Output CSV path")
    post_email_export.add_argument("--filter", default=None, help="NQL post filter (e.g. status:published)")
    post_email_export.add_argument("--limit", type=int, default=100, help="Page size (default: 100)")
    post_email_export.add_argument("--max-pages", type=int, default=200, help="Max pages to fetch (default: 200)")
    post_email_export.add_argument("--include-unsent", action="store_true", help="Include posts without an email object")
    post_email_export.set_defaults(func=cmd_post_email_stats_export)

    post_set_status = post_sub.add_parser("set-status", help="Change post status (dry-run by default)")
    post_set_status.add_argument("--slug", default=None)
    post_set_status.add_argument("--id", default=None)
    post_set_status.add_argument("--to", required=True, help="draft|published|scheduled")
    post_set_status.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    post_set_status.add_argument("--published-at", default=None, help="ISO timestamp for scheduled posts")
    post_set_status.add_argument("--newsletter", default=None, help="Newsletter slug (send on publish/schedule)")
    post_set_status.add_argument("--email-segment", default=None, help="Member segment filter")
    post_set_status.add_argument("--email-only", action="store_true", help="Send as email-only post")
    post_set_status.set_defaults(func=cmd_post_set_status)

    post_patch = post_sub.add_parser("patch", help="Patch post fields from a JSON file (dry-run by default)")
    post_patch.add_argument("--slug", default=None)
    post_patch.add_argument("--id", default=None)
    post_patch.add_argument("--file", required=True, help="JSON file with patch fields")
    post_patch.add_argument("--require-current", default=None)
    post_patch.add_argument(
        "--source",
        default=None,
        help="Optional source param (advanced). Use source=html when updating html content.",
    )
    post_patch.set_defaults(func=cmd_post_patch)

    post_create = post_sub.add_parser("create", help="Create a new post (dry-run by default)")
    post_create.add_argument("--title", required=True)
    post_create.add_argument("--slug", default=None)
    post_create.add_argument("--status", default="draft", help="draft|published")
    post_create.add_argument("--visibility", default="public", help="public|members|paid")
    post_create.add_argument("--html-file", default=None, help="Path to HTML file (use with --source html)")
    post_create.add_argument("--lexical-file", default=None, help="Path to Lexical JSON string file")
    post_create.add_argument("--source", default=None, help="Optional source param (e.g. html)")
    post_create.set_defaults(func=cmd_post_create)

    post_copy = post_sub.add_parser("copy", help="Copy a post (creates a new draft; dry-run by default)")
    post_copy.add_argument("--slug", default=None)
    post_copy.add_argument("--id", default=None)
    post_copy.set_defaults(func=cmd_post_copy)

    post_delete = post_sub.add_parser("delete", help="Delete a post (dry-run by default; apply requires --yes)")
    post_delete.add_argument("--slug", default=None)
    post_delete.add_argument("--id", default=None)
    post_delete.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    post_delete.set_defaults(func=cmd_post_delete)

    post_convert = post_sub.add_parser(
        "convert-from-html",
        help="Convert an HTML-only post to Lexical (via source=html). Needed for Lexical tools.",
    )
    post_convert.add_argument("--slug", default=None)
    post_convert.add_argument("--id", default=None)
    post_convert.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    post_convert.add_argument(
        "--from-mobiledoc",
        action="store_true",
        help="Allow converting a Mobiledoc post by re-sending its current HTML via source=html (default refuses).",
    )
    post_convert.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    post_convert.set_defaults(func=cmd_post_convert_from_html)

    post_set_feature = post_sub.add_parser(
        "set-feature-image",
        help="Upload an image and set as feature image (dry-run by default)",
    )
    post_set_feature.add_argument("--slug", default=None, help="Target post slug")
    post_set_feature.add_argument("--id", default=None, help="Target post id")
    post_set_feature.add_argument("--file", required=True, help="Local image file path")
    post_set_feature.add_argument(
        "--upload-name",
        default=None,
        help="Optional filename to use in Ghost storage (affects URL path)",
    )
    post_set_feature.add_argument("--alt", default=None, help="Feature image alt text")
    post_set_feature.add_argument("--caption", default=None, help="Feature image caption")
    post_set_feature.set_defaults(func=cmd_post_set_feature_image)

    post_set_feature_from_body = post_sub.add_parser(
        "set-feature-from-body",
        help="Set feature image to an existing body image src (no upload; dry-run by default)",
    )
    post_set_feature_from_body.add_argument("--slug", default=None)
    post_set_feature_from_body.add_argument("--id", default=None)
    post_set_feature_from_body.add_argument("--nth", type=int, default=1, help="1-based body image index (default: 1)")
    post_set_feature_from_body.add_argument("--alt", default=None, help="Optional override alt text")
    post_set_feature_from_body.add_argument("--caption", default=None, help="Optional override caption text")
    post_set_feature_from_body.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    post_set_feature_from_body.add_argument(
        "--allow-published",
        action="store_true",
        help="Allow applying edits to non-draft posts (default refuses on non-draft)",
    )
    post_set_feature_from_body.set_defaults(func=cmd_post_set_feature_from_body)

    post_freepik = post_sub.add_parser("freepik", help="Freepik image replacement helpers (manual alt/caption)")
    freepik_sub = post_freepik.add_subparsers(dest="post_freepik_cmd", required=True)
    apply_one = freepik_sub.add_parser(
        "apply-one",
        help="Remove all body images, (optionally) fix split numbered Instructions list, upload/set featured image, verify, and optionally publish",
    )
    apply_one.add_argument("--slug", default=None)
    apply_one.add_argument("--id", default=None)
    apply_one.add_argument("--require-current", default="draft", help="Refuse unless current status matches (default: draft)")
    apply_one.add_argument(
        "--snapshots-dir",
        default=None,
        help="Directory for local pre-apply JSON snapshots (gitignored). Default: project config `snapshots_dir` else <project_dir>/snapshots",
    )
    apply_one.add_argument(
        "--tracking-csv",
        default=None,
        help="Tracking CSV to update after apply (set empty string to disable). Default: project config `tracking_csv`",
    )
    apply_one.add_argument(
        "--placements-file",
        default=None,
        help="Optional JSON placements file for body images (same format as `post bodylex image sync-before-headings`)",
    )
    apply_one.add_argument(
        "--body-images-json",
        default=None,
        help="Optional JSON list of body images to upload + place (requires manual alt/caption); mutually exclusive with --placements-file",
    )
    apply_one.add_argument(
        "--no-fix-split-numbered-lists",
        action="store_true",
        help="Disable safe auto-fixing of split numbered lists (HTML <ol> cards) when detected",
    )
    apply_one.add_argument(
        "--no-fix-numbered-paragraphs",
        action="store_true",
        help='Disable safe auto-fixing of numbered paragraph steps ("1. ...") after Instructions',
    )
    apply_one.add_argument("--diff", action="store_true", help="Include lexical diff in dry-run output")
    apply_one.add_argument("--freepik-featured-id", default=None, help="Freepik resource id for the featured image (recorded to tracking.csv)")
    apply_one.add_argument("--featured-file", default=None, help="Local featured image file path (optional if auto-resolving by id)")
    apply_one.add_argument("--freepik-inventory-csv", default=None, help="Optional inventory CSV to auto-resolve --featured-file by id (project config key: freepik_inventory_csv)")
    apply_one.add_argument("--freepik-downloads-root", default=None, help="Optional downloads root to auto-resolve --featured-file by id (project config key: freepik_downloads_root)")
    apply_one.add_argument("--featured-upload-name", default=None, help="Optional Ghost upload filename (default: <slug>-featured.jpg)")
    apply_one.add_argument("--featured-alt", required=True, help="Manual featured image alt text")
    apply_one.add_argument("--featured-caption", required=True, help="Manual featured image caption (must end with stock disclosure)")
    apply_one.add_argument("--publish", action="store_true", help="Publish after successful verification (requires --apply --yes)")
    apply_one.set_defaults(func=cmd_post_freepik_apply_one)

    scaffold = post_sub.add_parser("scaffold", help="Generate editable helper files (no API writes)")
    scaffold_sub = scaffold.add_subparsers(dest="post_scaffold_cmd", required=True)

    seo_patch = scaffold_sub.add_parser(
        "seo-patch",
        help="Write a post patch JSON for SEO/social/title/tags fields (fill in manually)",
    )
    seo_patch.add_argument("--slug", default=None)
    seo_patch.add_argument("--id", default=None)
    seo_patch.add_argument("--out", required=True, help="Output JSON path")
    seo_patch.add_argument("--force", action="store_true", help="Overwrite output file if it exists")
    seo_patch.add_argument(
        "--include-internal-tags",
        action="store_true",
        help="Include internal tags (defaults to public tags only)",
    )
    seo_patch.set_defaults(func=cmd_post_scaffold_seo_patch)

    post_audit = post_sub.add_parser("audit", help="Audit a post for migration readiness (read-only)")
    post_audit.add_argument("--slug", default=None)
    post_audit.add_argument("--id", default=None)
    post_audit.add_argument(
        "--legacy-host",
        action="append",
        default=None,
        help="Legacy WordPress host to flag (repeatable). Default: project config `legacy_hosts` (or none).",
    )
    post_audit.add_argument(
        "--enforce-caption-policy",
        action="store_true",
        help="Also flag captions that don't match the migration caption policy (stock vs infographic).",
    )
    post_audit.set_defaults(func=cmd_post_audit)

    add_post_authors_commands(post_sub)
    add_post_images_commands(post_sub)
    add_post_links_commands(post_sub)

    body = post_sub.add_parser("body", help="Post body (HTML card mode) helpers")
    body_sub = body.add_subparsers(dest="body_cmd", required=True)

    body_show = body_sub.add_parser("show-images", help="List images in the HTML card")
    body_show.add_argument("--slug", default=None)
    body_show.add_argument("--id", default=None)
    body_show.set_defaults(func=cmd_post_body_show_images)

    body_set = body_sub.add_parser("set-captions", help="Set figcaptions by image src in HTML card")
    body_set.add_argument("--slug", default=None)
    body_set.add_argument("--id", default=None)
    body_set.add_argument("--captions-file", required=True, help="JSON mapping {src: caption}")
    body_set.add_argument("--diff", action="store_true", help="Include unified diff")
    body_set.set_defaults(func=cmd_post_body_set_captions)

    add_bodylex_commands(post_sub)
    add_bodymob_commands(post_sub)


def _refuse_on_non_draft(status: str | None, *, allow_published: bool) -> list[str]:
    if status != "draft" and not allow_published:
        return [f"Refused: post status is {status}; pass --allow-published or use --require-current draft"]
    return []


def cmd_post_get(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats=args.formats)
    ctx["out"].print(post)
    return 0


def cmd_post_id(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats=None)
    ctx["out"].print(
        {
            "selector": {"slug": args.slug} if args.slug else {"id": args.id},
            "id": post.get("id"),
            "slug": post.get("slug"),
            "status": post.get("status"),
            "title": post.get("title"),
        }
    )
    return 0


def cmd_post_copy(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats=None)
    post_id = before.get("id")
    if not isinstance(post_id, str) or not post_id.strip():
        raise RuntimeError("Post id not found")

    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.copy"
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.copy",
                before=before,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                },
            )
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "copy": {"from_id": post_id, "from_slug": before.get("slug"), "from_title": before.get("title")},
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{post_id}-post.copy"
        backup.write_before_after(
            kind="post",
            resource_id=f"id:{post_id}",
            slug=str(before.get("slug") or ""),
            action="post.copy",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "from_id": post_id},
        )

    try:
        res = api.posts_copy(post_id)
        created = (res.get("posts") or [{}])[0] if isinstance(res, dict) else {}
        new_id = created.get("id") if isinstance(created, dict) else None
        if not isinstance(new_id, str) or not new_id.strip():
            raise RuntimeError(f"Unexpected copy response (missing id): {res}")
        if new_id == post_id:
            raise RuntimeError("Unexpected copy response: new_id is the same as from_id")

        verified = resolve_post(api, slug=None, post_id=new_id, formats=None)
        if verified.get("id") != new_id:
            raise RuntimeError(f"Verification failed: id mismatch (got={verified.get('id')!r})")
        if verified.get("status") != "draft":
            raise RuntimeError(f"Verification failed: expected status=draft (got={verified.get('status')!r})")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=f"id:{post_id}",
                slug=str(before.get("slug") or ""),
                action="post.copy",
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "from_id": post_id,
                    "error": str(e),
                },
            )
        raise

    ctx["audit"].write("post.copy", {"apply": True, "from_id": post_id, "to_id": new_id, "status": verified.get("status")})
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=f"id:{new_id}",
            slug=str(verified.get("slug") or ""),
            action="post.copy",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "from_id": post_id, "to_id": new_id, "verified": True},
        )

    ctx["out"].print({"ok": True, "from_id": post_id, "to_id": new_id, "status": verified.get("status")})
    return 0


def cmd_post_find(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit}
    if args.filter:
        params["filter"] = args.filter
    if args.page is not None:
        params["page"] = args.page
    if args.order:
        params["order"] = args.order
    if args.formats:
        params["formats"] = args.formats
    if args.fields:
        params["fields"] = args.fields
    if args.include:
        params["include"] = args.include
    res = api.posts_browse(params=params)
    ctx["out"].print(res)
    return 0


def cmd_post_email_stats_export(args, ctx) -> int:
    api = get_api(ctx)
    limit = int(args.limit)
    if limit < 1 or limit > 200:
        raise RuntimeError("--limit must be between 1 and 200")
    max_pages = int(args.max_pages)
    if max_pages < 1:
        raise RuntimeError("--max-pages must be >= 1")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    page = 1
    while page <= max_pages:
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "include": "email,newsletter",
            "fields": "id,slug,title,published_at,updated_at,status",
        }
        if args.filter:
            params["filter"] = args.filter
        res = api.posts_browse(params=params)
        posts = res.get("posts") or []
        if not isinstance(posts, list) or not posts:
            break
        for post in posts:
            if not isinstance(post, dict):
                continue
            email_obj = post.get("email")
            if email_obj is None and not args.include_unsent:
                continue
            email = email_obj if isinstance(email_obj, dict) else {}
            newsletter = post.get("newsletter") if isinstance(post.get("newsletter"), dict) else {}
            rows.append(
                {
                    "post_id": post.get("id"),
                    "slug": post.get("slug"),
                    "title": post.get("title"),
                    "status": post.get("status"),
                    "published_at": post.get("published_at"),
                    "newsletter_slug": newsletter.get("slug"),
                    "newsletter_name": newsletter.get("name"),
                    "email_id": email.get("id"),
                    "email_status": email.get("status"),
                    "recipient_filter": email.get("recipient_filter"),
                    "email_count": email.get("email_count"),
                    "delivered_count": email.get("delivered_count"),
                    "opened_count": email.get("opened_count"),
                    "failed_count": email.get("failed_count"),
                    "submitted_at": email.get("submitted_at"),
                }
            )
        meta = res.get("meta") if isinstance(res, dict) else None
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        pages = pagination.get("pages") if isinstance(pagination, dict) else None
        if isinstance(pages, int) and page >= pages:
            break
        page += 1

    # Write CSV (contains no member PII).
    fieldnames = [
        "post_id",
        "slug",
        "title",
        "status",
        "published_at",
        "newsletter_slug",
        "newsletter_name",
        "email_id",
        "email_status",
        "recipient_filter",
        "email_count",
        "delivered_count",
        "opened_count",
        "failed_count",
        "submitted_at",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})

    ctx["audit"].write("post.email_stats_export", {"apply": True, "out": str(out_path), "rows": len(rows)})
    ctx["out"].print({"ok": True, "out": str(out_path), "rows": len(rows)})
    return 0


def cmd_post_audit(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="lexical,mobiledoc")
    project_cfg = ctx.get("project_cfg") or {}
    legacy_hosts = args.legacy_host or project_cfg.get("legacy_hosts") or []
    if not isinstance(legacy_hosts, list):
        legacy_hosts = []
    rep = audit_post(post, legacy_hosts=legacy_hosts, enforce_caption_policy=bool(args.enforce_caption_policy))
    ctx["out"].print(
        {
            "selector": {"slug": args.slug} if args.slug else {"id": args.id},
            "post_id": str(post.get("id")),
            "slug": post.get("slug"),
            "status": post.get("status"),
            **rep,
        }
    )
    return 0


def cmd_post_set_status(args, ctx) -> int:
    api = get_api(ctx)

    patch: dict[str, Any] = {"status": args.to}
    if args.to == "scheduled":
        if not args.published_at:
            raise RuntimeError("--published-at is required when --to scheduled")
        patch["published_at"] = args.published_at
    if args.email_only:
        patch["email_only"] = True

    params: dict[str, Any] = {}
    if args.newsletter:
        params["newsletter"] = args.newsletter
    if args.email_segment:
        params["email_segment"] = args.email_segment

    if ctx["apply"] and not ctx["yes"]:
        before = resolve_post(api, slug=args.slug, post_id=args.id, formats=None)
        ctx["out"].print(
            {
                "apply": True,
                "refused": True,
                "reasons": ["Refused: post set-status requires --yes"],
                "post_id": before.get("id"),
                "slug": before.get("slug"),
                "status": before.get("status"),
                "to": args.to,
                "params": params if params else None,
            }
        )
        return 0

    plan = apply_post_patch(
        api,
        slug=args.slug,
        post_id=args.id,
        patch=patch,
        apply=bool(ctx["apply"]),
        require_current=args.require_current,
        params=params if params else None,
        source=None,
        snapshot=ctx.get("backup"),
        snapshot_action="post.set_status",
        snapshot_meta={"params": params if params else None},
    )
    ctx["audit"].write(
        "post.set_status",
        {
            "apply": ctx["apply"],
            "selector": plan.selector,
            "post_id": plan.resource_id,
            "changes": plan.changes,
            "params": params if params else None,
        },
    )
    ctx["out"].print(
        {
            "apply": ctx["apply"],
            "refused": plan.refused,
            "reasons": plan.reasons,
            "post_id": plan.resource_id,
            "changes": plan.changes,
            "params": params if params else None,
        }
    )
    return 0


def cmd_post_patch(args, ctx) -> int:
    api = get_api(ctx)
    with open(args.file, encoding="utf-8") as f:
        patch = json.load(f)
    if not isinstance(patch, dict):
        raise RuntimeError("Patch file must contain a JSON object of fields")

    plan = apply_post_patch(
        api,
        slug=args.slug,
        post_id=args.id,
        patch=patch,
        apply=bool(ctx["apply"]),
        require_current=args.require_current,
        source=args.source,
        snapshot=ctx.get("backup"),
        snapshot_action="post.patch",
        snapshot_meta={"patch_file": args.file},
    )
    ctx["audit"].write(
        "post.patch",
        {"apply": ctx["apply"], "selector": plan.selector, "post_id": plan.resource_id, "changes": plan.changes},
    )
    ctx["out"].print(
        {
            "apply": ctx["apply"],
            "refused": plan.refused,
            "reasons": plan.reasons,
            "post_id": plan.resource_id,
            "changes": plan.changes,
        }
    )
    return 0


def cmd_post_create(args, ctx) -> int:
    api = get_api(ctx)
    if bool(args.html_file) == bool(args.lexical_file):
        raise ValidationError("Provide exactly one of: --html-file or --lexical-file")

    if args.slug:
        try:
            _ = resolve_post(api, slug=args.slug, post_id=None)
            ctx["out"].print(
                {
                    "apply": ctx["apply"],
                    "refused": True,
                    "reasons": [f"Post already exists with slug={args.slug}. Delete it first or use patch."],
                }
            )
            return 0
        except RuntimeError as e:
            msg = str(e)
            if "HTTP 404" not in msg and "Post not found" not in msg:
                raise

    post: dict[str, Any] = {
        "title": args.title,
        "status": args.status,
        "visibility": args.visibility,
    }
    if args.slug:
        post["slug"] = args.slug

    content_key: str
    content_value: str
    if args.html_file:
        content_key = "html"
        with open(args.html_file, encoding="utf-8") as f:
            content_value = f.read()
    else:
        content_key = "lexical"
        with open(args.lexical_file, encoding="utf-8") as f:
            content_value = f.read()
    post[content_key] = content_value

    params: dict[str, Any] = {}
    if args.source:
        params["source"] = args.source
    elif content_key == "html":
        params["source"] = "html"

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "reasons": [],
                "create": {"title": args.title, "slug": args.slug, "status": args.status, "visibility": args.visibility},
                "source": params.get("source"),
                "content": {"field": content_key, "chars": len(content_value)},
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-slug-{args.slug or 'auto'}-post.create"
        backup.write_before_after(
            kind="post",
            resource_id=f"slug:{args.slug}" if args.slug else "new",
            slug=str(args.slug or ""),
            action="post.create",
            before=None,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "create": {"title": args.title, "slug": args.slug, "status": args.status, "visibility": args.visibility},
                "source": params.get("source"),
                "content": {"field": content_key, "chars": len(content_value)},
            },
        )

    try:
        res = api.posts_create({"posts": [post]}, params=params if params else None)
        created = (res.get("posts") or [{}])[0]
        post_id = created.get("id")
        if not isinstance(post_id, str) or not post_id:
            raise RuntimeError(f"Unexpected create response (missing id): {res}")

        verified = resolve_post(api, slug=None, post_id=post_id, formats="html,lexical,mobiledoc")
        if verified.get("title") != args.title:
            raise RuntimeError(f"Verification failed: title mismatch (got={verified.get('title')!r})")
        if args.slug and verified.get("slug") != args.slug:
            raise RuntimeError(f"Verification failed: slug mismatch (got={verified.get('slug')!r})")
        if verified.get("status") != args.status:
            raise RuntimeError(f"Verification failed: status mismatch (got={verified.get('status')!r})")
        if not verified.get("lexical"):
            raise RuntimeError("Verification failed: lexical content is empty after create")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=f"slug:{args.slug}" if args.slug else "new",
                slug=str(args.slug or ""),
                action="post.create",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    ctx["audit"].write(
        "post.create",
        {"apply": True, "post_id": post_id, "slug": verified.get("slug"), "status": verified.get("status")},
    )
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(post_id),
            slug=str(verified.get("slug") or args.slug or ""),
            action="post.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True},
        )
    ctx["out"].print({"apply": True, "post_id": post_id, "slug": verified.get("slug"), "status": verified.get("status")})
    return 0


def cmd_post_delete(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")

    if args.require_current and post.get("status") != args.require_current:
        ctx["out"].print(
            {
                "apply": ctx["apply"],
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={post.get('status')}"],
                "post_id": post.get("id"),
                "slug": post.get("slug"),
            }
        )
        return 0

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "reasons": [],
                "post_id": post.get("id"),
                "slug": post.get("slug"),
                "status": post.get("status"),
                "title": post.get("title"),
            }
        )
        return 0

    if not ctx["yes"]:
        ctx["out"].print(
            {
                "apply": True,
                "refused": True,
                "reasons": ["Refused: delete requires --yes"],
                "post_id": post.get("id"),
                "slug": post.get("slug"),
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{post.get('id')}-post.delete"
        backup.write_before_after(
            kind="post",
            resource_id=str(post.get("id")),
            slug=str(post.get("slug") or ""),
            action="post.delete",
            before=post,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": {"slug": args.slug} if args.slug else {"id": args.id}},
        )

    try:
        resp = api.posts_delete(str(post.get("id")))
        if resp.status not in (200, 204):
            raise RuntimeError(f"Unexpected delete response: HTTP {resp.status}")

        # Verify: expect 404 when re-fetching by id.
        try:
            _ = resolve_post(api, slug=None, post_id=str(post.get("id")))
        except RuntimeError as e:
            msg = str(e)
            if "HTTP 404" not in msg and "Post not found" not in msg:
                raise
        else:
            raise RuntimeError("Verification failed: post still exists after delete")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(post.get("id")),
                slug=str(post.get("slug") or ""),
                action="post.delete",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(post.get("id")),
            slug=str(post.get("slug") or ""),
            action="post.delete",
            before=None,
            after=None,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "deleted": {"post_id": post.get("id"), "slug": post.get("slug")}},
        )
    ctx["audit"].write("post.delete", {"apply": True, "post_id": post.get("id"), "slug": post.get("slug")})
    ctx["out"].print({"apply": True, "post_id": post.get("id"), "slug": post.get("slug")})
    return 0


def cmd_post_set_feature_image(args, ctx) -> int:
    api = get_api(ctx)

    if not ctx["apply"]:
        before = resolve_post(api, slug=args.slug, post_id=args.id, formats=None)
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.set_feature_image"
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.set_feature_image",
                before=before,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                    "upload": {"file": args.file, "upload_name": args.upload_name},
                },
            )
        ctx["out"].print(
            {
                "apply": False,
                "would_upload": {"file": args.file, "upload_name": args.upload_name, "purpose": "image"},
                "would_patch": {
                    "feature_image": "<uploaded-url>",
                    "feature_image_alt": args.alt,
                    "feature_image_caption": args.caption,
                },
            }
        )
        return 0

    upload = api.upload_image(file_path=args.file, purpose="image", ref=args.file, upload_name=args.upload_name)
    imgs = upload.get("images") or []
    if not imgs or not imgs[0].get("url"):
        raise RuntimeError(f"Upload did not return an image url: {upload}")
    url = imgs[0]["url"]

    patch: dict[str, Any] = {"feature_image": url}
    if args.alt is not None:
        patch["feature_image_alt"] = args.alt
    if args.caption is not None:
        patch["feature_image_caption"] = args.caption

    plan = apply_post_patch(
        api,
        slug=args.slug,
        post_id=args.id,
        patch=patch,
        apply=True,
        snapshot=ctx.get("backup"),
        snapshot_action="post.set_feature_image",
        snapshot_meta={"feature_image": url, "upload": {"file": args.file, "upload_name": args.upload_name}},
    )
    ctx["out"].print({"apply": True, "post_id": plan.resource_id, "feature_image": url})
    return 0


def cmd_post_set_feature_from_body(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="lexical,mobiledoc")
    base = {"apply": bool(ctx["apply"]), "selector": {"slug": args.slug} if args.slug else {"id": args.id}}
    status = before.get("status")

    if args.require_current and status != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={status}"],
            }
        )
        return 0

    if ctx["apply"]:
        reasons = _refuse_on_non_draft(status, allow_published=bool(args.allow_published))
        if reasons:
            ctx["out"].print({**base, "refused": True, "reasons": reasons})
            return 0

    chosen_src: str | None = None
    chosen_alt: str | None = None
    chosen_caption: str | None = None

    lexical_obj, parse_reasons = parse_lexical_field(before.get("lexical"))
    if lexical_obj is not None:
        imgs: list[Any] = list_lexical_images(lexical_obj)
    else:
        from ..content_mobiledoc import list_images as list_mobiledoc_images
        from ..content_mobiledoc import parse_mobiledoc_field

        mob_obj, mob_reasons = parse_mobiledoc_field(before.get("mobiledoc"))
        if mob_obj is None:
            ctx["out"].print({**base, "refused": True, "reasons": {"lexical": parse_reasons, "mobiledoc": mob_reasons}})
            return 0
        mob_imgs, mob_list_reasons = list_mobiledoc_images(mob_obj)
        if mob_list_reasons:
            ctx["out"].print({**base, "refused": True, "reasons": mob_list_reasons})
            return 0
        imgs = mob_imgs
    if args.nth < 1 or args.nth > len(imgs):
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"--nth out of range (1..{len(imgs)})"],
                "image_count": len(imgs),
            }
        )
        return 0

    chosen = imgs[args.nth - 1]
    chosen_src = getattr(chosen, "src", None)
    chosen_alt = getattr(chosen, "alt", None)
    chosen_caption = getattr(chosen, "caption_text", None) if hasattr(chosen, "caption_text") else getattr(chosen, "caption", None)
    if not isinstance(chosen_src, str) or not chosen_src:
        ctx["out"].print({**base, "refused": True, "reasons": ["Chosen image is missing src"]})
        return 0

    patch: dict[str, Any] = {"feature_image": chosen_src}

    if args.alt is not None:
        patch["feature_image_alt"] = args.alt
    elif chosen_alt is not None:
        patch["feature_image_alt"] = chosen_alt

    if args.caption is not None:
        patch["feature_image_caption"] = args.caption
    elif isinstance(chosen_caption, str) and chosen_caption.strip():
        patch["feature_image_caption"] = chosen_caption

    plan = apply_post_patch(
        api,
        slug=args.slug,
        post_id=args.id,
        patch=patch,
        apply=bool(ctx["apply"]),
        require_current=args.require_current,
        snapshot=ctx.get("backup"),
        snapshot_action="post.set_feature_from_body",
        snapshot_meta={"nth": args.nth, "chosen_src": chosen_src},
    )
    ctx["audit"].write(
        "post.set_feature_from_body",
        {
            "apply": ctx["apply"],
            "selector": plan.selector,
            "post_id": plan.resource_id,
            "nth": args.nth,
            "chosen_src": chosen_src,
            "changes": plan.changes,
        },
    )
    ctx["out"].print(
        {
            "apply": ctx["apply"],
            "refused": plan.refused,
            "reasons": plan.reasons,
            "post_id": plan.resource_id,
            "nth": args.nth,
            "chosen_src": chosen_src,
            "chosen_alt": chosen_alt,
            "chosen_caption": chosen_caption,
            "changes": plan.changes,
        }
    )
    return 0


def cmd_post_scaffold_seo_patch(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats=None)
    base = {"apply": bool(ctx["apply"]), "selector": {"slug": args.slug} if args.slug else {"id": args.id}}

    tags: list[str] = []
    for t in post.get("tags") or []:
        if not isinstance(t, dict):
            continue
        vis = t.get("visibility")
        if vis == "internal" and not args.include_internal_tags:
            continue
        name = t.get("name")
        if isinstance(name, str) and name:
            tags.append(name)

    patch: dict[str, Any] = {
        "title": post.get("title"),
        "custom_excerpt": post.get("custom_excerpt"),
        "meta_title": post.get("meta_title"),
        "meta_description": post.get("meta_description"),
        "og_title": post.get("og_title"),
        "og_description": post.get("og_description"),
        "twitter_title": post.get("twitter_title"),
        "twitter_description": post.get("twitter_description"),
        "tags": tags,
        "feature_image": post.get("feature_image"),
        "feature_image_alt": post.get("feature_image_alt"),
        "feature_image_caption": post.get("feature_image_caption"),
    }

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
    out_path.write_text(json.dumps(patch, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ctx["out"].print(
        {
            **base,
            "refused": False,
            "out": args.out,
            "note": "Edit fields as needed, then apply with: ghost-api-tool post patch --file ... (and --apply)",
            "tag_count": len(tags),
        }
    )
    return 0


def cmd_post_convert_from_html(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    base = {"apply": bool(ctx["apply"]), "selector": {"slug": args.slug} if args.slug else {"id": args.id}}
    status = before.get("status")

    if args.require_current and status != args.require_current:
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={status}"],
            }
        )
        return 0

    html = before.get("html") or ""
    if not html:
        ctx["out"].print({**base, "refused": True, "reasons": ["Missing html field; cannot convert"]})
        return 0

    lexical_obj, _ = parse_lexical_field(before.get("lexical"))
    if lexical_obj is not None:
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "changed": False,
                "note": "Post already has a Lexical field; no conversion needed",
            }
        )
        return 0

    from ..content_mobiledoc import parse_mobiledoc_field

    mob_obj, _mob_reasons = parse_mobiledoc_field(before.get("mobiledoc"))
    if mob_obj is not None:
        if not bool(args.from_mobiledoc):
            ctx["out"].print(
                {
                    **base,
                    "refused": True,
                    "reasons": [
                        "Post uses mobiledoc. Refused by default.",
                        "If you want to convert it to Lexical, re-run with --from-mobiledoc.",
                    ],
                }
            )
            return 0

    if ctx["apply"] and bool(mob_obj is not None) and bool(args.from_mobiledoc) and not bool(ctx.get("yes")):
        ctx["out"].print(
            {
                **base,
                "refused": True,
                "reasons": ["Refused: converting mobiledoc posts requires --yes (bulk/format-changing write)"],
                "post_id": before.get("id"),
                "status": status,
            }
        )
        return 0

    if ctx["apply"]:
        reasons = _refuse_on_non_draft(status, allow_published=bool(args.allow_published))
        if reasons:
            ctx["out"].print({**base, "refused": True, "reasons": reasons})
            return 0

    img_count = html.lower().count("<img")
    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.convert_from_html"
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.convert_from_html",
                before=before,
                after=None,
                meta={"stage": "before", "correlation_id": correlation_id, "selector": {"slug": args.slug} if args.slug else {"id": args.id}},
            )
        ctx["out"].print(
            {
                **base,
                "refused": False,
                "changed": True,
                "from_mobiledoc": bool(mob_obj is not None),
                "would_update": {"source": "html", "html_len": len(html), "img_count": img_count},
                "note": "Apply will send the current html back via source=html to generate a Lexical document",
            }
        )
        return 0

    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError("Post is missing updated_at; cannot safely update")

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.convert_from_html"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.convert_from_html",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": {"slug": args.slug} if args.slug else {"id": args.id}},
        )
    after: dict[str, Any] | None = None
    after_obj: Any | None = None
    lexical_image_count: int | None = None
    fallback_used = False
    temp_post_id: str | None = None
    temp_post_slug: str | None = None
    try:
        # Attempt 1: in-place source=html update.
        api.posts_update(str(before["id"]), {"posts": [{"updated_at": updated_at, "html": html}]}, params={"source": "html"})
        after = resolve_post(api, slug=None, post_id=str(before["id"]), formats="html,lexical,mobiledoc")
        after_obj, reasons = parse_lexical_field(after.get("lexical"))

        # Fallback: some Mobiledoc posts won't generate Lexical on PUT + source=html.
        # For those, create a temporary Lexical post from the same HTML, then copy its Lexical field back.
        if after_obj is None and mob_obj is not None and bool(args.from_mobiledoc):
            fallback_used = True
            ts = int(time.time() * 1000)
            base_slug = str(before.get("slug") or "post")
            temp_post_slug = f"{base_slug}-lexical-tmp-{ts}"
            temp_title = f"TEMP CONVERT: {before.get('title') or base_slug}"

            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=f"slug:{temp_post_slug}",
                    slug=temp_post_slug,
                    action="post.convert_from_html.temp_create",
                    before=None,
                    after=None,
                    meta={"stage": "before", "correlation_id": correlation_id, "source_post_id": str(before.get("id"))},
                )

            res = api.posts_create(
                {"posts": [{"title": temp_title, "slug": temp_post_slug, "status": "draft", "html": html}]},
                params={"source": "html"},
            )
            created = (res.get("posts") or [{}])[0]
            temp_post_id = created.get("id")
            if not isinstance(temp_post_id, str) or not temp_post_id:
                raise RuntimeError(f"Unexpected temp create response (missing id): {res}")

            temp_verified = resolve_post(api, slug=None, post_id=temp_post_id, formats="lexical")
            temp_lexical = temp_verified.get("lexical")
            temp_obj, temp_reasons = parse_lexical_field(temp_lexical)
            if temp_obj is None:
                raise RuntimeError(f"Temp post did not produce a parseable Lexical field: {temp_reasons}")

            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=str(temp_post_id),
                    slug=temp_post_slug,
                    action="post.convert_from_html.temp_create",
                    before=None,
                    after=temp_verified,
                    meta={"stage": "after", "correlation_id": correlation_id, "verified": True},
                )

            # Copy Lexical back onto the original post.
            api.posts_update(str(before["id"]), {"posts": [{"updated_at": updated_at, "lexical": temp_lexical}]})
            after = resolve_post(api, slug=None, post_id=str(before["id"]), formats="html,lexical,mobiledoc")
            after_obj, reasons = parse_lexical_field(after.get("lexical"))
            if after_obj is None:
                raise RuntimeError(f"Fallback conversion did not produce a parseable Lexical field: {reasons}")

            # Delete the temp post (keep the original URL/id intact).
            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=str(temp_post_id),
                    slug=temp_post_slug,
                    action="post.convert_from_html.temp_delete",
                    before=temp_verified,
                    after=None,
                    meta={"stage": "before", "correlation_id": correlation_id},
                )
            resp = api.posts_delete(str(temp_post_id))
            if resp.status not in (200, 204):
                raise RuntimeError(f"Unexpected temp delete response: HTTP {resp.status}")
            try:
                _ = resolve_post(api, slug=None, post_id=str(temp_post_id))
            except RuntimeError as e:
                msg = str(e)
                if "HTTP 404" not in msg and "Post not found" not in msg:
                    raise
            else:
                raise RuntimeError("Verification failed: temp post still exists after delete")
            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=str(temp_post_id),
                    slug=temp_post_slug,
                    action="post.convert_from_html.temp_delete",
                    before=None,
                    after=None,
                    meta={"stage": "after", "correlation_id": correlation_id, "verified": True},
                )

        if after_obj is None:
            raise RuntimeError(f"Conversion did not produce a parseable Lexical field: {reasons}")

        lexical_image_count = len(list_lexical_images(after_obj))
    except Exception as e:
        cleanup = {"attempted": False, "deleted": False, "error": None}
        if temp_post_id is not None:
            cleanup["attempted"] = True
            try:
                # Best-effort cleanup if the fallback created a temp post but failed before deleting it.
                resp = api.posts_delete(str(temp_post_id))
                if resp.status not in (200, 204):
                    raise RuntimeError(f"Unexpected temp delete response: HTTP {resp.status}")
                try:
                    _ = resolve_post(api, slug=None, post_id=str(temp_post_id))
                except RuntimeError as e2:
                    msg = str(e2)
                    if "HTTP 404" not in msg and "Post not found" not in msg:
                        raise
                else:
                    raise RuntimeError("Verification failed: temp post still exists after delete")
                cleanup["deleted"] = True
            except Exception as e3:
                cleanup["error"] = str(e3)
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.convert_from_html",
                before=None,
                after=after,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "error": str(e),
                    "fallback_used": fallback_used,
                    "temp_post_id": temp_post_id,
                    "temp_post_slug": temp_post_slug,
                    "temp_cleanup": cleanup,
                },
            )
        raise

    ctx["audit"].write(
        "post.convert_from_html",
        {
            "apply": True,
            "selector": {"slug": args.slug} if args.slug else {"id": args.id},
            "post_id": str(before["id"]),
            "html_len": len(html),
            "html_img_count": img_count,
            "lexical_image_count": lexical_image_count,
            "fallback_used": fallback_used,
            "temp_post_id": temp_post_id,
        },
    )
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.convert_from_html",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                "html_len": len(html),
                "html_img_count": img_count,
                "lexical_image_count": lexical_image_count,
                "fallback_used": fallback_used,
                "temp_post_id": temp_post_id,
            },
        )
    ctx["out"].print(
        {
            **base,
            "refused": False,
            "changed": True,
            "post_id": str(before["id"]),
            "html_img_count": img_count,
            "lexical_image_count": lexical_image_count,
            "fallback_used": fallback_used,
        }
    )
    return 0


def cmd_post_body_show_images(args, ctx) -> int:
    api = get_api(ctx)
    post = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical")
    html = post.get("html") or ""
    from ..content_html_card import extract_html_card

    card = extract_html_card(html)
    if card is None:
        ctx["out"].print({"refused": True, "reasons": ["Not HTML-card mode"], "images": []})
        return 0
    imgs = list_images_in_html_card(card)
    ctx["out"].print({"refused": False, "images": imgs})
    return 0


def cmd_post_body_set_captions(args, ctx) -> int:
    api = get_api(ctx)
    with open(args.captions_file, encoding="utf-8") as f:
        mapping = json.load(f)
    if not isinstance(mapping, dict):
        raise RuntimeError("--captions-file must be a JSON object mapping src -> caption")
    captions_by_src = {str(k): str(v) for k, v in mapping.items()}

    before = resolve_post(api, slug=args.slug, post_id=args.id, formats="html,lexical,mobiledoc")
    html = before.get("html") or ""

    rep, new_html = set_figcaptions_by_src(
        html, captions_by_src=captions_by_src, include_diff=bool(args.diff)
    )
    if rep.refused:
        ctx["out"].print({"apply": ctx["apply"], "refused": True, "reasons": rep.reasons})
        return 0

    if new_html == html:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "matched": rep.matched_images, "updated": 0})
        return 0

    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.body.set_captions"
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.body.set_captions",
                before=before,
                after=None,
                meta={
                    "stage": "before",
                    "correlation_id": correlation_id,
                    "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                    "captions_file": args.captions_file,
                    "matched": rep.matched_images,
                    "updated": rep.updated_figcaptions,
                },
            )
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "matched": rep.matched_images,
                "updated": rep.updated_figcaptions,
                "reasons": rep.reasons,
                "diff": rep.diff,
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-post.body.set_captions"
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(before.get("slug") or ""),
            action="post.body.set_captions",
            before=before,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                "captions_file": args.captions_file,
                "matched": rep.matched_images,
                "updated": rep.updated_figcaptions,
            },
        )

    updated_at = before.get("updated_at")
    if not updated_at:
        raise RuntimeError("Post is missing updated_at; cannot safely update")

    try:
        # Write back using source=html; this relies on Ghost accepting ?source=html on PUT.
        api.posts_update(
            str(before["id"]),
            {"posts": [{"updated_at": updated_at, "html": new_html}]},
            params={"source": "html"},
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="post",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="post.body.set_captions",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    # Verify: re-fetch and ensure the transform is now a no-op (idempotent).
    after = resolve_post(api, slug=None, post_id=str(before["id"]), formats="html,lexical,mobiledoc")
    after_html = after.get("html") or ""
    vrep, vhtml = set_figcaptions_by_src(
        after_html,
        captions_by_src=captions_by_src,
        include_diff=True,
    )
    if vrep.refused:
        raise RuntimeError(f"Verification refused after update: {vrep.reasons}")
    if vhtml != after_html:
        raise RuntimeError(
            "Verification failed after update: re-running the same transform would still change the post.\n"
            + (vrep.diff or "")
        )

    ctx["audit"].write(
        "post.body.set_captions",
        {
            "apply": True,
            "selector": {"slug": args.slug} if args.slug else {"id": args.id},
            "post_id": str(before["id"]),
            "matched": rep.matched_images,
            "updated": rep.updated_figcaptions,
        },
    )
    if backup is not None:
        backup.write_before_after(
            kind="post",
            resource_id=str(before.get("id")),
            slug=str(after.get("slug") or before.get("slug") or ""),
            action="post.body.set_captions",
            before=None,
            after=after,
            meta={
                "stage": "after",
                "correlation_id": correlation_id,
                "verified": True,
                "selector": {"slug": args.slug} if args.slug else {"id": args.id},
                "captions_file": args.captions_file,
                "matched": rep.matched_images,
                "updated": rep.updated_figcaptions,
            },
        )
    ctx["out"].print(
        {
            "apply": True,
            "post_id": str(before["id"]),
            "matched": rep.matched_images,
            "updated": rep.updated_figcaptions,
        }
    )
    return 0
