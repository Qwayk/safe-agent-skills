from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


def _cf(s: object) -> str:
    return str(s or "").strip().casefold()


def _min_user(u: dict[str, Any]) -> dict[str, Any]:
    roles: list[str] = []
    for r in u.get("roles") or []:
        if isinstance(r, dict):
            name = r.get("name")
            if isinstance(name, str) and name.strip():
                roles.append(name.strip())
    return {
        "id": u.get("id"),
        "name": u.get("name"),
        "slug": u.get("slug"),
        "status": u.get("status"),
        "roles": roles,
    }


def find_users_by_name(users: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    target = _cf(name)
    if not target:
        return []
    out: list[dict[str, Any]] = []
    for u in users:
        if not isinstance(u, dict):
            continue
        if _cf(u.get("name")) == target:
            out.append(u)
    return out


def find_users_by_name_contains(users: list[dict[str, Any]], needle: str) -> list[dict[str, Any]]:
    n = _cf(needle)
    if not n:
        return []
    out: list[dict[str, Any]] = []
    for u in users:
        if not isinstance(u, dict):
            continue
        if n in _cf(u.get("name")):
            out.append(u)
    return out


def post_primary_author(post: dict[str, Any]) -> dict[str, Any] | None:
    pa = post.get("primary_author")
    if isinstance(pa, dict):
        return pa
    authors = post.get("authors")
    if isinstance(authors, list) and authors:
        a0 = authors[0]
        if isinstance(a0, dict):
            return a0
    return None


def post_author_ids(post: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for a in post.get("authors") or []:
        if not isinstance(a, dict):
            continue
        aid = a.get("id")
        if isinstance(aid, str) and aid.strip():
            out.append(aid.strip())
    return out


def post_author_names(post: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for a in post.get("authors") or []:
        if not isinstance(a, dict):
            continue
        name = a.get("name")
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out


@dataclass(frozen=True)
class AuthorsAuditResult:
    users_min: list[dict[str, Any]]
    primary_author_users_min: list[dict[str, Any]]
    ghost_admin_users_min: list[dict[str, Any]]
    ghost_admin_candidates_min: list[dict[str, Any]]
    counts_any_author: list[dict[str, Any]]
    counts_primary_author: list[dict[str, Any]]
    posts_primary_author_ghost_admin: list[dict[str, Any]]
    posts_any_author_ghost_admin: list[dict[str, Any]]


def audit_authors(
    *,
    users: list[dict[str, Any]],
    posts: list[dict[str, Any]],
    primary_author_name: str,
    ghost_admin_name: str,
) -> AuthorsAuditResult:
    users_min = [_min_user(u) for u in users if isinstance(u, dict)]

    primary_author_users = find_users_by_name(users, primary_author_name)
    ghost_admin_users = find_users_by_name(users, ghost_admin_name)

    # Candidates are provided for operator choice, but we only classify "Ghost Admin" posts
    # using the exact matches to avoid mislabeling.
    candidates_by_id: dict[str, dict[str, Any]] = {}
    for u in find_users_by_name_contains(users, "ghost"):
        if isinstance(u, dict) and isinstance(u.get("id"), str):
            candidates_by_id[u["id"]] = u
    for u in find_users_by_name_contains(users, "admin"):
        if isinstance(u, dict) and isinstance(u.get("id"), str):
            candidates_by_id[u["id"]] = u
    ghost_admin_candidates = list(candidates_by_id.values())

    primary_author_users_min = [_min_user(u) for u in primary_author_users]
    ghost_admin_users_min = [_min_user(u) for u in ghost_admin_users]
    ghost_admin_candidates_min = [_min_user(u) for u in ghost_admin_candidates]

    any_author_counts: Counter[str] = Counter()
    primary_author_counts: Counter[str] = Counter()

    # Keep post id -> primary author id/name for reporting
    primary_by_post: dict[str, dict[str, Any]] = {}

    for p in posts:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        if not isinstance(pid, str) or not pid.strip():
            continue
        pa = post_primary_author(p) or {}
        if isinstance(pa, dict):
            paid = pa.get("id")
            if isinstance(paid, str) and paid.strip():
                primary_author_counts[paid] += 1
                primary_by_post[pid] = {"id": paid, "name": pa.get("name"), "slug": pa.get("slug")}

        for aid in post_author_ids(p):
            any_author_counts[aid] += 1

    def _sorted_counts(counter: Counter[str]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        # user id -> user min
        by_id = {u.get("id"): u for u in users_min if isinstance(u.get("id"), str)}
        for uid, count in counter.most_common():
            u = by_id.get(uid) or {}
            rows.append(
                {
                    "user_id": uid,
                    "user_name": u.get("name"),
                    "user_slug": u.get("slug"),
                    "user_status": u.get("status"),
                    "user_roles": u.get("roles") or [],
                    "posts_count": int(count),
                }
            )
        return rows

    counts_any_author = _sorted_counts(any_author_counts)
    counts_primary_author = _sorted_counts(primary_author_counts)

    ghost_admin_ids = {
        u.get("id")
        for u in ghost_admin_users_min
        if isinstance(u, dict) and isinstance(u.get("id"), str) and u.get("id").strip()
    }

    posts_primary_author_ghost_admin: list[dict[str, Any]] = []
    posts_any_author_ghost_admin: list[dict[str, Any]] = []

    for p in posts:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        if not isinstance(pid, str) or not pid.strip():
            continue

        base = {
            "id": pid,
            "slug": p.get("slug"),
            "title": p.get("title"),
            "status": p.get("status"),
            "published_at": p.get("published_at"),
            "updated_at": p.get("updated_at"),
            "primary_author_id": primary_by_post.get(pid, {}).get("id"),
            "primary_author_name": primary_by_post.get(pid, {}).get("name"),
            "authors_ids": "|".join(post_author_ids(p)),
            "authors_names": "|".join(post_author_names(p)),
        }

        if base["primary_author_id"] in ghost_admin_ids:
            posts_primary_author_ghost_admin.append(base)

        if any(aid in ghost_admin_ids for aid in post_author_ids(p)):
            posts_any_author_ghost_admin.append(base)

    return AuthorsAuditResult(
        users_min=users_min,
        primary_author_users_min=primary_author_users_min,
        ghost_admin_users_min=ghost_admin_users_min,
        ghost_admin_candidates_min=ghost_admin_candidates_min,
        counts_any_author=counts_any_author,
        counts_primary_author=counts_primary_author,
        posts_primary_author_ghost_admin=posts_primary_author_ghost_admin,
        posts_any_author_ghost_admin=posts_any_author_ghost_admin,
    )
