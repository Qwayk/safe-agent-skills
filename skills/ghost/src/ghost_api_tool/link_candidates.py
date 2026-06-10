from __future__ import annotations

from typing import Any


def estimate_word_count_from_lexical(lexical_obj: dict[str, Any]) -> int:
    words = 0

    def walk(node: Any) -> None:
        nonlocal words
        if isinstance(node, dict):
            txt = node.get("text")
            if isinstance(txt, str) and txt.strip():
                words += len(txt.split())
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(lexical_obj)
    return words


def pick_hub_shortlist_post_ids(
    posts: list[dict[str, Any]],
    *,
    limit: int,
    metric_key: str,
) -> set[str]:
    """
    Heuristic shortlist of "hub" candidates for a given topic/tag.

    Rules (simple on purpose):
    - Prefer longer posts (higher reading_time).
    - Stable tie-breakers by published_at then title.
    """
    n = max(0, int(limit))
    if n == 0:
        return set()

    def sort_key(p: dict[str, Any]) -> tuple[int, str, str]:
        m = p.get(metric_key)
        metric = int(m) if isinstance(m, int) else 0
        published_at = p.get("published_at")
        published = published_at if isinstance(published_at, str) else ""
        title = p.get("title")
        t = title if isinstance(title, str) else ""
        return (metric, published, t.casefold())

    ordered = sorted(posts, key=sort_key, reverse=True)
    out: set[str] = set()
    for p in ordered:
        pid = p.get("id")
        if isinstance(pid, str) and pid.strip():
            out.add(pid.strip())
        if len(out) >= n:
            break
    return out


def tag_candidate_rows(
    *,
    tag_slug: str,
    posts: list[dict[str, Any]],
    hub_shortlist_post_ids: set[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in posts:
        pid = p.get("id")
        post_id = pid if isinstance(pid, str) else ""
        slug = p.get("slug") if isinstance(p.get("slug"), str) else ""
        title = p.get("title") if isinstance(p.get("title"), str) else ""
        url = p.get("url") if isinstance(p.get("url"), str) else ""
        status = p.get("status") if isinstance(p.get("status"), str) else ""
        published_at = p.get("published_at") if isinstance(p.get("published_at"), str) else ""
        updated_at = p.get("updated_at") if isinstance(p.get("updated_at"), str) else ""
        wc = p.get("word_count_est")
        word_count_est = int(wc) if isinstance(wc, int) else ""
        rt = p.get("reading_time_est")
        reading_time_est = int(rt) if isinstance(rt, int) else ""
        out.append(
            {
                "tag_slug": tag_slug,
                "post_id": post_id,
                "slug": slug,
                "title": title,
                "url": url,
                "status": status,
                "published_at": published_at,
                "updated_at": updated_at,
                "word_count_est": word_count_est,
                "reading_time_est": reading_time_est,
                "hub_shortlist": "true" if post_id in hub_shortlist_post_ids else "false",
            }
        )
    return out
