from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ..amazon_links import amazon_link_row, parse_amazon_link
from ..content_lexical import parse_lexical_field
from ..internal_links import (
    build_url_index,
    extract_links_from_lexical,
    inbound_sources_from_edges,
    internal_hosts_from_site_url,
    resolve_targets,
    write_orphans_csv,
    write_unresolved_internal_csv,
)
from ..link_candidates import estimate_word_count_from_lexical, pick_hub_shortlist_post_ids, tag_candidate_rows
from ..runtime import get_api


def add_post_links_commands(post_sub) -> None:
    links = post_sub.add_parser("links", help="Internal linking helpers (read-only)")
    links_sub = links.add_subparsers(dest="post_links_cmd", required=True)

    audit = links_sub.add_parser(
        "audit",
        help="Audit internal links in post bodies (Lexical + HTML cards) and export reports",
    )
    audit.add_argument("--filter", default=None, help="Ghost filter string (same syntax as Ghost Admin API)")
    audit.add_argument("--out-dir", default=None, help="Optional output directory for CSV/JSON reports")
    audit.add_argument("--limit", type=int, default=25, help="Posts per page (API limit)")
    audit.add_argument("--max-pages", type=int, default=None, help="Optional max page count (for testing)")
    audit.add_argument("--include", default="tags", help="Comma-separated include list (default: tags)")
    audit.add_argument("--order", default=None, help='Order string, e.g. "published_at desc"')
    audit.add_argument(
        "--include-pages",
        action="store_true",
        help="Also index pages as internal link targets (recommended)",
    )
    audit.add_argument(
        "--internal-host",
        action="append",
        default=None,
        help="Extra hostnames to treat as internal (repeatable)",
    )
    audit.set_defaults(func=cmd_post_links_audit)

    tag_candidates = links_sub.add_parser(
        "tag-candidates",
        help="Export per-tag post lists + simple hub shortlists (read-only)",
    )
    tag_candidates.add_argument(
        "--tag",
        action="append",
        default=None,
        help="Tag slug to export (repeatable; supports comma-separated too)",
    )
    tag_candidates.add_argument("--filter", default=None, help="Optional extra Ghost filter string")
    tag_candidates.add_argument(
        "--status",
        default="published",
        help="Post status filter (default: published). Use 'any' to skip status filtering.",
    )
    tag_candidates.add_argument("--out-dir", default=None, help="Optional output directory for CSV/JSON export")
    tag_candidates.add_argument("--limit", type=int, default=25, help="Posts per page (API limit)")
    tag_candidates.add_argument("--max-pages", type=int, default=None, help="Optional max page count (for testing)")
    tag_candidates.add_argument("--include", default="tags", help="Comma-separated include list (default: tags)")
    tag_candidates.add_argument("--order", default='published_at desc', help='Order string, e.g. "published_at desc"')
    tag_candidates.add_argument("--hub-limit", type=int, default=5, help="How many hub candidates to shortlist per tag")
    tag_candidates.add_argument(
        "--hub-metric",
        default="lexical_word_count",
        choices=["lexical_word_count", "none"],
        help="How to rank hub candidates (default: lexical_word_count)",
    )
    tag_candidates.add_argument(
        "--words-per-minute",
        type=int,
        default=200,
        help="Used to estimate reading_time from word count (default: 200)",
    )
    tag_candidates.set_defaults(func=cmd_post_links_tag_candidates)

    amazon_audit = links_sub.add_parser(
        "amazon-audit",
        help="Find Amazon links (amzn.to + amazon.*) in post bodies and export CSV reports",
    )
    amazon_audit.add_argument("--filter", default=None, help="Optional extra Ghost filter string")
    amazon_audit.add_argument(
        "--status",
        default="published",
        help="Post status filter (default: published). Use 'any' to include all statuses.",
    )
    amazon_audit.add_argument("--out-dir", default=None, help="Optional output directory for CSV/JSON export")
    amazon_audit.add_argument("--limit", type=int, default=25, help="Posts per page (API limit)")
    amazon_audit.add_argument("--max-pages", type=int, default=None, help="Optional max page count (for testing)")
    amazon_audit.add_argument("--include", default="tags", help="Comma-separated include list (default: tags)")
    amazon_audit.add_argument("--order", default="published_at desc", help='Order string, e.g. "published_at desc"')
    amazon_audit.add_argument(
        "--require-affiliate-tag",
        action="store_true",
        help="Only include amazon.* links that contain ?tag= (amzn.to short links are excluded)",
    )
    amazon_audit.set_defaults(func=cmd_post_links_amazon_audit)


def _coerce_str(v: Any) -> str:
    return v if isinstance(v, str) else ""


def _fetch_all_posts(api, *, params: dict[str, Any], max_pages: int | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    fetched = 0
    while True:
        if max_pages is not None and fetched >= int(max_pages):
            break
        res = api.posts_browse(params={**params, "page": page})
        fetched += 1
        posts = res.get("posts")
        if not isinstance(posts, list):
            raise RuntimeError("Unexpected Ghost response: missing posts list")
        for p in posts:
            if isinstance(p, dict):
                out.append(p)
        meta = res.get("meta") or {}
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        if not isinstance(pagination, dict):
            break
        next_page = pagination.get("next")
        if not next_page:
            break
        page = int(next_page)
    return out


def _fetch_all_pages(api, *, params: dict[str, Any], max_pages: int | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    fetched = 0
    while True:
        if max_pages is not None and fetched >= int(max_pages):
            break
        res = api.pages_browse(params={**params, "page": page})
        fetched += 1
        pages = res.get("pages")
        if not isinstance(pages, list):
            raise RuntimeError("Unexpected Ghost response: missing pages list")
        for p in pages:
            if isinstance(p, dict):
                out.append(p)
        meta = res.get("meta") or {}
        pagination = meta.get("pagination") if isinstance(meta, dict) else None
        if not isinstance(pagination, dict):
            break
        next_page = pagination.get("next")
        if not next_page:
            break
        page = int(next_page)
    return out


def cmd_post_links_audit(args, ctx) -> int:
    api = get_api(ctx)

    site = api.get_site().get("site") or {}
    site_url = _coerce_str(site.get("url")).strip()
    internal_hosts = internal_hosts_from_site_url(site_url, extra_hosts=args.internal_host)
    if not internal_hosts:
        raise RuntimeError("Cannot determine internal hosts (missing site.url); pass --internal-host explicitly")

    include = [s.strip() for s in str(args.include or "").split(",") if s.strip()]
    params: dict[str, Any] = {
        "limit": int(args.limit),
        "formats": "lexical",
        "fields": "id,slug,title,status,url,lexical",
    }
    if args.filter:
        params["filter"] = str(args.filter)
    if include:
        params["include"] = ",".join(include)
    if args.order:
        params["order"] = str(args.order)

    posts = _fetch_all_posts(api, params=params, max_pages=args.max_pages)

    pages: list[dict[str, Any]] = []
    if args.include_pages:
        page_params: dict[str, Any] = {"limit": int(args.limit), "fields": "id,slug,title,status,url"}
        pages = _fetch_all_pages(api, params=page_params, max_pages=args.max_pages)

    post_index_by_slug = {
        _coerce_str(p.get("slug")).strip(): str(p.get("id") or "")
        for p in posts
        if isinstance(p.get("slug"), str) and str(p.get("id") or "").strip()
    }
    page_index_by_slug = {
        _coerce_str(p.get("slug")).strip(): str(p.get("id") or "")
        for p in pages
        if isinstance(p.get("slug"), str) and str(p.get("id") or "").strip()
    }
    url_index = build_url_index(posts, pages)

    occurrences = []
    parse_warnings: dict[str, list[str]] = {}
    for post in posts:
        pid = str(post.get("id") or "")
        slug = _coerce_str(post.get("slug")).strip()
        title = _coerce_str(post.get("title")).strip()
        status = _coerce_str(post.get("status")).strip()
        lexical_obj, reasons = parse_lexical_field(post.get("lexical"))
        if lexical_obj is None:
            parse_warnings[pid or slug or "unknown"] = reasons
            continue
        occurrences.extend(
            extract_links_from_lexical(
                lexical_obj,
                source_id=pid,
                source_slug=slug,
                source_title=title,
                source_status=status,
            )
        )

    edges, summary = resolve_targets(
        occurrences,
        internal_hosts=internal_hosts,
        post_index_by_slug=post_index_by_slug,
        page_index_by_slug=page_index_by_slug,
        url_index=url_index,
    )
    inbound_sources = inbound_sources_from_edges(edges)

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "link_graph.json").write_text(json.dumps(edges, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

        unresolved = summary.get("unresolved_internal_sample") or []
        if isinstance(unresolved, list) and unresolved:
            write_unresolved_internal_csv(out_dir / "unresolved_internal_links.csv", unresolved)
        else:
            (out_dir / "unresolved_internal_links.csv").write_text("source_id,source_slug,url,anchor_text,origin,node_path\n", encoding="utf-8")

        # Orphans: published posts with 0 inbound sources (within the scanned graph).
        published_posts = [p for p in posts if _coerce_str(p.get("status")) == "published"]
        orphans = [p for p in published_posts if len(inbound_sources.get(str(p.get("id") or ""), set())) == 0]
        write_orphans_csv(out_dir / "orphans.csv", posts=orphans, inbound_sources_by_post_id=inbound_sources)

        (out_dir / "summary.json").write_text(
            json.dumps(
                {
                    "site_url": site_url,
                    "internal_hosts": sorted(internal_hosts),
                    "filter": params.get("filter"),
                    "posts_seen": len(posts),
                    "pages_indexed": len(pages),
                    "links_total": len(occurrences),
                    "orphans_published": len(orphans),
                    "parse_warnings": parse_warnings if parse_warnings else None,
                    "audit_summary": summary,
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    ctx["out"].print(
        {
            "site_url": site_url,
            "internal_hosts": sorted(internal_hosts),
            "filter": params.get("filter"),
            "posts_seen": len(posts),
            "pages_indexed": len(pages),
            "links_total": len(occurrences),
            "edges_total": len(edges),
            "orphans_published": sum(
                1
                for p in posts
                if _coerce_str(p.get("status")) == "published" and len(inbound_sources.get(str(p.get("id") or ""), set())) == 0
            ),
            "parse_warnings_count": len(parse_warnings),
            "out_dir": str(out_dir) if out_dir is not None else None,
            "audit_summary": summary,
        }
    )
    return 0


def _split_tags(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for v in values or []:
        for t in str(v).split(","):
            s = t.strip()
            if s:
                out.append(s)
    # Preserve order, de-dupe.
    seen: set[str] = set()
    deduped: list[str] = []
    for t in out:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text(
            "tag_slug,post_id,slug,title,url,status,published_at,updated_at,word_count_est,reading_time_est,hub_shortlist\n",
            encoding="utf-8",
        )
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def cmd_post_links_tag_candidates(args, ctx) -> int:
    api = get_api(ctx)

    tags = _split_tags(args.tag)
    if not tags:
        raise RuntimeError("At least one --tag is required")

    include = [s.strip() for s in str(args.include or "").split(",") if s.strip()]
    base_params: dict[str, Any] = {
        "limit": int(args.limit),
        "fields": "id,slug,title,status,url,published_at,updated_at",
    }
    if str(args.hub_metric) == "lexical_word_count":
        base_params["formats"] = "lexical"
        base_params["fields"] += ",lexical"
    if include:
        base_params["include"] = ",".join(include)
    if args.order:
        base_params["order"] = str(args.order)

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []

    for tag in tags:
        filter_parts: list[str] = []
        if args.filter:
            filter_parts.append(str(args.filter))
        filter_parts.append(f"tag:{tag}")
        status = str(args.status or "").strip()
        if status and status != "any":
            filter_parts.append(f"status:{status}")
        tag_filter = "+".join(filter_parts)

        posts = _fetch_all_posts(api, params={**base_params, "filter": tag_filter}, max_pages=args.max_pages)

        if str(args.hub_metric) == "lexical_word_count":
            wpm = max(1, int(args.words_per_minute))
            for p in posts:
                lexical_obj, reasons = parse_lexical_field(p.get("lexical"))
                if lexical_obj is None:
                    p["word_count_est"] = 0
                    p["reading_time_est"] = 0
                    p["_lexical_parse_reasons"] = reasons
                    continue
                wc = estimate_word_count_from_lexical(lexical_obj)
                p["word_count_est"] = int(wc)
                p["reading_time_est"] = max(1, int((wc + wpm - 1) / wpm)) if wc > 0 else 0
                # Keep memory down (we don't export lexical from this command).
                p["lexical"] = None
        else:
            for p in posts:
                p["word_count_est"] = 0
                p["reading_time_est"] = 0

        metric_key = "word_count_est" if str(args.hub_metric) == "lexical_word_count" else "word_count_est"
        hub_ids = pick_hub_shortlist_post_ids(posts, limit=int(args.hub_limit), metric_key=metric_key)
        rows = tag_candidate_rows(tag_slug=tag, posts=posts, hub_shortlist_post_ids=hub_ids)
        all_rows.extend(rows)

        results.append(
            {
                "tag": tag,
                "filter": tag_filter,
                "posts_count": len(posts),
                "hub_shortlist_post_ids": sorted(hub_ids),
                "hub_shortlist": [
                    {
                        "id": p.get("id"),
                        "slug": p.get("slug"),
                        "title": p.get("title"),
                        "url": p.get("url"),
                        "word_count_est": p.get("word_count_est"),
                        "reading_time_est": p.get("reading_time_est"),
                    }
                    for p in posts
                    if isinstance(p.get("id"), str) and p.get("id") in hub_ids
                ],
            }
        )

        if out_dir is not None:
            safe_tag = tag.replace("/", "_")
            _write_csv(out_dir / f"tag_candidates_{safe_tag}.csv", rows)

    if out_dir is not None:
        (out_dir / "tag_candidates.json").write_text(
            json.dumps({"tags": results}, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _write_csv(out_dir / "tag_candidates_all.csv", all_rows)

    ctx["out"].print({"tags": results, "out_dir": str(out_dir) if out_dir is not None else None})
    return 0


def _write_csv_rows(path: Path, *, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def cmd_post_links_amazon_audit(args, ctx) -> int:
    api = get_api(ctx)

    include = [s.strip() for s in str(args.include or "").split(",") if s.strip()]
    base_params: dict[str, Any] = {
        "limit": int(args.limit),
        "formats": "lexical",
        "fields": "id,slug,title,status,url,published_at,lexical",
    }
    if include:
        base_params["include"] = ",".join(include)
    if args.order:
        base_params["order"] = str(args.order)

    filter_parts: list[str] = []
    if args.filter:
        filter_parts.append(str(args.filter))
    status = str(args.status or "").strip()
    if status and status != "any":
        filter_parts.append(f"status:{status}")
    final_filter = "+".join(filter_parts) if filter_parts else None

    posts = _fetch_all_posts(api, params={**base_params, **({"filter": final_filter} if final_filter else {})}, max_pages=args.max_pages)

    occurrences = []
    parse_warnings: dict[str, list[str]] = {}
    for post in posts:
        pid = str(post.get("id") or "")
        slug = _coerce_str(post.get("slug")).strip()
        title = _coerce_str(post.get("title")).strip()
        status_s = _coerce_str(post.get("status")).strip()
        lexical_obj, reasons = parse_lexical_field(post.get("lexical"))
        if lexical_obj is None:
            parse_warnings[pid or slug or "unknown"] = reasons
            continue
        occurrences.extend(
            extract_links_from_lexical(
                lexical_obj,
                source_id=pid,
                source_slug=slug,
                source_title=title,
                source_status=status_s,
            )
        )

    amazon_rows: list[dict[str, Any]] = []
    per_post: dict[str, dict[str, Any]] = {}
    posts_with_missing_sponsored: set[str] = set()
    for occ in occurrences:
        info = parse_amazon_link(occ.url)
        if info is None:
            continue
        if bool(args.require_affiliate_tag):
            if info.is_amzn_short:
                continue
            if not info.affiliate_tag:
                continue

        rel = occ.rel if occ.origin == "lexical_link" else None
        rel_tokens = [t.strip().lower() for t in (rel or "").split() if t.strip()]
        rel_has_sponsored = ("sponsored" in rel_tokens) if rel is not None else None
        rel_has_nofollow = ("nofollow" in rel_tokens) if rel is not None else None

        row = {
            "source_id": occ.source_id,
            "source_slug": occ.source_slug,
            "source_title": occ.source_title,
            "source_status": occ.source_status,
            "anchor_text": occ.anchor_text,
            "origin": occ.origin,
            "node_path": occ.node_path,
            "rel": rel,
            "rel_has_sponsored": rel_has_sponsored,
            "rel_has_nofollow": rel_has_nofollow,
            **amazon_link_row(info),
        }
        amazon_rows.append(row)

        key = occ.source_id or occ.source_slug
        if key not in per_post:
            per_post[key] = {
                "source_id": occ.source_id,
                "source_slug": occ.source_slug,
                "source_title": occ.source_title,
                "source_status": occ.source_status,
                "amazon_links": 0,
                "amazon_affiliate_links": 0,
                "amzn_short_links": 0,
                "amazon_lexical_links": 0,
                "amazon_lexical_links_missing_sponsored": 0,
                "example_url": "",
            }
        per_post[key]["amazon_links"] += 1
        if info.is_amzn_short:
            per_post[key]["amzn_short_links"] += 1
        if info.affiliate_tag:
            per_post[key]["amazon_affiliate_links"] += 1
        if occ.origin == "lexical_link":
            per_post[key]["amazon_lexical_links"] += 1
            if rel_has_sponsored is False:
                per_post[key]["amazon_lexical_links_missing_sponsored"] += 1
                posts_with_missing_sponsored.add(key)
        if not per_post[key]["example_url"]:
            per_post[key]["example_url"] = info.url

    posts_rows = sorted(per_post.values(), key=lambda r: int(r.get("amazon_links") or 0), reverse=True)

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        _write_csv_rows(
            out_dir / "amazon_links.csv",
            fieldnames=[
                "source_id",
                "source_slug",
                "source_title",
                "source_status",
                "url",
                "host",
                "is_amzn_short",
                "is_affiliate",
                "affiliate_tag",
                "anchor_text",
                "origin",
                "node_path",
                "rel",
                "rel_has_sponsored",
                "rel_has_nofollow",
            ],
            rows=amazon_rows,
        )
        _write_csv_rows(
            out_dir / "amazon_posts_summary.csv",
            fieldnames=[
                "source_id",
                "source_slug",
                "source_title",
                "source_status",
                "amazon_links",
                "amazon_affiliate_links",
                "amzn_short_links",
                "amazon_lexical_links",
                "amazon_lexical_links_missing_sponsored",
                "example_url",
            ],
            rows=posts_rows,
        )
        (out_dir / "amazon_summary.json").write_text(
            json.dumps(
                {
                    "filter": final_filter,
                    "posts_seen": len(posts),
                    "links_total": len(occurrences),
                    "amazon_links_total": len(amazon_rows),
                    "posts_with_amazon_links": sum(1 for r in posts_rows if int(r.get("amazon_links") or 0) > 0),
                    "posts_with_affiliate_tag": sum(1 for r in posts_rows if int(r.get("amazon_affiliate_links") or 0) > 0),
                    "posts_with_lexical_links_missing_sponsored": len(posts_with_missing_sponsored),
                    "parse_warnings": parse_warnings if parse_warnings else None,
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    ctx["out"].print(
        {
            "filter": final_filter,
            "posts_seen": len(posts),
            "links_total": len(occurrences),
            "amazon_links_total": len(amazon_rows),
            "posts_with_amazon_links": sum(1 for r in posts_rows if int(r.get("amazon_links") or 0) > 0),
            "posts_with_affiliate_tag": sum(1 for r in posts_rows if int(r.get("amazon_affiliate_links") or 0) > 0),
            "posts_with_lexical_links_missing_sponsored": len(posts_with_missing_sponsored),
            "parse_warnings_count": len(parse_warnings),
            "out_dir": str(out_dir) if out_dir is not None else None,
        }
    )
    return 0
