from __future__ import annotations

from typing import Any, Type

from ..errors import ValidationError
from ..runtime import get_content_api


def add_content_commands(content_sub, *, parser_class: Type) -> None:
    posts = content_sub.add_parser("posts", help="Content API posts (read-only)")
    posts_sub = posts.add_subparsers(dest="content_posts_cmd", required=True, parser_class=parser_class)
    _add_posts_commands(posts_sub)

    pages = content_sub.add_parser("pages", help="Content API pages (read-only)")
    pages_sub = pages.add_subparsers(dest="content_pages_cmd", required=True, parser_class=parser_class)
    _add_pages_commands(pages_sub)

    tags = content_sub.add_parser("tags", help="Content API tags (read-only)")
    tags_sub = tags.add_subparsers(dest="content_tags_cmd", required=True, parser_class=parser_class)
    _add_tags_commands(tags_sub)

    authors = content_sub.add_parser("authors", help="Content API authors (read-only)")
    authors_sub = authors.add_subparsers(dest="content_authors_cmd", required=True, parser_class=parser_class)
    _add_authors_commands(authors_sub)

    tiers = content_sub.add_parser("tiers", help="Content API tiers (read-only)")
    tiers_sub = tiers.add_subparsers(dest="content_tiers_cmd", required=True, parser_class=parser_class)
    tiers_list = tiers_sub.add_parser("list", help="List tiers (read-only)")
    tiers_list.add_argument("--include", default=None, help="Comma-separated include (e.g. benefits,monthly_price,yearly_price)")
    tiers_list.add_argument("--limit", type=int, default=50, help="Page size (default: 50)")
    tiers_list.add_argument("--page", type=int, default=None, help="Page number (default: fetch all pages)")
    tiers_list.set_defaults(func=cmd_content_tiers_list)

    settings = content_sub.add_parser("settings", help="Content API settings (read-only)")
    settings_sub = settings.add_subparsers(dest="content_settings_cmd", required=True, parser_class=parser_class)
    settings_get = settings_sub.add_parser("get", help="Get global site settings (read-only)")
    settings_get.set_defaults(func=cmd_content_settings_get)


def _add_common_browse_args(p) -> None:
    p.add_argument("--limit", type=int, default=15, help="Page size (default: 15)")
    p.add_argument("--page", type=int, default=None, help="Page number (default: fetch all pages)")
    p.add_argument("--filter", default=None, help="Raw API filter (advanced)")
    p.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    p.add_argument("--include", default=None, help="Comma-separated include (API include param)")
    p.add_argument("--order", default=None, help='Order (e.g. "published_at desc")')


def _add_posts_commands(posts_sub) -> None:
    posts_list = posts_sub.add_parser("list", help="List posts (read-only)")
    _add_common_browse_args(posts_list)
    posts_list.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,plaintext)")
    posts_list.set_defaults(func=cmd_content_posts_list)

    posts_get = posts_sub.add_parser("get", help="Get one post by id or slug (read-only)")
    posts_get.add_argument("--id", default=None, help="Post id")
    posts_get.add_argument("--slug", default=None, help="Post slug")
    posts_get.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    posts_get.add_argument("--include", default=None, help="Comma-separated include (API include param)")
    posts_get.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,plaintext)")
    posts_get.set_defaults(func=cmd_content_posts_get)


def _add_pages_commands(pages_sub) -> None:
    pages_list = pages_sub.add_parser("list", help="List pages (read-only)")
    _add_common_browse_args(pages_list)
    pages_list.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,plaintext)")
    pages_list.set_defaults(func=cmd_content_pages_list)

    pages_get = pages_sub.add_parser("get", help="Get one page by id or slug (read-only)")
    pages_get.add_argument("--id", default=None, help="Page id")
    pages_get.add_argument("--slug", default=None, help="Page slug")
    pages_get.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    pages_get.add_argument("--include", default=None, help="Comma-separated include (API include param)")
    pages_get.add_argument("--formats", default=None, help="Comma-separated formats (e.g. html,plaintext)")
    pages_get.set_defaults(func=cmd_content_pages_get)


def _add_tags_commands(tags_sub) -> None:
    tags_list = tags_sub.add_parser("list", help="List tags (read-only)")
    _add_common_browse_args(tags_list)
    tags_list.set_defaults(func=cmd_content_tags_list)

    tags_get = tags_sub.add_parser("get", help="Get one tag by id or slug (read-only)")
    tags_get.add_argument("--id", default=None, help="Tag id")
    tags_get.add_argument("--slug", default=None, help="Tag slug")
    tags_get.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    tags_get.add_argument("--include", default=None, help="Comma-separated include (API include param)")
    tags_get.set_defaults(func=cmd_content_tags_get)


def _add_authors_commands(authors_sub) -> None:
    authors_list = authors_sub.add_parser("list", help="List authors (read-only)")
    _add_common_browse_args(authors_list)
    authors_list.set_defaults(func=cmd_content_authors_list)

    authors_get = authors_sub.add_parser("get", help="Get one author by id or slug (read-only)")
    authors_get.add_argument("--id", default=None, help="Author id")
    authors_get.add_argument("--slug", default=None, help="Author slug")
    authors_get.add_argument("--fields", default=None, help="Comma-separated field list (API fields param)")
    authors_get.add_argument("--include", default=None, help="Comma-separated include (API include param)")
    authors_get.set_defaults(func=cmd_content_authors_get)


def _selector_from_id_slug(args) -> dict[str, Any]:
    selector: dict[str, Any] = {}
    if getattr(args, "id", None):
        selector["id"] = args.id
    if getattr(args, "slug", None):
        selector["slug"] = args.slug
    return selector


def _params_from_args(
    args,
    *,
    allow_filter: bool = True,
    allow_order: bool = True,
    allow_limit_page: bool = True,
    allow_formats: bool = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if allow_limit_page:
        if getattr(args, "limit", None) is not None:
            params["limit"] = int(args.limit)
        if getattr(args, "page", None) is not None:
            params["page"] = int(args.page)
    if allow_filter and getattr(args, "filter", None):
        params["filter"] = args.filter
    if getattr(args, "fields", None):
        params["fields"] = args.fields
    if getattr(args, "include", None):
        params["include"] = args.include
    if allow_order and getattr(args, "order", None):
        params["order"] = args.order
    if allow_formats and getattr(args, "formats", None):
        params["formats"] = args.formats
    return params


def _browse_all(fetch_page, *, items_key: str, params: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    items: list[dict[str, Any]] = []
    meta: dict[str, Any] | None = None

    page = 1
    limit = int(params.get("limit") or 15)
    while True:
        res = fetch_page(params={**params, "page": page, "limit": limit})
        batch = res.get(items_key)
        if not isinstance(batch, list):
            raise RuntimeError(f"Unexpected response (missing {items_key} list): {res}")
        for it in batch:
            if isinstance(it, dict):
                items.append(it)
        meta = res.get("meta") if isinstance(res.get("meta"), dict) else meta
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        next_page = pagination.get("next") if isinstance(pagination, dict) else None
        if not next_page:
            break
        page = int(next_page)

    return items, meta


def cmd_content_posts_list(args, ctx) -> int:
    api = get_content_api(ctx)
    params = _params_from_args(args, allow_formats=True)
    base_params = dict(params)
    if args.page is not None:
        res = api.posts_browse(params=params)
        posts = res.get("posts") if isinstance(res, dict) else None
        meta = res.get("meta") if isinstance(res, dict) else None
        ctx["out"].print({"kind": "content.posts.list", "selector": {}, "params": base_params, "posts": posts, "meta": meta})
        return 0

    params.pop("page", None)
    posts, meta = _browse_all(api.posts_browse, items_key="posts", params=params)
    ctx["out"].print(
        {
            "kind": "content.posts.list",
            "selector": {},
            "params": base_params,
            "posts": posts,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(posts)},
        }
    )
    return 0


def cmd_content_posts_get(args, ctx) -> int:
    api = get_content_api(ctx)
    selector = _selector_from_id_slug(args)
    if bool(selector.get("id")) == bool(selector.get("slug")):
        raise ValidationError("Provide exactly one of --id or --slug")
    params = _params_from_args(args, allow_filter=False, allow_order=False, allow_limit_page=False, allow_formats=True)
    if selector.get("id"):
        res = api.posts_read_by_id(str(selector["id"]), params=params or None)
    else:
        res = api.posts_read_by_slug(str(selector["slug"]), params=params or None)
    ctx["out"].print(
        {
            "kind": "content.posts.get",
            "selector": selector,
            "params": params,
            "posts": (res or {}).get("posts") if isinstance(res, dict) else None,
            "meta": (res or {}).get("meta") if isinstance(res, dict) else None,
        }
    )
    return 0


def cmd_content_pages_list(args, ctx) -> int:
    api = get_content_api(ctx)
    params = _params_from_args(args, allow_formats=True)
    base_params = dict(params)
    if args.page is not None:
        res = api.pages_browse(params=params)
        pages = res.get("pages") if isinstance(res, dict) else None
        meta = res.get("meta") if isinstance(res, dict) else None
        ctx["out"].print({"kind": "content.pages.list", "selector": {}, "params": base_params, "pages": pages, "meta": meta})
        return 0

    params.pop("page", None)
    pages, meta = _browse_all(api.pages_browse, items_key="pages", params=params)
    ctx["out"].print(
        {
            "kind": "content.pages.list",
            "selector": {},
            "params": base_params,
            "pages": pages,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(pages)},
        }
    )
    return 0


def cmd_content_pages_get(args, ctx) -> int:
    api = get_content_api(ctx)
    selector = _selector_from_id_slug(args)
    if bool(selector.get("id")) == bool(selector.get("slug")):
        raise ValidationError("Provide exactly one of --id or --slug")
    params = _params_from_args(args, allow_filter=False, allow_order=False, allow_limit_page=False, allow_formats=True)
    if selector.get("id"):
        res = api.pages_read_by_id(str(selector["id"]), params=params or None)
    else:
        res = api.pages_read_by_slug(str(selector["slug"]), params=params or None)
    ctx["out"].print(
        {
            "kind": "content.pages.get",
            "selector": selector,
            "params": params,
            "pages": (res or {}).get("pages") if isinstance(res, dict) else None,
            "meta": (res or {}).get("meta") if isinstance(res, dict) else None,
        }
    )
    return 0


def cmd_content_tags_list(args, ctx) -> int:
    api = get_content_api(ctx)
    params = _params_from_args(args, allow_formats=False)
    base_params = dict(params)
    if args.page is not None:
        res = api.tags_browse(params=params)
        tags = res.get("tags") if isinstance(res, dict) else None
        meta = res.get("meta") if isinstance(res, dict) else None
        ctx["out"].print({"kind": "content.tags.list", "selector": {}, "params": base_params, "tags": tags, "meta": meta})
        return 0

    params.pop("page", None)
    tags, meta = _browse_all(api.tags_browse, items_key="tags", params=params)
    ctx["out"].print(
        {
            "kind": "content.tags.list",
            "selector": {},
            "params": base_params,
            "tags": tags,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(tags)},
        }
    )
    return 0


def cmd_content_tags_get(args, ctx) -> int:
    api = get_content_api(ctx)
    selector = _selector_from_id_slug(args)
    if bool(selector.get("id")) == bool(selector.get("slug")):
        raise ValidationError("Provide exactly one of --id or --slug")
    params = _params_from_args(args, allow_filter=False, allow_order=False, allow_limit_page=False)
    if selector.get("id"):
        res = api.tags_read_by_id(str(selector["id"]), params=params or None)
    else:
        res = api.tags_read_by_slug(str(selector["slug"]), params=params or None)
    ctx["out"].print(
        {
            "kind": "content.tags.get",
            "selector": selector,
            "params": params,
            "tags": (res or {}).get("tags") if isinstance(res, dict) else None,
            "meta": (res or {}).get("meta") if isinstance(res, dict) else None,
        }
    )
    return 0


def cmd_content_authors_list(args, ctx) -> int:
    api = get_content_api(ctx)
    params = _params_from_args(args, allow_formats=False)
    base_params = dict(params)
    if args.page is not None:
        res = api.authors_browse(params=params)
        authors = res.get("authors") if isinstance(res, dict) else None
        meta = res.get("meta") if isinstance(res, dict) else None
        ctx["out"].print(
            {"kind": "content.authors.list", "selector": {}, "params": base_params, "authors": authors, "meta": meta}
        )
        return 0

    params.pop("page", None)
    authors, meta = _browse_all(api.authors_browse, items_key="authors", params=params)
    ctx["out"].print(
        {
            "kind": "content.authors.list",
            "selector": {},
            "params": base_params,
            "authors": authors,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(authors)},
        }
    )
    return 0


def cmd_content_authors_get(args, ctx) -> int:
    api = get_content_api(ctx)
    selector = _selector_from_id_slug(args)
    if bool(selector.get("id")) == bool(selector.get("slug")):
        raise ValidationError("Provide exactly one of --id or --slug")
    params = _params_from_args(args, allow_filter=False, allow_order=False, allow_limit_page=False)
    if selector.get("id"):
        res = api.authors_read_by_id(str(selector["id"]), params=params or None)
    else:
        res = api.authors_read_by_slug(str(selector["slug"]), params=params or None)
    ctx["out"].print(
        {
            "kind": "content.authors.get",
            "selector": selector,
            "params": params,
            "authors": (res or {}).get("authors") if isinstance(res, dict) else None,
            "meta": (res or {}).get("meta") if isinstance(res, dict) else None,
        }
    )
    return 0


def cmd_content_tiers_list(args, ctx) -> int:
    api = get_content_api(ctx)
    params: dict[str, Any] = {"limit": int(args.limit)}
    if args.page is not None:
        params["page"] = int(args.page)
    if args.include:
        params["include"] = args.include

    base_params = dict(params)
    if args.page is not None:
        res = api.tiers_browse(params=params)
        tiers = res.get("tiers") if isinstance(res, dict) else None
        meta = res.get("meta") if isinstance(res, dict) else None
        ctx["out"].print({"kind": "content.tiers.list", "selector": {}, "params": base_params, "tiers": tiers, "meta": meta})
        return 0

    params.pop("page", None)
    tiers, meta = _browse_all(api.tiers_browse, items_key="tiers", params=params)
    ctx["out"].print(
        {
            "kind": "content.tiers.list",
            "selector": {},
            "params": base_params,
            "tiers": tiers,
            "meta": meta,
            "fetched": {"pages": (meta or {}).get("pagination", {}).get("pages"), "total": len(tiers)},
        }
    )
    return 0


def cmd_content_settings_get(_args, ctx) -> int:
    api = get_content_api(ctx)
    res = api.settings_get()
    ctx["out"].print({"kind": "content.settings.get", "selector": {}, "params": {}, "settings": res.get("settings") if isinstance(res, dict) else None})
    return 0
