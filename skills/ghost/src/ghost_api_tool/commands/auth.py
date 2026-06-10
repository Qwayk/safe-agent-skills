from __future__ import annotations

from ..runtime import get_api


def cmd_auth_check(args, ctx) -> int:
    api = get_api(ctx)

    # Read-only site endpoint (unauthenticated, but checks base URL correctness).
    site = api.get_site().get("site") or {}
    # Authenticated call to prove JWT is valid.
    posts = api.posts_browse(params={"limit": 1})

    if not args.full_site and isinstance(site, dict):
        site = {
            "title": site.get("title"),
            "url": site.get("url"),
            "version": site.get("version"),
        }

    ctx["out"].print(
        {
            "ok": True,
            "site": site,
            "posts_count": len(posts.get("posts") or []),
        }
    )
    return 0
