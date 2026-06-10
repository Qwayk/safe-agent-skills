from __future__ import annotations

import json
import time
from typing import Any

from ..errors import ValidationError
from ..post_patch import apply_page_patch, resolve_page
from ..runtime import get_api


def add_page_commands(page_sub) -> None:
    page_get = page_sub.add_parser("get", help="Fetch page by slug or id")
    page_get.add_argument("--slug", default=None)
    page_get.add_argument("--id", default=None)
    page_get.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,lexical)")
    page_get.set_defaults(func=cmd_page_get)

    page_find = page_sub.add_parser("find", help="Browse pages with filter/limit/order")
    page_find.add_argument("--filter", default=None)
    page_find.add_argument("--limit", type=int, default=15)
    page_find.add_argument("--page", type=int, default=None)
    page_find.add_argument("--order", default=None)
    page_find.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,lexical)")
    page_find.set_defaults(func=cmd_page_find)

    page_set_status = page_sub.add_parser("set-status", help="Change page status (dry-run by default)")
    page_set_status.add_argument("--slug", default=None)
    page_set_status.add_argument("--id", default=None)
    page_set_status.add_argument("--to", required=True, help="draft|published|scheduled")
    page_set_status.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    page_set_status.add_argument("--published-at", default=None, help="ISO timestamp for scheduled pages")
    page_set_status.set_defaults(func=cmd_page_set_status)

    page_patch = page_sub.add_parser("patch", help="Patch page fields from a JSON file (dry-run by default)")
    page_patch.add_argument("--slug", default=None)
    page_patch.add_argument("--id", default=None)
    page_patch.add_argument("--file", required=True, help="JSON file with patch fields")
    page_patch.add_argument("--require-current", default=None)
    page_patch.add_argument("--source", default=None, help="Optional source param (advanced)")
    page_patch.set_defaults(func=cmd_page_patch)

    page_set_feature_image = page_sub.add_parser(
        "set-feature-image",
        help="Upload an image and set it as the page feature image (dry-run by default)",
    )
    page_set_feature_image.add_argument("--slug", default=None)
    page_set_feature_image.add_argument("--id", default=None)
    page_set_feature_image.add_argument("--file", required=True, help="Local image path")
    page_set_feature_image.add_argument("--upload-name", default=None, help="Optional uploaded filename")
    page_set_feature_image.add_argument("--alt", default=None, help="Optional alt text")
    page_set_feature_image.add_argument("--caption", default=None, help="Optional caption")
    page_set_feature_image.set_defaults(func=cmd_page_set_feature_image)

    page_create = page_sub.add_parser("create", help="Create a new page (dry-run by default)")
    page_create.add_argument("--title", required=True)
    page_create.add_argument("--slug", default=None)
    page_create.add_argument("--status", default="draft", help="draft|published")
    page_create.add_argument("--visibility", default="public", help="public|members|paid")
    page_create.add_argument("--html-file", default=None, help="Path to HTML file (use with --source html)")
    page_create.add_argument("--lexical-file", default=None, help="Path to Lexical JSON string file")
    page_create.add_argument("--source", default=None, help="Optional source param (e.g. html)")
    page_create.set_defaults(func=cmd_page_create)

    page_copy = page_sub.add_parser("copy", help="Copy a page (creates a new draft; dry-run by default)")
    page_copy.add_argument("--slug", default=None)
    page_copy.add_argument("--id", default=None)
    page_copy.set_defaults(func=cmd_page_copy)

    page_delete = page_sub.add_parser("delete", help="Delete a page (dry-run by default; apply requires --yes)")
    page_delete.add_argument("--slug", default=None)
    page_delete.add_argument("--id", default=None)
    page_delete.add_argument("--require-current", default=None, help="Refuse unless current status matches")
    page_delete.set_defaults(func=cmd_page_delete)

    page_sync_md = page_sub.add_parser(
        "sync-md",
        help="Create (or replace) a page from a Markdown file, converting to Lexical via source=html (dry-run by default)",
    )
    page_sync_md.add_argument("--slug", required=True)
    page_sync_md.add_argument("--title", required=True)
    page_sync_md.add_argument("--md-file", required=True, help="Path to Markdown file")
    page_sync_md.add_argument("--status", default="draft", help="draft|published")
    page_sync_md.add_argument("--visibility", default="public", help="public|members|paid")
    page_sync_md.add_argument(
        "--replace-existing",
        action="store_true",
        help="If a page already exists with this slug, delete it and recreate it",
    )
    page_sync_md.set_defaults(func=cmd_page_sync_md)


def cmd_page_get(args, ctx) -> int:
    api = get_api(ctx)
    page = resolve_page(api, slug=args.slug, page_id=args.id, formats=args.formats)
    ctx["out"].print(page)
    return 0


def cmd_page_find(args, ctx) -> int:
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
    res = api.pages_browse(params=params)
    ctx["out"].print(res)
    return 0


def cmd_page_copy(args, ctx) -> int:
    api = get_api(ctx)
    before = resolve_page(api, slug=args.slug, page_id=args.id, formats=None)
    page_id = before.get("id")
    if not isinstance(page_id, str) or not page_id.strip():
        raise RuntimeError("Page id not found")

    if not ctx["apply"]:
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-page.copy"
            backup.write_before_after(
                kind="page",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="page.copy",
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
                "copy": {"from_id": page_id, "from_slug": before.get("slug"), "from_title": before.get("title")},
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{page_id}-page.copy"
        backup.write_before_after(
            kind="page",
            resource_id=f"id:{page_id}",
            slug=str(before.get("slug") or ""),
            action="page.copy",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "from_id": page_id},
        )

    try:
        res = api.pages_copy(page_id)
        created = (res.get("pages") or [{}])[0] if isinstance(res, dict) else {}
        new_id = created.get("id") if isinstance(created, dict) else None
        if not isinstance(new_id, str) or not new_id.strip():
            raise RuntimeError(f"Unexpected copy response (missing id): {res}")
        if new_id == page_id:
            raise RuntimeError("Unexpected copy response: new_id is the same as from_id")

        verified = resolve_page(api, slug=None, page_id=new_id, formats=None)
        if verified.get("id") != new_id:
            raise RuntimeError(f"Verification failed: id mismatch (got={verified.get('id')!r})")
        if verified.get("status") != "draft":
            raise RuntimeError(f"Verification failed: expected status=draft (got={verified.get('status')!r})")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="page",
                resource_id=f"id:{page_id}",
                slug=str(before.get("slug") or ""),
                action="page.copy",
                before=None,
                after=None,
                meta={
                    "stage": "error",
                    "correlation_id": correlation_id,
                    "from_id": page_id,
                    "error": str(e),
                },
            )
        raise

    ctx["audit"].write("page.copy", {"apply": True, "from_id": page_id, "to_id": new_id, "status": verified.get("status")})
    if backup is not None:
        backup.write_before_after(
            kind="page",
            resource_id=f"id:{new_id}",
            slug=str(verified.get("slug") or ""),
            action="page.copy",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "from_id": page_id, "to_id": new_id, "verified": True},
        )

    ctx["out"].print({"ok": True, "from_id": page_id, "to_id": new_id, "status": verified.get("status")})
    return 0


def cmd_page_set_status(args, ctx) -> int:
    api = get_api(ctx)
    patch: dict[str, Any] = {"status": args.to}
    if args.to == "scheduled":
        if not args.published_at:
            raise RuntimeError("--published-at is required when --to scheduled")
        patch["published_at"] = args.published_at

    if ctx["apply"] and not ctx["yes"]:
        before = resolve_page(api, slug=args.slug, page_id=args.id, formats=None)
        ctx["out"].print(
            {
                "apply": True,
                "refused": True,
                "reasons": ["Refused: page set-status requires --yes"],
                "page_id": before.get("id"),
                "slug": before.get("slug"),
                "status": before.get("status"),
                "to": args.to,
            }
        )
        return 0

    plan = apply_page_patch(
        api,
        slug=args.slug,
        page_id=args.id,
        patch=patch,
        apply=bool(ctx["apply"]),
        require_current=args.require_current,
        snapshot=ctx.get("backup"),
        snapshot_action="page.set_status",
    )
    ctx["audit"].write(
        "page.set_status",
        {"apply": ctx["apply"], "selector": plan.selector, "page_id": plan.resource_id, "changes": plan.changes},
    )
    ctx["out"].print(
        {
            "apply": ctx["apply"],
            "refused": plan.refused,
            "reasons": plan.reasons,
            "page_id": plan.resource_id,
            "changes": plan.changes,
        }
    )
    return 0


def cmd_page_patch(args, ctx) -> int:
    api = get_api(ctx)
    with open(args.file, encoding="utf-8") as f:
        patch = json.load(f)
    if not isinstance(patch, dict):
        raise RuntimeError("Patch file must contain a JSON object of fields")

    plan = apply_page_patch(
        api,
        slug=args.slug,
        page_id=args.id,
        patch=patch,
        apply=bool(ctx["apply"]),
        require_current=args.require_current,
        source=args.source,
        snapshot=ctx.get("backup"),
        snapshot_action="page.patch",
        snapshot_meta={"patch_file": args.file},
    )
    ctx["audit"].write(
        "page.patch",
        {"apply": ctx["apply"], "selector": plan.selector, "page_id": plan.resource_id, "changes": plan.changes},
    )
    ctx["out"].print(
        {
            "apply": ctx["apply"],
            "refused": plan.refused,
            "reasons": plan.reasons,
            "page_id": plan.resource_id,
            "changes": plan.changes,
        }
    )
    return 0


def cmd_page_set_feature_image(args, ctx) -> int:
    api = get_api(ctx)

    if not ctx["apply"]:
        before = resolve_page(api, slug=args.slug, page_id=args.id, formats=None)
        backup = ctx.get("backup")
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{before.get('id')}-page.set_feature_image"
            backup.write_before_after(
                kind="page",
                resource_id=str(before.get("id")),
                slug=str(before.get("slug") or ""),
                action="page.set_feature_image",
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

    if bool(args.slug) == bool(args.id):
        raise ValidationError("Provide exactly one selector: --slug or --id")

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

    plan = apply_page_patch(
        api,
        slug=args.slug,
        page_id=args.id,
        patch=patch,
        apply=True,
        snapshot=ctx.get("backup"),
        snapshot_action="page.set_feature_image",
        snapshot_meta={"feature_image": url, "upload": {"file": args.file, "upload_name": args.upload_name}},
    )
    ctx["out"].print({"apply": True, "page_id": plan.resource_id, "feature_image": url})
    return 0


def cmd_page_create(args, ctx) -> int:
    api = get_api(ctx)
    if bool(args.html_file) == bool(args.lexical_file):
        raise ValidationError("Provide exactly one of: --html-file or --lexical-file")

    if args.slug:
        try:
            _ = resolve_page(api, slug=args.slug, page_id=None)
            ctx["out"].print(
                {
                    "apply": ctx["apply"],
                    "refused": True,
                    "reasons": [f"Page already exists with slug={args.slug}. Delete it first or use patch."],
                }
            )
            return 0
        except RuntimeError as e:
            msg = str(e)
            if "HTTP 404" not in msg and "Page not found" not in msg:
                raise

    page: dict[str, Any] = {
        "title": args.title,
        "status": args.status,
        "visibility": args.visibility,
    }
    if args.slug:
        page["slug"] = args.slug

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
    page[content_key] = content_value

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
        correlation_id = f"{int(time.time() * 1000)}-slug-{args.slug or 'auto'}-page.create"
        backup.write_before_after(
            kind="page",
            resource_id=f"slug:{args.slug}" if args.slug else "new",
            slug=str(args.slug or ""),
            action="page.create",
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
        res = api.pages_create({"pages": [page]}, params=params if params else None)
        created = (res.get("pages") or [{}])[0]
        page_id = created.get("id")
        if not isinstance(page_id, str) or not page_id:
            raise RuntimeError(f"Unexpected create response (missing id): {res}")

        verified = resolve_page(api, slug=None, page_id=page_id, formats="html,lexical")
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
                kind="page",
                resource_id=f"slug:{args.slug}" if args.slug else "new",
                slug=str(args.slug or ""),
                action="page.create",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    ctx["audit"].write(
        "page.create",
        {"apply": True, "page_id": page_id, "slug": verified.get("slug"), "status": verified.get("status")},
    )
    if backup is not None:
        backup.write_before_after(
            kind="page",
            resource_id=str(page_id),
            slug=str(verified.get("slug") or args.slug or ""),
            action="page.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True},
        )
    ctx["out"].print({"apply": True, "page_id": page_id, "slug": verified.get("slug"), "status": verified.get("status")})
    return 0


def cmd_page_delete(args, ctx) -> int:
    api = get_api(ctx)
    page = resolve_page(api, slug=args.slug, page_id=args.id)

    if args.require_current and page.get("status") != args.require_current:
        ctx["out"].print(
            {
                "apply": ctx["apply"],
                "refused": True,
                "reasons": [f"Refused: require-current={args.require_current} but status={page.get('status')}"],
                "page_id": page.get("id"),
                "slug": page.get("slug"),
            }
        )
        return 0

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "reasons": [],
                "page_id": page.get("id"),
                "slug": page.get("slug"),
                "status": page.get("status"),
                "title": page.get("title"),
            }
        )
        return 0

    if not ctx["yes"]:
        ctx["out"].print(
            {
                "apply": True,
                "refused": True,
                "reasons": ["Refused: delete requires --yes"],
                "page_id": page.get("id"),
                "slug": page.get("slug"),
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{page.get('id')}-page.delete"
        backup.write_before_after(
            kind="page",
            resource_id=str(page.get("id")),
            slug=str(page.get("slug") or ""),
            action="page.delete",
            before=page,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "selector": {"slug": args.slug} if args.slug else {"id": args.id}},
        )

    try:
        resp = api.pages_delete(str(page.get("id")))
        if resp.status != 204:
            raise RuntimeError(f"Unexpected delete status: {resp.status}")

        # Verify: expect 404 when re-fetching by id.
        try:
            _ = resolve_page(api, slug=None, page_id=str(page.get("id")))
        except RuntimeError as e:
            msg = str(e)
            if "HTTP 404" not in msg and "Page not found" not in msg:
                raise
        else:
            raise RuntimeError("Verification failed: page still exists after delete")
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="page",
                resource_id=str(page.get("id")),
                slug=str(page.get("slug") or ""),
                action="page.delete",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    if backup is not None:
        backup.write_before_after(
            kind="page",
            resource_id=str(page.get("id")),
            slug=str(page.get("slug") or ""),
            action="page.delete",
            before=None,
            after=None,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "deleted": {"page_id": page.get("id"), "slug": page.get("slug")}},
        )
    ctx["audit"].write("page.delete", {"apply": True, "page_id": page.get("id"), "slug": page.get("slug")})
    ctx["out"].print({"apply": True, "page_id": page.get("id"), "slug": page.get("slug")})
    return 0


def cmd_page_sync_md(args, ctx) -> int:
    api = get_api(ctx)

    with open(args.md_file, encoding="utf-8") as f:
        md_text = f.read()
    from ..markdown_render import render_markdown

    rendered = render_markdown(md_text, strip_h1=True)

    existing = None
    try:
        existing = resolve_page(api, slug=args.slug, page_id=None, formats="html,lexical,mobiledoc")
    except RuntimeError as e:
        msg = str(e)
        if "HTTP 404" not in msg and "Page not found" not in msg:
            raise

    if existing and not args.replace_existing:
        ctx["out"].print(
            {
                "apply": ctx["apply"],
                "refused": True,
                "reasons": [f"Page already exists with slug={args.slug}. Use --replace-existing to recreate it."],
                "existing_page_id": existing.get("id"),
            }
        )
        return 0

    plan_actions: list[dict[str, Any]] = []
    if existing:
        plan_actions.append({"action": "delete", "page_id": existing.get("id"), "slug": existing.get("slug")})
    plan_actions.append(
        {
            "action": "create",
            "title": args.title,
            "slug": args.slug,
            "status": args.status,
            "visibility": args.visibility,
            "source": "html",
            "html_chars": len(rendered.html),
            "dropped_h1": rendered.dropped_h1,
        }
    )

    if not ctx["apply"]:
        if existing:
            backup = ctx.get("backup")
            if backup is not None:
                correlation_id = f"{int(time.time() * 1000)}-{existing.get('id')}-page.sync_md"
                backup.write_before_after(
                    kind="page",
                    resource_id=str(existing.get("id")),
                    slug=str(existing.get("slug") or args.slug),
                    action="page.sync_md",
                    before=existing,
                    after=None,
                    meta={"stage": "before", "correlation_id": correlation_id, "replace_existing": True, "md_file": args.md_file},
                )
        ctx["out"].print({"apply": False, "refused": False, "reasons": [], "actions": plan_actions})
        return 0

    if existing:
        if not ctx["yes"]:
            ctx["out"].print(
                {
                    "apply": True,
                    "refused": True,
                    "reasons": ["Refused: --replace-existing delete requires --yes"],
                    "actions": plan_actions,
                }
            )
            return 0
        backup = ctx.get("backup")
        correlation_id = None
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-{existing.get('id')}-page.sync_md"
            backup.write_before_after(
                kind="page",
                resource_id=str(existing.get("id")),
                slug=str(existing.get("slug") or args.slug),
                action="page.sync_md",
                before=existing,
                after=None,
                meta={"stage": "before", "correlation_id": correlation_id, "replace_existing": True, "md_file": args.md_file},
            )
        resp = api.pages_delete(str(existing.get("id")))
        if resp.status != 204:
            raise RuntimeError(f"Unexpected delete status: {resp.status}")
    else:
        backup = ctx.get("backup")
        correlation_id = None
        if backup is not None:
            correlation_id = f"{int(time.time() * 1000)}-slug-{args.slug}-page.sync_md"
            backup.write_before_after(
                kind="page",
                resource_id=f"slug:{args.slug}",
                slug=str(args.slug),
                action="page.sync_md",
                before=None,
                after=None,
                meta={"stage": "before", "correlation_id": correlation_id, "replace_existing": False, "md_file": args.md_file},
            )

    try:
        res = api.pages_create(
            {
                "pages": [
                    {
                        "title": args.title,
                        "slug": args.slug,
                        "status": args.status,
                        "visibility": args.visibility,
                        "html": rendered.html,
                    }
                ]
            },
            params={"source": "html"},
        )
    except Exception as e:
        backup = ctx.get("backup")
        if backup is not None:
            backup.write_before_after(
                kind="page",
                resource_id=f"slug:{args.slug}",
                slug=str(args.slug),
                action="page.sync_md",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e), "md_file": args.md_file},
            )
        raise
    created = (res.get("pages") or [{}])[0]
    page_id = created.get("id")
    if not isinstance(page_id, str) or not page_id:
        raise RuntimeError(f"Unexpected create response (missing id): {res}")

    verified = resolve_page(api, slug=None, page_id=page_id, formats="html,lexical,mobiledoc")
    if verified.get("title") != args.title:
        raise RuntimeError(f"Verification failed: title mismatch (got={verified.get('title')!r})")
    if verified.get("slug") != args.slug:
        raise RuntimeError(f"Verification failed: slug mismatch (got={verified.get('slug')!r})")
    if verified.get("status") != args.status:
        raise RuntimeError(f"Verification failed: status mismatch (got={verified.get('status')!r})")
    if not verified.get("lexical"):
        raise RuntimeError("Verification failed: lexical content is empty after create")

    ctx["audit"].write(
        "page.sync_md",
        {"apply": True, "page_id": page_id, "slug": verified.get("slug"), "status": verified.get("status")},
    )
    backup = ctx.get("backup")
    if backup is not None:
        backup.write_before_after(
            kind="page",
            resource_id=str(page_id),
            slug=str(verified.get("slug") or args.slug),
            action="page.sync_md",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "md_file": args.md_file, "replace_existing": bool(args.replace_existing)},
        )
    ctx["out"].print({"apply": True, "page_id": page_id, "slug": verified.get("slug"), "status": verified.get("status")})
    return 0
