from __future__ import annotations

import re
import time
from typing import Any

from ..errors import ValidationError
from ..runtime import get_api


def add_tag_commands(tag_sub) -> None:
    tag_list = tag_sub.add_parser("list", help="List tags (read-only)")
    tag_list.add_argument(
        "--visibility",
        choices=("all", "public", "internal"),
        default="all",
        help="Filter tags by visibility (default: all)",
    )
    tag_list.add_argument(
        "--include-count",
        action="store_true",
        help="Include count.posts (requires include=count.posts)",
    )
    tag_list.add_argument("--filter", default=None, help="Raw API filter (advanced)")
    tag_list.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    tag_list.add_argument("--order", default=None, help='Order (e.g. "name asc" or "count.posts desc")')
    tag_list.add_argument("--limit", type=int, default=100, help="Page size (default: 100)")
    tag_list.add_argument("--page", type=int, default=None, help="Page number (default: fetch all pages)")
    tag_list.set_defaults(func=cmd_tag_list)

    tag_audit = tag_sub.add_parser("audit", help="Audit tags for cleanup candidates (read-only)")
    tag_audit.add_argument(
        "--exclude-empty",
        action="store_true",
        help="Exclude 0-post tags from duplicate grouping (default: include them)",
    )
    tag_audit.set_defaults(func=cmd_tag_audit)

    tag_create = tag_sub.add_parser("create", help="Create a tag (dry-run by default)")
    tag_create.add_argument("--name", required=True, help="Tag name")
    tag_create.add_argument("--slug", default=None, help="Optional slug (Ghost may ignore/override)")
    tag_create.add_argument("--description", default=None)
    tag_create.add_argument("--visibility", choices=("public", "internal"), default="public")
    tag_create.add_argument("--meta-title", default=None)
    tag_create.add_argument("--meta-description", default=None)
    tag_create.add_argument("--feature-image", default=None, help="URL for tag feature image")
    tag_create.set_defaults(func=cmd_tag_create)

    tag_update = tag_sub.add_parser("update", help="Update a tag (dry-run by default)")
    tag_update.add_argument("--id", required=True, help="Tag id")
    tag_update.add_argument("--name", default=None)
    tag_update.add_argument("--slug", default=None, help="Optional slug (Ghost may ignore/override)")
    tag_update.add_argument("--description", default=None)
    tag_update.add_argument("--visibility", choices=("public", "internal"), default=None)
    tag_update.add_argument("--meta-title", default=None)
    tag_update.add_argument("--meta-description", default=None)
    tag_update.add_argument("--feature-image", default=None, help="URL for tag feature image")
    tag_update.set_defaults(func=cmd_tag_update)

    tag_delete = tag_sub.add_parser("delete", help="Delete a single tag by id (dry-run by default; apply requires --yes)")
    tag_delete.add_argument("--id", required=True, help="Tag id")
    tag_delete.set_defaults(func=cmd_tag_delete)

    tag_delete_zero = tag_sub.add_parser(
        "delete-zero",
        help="Delete all tags with count.posts=0 (dry-run by default). Requires --apply and --yes.",
    )
    tag_delete_zero.add_argument(
        "--visibility",
        choices=("all", "public", "internal"),
        default="all",
        help="Filter tags by visibility (default: all)",
    )
    tag_delete_zero.add_argument("--limit", type=int, default=None, help="Safety cap on deletions")
    tag_delete_zero.set_defaults(func=cmd_tag_delete_zero)

    tag_merge = tag_sub.add_parser(
        "merge",
        help="Replace one tag with another on all matching posts (dry-run by default). Requires --apply and --yes.",
    )
    tag_merge.add_argument("--from-slug", required=True, help="Source tag slug to remove from posts")
    tag_merge.add_argument("--to-slug", required=True, help="Destination tag slug to add to posts")
    tag_merge.add_argument(
        "--delete-from-tag",
        action="store_true",
        help="After updating posts, delete the source tag (destructive; still requires --yes).",
    )
    tag_merge.add_argument("--limit", type=int, default=None, help="Safety cap on number of posts to update")
    tag_merge.set_defaults(func=cmd_tag_merge)


def _tags_count_posts(tag: dict[str, Any]) -> int | None:
    count = tag.get("count")
    if not isinstance(count, dict):
        return None
    posts = count.get("posts")
    if isinstance(posts, int):
        return posts
    return None


def _normalize_tag_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


def _browse_all(api, *, params: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    tags: list[dict[str, Any]] = []
    meta: dict[str, Any] | None = None

    page = 1
    limit = int(params.get("limit") or 100)
    while True:
        res = api.tags_browse(params={**params, "page": page, "limit": limit})
        batch = res.get("tags")
        if not isinstance(batch, list):
            raise RuntimeError(f"Unexpected response (missing tags list): {res}")
        for t in batch:
            if isinstance(t, dict):
                tags.append(t)
        meta = res.get("meta") if isinstance(res.get("meta"), dict) else meta
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        next_page = pagination.get("next") if isinstance(pagination, dict) else None
        if not next_page:
            break
        page = int(next_page)
    return tags, meta


def _visibility_to_filter(visibility: str) -> str | None:
    if visibility == "public":
        return "visibility:public"
    if visibility == "internal":
        return "visibility:internal"
    return None


def _is_http_404(err: Exception) -> bool:
    msg = str(err)
    return "HTTP 404" in msg


def _verify_deleted(api, tag_id: str) -> None:
    try:
        _ = api.tags_read_by_id(tag_id)
    except RuntimeError as e:
        if _is_http_404(e):
            return
        raise
    raise RuntimeError(f"Verification failed: tag still exists after delete (id={tag_id})")


def _extract_tag_from_read(obj: dict[str, Any], *, tag_id: str) -> dict[str, Any]:
    tags = obj.get("tags") or []
    if not isinstance(tags, list) or not tags or not isinstance(tags[0], dict):
        raise RuntimeError(f"Tag not found: {tag_id}")
    return tags[0]


def _build_tag_patch(args) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    if getattr(args, "name", None) is not None:
        patch["name"] = args.name
    if getattr(args, "slug", None) is not None:
        patch["slug"] = args.slug
    if getattr(args, "description", None) is not None:
        patch["description"] = args.description
    if getattr(args, "visibility", None) is not None:
        patch["visibility"] = args.visibility
    if getattr(args, "meta_title", None) is not None:
        patch["meta_title"] = args.meta_title
    if getattr(args, "meta_description", None) is not None:
        patch["meta_description"] = args.meta_description
    if getattr(args, "feature_image", None) is not None:
        patch["feature_image"] = args.feature_image
    return patch


def _verify_requested_fields(*, verified_tag: dict[str, Any], requested: dict[str, Any]) -> None:
    for key, value in requested.items():
        # Ghost can canonicalize slugs; skip strict verification here.
        if key == "slug":
            continue
        if verified_tag.get(key) != value:
            raise RuntimeError(f"Verification failed: {key} mismatch")


def cmd_tag_create(args, ctx) -> int:
    tag: dict[str, Any] = {
        "name": args.name,
        "visibility": args.visibility,
    }
    if args.slug is not None:
        tag["slug"] = args.slug
    if args.description is not None:
        tag["description"] = args.description
    if args.meta_title is not None:
        tag["meta_title"] = args.meta_title
    if args.meta_description is not None:
        tag["meta_description"] = args.meta_description
    if args.feature_image is not None:
        tag["feature_image"] = args.feature_image

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "create": tag})
        return 0

    api = get_api(ctx)
    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-tag.create"
        backup.write_before_after(
            kind="tag",
            resource_id=f"name:{args.name}",
            slug=str(args.slug or ""),
            action="tag.create",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "create": {"name": args.name}},
        )

    res = api.tags_create({"tags": [tag]})
    created = _extract_tag_from_read(res, tag_id="(created)")
    tag_id = created.get("id") if isinstance(created.get("id"), str) else None
    verified = api.tags_read_by_id(tag_id) if isinstance(tag_id, str) and tag_id else res

    v_tag = _extract_tag_from_read(verified, tag_id=str(tag_id or "(created)"))
    _verify_requested_fields(verified_tag=v_tag, requested=tag)

    ctx["audit"].write("tag.create", {"apply": True, "name": args.name})
    if backup is not None:
        backup.write_before_after(
            kind="tag",
            resource_id=f"id:{tag_id}" if isinstance(tag_id, str) else f"name:{args.name}",
            slug=str(v_tag.get("slug") or args.slug or ""),
            action="tag.create",
            before=None,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id},
        )

    ctx["out"].print({"ok": True, "tag_id": tag_id, "created": {"name": args.name}})
    return 0


def cmd_tag_update(args, ctx) -> int:
    api = get_api(ctx)
    current = api.tags_read_by_id(args.id)
    cur = _extract_tag_from_read(current, tag_id=args.id)

    patch = _build_tag_patch(args)
    if not patch:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "tag_id": args.id, "planned": {"fields": sorted(patch.keys())}})
        return 0

    payload = {"tags": [{**patch, "id": args.id, "updated_at": cur.get("updated_at")}]}

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-id-{args.id}-tag.update"
        backup.write_before_after(
            kind="tag",
            resource_id=f"id:{args.id}",
            slug=str(cur.get("slug") or ""),
            action="tag.update",
            before=current,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    _ = api.tags_update(args.id, payload)
    verified = api.tags_read_by_id(args.id)
    v_tag = _extract_tag_from_read(verified, tag_id=args.id)
    _verify_requested_fields(verified_tag=v_tag, requested=patch)

    ctx["audit"].write("tag.update", {"apply": True, "tag_id": args.id, "fields": sorted(patch.keys())})
    if backup is not None:
        backup.write_before_after(
            kind="tag",
            resource_id=f"id:{args.id}",
            slug=str(v_tag.get("slug") or ""),
            action="tag.update",
            before=current,
            after=verified,
            meta={"stage": "after", "correlation_id": correlation_id, "patch_fields": sorted(patch.keys())},
        )

    ctx["out"].print({"ok": True, "tag_id": args.id, "updated_fields": sorted(patch.keys())})
    return 0


def _merge_tag_refs(
    tags: list[dict[str, Any]],
    *,
    from_id: str,
    to_id: str,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Returns (new_tags, changed).

    - Removes tag with id=from_id.
    - Ensures tag with id=to_id exists.
    - Preserves order as much as possible: if from_id existed, replace its position with to_id (unless to_id already exists).
    """
    if not from_id or not to_id:
        return tags, False

    ids = [t.get("id") for t in tags if isinstance(t, dict)]
    has_from = from_id in ids
    has_to = to_id in ids
    if not has_from and has_to:
        return tags, False
    if not has_from and not has_to:
        return tags, False

    out: list[dict[str, Any]] = []
    changed = False
    replaced_to = False
    for t in tags:
        if not isinstance(t, dict):
            continue
        tid = t.get("id")
        if tid == from_id:
            changed = True
            if not has_to and not replaced_to:
                out.append({"id": to_id})
                replaced_to = True
            continue
        if tid == to_id:
            out.append({"id": to_id})
            continue
        if isinstance(tid, str) and tid.strip():
            out.append({"id": tid})

    if not has_to and not replaced_to:
        out.append({"id": to_id})
        changed = True

    # Dedupe by id while preserving order
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for t in out:
        tid = t.get("id")
        if not isinstance(tid, str) or not tid.strip():
            continue
        if tid in seen:
            changed = True
            continue
        seen.add(tid)
        deduped.append({"id": tid})

    if not changed and deduped != tags:
        changed = True
    return deduped, changed


def cmd_tag_list(args, ctx) -> int:
    api = get_api(ctx)
    params: dict[str, Any] = {"limit": args.limit}

    if args.include_count:
        params["include"] = "count.posts"
    if args.fields:
        params["fields"] = args.fields
    if args.order:
        params["order"] = args.order

    filters: list[str] = []
    vis_filter = _visibility_to_filter(args.visibility)
    if vis_filter:
        filters.append(vis_filter)
    if args.filter:
        filters.append(str(args.filter))
    if filters:
        params["filter"] = "+".join(filters)

    if args.page is not None:
        params["page"] = args.page
        res = api.tags_browse(params=params)
        ctx["out"].print(res)
        return 0

    tags, meta = _browse_all(api, params=params)
    ctx["out"].print(
        {
            "tags": tags,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(tags)},
        }
    )
    return 0


def cmd_tag_audit(args, ctx) -> int:
    api = get_api(ctx)
    tags, meta = _browse_all(
        api,
        params={
            "limit": 100,
            "include": "count.posts",
            "order": "name asc",
        },
    )

    public_tags = [t for t in tags if t.get("visibility") == "public"]
    internal_tags = [t for t in tags if t.get("visibility") == "internal"]

    zero_post_tags: list[dict[str, Any]] = []
    for t in tags:
        posts = _tags_count_posts(t)
        if posts == 0:
            zero_post_tags.append(
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "slug": t.get("slug"),
                    "visibility": t.get("visibility"),
                }
            )

    by_name: dict[str, list[dict[str, Any]]] = {}
    for t in tags:
        name = t.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        norm = _normalize_tag_name(name)
        by_name.setdefault(norm, []).append(t)

    dup_groups: list[dict[str, Any]] = []
    for norm, group in by_name.items():
        if len(group) < 2:
            continue
        if args.exclude_empty:
            group = [t for t in group if _tags_count_posts(t) != 0]
        if len(group) < 2:
            continue
        group_sorted = sorted(
            group,
            key=lambda t: (
                0 if t.get("visibility") == "public" else 1,
                -(int(_tags_count_posts(t) or 0)),
                str(t.get("slug") or ""),
            ),
        )
        display_name = next((t.get("name") for t in group_sorted if isinstance(t.get("name"), str)), norm)
        dup_groups.append(
            {
                "name": display_name,
                "normalized": norm,
                "tags": [
                    {
                        "id": t.get("id"),
                        "slug": t.get("slug"),
                        "visibility": t.get("visibility"),
                        "count_posts": _tags_count_posts(t),
                    }
                    for t in group_sorted
                ],
            }
        )

    internal_suspects: list[dict[str, Any]] = []
    for t in internal_tags:
        name = t.get("name")
        if not isinstance(name, str):
            continue
        if name.startswith("#Import") or name.startswith("#api-tool-") or name.startswith("#API"):
            internal_suspects.append(
                {
                    "id": t.get("id"),
                    "name": name,
                    "slug": t.get("slug"),
                    "count_posts": _tags_count_posts(t),
                }
            )

    ctx["out"].print(
        {
            "summary": {
                "total": len(tags),
                "public": len(public_tags),
                "internal": len(internal_tags),
                "zero_post": len(zero_post_tags),
                "duplicate_name_groups": len(dup_groups),
            },
            "candidates": {
                "zero_post_tags": zero_post_tags,
                "duplicate_name_groups": dup_groups,
                "internal_suspects": internal_suspects,
            },
            "meta": meta,
        }
    )
    return 0


def cmd_tag_delete(args, ctx) -> int:
    api = get_api(ctx)
    tag_id = str(args.id)

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "delete": {"id": tag_id}})
        return 0

    if not ctx["yes"]:
        ctx["out"].print({"apply": True, "refused": True, "reasons": ["Refused: delete requires --yes"], "delete": {"id": tag_id}})
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    before = api.tags_read_by_id(tag_id)
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-{tag_id}-tag.delete"
        backup.write_before_after(
            kind="tag",
            resource_id=tag_id,
            slug=None,
            action="tag.delete",
            before=before,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "id": tag_id},
        )

    try:
        resp = api.tags_delete(tag_id)
        if resp.status not in (200, 204):
            raise RuntimeError(f"Unexpected delete response: HTTP {resp.status}")
        _verify_deleted(api, tag_id)
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="tag",
                resource_id=tag_id,
                slug=None,
                action="tag.delete",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    if backup is not None:
        backup.write_before_after(
            kind="tag",
            resource_id=tag_id,
            slug=None,
            action="tag.delete",
            before=None,
            after=None,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "deleted": {"id": tag_id}},
        )
    ctx["audit"].write("tag.delete", {"apply": True, "id": tag_id})
    ctx["out"].print({"apply": True, "deleted": {"id": tag_id}})
    return 0


def cmd_tag_delete_zero(args, ctx) -> int:
    api = get_api(ctx)

    params: dict[str, Any] = {"limit": 100, "include": "count.posts", "order": "name asc"}
    vis_filter = _visibility_to_filter(args.visibility)
    if vis_filter:
        params["filter"] = vis_filter

    tags, _meta = _browse_all(api, params=params)
    zero_tags = [t for t in tags if _tags_count_posts(t) == 0]
    delete_ids: list[str] = []
    for t in zero_tags:
        tag_id = t.get("id")
        if isinstance(tag_id, str) and tag_id:
            delete_ids.append(tag_id)

    if args.limit is not None:
        delete_ids = delete_ids[: int(args.limit)]

    plan = {
        "apply": bool(ctx["apply"]),
        "selector": {"visibility": args.visibility},
        "candidates": len(zero_tags),
        "to_delete": len(delete_ids),
        "ids": delete_ids,
    }

    if not ctx["apply"]:
        ctx["out"].print(plan)
        return 0

    if not ctx["yes"]:
        ctx["out"].print({**plan, "refused": True, "reasons": ["Refused: bulk delete requires --yes"]})
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-tag.delete_zero"
        backup.write_before_after(
            kind="tag",
            resource_id="bulk",
            slug=None,
            action="tag.delete_zero",
            before={"plan": plan, "tags": zero_tags},
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id},
        )

    deleted: list[str] = []
    try:
        for tag_id in delete_ids:
            resp = api.tags_delete(tag_id)
            if resp.status not in (200, 204):
                raise RuntimeError(f"Unexpected delete response: HTTP {resp.status} (id={tag_id})")
            _verify_deleted(api, tag_id)
            deleted.append(tag_id)
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="tag",
                resource_id="bulk",
                slug=None,
                action="tag.delete_zero",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e), "deleted_so_far": deleted},
            )
        raise

    if backup is not None:
        backup.write_before_after(
            kind="tag",
            resource_id="bulk",
            slug=None,
            action="tag.delete_zero",
            before=None,
            after=None,
            meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "deleted_count": len(deleted), "deleted_ids": deleted},
        )
    ctx["audit"].write(
        "tag.delete_zero",
        {"apply": True, "selector": {"visibility": args.visibility}, "deleted_count": len(deleted), "deleted_ids": deleted},
    )
    ctx["out"].print({"apply": True, "deleted_count": len(deleted), "deleted_ids": deleted})
    return 0


def cmd_tag_merge(args, ctx) -> int:
    api = get_api(ctx)
    from_slug = str(args.from_slug or "").strip()
    to_slug = str(args.to_slug or "").strip()
    if not from_slug or not to_slug:
        raise ValidationError("Missing --from-slug or --to-slug")
    if from_slug == to_slug:
        raise ValidationError("--from-slug and --to-slug must be different")

    tags, _meta = _browse_all(
        api,
        params={
            "limit": 100,
            "include": "count.posts",
            "order": "name asc",
            "fields": "id,slug,name,visibility,count",
        },
    )
    by_slug: dict[str, dict[str, Any]] = {}
    for t in tags:
        slug = t.get("slug")
        if isinstance(slug, str) and slug.strip():
            by_slug[slug.strip()] = t

    from_tag = by_slug.get(from_slug)
    to_tag = by_slug.get(to_slug)
    if not from_tag:
        raise RuntimeError(f"Refused: source tag slug not found: {from_slug}")
    if not to_tag:
        raise RuntimeError(f"Refused: destination tag slug not found: {to_slug}")
    from_id = str(from_tag.get("id") or "").strip()
    to_id = str(to_tag.get("id") or "").strip()
    if not from_id or not to_id:
        raise ValidationError("Missing tag id(s)")

    # Fetch posts that currently have the source tag.
    posts: list[dict[str, Any]] = []
    page = 1
    while True:
        res = api.posts_browse(
            params={
                "limit": 100,
                "page": page,
                "filter": f"tag:{from_slug}",
                "fields": "id,slug,title,status,updated_at",
                "include": "tags",
            }
        )
        batch = res.get("posts")
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected response: missing posts list")
        for p in batch:
            if isinstance(p, dict):
                posts.append(p)
        pagination = (res.get("meta") or {}).get("pagination") if isinstance(res.get("meta"), dict) else None
        next_page = pagination.get("next") if isinstance(pagination, dict) else None
        if not next_page:
            break
        page = int(next_page)

    if args.limit is not None:
        posts = posts[: int(args.limit)]

    plan_posts: list[dict[str, Any]] = []
    for p in posts:
        cur_tags = p.get("tags")
        if not isinstance(cur_tags, list):
            cur_tags = []
        new_tags, changed = _merge_tag_refs(cur_tags, from_id=from_id, to_id=to_id)
        plan_posts.append(
            {
                "id": p.get("id"),
                "slug": p.get("slug"),
                "status": p.get("status"),
                "title": p.get("title"),
                "changed": changed,
                "tags_before": [t.get("slug") for t in cur_tags if isinstance(t, dict) and isinstance(t.get("slug"), str)],
                "tags_after_ids": [t.get("id") for t in new_tags if isinstance(t, dict)],
            }
        )

    plan = {
        "apply": bool(ctx["apply"]),
        "selector": {"from_slug": from_slug, "to_slug": to_slug},
        "from_tag": {
            "id": from_id,
            "slug": from_slug,
            "name": from_tag.get("name"),
            "visibility": from_tag.get("visibility"),
            "count_posts": _tags_count_posts(from_tag),
        },
        "to_tag": {
            "id": to_id,
            "slug": to_slug,
            "name": to_tag.get("name"),
            "visibility": to_tag.get("visibility"),
            "count_posts": _tags_count_posts(to_tag),
        },
        "posts_found": len(posts),
        "posts_to_update": sum(1 for p in plan_posts if p.get("changed")),
        "delete_from_tag": bool(args.delete_from_tag),
        "posts": plan_posts,
    }

    if not ctx["apply"]:
        ctx["out"].print(plan)
        return 0

    if not ctx["yes"]:
        ctx["out"].print({**plan, "refused": True, "reasons": ["Refused: tag merge requires --yes"]})
        return 0

    backup = ctx.get("backup")
    correlation_id = f"{int(time.time() * 1000)}-tag.merge-{from_slug}-to-{to_slug}"

    updated: list[str] = []
    try:
        for p in posts:
            post_id = str(p.get("id") or "").strip()
            if not post_id:
                continue
            updated_at = p.get("updated_at")
            if not updated_at:
                raise RuntimeError(f"Post missing updated_at (id={post_id})")
            cur_tags = p.get("tags")
            if not isinstance(cur_tags, list):
                cur_tags = []
            new_tags, changed = _merge_tag_refs(cur_tags, from_id=from_id, to_id=to_id)
            if not changed:
                continue

            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=post_id,
                    slug=str(p.get("slug") or ""),
                    action="tag.merge",
                    before=p,
                    after=None,
                    meta={"stage": "before", "correlation_id": correlation_id, "from": from_slug, "to": to_slug},
                )

            api.posts_update(post_id, {"posts": [{"updated_at": updated_at, "tags": new_tags}]})
            after = api.posts_read_by_id(post_id, params={"fields": "id,slug,title,status,updated_at", "include": "tags"}).get("posts")
            if not isinstance(after, list) or not after or not isinstance(after[0], dict):
                raise RuntimeError(f"Unexpected read-after response for post id={post_id}")
            after_post = after[0]
            after_tags = after_post.get("tags")
            if not isinstance(after_tags, list):
                after_tags = []
            # Verification: idempotence + from removed + to present
            v_tags, v_changed = _merge_tag_refs(after_tags, from_id=from_id, to_id=to_id)
            after_ids = [t.get("id") for t in after_tags if isinstance(t, dict)]
            if from_id in after_ids:
                raise RuntimeError(f"Verification failed: from tag still present on post id={post_id}")
            if to_id not in after_ids:
                raise RuntimeError(f"Verification failed: to tag missing on post id={post_id}")
            if v_changed:
                raise RuntimeError(f"Verification failed: re-running merge would still change post id={post_id}")

            if backup is not None:
                backup.write_before_after(
                    kind="post",
                    resource_id=post_id,
                    slug=str(after_post.get("slug") or p.get("slug") or ""),
                    action="tag.merge",
                    before=None,
                    after=after_post,
                    meta={"stage": "after", "correlation_id": correlation_id, "verified": True},
                )
            updated.append(post_id)

        deleted_tag = None
        if args.delete_from_tag:
            before_tag = api.tags_read_by_id(from_id)
            if backup is not None:
                backup.write_before_after(
                    kind="tag",
                    resource_id=from_id,
                    slug=from_slug,
                    action="tag.merge.delete_from_tag",
                    before=before_tag,
                    after=None,
                    meta={"stage": "before", "correlation_id": correlation_id},
                )
            resp = api.tags_delete(from_id)
            if resp.status not in (200, 204):
                raise RuntimeError(f"Unexpected delete response: HTTP {resp.status} (id={from_id})")
            _verify_deleted(api, from_id)
            deleted_tag = {"id": from_id, "slug": from_slug}
            if backup is not None:
                backup.write_before_after(
                    kind="tag",
                    resource_id=from_id,
                    slug=from_slug,
                    action="tag.merge.delete_from_tag",
                    before=None,
                    after=None,
                    meta={"stage": "after", "correlation_id": correlation_id, "verified": True, "deleted": deleted_tag},
                )

    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="tag",
                resource_id="tag.merge",
                slug=None,
                action="tag.merge",
                before={"plan": plan},
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e), "updated_posts_so_far": updated},
            )
        raise

    ctx["audit"].write(
        "tag.merge",
        {"apply": True, "from_slug": from_slug, "to_slug": to_slug, "updated_posts": len(updated), "updated_post_ids": updated},
    )
    ctx["out"].print({**plan, "apply": True, "updated_post_ids": updated})
    return 0
