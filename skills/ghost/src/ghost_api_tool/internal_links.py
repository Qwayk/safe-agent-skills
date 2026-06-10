from __future__ import annotations

import csv
import dataclasses
import html as html_lib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


_A_HREF_RE = re.compile(
    r"""<a\b[^>]*\bhref=(?P<q>["'])(?P<href>.*?)(?P=q)[^>]*>(?P<body>.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")

_GENERIC_ANCHORS = {
    "click here",
    "here",
    "read more",
    "learn more",
    "this",
    "this link",
}


@dataclasses.dataclass(frozen=True)
class LinkOccurrence:
    source_id: str
    source_slug: str
    source_title: str
    source_status: str
    url: str
    anchor_text: str
    rel: str | None
    origin: str  # lexical_link | html_card
    node_path: str | None


@dataclasses.dataclass(frozen=True)
class TargetRef:
    kind: str  # post|page|tag|author|other
    slug: str | None
    url: str
    host: str | None
    path: str


@dataclasses.dataclass(frozen=True)
class ResolvedTarget:
    kind: str  # post|page|unknown
    id: str | None
    slug: str | None
    url: str


def _strip_html(s: str) -> str:
    return html_lib.unescape(_TAG_RE.sub("", s or "")).strip()


def _extract_text_from_lexical(node: Any) -> str:
    if isinstance(node, dict):
        t = node.get("type")
        if t in ("extended-text", "text") and isinstance(node.get("text"), str):
            return node["text"]
        children = node.get("children")
        if isinstance(children, list):
            return "".join(_extract_text_from_lexical(c) for c in children)
        return "".join(_extract_text_from_lexical(v) for v in node.values() if isinstance(v, (dict, list)))
    if isinstance(node, list):
        return "".join(_extract_text_from_lexical(v) for v in node)
    return ""


def extract_links_from_lexical(
    lexical_obj: dict[str, Any],
    *,
    source_id: str,
    source_slug: str,
    source_title: str,
    source_status: str,
) -> list[LinkOccurrence]:
    out: list[LinkOccurrence] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            node_type = node.get("type")
            if node_type == "link":
                url = node.get("url")
                if isinstance(url, str) and url.strip():
                    rel = node.get("rel")
                    out.append(
                        LinkOccurrence(
                            source_id=source_id,
                            source_slug=source_slug,
                            source_title=source_title,
                            source_status=source_status,
                            url=url.strip(),
                            anchor_text=_extract_text_from_lexical(node),
                            rel=rel if isinstance(rel, str) else None,
                            origin="lexical_link",
                            node_path=path,
                        )
                    )
            if node_type == "html":
                html = node.get("html")
                if isinstance(html, str) and html.strip():
                    for m in _A_HREF_RE.finditer(html):
                        href = (m.group("href") or "").strip()
                        if not href:
                            continue
                        out.append(
                            LinkOccurrence(
                                source_id=source_id,
                                source_slug=source_slug,
                                source_title=source_title,
                                source_status=source_status,
                                url=href,
                                anchor_text=_strip_html(m.group("body") or ""),
                                rel=None,
                                origin="html_card",
                                node_path=path,
                            )
                        )
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(lexical_obj, "root")
    return out


def classify_target(
    url: str,
    *,
    internal_hosts: set[str],
) -> tuple[bool, TargetRef]:
    raw = (url or "").strip()
    if not raw:
        return False, TargetRef(kind="other", slug=None, url=url, host=None, path="")

    # Relative links are internal by definition.
    if raw.startswith("/"):
        path = raw
        slug = _slug_from_path(path)
        kind = _kind_from_path(path)
        return True, TargetRef(kind=kind, slug=slug, url=raw, host=None, path=path)

    try:
        p = urlparse(raw)
    except Exception:
        return False, TargetRef(kind="other", slug=None, url=raw, host=None, path="")

    host = (p.hostname or "").lower() if p.hostname else None
    path = p.path or ""
    is_internal = bool(host and host in internal_hosts)
    kind = _kind_from_path(path)
    slug = _slug_from_path(path)
    norm_url = raw
    return is_internal, TargetRef(kind=kind, slug=slug, url=norm_url, host=host, path=path)


def _kind_from_path(path: str) -> str:
    p = (path or "").strip()
    if not p.startswith("/"):
        return "other"
    parts = [x for x in p.strip("/").split("/") if x]
    if not parts:
        return "other"
    if parts[0] == "tag":
        return "tag"
    if parts[0] == "author":
        return "author"
    return "post_or_page"


def _slug_from_path(path: str) -> str | None:
    p = (path or "").strip()
    if not p.startswith("/"):
        return None
    parts = [x for x in p.strip("/").split("/") if x]
    if not parts:
        return None
    if parts[0] in ("tag", "author"):
        return parts[1] if len(parts) >= 2 else None
    # Most Ghost post/page URLs are /{slug}/
    if len(parts) == 1:
        return parts[0]
    return None


def _norm_url(u: str) -> str:
    s = (u or "").strip()
    if s.endswith("/") and s != "/":
        s = s[:-1]
    return s


def resolve_targets(
    occurrences: list[LinkOccurrence],
    *,
    internal_hosts: set[str],
    post_index_by_slug: dict[str, str],
    page_index_by_slug: dict[str, str],
    url_index: dict[str, ResolvedTarget],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Returns:
    - edges: list of link edge dicts with resolution metadata
    - summary: counts and issue flags
    """
    edges: list[dict[str, Any]] = []
    counts = Counter()
    anchor_flags = Counter()
    unresolved_internal: list[dict[str, Any]] = []

    for occ in occurrences:
        counts["links_total"] += 1

        is_internal, tref = classify_target(occ.url, internal_hosts=internal_hosts)
        counts["links_internal" if is_internal else "links_external"] += 1

        resolved = None
        if is_internal:
            # Try resolution by URL first (exact-ish).
            resolved = url_index.get(_norm_url(tref.url)) or url_index.get(_norm_url(tref.path))
            if resolved is None and tref.slug and tref.kind == "post_or_page":
                if tref.slug in post_index_by_slug:
                    resolved = ResolvedTarget(kind="post", id=post_index_by_slug[tref.slug], slug=tref.slug, url=tref.url)
                elif tref.slug in page_index_by_slug:
                    resolved = ResolvedTarget(kind="page", id=page_index_by_slug[tref.slug], slug=tref.slug, url=tref.url)
            if resolved is None:
                counts["internal_unresolved"] += 1
                unresolved_internal.append(
                    {
                        "source_id": occ.source_id,
                        "source_slug": occ.source_slug,
                        "url": occ.url,
                        "anchor_text": occ.anchor_text,
                        "origin": occ.origin,
                        "node_path": occ.node_path,
                    }
                )

        anchor = (occ.anchor_text or "")
        a_norm = " ".join(anchor.strip().split()).casefold()
        if not a_norm:
            anchor_flags["empty"] += 1
        if a_norm in _GENERIC_ANCHORS:
            anchor_flags["generic"] += 1
        if len(anchor) > 140:
            anchor_flags["too_long"] += 1
        if (anchor[:1].isspace() or anchor[-1:].isspace()) and anchor:
            anchor_flags["edge_whitespace"] += 1

        edges.append(
            {
                "source": {
                    "id": occ.source_id,
                    "slug": occ.source_slug,
                    "title": occ.source_title,
                    "status": occ.source_status,
                },
                "link": {
                    "url": occ.url,
                    "anchor_text": occ.anchor_text,
                    "origin": occ.origin,
                    "node_path": occ.node_path,
                },
                "target": {
                    "is_internal": is_internal,
                    "kind": tref.kind,
                    "slug": tref.slug,
                    "resolved_kind": resolved.kind if resolved else None,
                    "resolved_id": resolved.id if resolved else None,
                    "resolved_slug": resolved.slug if resolved else None,
                    "resolved_url": resolved.url if resolved else None,
                },
            }
        )

    summary: dict[str, Any] = {
        "counts": dict(counts),
        "anchor_flags": dict(anchor_flags),
        "unresolved_internal_sample": unresolved_internal[:25] if unresolved_internal else None,
    }
    return edges, summary


def write_orphans_csv(
    path: Path,
    *,
    posts: list[dict[str, Any]],
    inbound_sources_by_post_id: dict[str, set[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["post_id", "slug", "status", "title", "inbound_sources"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for p in posts:
            pid = str(p.get("id") or "")
            w.writerow(
                {
                    "post_id": pid,
                    "slug": str(p.get("slug") or ""),
                    "status": str(p.get("status") or ""),
                    "title": str(p.get("title") or ""),
                    "inbound_sources": str(len(inbound_sources_by_post_id.get(pid, set()))),
                }
            )


def write_unresolved_internal_csv(path: Path, unresolved: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["source_id", "source_slug", "url", "anchor_text", "origin", "node_path"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for row in unresolved:
            w.writerow({k: row.get(k, "") for k in header})


def inbound_sources_from_edges(edges: list[dict[str, Any]]) -> dict[str, set[str]]:
    inbound: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        tgt = (e.get("target") or {})
        if tgt.get("resolved_kind") != "post":
            continue
        target_id = tgt.get("resolved_id")
        source_id = ((e.get("source") or {}).get("id"))
        if isinstance(target_id, str) and target_id and isinstance(source_id, str) and source_id:
            if target_id != source_id:
                inbound[target_id].add(source_id)
    return inbound


def build_url_index(posts: list[dict[str, Any]], pages: list[dict[str, Any]]) -> dict[str, ResolvedTarget]:
    idx: dict[str, ResolvedTarget] = {}
    for p in posts:
        pid = str(p.get("id") or "")
        slug = p.get("slug")
        url = p.get("url")
        if isinstance(url, str) and url.strip():
            idx[_norm_url(url)] = ResolvedTarget(kind="post", id=pid, slug=str(slug or ""), url=url)
        if isinstance(slug, str) and slug.strip():
            idx[_norm_url(f"/{slug.strip()}/")] = ResolvedTarget(kind="post", id=pid, slug=slug.strip(), url=str(url or ""))  # best effort
    for pg in pages:
        pid = str(pg.get("id") or "")
        slug = pg.get("slug")
        url = pg.get("url")
        if isinstance(url, str) and url.strip():
            idx[_norm_url(url)] = ResolvedTarget(kind="page", id=pid, slug=str(slug or ""), url=url)
        if isinstance(slug, str) and slug.strip():
            idx[_norm_url(f"/{slug.strip()}/")] = ResolvedTarget(kind="page", id=pid, slug=slug.strip(), url=str(url or ""))  # best effort
    return idx


def internal_hosts_from_site_url(site_url: str, extra_hosts: list[str] | None) -> set[str]:
    hosts: set[str] = set()
    try:
        p = urlparse(site_url)
        if p.hostname:
            hosts.add(p.hostname.lower())
    except Exception:
        pass
    for h in extra_hosts or []:
        hh = (h or "").strip().lower()
        if hh:
            hosts.add(hh)
    return hosts
