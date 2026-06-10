from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

from ..authors_audit import audit_authors
from ..runtime import get_api


def add_post_authors_commands(post_sub) -> None:
    authors = post_sub.add_parser("authors", help="Author-related audits (read-only)")
    authors_sub = authors.add_subparsers(dest="post_authors_cmd", required=True)

    audit = authors_sub.add_parser("audit", help="Audit posts by author (read-only)")
    audit.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: <project_dir>/audits; override via --out-dir or project config `audits_dir`)",
    )
    audit.add_argument("--force", action="store_true", help="Overwrite output files if they already exist")
    audit.add_argument("--filter", default=None, help="Optional Ghost NQL filter (advanced)")
    audit.add_argument("--limit", type=int, default=100, help="Page size (default: 100)")
    audit.add_argument("--max-pages", type=int, default=500, help="Max pages to fetch (default: 500)")
    audit.add_argument("--primary-author-name", default="", help="Optional user display name to match (default: empty)")
    audit.add_argument(
        "--ghost-admin-name",
        default="Ghost Admin",
        help='User display name to match (default: "Ghost Admin")',
    )
    audit.set_defaults(func=cmd_post_authors_audit)


def _browse_all(api, *, path: str, key: str, params: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    items: list[dict[str, Any]] = []
    meta: dict[str, Any] | None = None

    page = 1
    limit = int(params.get("limit") or 100)
    max_pages = int(params.get("max_pages") or 500)
    while True:
        if page > max_pages:
            break
        res = api.request("GET", path, params={**params, "page": page, "limit": limit}).json()
        batch = res.get(key)
        if not isinstance(batch, list):
            raise RuntimeError(f"Unexpected response (missing {key} list): {res}")
        for item in batch:
            if isinstance(item, dict):
                items.append(item)
        meta = res.get("meta") if isinstance(res.get("meta"), dict) else meta
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        next_page = pagination.get("next") if isinstance(pagination, dict) else None
        if not next_page:
            break
        page = int(next_page)
        time.sleep(0.05)
    return items, meta


def _refuse_existing(path: Path, *, force: bool) -> list[str]:
    if force:
        return []
    if path.exists():
        return [f"Refused: output file exists (pass --force): {path}"]
    return []


def cmd_post_authors_audit(args, ctx) -> int:
    api = get_api(ctx)

    project_cfg = ctx.get("project_cfg") or {}
    project_dir = Path(str(ctx.get("project_dir") or Path.cwd())).expanduser().resolve()
    out_dir_str = str(args.out_dir) if args.out_dir else str(project_cfg.get("audits_dir") or (project_dir / "audits"))
    out_dir = Path(out_dir_str).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    out_summary = out_dir / "ghost_authors_audit.json"
    out_users = out_dir / "ghost_users_min.json"
    out_counts_any = out_dir / "ghost_author_counts_any.csv"
    out_counts_primary = out_dir / "ghost_author_counts_primary.csv"
    out_posts_primary = out_dir / "ghost_posts_primary_author_ghost_admin.csv"
    out_posts_any = out_dir / "ghost_posts_any_author_ghost_admin.csv"

    refused: list[str] = []
    for p in [out_summary, out_users, out_counts_any, out_counts_primary, out_posts_primary, out_posts_any]:
        refused.extend(_refuse_existing(p, force=bool(args.force)))
    if refused:
        ctx["out"].print(
            {
                "apply": bool(ctx["apply"]),
                "refused": True,
                "reasons": refused,
                "out_dir": str(out_dir),
            }
        )
        return 0

    users, _ = _browse_all(
        api,
        path="/users/",
        key="users",
        params={
            "limit": int(args.limit),
            "max_pages": int(args.max_pages),
        },
    )

    # Posts via the typed helper so we get the same behavior as the rest of the tool.
    posts: list[dict[str, Any]] = []
    page = 1
    pages_fetched = 0
    while True:
        if pages_fetched >= int(args.max_pages):
            break
        params: dict[str, Any] = {
            "limit": int(args.limit),
            "page": page,
            "include": "authors",
            "fields": "id,slug,title,status,published_at,updated_at,created_at",
        }
        if args.filter:
            params["filter"] = str(args.filter)
        res = api.posts_browse(params=params)
        pages_fetched += 1
        batch = res.get("posts")
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected Ghost response: missing posts list")
        for p in batch:
            if isinstance(p, dict):
                posts.append(p)

        meta = res.get("meta") or {}
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        if not isinstance(pagination, dict) or not pagination.get("next"):
            break
        page = int(pagination["next"])
        time.sleep(0.05)

    result = audit_authors(
        users=users,
        posts=posts,
        primary_author_name=str(args.primary_author_name),
        ghost_admin_name=str(args.ghost_admin_name),
    )

    # Write files (no secrets; omit user emails by design).
    out_users.write_text(json.dumps(result.users_min, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k) for k in fieldnames})

    write_csv(
        out_counts_any,
        result.counts_any_author,
        ["user_id", "user_name", "user_slug", "user_status", "user_roles", "posts_count"],
    )
    write_csv(
        out_counts_primary,
        result.counts_primary_author,
        ["user_id", "user_name", "user_slug", "user_status", "user_roles", "posts_count"],
    )
    write_csv(
        out_posts_primary,
        result.posts_primary_author_ghost_admin,
        [
            "id",
            "slug",
            "title",
            "status",
            "published_at",
            "updated_at",
            "primary_author_id",
            "primary_author_name",
            "authors_ids",
            "authors_names",
        ],
    )
    write_csv(
        out_posts_any,
        result.posts_any_author_ghost_admin,
        [
            "id",
            "slug",
            "title",
            "status",
            "published_at",
            "updated_at",
            "primary_author_id",
            "primary_author_name",
            "authors_ids",
            "authors_names",
        ],
    )

    summary = {
        "ok": True,
        "note": "Read-only audit; no changes made.",
        "filter": args.filter,
        "pages_fetched_posts": pages_fetched,
        "posts_seen": len(posts),
        "users_seen": len(users),
        "ghost_admin_name": args.ghost_admin_name,
        "ghost_admin_users": result.ghost_admin_users_min,
        "ghost_admin_candidates": result.ghost_admin_candidates_min if not result.ghost_admin_users_min else [],
        "primary_author_name": args.primary_author_name,
        "primary_author_users": result.primary_author_users_min,
        "posts_primary_author_ghost_admin_count": len(result.posts_primary_author_ghost_admin),
        "posts_any_author_ghost_admin_count": len(result.posts_any_author_ghost_admin),
        "out_dir": str(out_dir),
        "out_summary": str(out_summary),
        "out_users": str(out_users),
        "out_counts_any": str(out_counts_any),
        "out_counts_primary": str(out_counts_primary),
        "out_posts_primary": str(out_posts_primary),
        "out_posts_any": str(out_posts_any),
    }
    out_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ctx["out"].print(summary)
    return 0
