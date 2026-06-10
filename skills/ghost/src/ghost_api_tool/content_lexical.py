from __future__ import annotations

import dataclasses
import html
import json
import re
from collections.abc import Iterator
from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

from .diffutil import stable_json, unified_diff
from .amazon_links import is_amazon_link
from .errors import ValidationError


@dataclasses.dataclass(frozen=True)
class LexicalImage:
    index: int
    path: str
    src: str
    alt: str | None
    title: str | None
    caption: str | None
    caption_text: str | None
    context_heading: str | None


@dataclasses.dataclass(frozen=True)
class LexicalEditReport:
    refused: bool
    reasons: list[str]
    matched: int
    changed: bool
    diff: str | None


@dataclasses.dataclass(frozen=True)
class ReplaceManyItemResult:
    old_src: str
    new_src: str
    matched: int
    changed: bool
    reasons: list[str]


_TAG_RE = re.compile(r"<[^>]+>")
_A_HREF_RE = re.compile(
    r"""<a\b[^>]*\bhref=(?P<q>["'])(?P<href>.*?)(?P=q)[^>]*>(?P<body>.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
_HTML_OL_LI_RE = re.compile(r"<ol\b[^>]*>.*?<li\b[^>]*>(?P<li>.*?)</li>.*?</ol>", re.IGNORECASE | re.DOTALL)
_HTML_UL_LI_RE = re.compile(r"<ul\b(?P<ul_attrs>[^>]*)>.*?<li\b[^>]*>(?P<li>.*?)</li>.*?</ul>", re.IGNORECASE | re.DOTALL)
_HTML_OL_LI_WITH_ATTRS_RE = re.compile(r"<ol\b(?P<ol_attrs>[^>]*)>.*?<li\b[^>]*>(?P<li>.*?)</li>.*?</ol>", re.IGNORECASE | re.DOTALL)
_HTML_START_ATTR_RE = re.compile(r"\bstart\s*=\s*[\"']?(?P<start>\d+)[\"']?", re.IGNORECASE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_LIST_TAG_RE = re.compile(r"<(?P<close>/?)\s*(?P<tag>ul|ol|li)\b[^>]*>", re.IGNORECASE)
_HTML_OL_OPEN_RE = re.compile(r"<ol\b(?P<attrs>[^>]*)>", re.IGNORECASE)
_HTML_UL_OPEN_RE = re.compile(r"<ul\b(?P<attrs>[^>]*)>", re.IGNORECASE)
_HTML_STANDALONE_IMG_RE = re.compile(
    r"^\s*(?:<!--.*?-->\s*)*(?:<figure\b[^>]*>\s*)?(?:<p\b[^>]*>\s*)?<img\b[^>]*>\s*(?:</p>\s*)?(?:</figure>\s*)*(?:<!--.*?-->\s*)*$",
    re.IGNORECASE | re.DOTALL,
)
_LEADING_WS_RE = re.compile(r"^[\s\u00A0]+")
_TRAILING_WS_RE = re.compile(r"[\s\u00A0]+$")


def _to_path(path: list[str | int]) -> str:
    out: list[str] = []
    for p in path:
        if isinstance(p, int):
            out.append(f"[{p}]")
        else:
            if out:
                out.append(".")
            out.append(p)
    return "".join(out)


def parse_lexical_field(lexical: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if lexical is None:
        return None, ["Missing lexical field"]
    if isinstance(lexical, str):
        try:
            obj = json.loads(lexical)
        except json.JSONDecodeError as e:
            return None, [f"Lexical JSON decode failed: {e}"]
        if not isinstance(obj, dict):
            return None, ["Lexical root must be a JSON object"]
        return obj, []
    if isinstance(lexical, dict):
        return lexical, []
    return None, [f"Unsupported lexical type: {type(lexical).__name__}"]


def dump_lexical_field(obj: dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _iter_nodes(obj: Any, *, path: list[str | int] | None = None) -> Iterator[tuple[list[str | int], dict[str, Any]]]:
    if path is None:
        path = []
    if isinstance(obj, dict):
        yield path, obj
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                yield from _iter_nodes(v, path=path + [k])
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                yield from _iter_nodes(v, path=path + [i])


def _extract_text(node: Any) -> str:
    if isinstance(node, dict):
        if isinstance(node.get("text"), str):
            return node["text"]
        parts: list[str] = []
        for v in node.values():
            if isinstance(v, (dict, list)):
                parts.append(_extract_text(v))
        return "".join(parts)
    if isinstance(node, list):
        return "".join(_extract_text(v) for v in node)
    return ""


def _normalize_heading(s: str) -> str:
    return " ".join(s.strip().split()).casefold()


def _is_heading_node(node: dict[str, Any]) -> bool:
    t = node.get("type")
    return t in ("extended-heading", "heading")


def _is_image_node(node: dict[str, Any]) -> bool:
    return node.get("type") == "image" and isinstance(node.get("src"), str)


def _default_image_template() -> dict[str, Any]:
    return {
        "type": "image",
        "version": 1,
        "src": "",
        "width": None,
        "height": None,
        "title": "",
        "alt": "",
        "caption": _normalize_caption_input(""),
        "cardWidth": "regular",
        "href": "",
    }


def _strip_caption_html(caption: str) -> str:
    return html.unescape(_TAG_RE.sub("", caption)).strip()


def _normalize_caption_input(caption: str) -> str:
    c = caption.strip()
    if _TAG_RE.search(c):
        return c
    return f'<span style="white-space: pre-wrap;">{html.escape(c)}</span>'


def _changed_and_diff(before_obj: dict[str, Any], after_obj: dict[str, Any], *, include_diff: bool) -> tuple[bool, str | None]:
    before_s = stable_json(before_obj)
    after_s = stable_json(after_obj)
    changed = before_s != after_s
    diff = unified_diff(before_s, after_s) if include_diff and changed else None
    return changed, diff


def _is_text_node(node: Any) -> bool:
    return isinstance(node, dict) and node.get("type") in ("extended-text", "text") and isinstance(node.get("text"), str)


def _collect_text_nodes(node: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    def walk(n: Any) -> None:
        if _is_text_node(n):
            out.append(n)
            return
        if isinstance(n, dict):
            children = n.get("children")
            if isinstance(children, list):
                for c in children:
                    walk(c)
                return
            for v in n.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(node)
    return out


def _cleanup_empty_text_nodes(node: Any) -> None:
    if isinstance(node, dict):
        children = node.get("children")
        if isinstance(children, list):
            kept: list[Any] = []
            for c in children:
                _cleanup_empty_text_nodes(c)
                if _is_text_node(c) and c.get("text") == "":
                    continue
                kept.append(c)
            node["children"] = kept
        for v in node.values():
            if isinstance(v, (dict, list)):
                _cleanup_empty_text_nodes(v)
    elif isinstance(node, list):
        for v in node:
            _cleanup_empty_text_nodes(v)


_BOLD_FORMAT_MASK = 1


def audit_heading_bold(
    lexical_obj: dict[str, Any],
    *,
    max_examples: int = 10,
) -> dict[str, Any]:
    """
    Inspect heading nodes and report whether any heading text nodes use bold formatting.

    Notes:
    - Heading nodes are `type=extended-heading` and `type=heading`.
    - Bold is represented by bit 1 in the Lexical text node `format` integer.
    """
    examples: list[dict[str, Any]] = []
    heading_nodes_total = 0
    heading_nodes_with_bold = 0
    bold_text_nodes_total = 0

    for path, node in _iter_nodes(lexical_obj):
        if not _is_heading_node(node):
            continue
        heading_nodes_total += 1
        text_nodes = _collect_text_nodes(node)
        bold_nodes = 0
        for t in text_nodes:
            fmt = t.get("format")
            if isinstance(fmt, int) and (fmt & _BOLD_FORMAT_MASK):
                bold_nodes += 1
        if bold_nodes:
            heading_nodes_with_bold += 1
            bold_text_nodes_total += bold_nodes
            if len(examples) < max_examples:
                examples.append(
                    {
                        "path": _to_path(path),
                        "tag": node.get("tag"),
                        "text": _extract_text(node).strip(),
                        "bold_text_nodes": bold_nodes,
                    }
                )

    return {
        "heading_nodes_total": heading_nodes_total,
        "heading_nodes_with_bold": heading_nodes_with_bold,
        "bold_text_nodes_total": bold_text_nodes_total,
        "examples": examples,
    }


def clear_heading_bold(
    lexical_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Remove bold formatting from all heading text nodes (Lexical headings only).

    This does NOT change the heading text or structure; it only clears the bold bit on text nodes.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)

    matched = 0
    for _path, node in _iter_nodes(out):
        if not _is_heading_node(node):
            continue
        changed_this_heading = False
        for t in _collect_text_nodes(node):
            fmt = t.get("format")
            if not isinstance(fmt, int):
                continue
            if fmt & _BOLD_FORMAT_MASK:
                t["format"] = fmt & ~_BOLD_FORMAT_MASK
                changed_this_heading = True
        if changed_this_heading:
            matched += 1

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out,
    )


def fix_link_whitespace(
    lexical_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Fix link underline artifacts caused by leading/trailing whitespace inside a link node.

    Strategy:
    - For each Lexical `type=link` node, trim leading/trailing whitespace (including NBSP) from its text nodes.
    - Move the trimmed whitespace to plain text nodes immediately before/after the link (siblings).

    Safety:
    - Does not alter link URLs.
    - If a link ends up with no visible text after trimming, removes the empty link node and keeps only the whitespace.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing children list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)

    matched = 0

    def insert_ws_sibling(parent_children: list[Any], index: int, ws: str, template_node: dict[str, Any]) -> None:
        if not ws:
            return
        new_node = dict(template_node)
        new_node["text"] = ws
        parent_children.insert(index, new_node)

    def trim_link_in_parent(parent_children: list[Any]) -> None:
        nonlocal matched
        i = 0
        while i < len(parent_children):
            node = parent_children[i]
            if isinstance(node, dict) and node.get("type") == "link":
                text_nodes = _collect_text_nodes(node)
                if not text_nodes:
                    i += 1
                    continue

                first = text_nodes[0]
                last = text_nodes[-1]
                first_text = first.get("text") or ""
                last_text = last.get("text") or ""

                lead_m = _LEADING_WS_RE.match(first_text)
                trail_m = _TRAILING_WS_RE.search(last_text)
                lead_ws = lead_m.group(0) if lead_m else ""
                trail_ws = trail_m.group(0) if trail_m else ""
                if first is last and lead_ws and trail_ws and (len(lead_ws) + len(trail_ws) > len(first_text)):
                    # Avoid overlapping leading/trailing matches (e.g. link text is only whitespace).
                    trail_ws = ""

                if lead_ws or trail_ws:
                    matched += 1

                    if lead_ws:
                        first["text"] = first_text[len(lead_ws) :]
                        insert_ws_sibling(parent_children, i, lead_ws, template_node=first)
                        i += 1  # keep i pointing at the link after insertion

                    if trail_ws:
                        last["text"] = last_text[: -len(trail_ws)] if trail_ws else last_text

                    _cleanup_empty_text_nodes(node)

                    # If link now has no visible text, remove it (keep only whitespace siblings we inserted).
                    remaining_text_nodes = _collect_text_nodes(node)
                    remaining_text = "".join((tn.get("text") or "") for tn in remaining_text_nodes)
                    if remaining_text == "":
                        parent_children.pop(i)
                        # If we removed link and there is trailing whitespace, insert it where link used to be.
                        if trail_ws:
                            insert_ws_sibling(parent_children, i, trail_ws, template_node=last)
                        continue

                    if trail_ws:
                        insert_ws_sibling(parent_children, i + 1, trail_ws, template_node=last)
                        i += 1

            if isinstance(node, dict):
                ch = node.get("children")
                if isinstance(ch, list):
                    trim_link_in_parent(ch)
            i += 1

    trim_link_in_parent(out["root"]["children"])

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def set_paid_rel_on_amazon_links(
    lexical_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Ensure Amazon links are marked as paid/sponsored.

    Applies to Lexical `type=link` nodes whose `url` is an Amazon link (`amazon.*` or `amzn.to`).

    Behavior:
    - Ensures the link node `rel` contains: noreferrer noopener sponsored nofollow
    - Preserves any existing rel tokens (adds missing tokens only)

    Notes:
    - This only edits Lexical link nodes. Links inside HTML cards are not modified by this function.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)

    matched = 0
    required = ["noreferrer", "noopener", "sponsored", "nofollow"]

    def normalize_rel(rel: Any) -> str:
        if not isinstance(rel, str):
            tokens: list[str] = []
        else:
            tokens = [t.strip().lower() for t in rel.split() if t.strip()]
        seen: set[str] = set()
        keep: list[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                keep.append(t)
        for req in required:
            if req not in seen:
                seen.add(req)
                keep.append(req)
        return " ".join(keep)

    def walk(node: Any) -> None:
        nonlocal matched
        if isinstance(node, dict):
            if node.get("type") == "link" and isinstance(node.get("url"), str) and is_amazon_link(node.get("url", "")):
                matched += 1
                before_rel = node.get("rel")
                after_rel = normalize_rel(before_rel)
                if before_rel != after_rel:
                    node["rel"] = after_rel
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(out)
    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def set_paid_rel_on_links(
    lexical_obj: dict[str, Any],
    *,
    match_url: Any,
    required_tokens: list[str],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Generic "paid link rel" fixer for Lexical link nodes.

    - Only touches Lexical nodes where `type == "link"` and `url` is a string.
    - Links inside HTML cards are not modified by this function.
    - Preserves existing rel tokens (keeps order, de-dupes) and appends missing required tokens.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    if not callable(match_url):
        raise RuntimeError("Internal error: match_url must be callable")

    req = [str(t).strip().lower() for t in required_tokens if str(t).strip()]
    if not req:
        raise ValidationError("required_tokens must be a non-empty list")

    before = lexical_obj
    out = deepcopy(lexical_obj)
    matched = 0

    def normalize_rel(rel: Any) -> str:
        if not isinstance(rel, str):
            tokens: list[str] = []
        else:
            tokens = [t.strip().lower() for t in rel.split() if t.strip()]
        seen: set[str] = set()
        keep: list[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                keep.append(t)
        for t in req:
            if t not in seen:
                seen.add(t)
                keep.append(t)
        return " ".join(keep)

    def walk(node: Any) -> None:
        nonlocal matched
        if isinstance(node, dict):
            if node.get("type") == "link" and isinstance(node.get("url"), str):
                url = node.get("url") or ""
                try:
                    is_match = bool(match_url(url))
                except Exception as e:  # noqa: BLE001
                    raise RuntimeError(f"URL matcher failed for {url!r}: {e}") from e
                if is_match:
                    matched += 1
                    before_rel = node.get("rel")
                    after_rel = normalize_rel(before_rel)
                    if before_rel != after_rel:
                        node["rel"] = after_rel
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(out)
    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def unlink_links_by_url(
    lexical_obj: dict[str, Any],
    *,
    urls: list[str],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Remove hyperlinks for the specified URLs while keeping the visible text.

    Applies to Lexical `type=link` nodes whose `url` matches any URL in `urls`
    (exact match after `.strip()`).

    Behavior:
    - Replaces the link node with its children (unwraps the link).
    - If a matched link has no children, it is removed.
    - Only edits Lexical link nodes. Links inside HTML cards are not modified.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    targets = {str(u).strip() for u in urls if str(u).strip()}
    if not targets:
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Provide at least one non-empty URL"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    matched = 0

    def unwrap_in_children(children: list[Any]) -> None:
        nonlocal matched
        i = 0
        while i < len(children):
            n = children[i]
            if isinstance(n, dict) and n.get("type") == "link" and isinstance(n.get("url"), str):
                if n["url"].strip() in targets:
                    matched += 1
                    link_children = n.get("children")
                    if isinstance(link_children, list) and link_children:
                        children[i : i + 1] = link_children
                        i += len(link_children)
                        continue
                    children.pop(i)
                    continue

            if isinstance(n, dict):
                ch = n.get("children")
                if isinstance(ch, list):
                    unwrap_in_children(ch)
            elif isinstance(n, list):
                unwrap_in_children(n)
            i += 1

    root_children = out.get("root", {}).get("children")
    if isinstance(root_children, list):
        unwrap_in_children(root_children)
    _cleanup_empty_text_nodes(out.get("root", {}))

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def unlink_links_by_url_after_heading(
    lexical_obj: dict[str, Any],
    *,
    after_heading: str,
    urls: list[str],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Unlink (unwrap) specific URLs only in the section after a top-level H2 heading.

    Scope:
    - Finds the first top-level Lexical H2 heading (root.children) whose text matches after_heading
      (case/whitespace-insensitive).
    - Applies unlinking only to nodes after that heading, stopping at the next top-level H2 (or end).

    This is useful for removing a duplicate link in a specific section (example: Conclusion),
    without affecting the same URL elsewhere (example: a related-links block).
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    targets = {str(u).strip() for u in urls if str(u).strip()}
    if not targets:
        return (
            LexicalEditReport(refused=True, reasons=["Provide at least one non-empty URL"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    heading_norm = _normalize_heading(after_heading)

    def is_h2_heading(node: Any) -> bool:
        return (
            isinstance(node, dict)
            and node.get("type") == "extended-heading"
            and node.get("tag") == "h2"
            and _normalize_heading(_extract_text(node)) == heading_norm
        )

    start_idx = None
    for i, node in enumerate(children):
        if is_h2_heading(node):
            start_idx = i
            break
    if start_idx is None:
        # Safe no-op: the requested section is missing, so there is nothing to delete.
        return (
            LexicalEditReport(refused=False, reasons=[f"Heading not found: {after_heading!r}"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    # Stop at the next top-level H2 heading after the target.
    end_idx = len(children)
    for j in range(start_idx + 1, len(children)):
        node = children[j]
        if isinstance(node, dict) and node.get("type") == "extended-heading" and node.get("tag") == "h2":
            end_idx = j
            break

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]
    matched = 0

    def unwrap_in_children(children_list: list[Any]) -> None:
        nonlocal matched
        i = 0
        while i < len(children_list):
            n = children_list[i]
            if isinstance(n, dict) and n.get("type") == "link" and isinstance(n.get("url"), str):
                if n["url"].strip() in targets:
                    matched += 1
                    link_children = n.get("children")
                    if isinstance(link_children, list) and link_children:
                        children_list[i : i + 1] = link_children
                        i += len(link_children)
                        continue
                    children_list.pop(i)
                    continue
            if isinstance(n, dict):
                ch = n.get("children")
                if isinstance(ch, list):
                    unwrap_in_children(ch)
            elif isinstance(n, list):
                unwrap_in_children(n)
            i += 1

    # Apply only in range (after the heading).
    for node in out_children[start_idx + 1 : end_idx]:
        if isinstance(node, dict):
            ch = node.get("children")
            if isinstance(ch, list):
                unwrap_in_children(ch)
        elif isinstance(node, list):
            unwrap_in_children(node)
    _cleanup_empty_text_nodes(out.get("root", {}))

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def delete_linked_list_items_by_url_after_heading(
    lexical_obj: dict[str, Any],
    *,
    after_heading: str,
    urls: list[str],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Delete list items (or whole blocks) that contain specific link URLs, only after a top-level H2 heading.

    Scope:
    - Finds the first top-level Lexical H2 heading (root.children) whose text matches after_heading
      (case/whitespace-insensitive).
    - Applies deletion only to nodes after that heading, stopping at the next top-level H2 (or end).

    Behavior:
    - For list nodes, removes any listitem that contains a matching link URL anywhere inside it.
    - Removes any list node that becomes empty.
    - If no list items remain in the section after deletions, removes the whole section:
      the H2 heading + all nodes until the next H2.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    targets = {str(u).strip() for u in urls if str(u).strip()}
    if not targets:
        return (
            LexicalEditReport(refused=True, reasons=["Provide at least one non-empty URL"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    heading_norm = _normalize_heading(after_heading)

    def is_h2_heading(node: Any) -> bool:
        return (
            isinstance(node, dict)
            and node.get("type") == "extended-heading"
            and node.get("tag") == "h2"
            and _normalize_heading(_extract_text(node)) == heading_norm
        )

    def find_section_bounds(root_children: list[Any], start: int) -> tuple[int, int]:
        end = len(root_children)
        for j in range(start + 1, len(root_children)):
            node = root_children[j]
            if isinstance(node, dict) and node.get("type") == "extended-heading" and node.get("tag") == "h2":
                end = j
                break
        return start, end

    start_idx = None
    for i, node in enumerate(children):
        if is_h2_heading(node):
            start_idx = i
            break
    if start_idx is None:
        # Safe no-op: the requested section is missing, so there is nothing to delete.
        return (
            LexicalEditReport(refused=False, reasons=[f"Heading not found: {after_heading!r}"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]
    matched = 0

    def contains_target_link(node: Any) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "link" and isinstance(node.get("url"), str):
                if node["url"].strip() in targets:
                    return True
            ch = node.get("children")
            if isinstance(ch, list):
                return any(contains_target_link(c) for c in ch)
            return False
        if isinstance(node, list):
            return any(contains_target_link(c) for c in node)
        return False

    # Work only inside section after heading.
    start_idx, end_idx = find_section_bounds(out_children, start_idx)
    for i in range(start_idx + 1, end_idx):
        node = out_children[i]
        if not isinstance(node, dict):
            continue

        if node.get("type") == "list":
            li_children = node.get("children")
            if not isinstance(li_children, list):
                continue
            kept: list[Any] = []
            for li in li_children:
                if contains_target_link(li):
                    matched += 1
                else:
                    kept.append(li)
            node["children"] = kept
        else:
            # If a whole top-level block contains a matching link, drop the whole block.
            if contains_target_link(node):
                out_children[i] = None
                matched += 1

    # Remove null blocks and empty lists in the section.
    # Recompute bounds (they may shift after removals).
    out_children[:] = [n for n in out_children if n is not None]
    start_idx = None
    for i, node in enumerate(out_children):
        if is_h2_heading(node):
            start_idx = i
            break
    if start_idx is None:
        # If the heading disappeared somehow, treat as no-op.
        return (
            LexicalEditReport(refused=False, reasons=[], matched=matched, changed=False, diff=None),
            before,
        )
    start_idx, end_idx = find_section_bounds(out_children, start_idx)

    removed_empty_lists = 0
    new_slice: list[Any] = []
    for node in out_children[start_idx + 1 : end_idx]:
        if isinstance(node, dict) and node.get("type") == "list":
            ch = node.get("children")
            if not isinstance(ch, list) or not ch:
                removed_empty_lists += 1
                continue
        new_slice.append(node)

    out_children[start_idx + 1 : end_idx] = new_slice

    # If no list items remain, remove the entire section (heading + its content).
    start_idx, end_idx = find_section_bounds(out_children, start_idx)
    has_any_list_items = False
    for node in out_children[start_idx + 1 : end_idx]:
        if isinstance(node, dict) and node.get("type") == "list" and isinstance(node.get("children"), list) and node["children"]:
            has_any_list_items = True
            break
    if not has_any_list_items:
        del out_children[start_idx:end_idx]

    _cleanup_empty_text_nodes(out.get("root", {}))
    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def _is_internal_href(href: str, *, internal_hosts: set[str]) -> bool:
    raw = (href or "").strip()
    if not raw:
        return False
    if raw.startswith("/"):
        return True
    try:
        p = urlparse(raw)
    except Exception:
        return False
    host = (p.hostname or "").lower().strip() if p.hostname else ""
    return bool(host and host in internal_hosts)


def unlink_internal_links_in_image_captions(
    lexical_obj: dict[str, Any],
    *,
    internal_hosts: set[str],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Remove internal hyperlinks embedded inside Lexical image captions, keeping the visible text.

    Targets Lexical `type=image` nodes whose `caption` is an HTML string containing <a href="...">...</a>.
    If the href is internal (host matches internal_hosts, or href is relative), the <a> wrapper is removed
    and the inner HTML is kept.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )
    if not internal_hosts:
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Refused: internal_hosts is empty"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    matched = 0

    def unlink_anchors_in_html(html_str: str) -> tuple[str, int]:
        count = 0

        def repl(m: re.Match) -> str:
            nonlocal count
            href = html.unescape(m.group("href") or "").strip()
            if _is_internal_href(href, internal_hosts=internal_hosts):
                count += 1
                return m.group("body") or ""
            return m.group(0)

        return _A_HREF_RE.sub(repl, html_str), count

    def walk(node: Any) -> None:
        nonlocal matched
        if isinstance(node, dict):
            if node.get("type") == "image" and isinstance(node.get("caption"), str):
                caption = node.get("caption") or ""
                if "<a" in caption.lower() and "href=" in caption.lower():
                    new_caption, m = unlink_anchors_in_html(caption)
                    if m and new_caption != caption:
                        matched += m
                        node["caption"] = new_caption
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(out)
    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def insert_internal_links_section_before_heading(
    lexical_obj: dict[str, Any],
    *,
    before_heading: str,
    section_heading: str,
    intro_text: str,
    links: list[tuple[str, str]],
    skip_url: str | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Insert a standardized link section (H2 + paragraph + bullet list) before a top-level heading.

    - Searches top-level headings (root.children) matching before_heading (case/whitespace-insensitive).
    - If the heading is missing, inserts at end.
    - Refuses to insert if section_heading already exists as a top-level heading (idempotence guard).
    - Skips one link whose URL exactly matches skip_url (if provided).
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    target_heading = _normalize_heading(before_heading)
    section_heading_norm = _normalize_heading(section_heading)

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    # Idempotence guard: if section heading already exists, do nothing.
    for node in out_children:
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == section_heading_norm:
                return (
                    LexicalEditReport(refused=False, reasons=["Section already present"], matched=0, changed=False, diff=None),
                    before,
                )

    # Find insertion point (before first matching heading).
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == target_heading:
                heading_idxs.append(i)

    insert_idx = heading_idxs[0] if heading_idxs else len(out_children)

    # Build section nodes.
    h2 = {
        "type": "extended-heading",
        "version": 1,
        "tag": "h2",
        "direction": None,
        "format": "",
        "indent": 0,
        "children": [
            {"type": "extended-text", "version": 1, "text": section_heading, "format": 1, "detail": 0, "mode": "normal", "style": ""}
        ],
    }
    para = {
        "type": "paragraph",
        "version": 1,
        "direction": None,
        "format": "",
        "indent": 0,
        "children": [
            {"type": "extended-text", "version": 1, "text": intro_text, "format": 0, "detail": 0, "mode": "normal", "style": ""}
        ],
    }

    skip = (skip_url or "").strip()
    items: list[tuple[str, str]] = []
    for a, u in links:
        anchor = (a or "").strip()
        url = (u or "").strip()
        if not anchor or not url:
            continue
        if skip and url == skip:
            continue
        items.append((anchor, url))

    if not items:
        return (
            LexicalEditReport(refused=True, reasons=["Refused: no links to insert after filtering"], matched=0, changed=False, diff=None),
            before,
        )

    list_items: list[dict[str, Any]] = []
    value = 1
    for anchor, url in items:
        link_node = {
            "type": "link",
            "version": 1,
            "direction": None,
            "format": "",
            "indent": 0,
            "rel": None,
            "target": None,
            "title": None,
            "url": url,
            "children": [{"type": "extended-text", "version": 1, "text": anchor, "format": 0, "detail": 0, "mode": "normal", "style": ""}],
        }
        list_items.append({"type": "listitem", "version": 1, "value": value, "children": [link_node]})
        value += 1
    ul = {"type": "list", "version": 1, "listType": "bullet", "tag": "ul", "children": list_items}

    out_children[insert_idx:insert_idx] = [h2, para, ul]

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=len(items), changed=changed, diff=diff),
        out if changed else before,
    )


def linkify_text_in_paragraph(
    lexical_obj: dict[str, Any],
    *,
    paragraph_contains: str,
    paragraph_occurrence: int | None,
    anchor_text: str,
    anchor_occurrence: int | None,
    url: str,
    include_list_items: bool,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Wrap a specific anchor_text inside a paragraph node with a Lexical link node.

    Safety (fail-closed):
    - Selects the paragraph by a required `paragraph_contains` substring (case-insensitive), with optional occurrence.
    - When include_list_items is set, also selects listitem nodes.
    - Refuses on ambiguous paragraph match unless occurrence is provided.
    - Only linkifies anchors that live entirely inside a single direct text child node of that paragraph.
      (No cross-node matching; no nested links.)
    - Refuses if anchor_text has leading/trailing whitespace (avoids underline/whitespace artifacts).
    - Idempotent: if a link node already exists with the same url + anchor_text in the target paragraph, no-ops.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    needle = " ".join((paragraph_contains or "").strip().split())
    if not needle:
        return (
            LexicalEditReport(refused=True, reasons=["Refused: paragraph_contains must be non-empty"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    anchor = str(anchor_text or "")
    if not anchor.strip():
        return (
            LexicalEditReport(refused=True, reasons=["Refused: anchor_text must be non-empty"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    if anchor != anchor.strip():
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Refused: anchor_text has leading/trailing whitespace (would create underline artifacts)"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )
    link_url = (url or "").strip()
    if not link_url:
        return (
            LexicalEditReport(refused=True, reasons=["Refused: url must be non-empty"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)

    matches: list[tuple[list[str | int], dict[str, Any], str]] = []
    target_types = {"paragraph"}
    if include_list_items:
        target_types.add("listitem")
    for path, node in _iter_nodes(out):
        if not (isinstance(node, dict) and node.get("type") in target_types):
            continue
        txt = " ".join(_extract_text(node).strip().split())
        if not txt:
            continue
        if needle.casefold() in txt.casefold():
            matches.append((path, node, txt))

    label = "paragraph" if not include_list_items else "paragraph/list item"
    if not matches:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"No {label} matched paragraph_contains"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    if len(matches) > 1 and paragraph_occurrence is None:
        examples = [m[2][:80] + ("…" if len(m[2]) > 80 else "") for m in matches[:3]]
        return (
            LexicalEditReport(
                refused=True,
                reasons=[
                    f"Refused: {label} matched multiple times ({len(matches)}); pass --paragraph-occurrence",
                    *([f"Example: {e}" for e in examples] if examples else []),
                ],
                matched=len(matches),
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = paragraph_occurrence or 1
    if occ < 1 or occ > len(matches):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"paragraph-occurrence out of range (1..{len(matches)})"],
                matched=len(matches),
                changed=False,
                diff=None,
            ),
            before,
        )

    target_path, para, _ = matches[occ - 1]
    children = para.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Refused: paragraph has no children list"], matched=1, changed=False, diff=None),
            before,
        )

    # Idempotence: if the exact anchor is already linked to the same URL inside this paragraph, no-op.
    for ch in children:
        if isinstance(ch, dict) and ch.get("type") == "link" and (ch.get("url") or "").strip() == link_url:
            if " ".join(_extract_text(ch).strip().split()) == anchor:
                return (
                    LexicalEditReport(refused=False, reasons=["Anchor already linked"], matched=1, changed=False, diff=None),
                    before,
                )

    # Find anchor occurrences inside direct text nodes.
    occurrences: list[tuple[int, int]] = []  # (child_idx, start_pos)
    for i, ch in enumerate(children):
        if not _is_text_node(ch):
            continue
        t = ch.get("text") or ""
        start = 0
        while True:
            j = t.find(anchor, start)
            if j == -1:
                break
            occurrences.append((i, j))
            start = j + len(anchor)

    if not occurrences:
        # If the anchor exists, but only inside a link node, we refuse (would require editing an existing link).
        for ch in children:
            if isinstance(ch, dict) and ch.get("type") == "link":
                if anchor in _extract_text(ch):
                    return (
                        LexicalEditReport(
                            refused=True,
                            reasons=["Refused: anchor_text appears inside an existing link node (won't nest links)"],
                            matched=1,
                            changed=False,
                            diff=None,
                        ),
                        before,
                    )
        return (
            LexicalEditReport(refused=True, reasons=["Refused: anchor_text not found inside paragraph text node"], matched=1, changed=False, diff=None),
            before,
        )

    if len(occurrences) > 1 and anchor_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: anchor_text matched multiple times in paragraph ({len(occurrences)}); pass --anchor-occurrence"],
                matched=len(occurrences),
                changed=False,
                diff=None,
            ),
            before,
        )
    aocc = anchor_occurrence or 1
    if aocc < 1 or aocc > len(occurrences):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"anchor-occurrence out of range (1..{len(occurrences)})"],
                matched=len(occurrences),
                changed=False,
                diff=None,
            ),
            before,
        )

    child_idx, start_pos = occurrences[aocc - 1]
    template = children[child_idx]
    assert isinstance(template, dict)
    full_text = str(template.get("text") or "")
    pre = full_text[:start_pos]
    post = full_text[start_pos + len(anchor) :]

    new_inline: list[dict[str, Any]] = []
    if pre:
        new_inline.append(_make_extended_text_node(pre, template=template, format_override=None))
    link_node = {
        "type": "link",
        "version": 1,
        "direction": None,
        "format": "",
        "indent": 0,
        "rel": None,
        "target": None,
        "title": None,
        "url": link_url,
        "children": [_make_extended_text_node(anchor, template=template, format_override=None)],
    }
    new_inline.append(link_node)
    if post:
        new_inline.append(_make_extended_text_node(post, template=template, format_override=None))

    children[child_idx : child_idx + 1] = new_inline

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[f"Linked in paragraph {_to_path(target_path)}"], matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def insert_link_paragraph_after_heading_section_end(
    lexical_obj: dict[str, Any],
    *,
    heading: str,
    heading_occurrence: int | None,
    link_text: str,
    url: str,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Insert a link-only paragraph at the end of a heading section (top-level root.children).

    The insertion point is:
    - after the matched heading's content (including nested h3/h4 blocks), and
    - before the next heading with the same tag (usually the next h2), or end of document.

    Safety:
    - Refuses on ambiguous heading matches unless heading_occurrence is provided.
    - Idempotent: if the same (url + link_text) already exists as a link node within that section, no-ops.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    h = " ".join(str(heading or "").strip().split())
    if not h:
        return (LexicalEditReport(refused=True, reasons=["Refused: heading must be non-empty"], matched=0, changed=False, diff=None), lexical_obj)
    text = str(link_text or "")
    if not text.strip():
        return (LexicalEditReport(refused=True, reasons=["Refused: link_text must be non-empty"], matched=0, changed=False, diff=None), lexical_obj)
    if text != text.strip():
        return (
            LexicalEditReport(refused=True, reasons=["Refused: link_text has leading/trailing whitespace"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    link_url = (url or "").strip()
    if not link_url:
        return (
            LexicalEditReport(refused=True, reasons=["Refused: url must be non-empty"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    target_heading = _normalize_heading(h)

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children: list[Any] = out["root"]["children"]

    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == target_heading:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )
    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    heading_idx = heading_idxs[occ - 1]
    heading_node = out_children[heading_idx]
    assert isinstance(heading_node, dict)
    tag = str(heading_node.get("tag") or "h2").lower()

    # Find the end of this section: next heading with the same tag.
    insert_idx = len(out_children)
    j = heading_idx + 1
    while j < len(out_children):
        node = out_children[j]
        if isinstance(node, dict) and _is_heading_node(node):
            node_tag = str(node.get("tag") or "h2").lower()
            if node_tag == tag:
                insert_idx = j
                break
        j += 1

    # Idempotence: if the same url+text already exists in this section, no-op.
    for node in out_children[heading_idx + 1 : insert_idx]:
        if not isinstance(node, dict):
            continue
        if node.get("type") == "link" and (node.get("url") or "").strip() == link_url:
            if " ".join(_extract_text(node).strip().split()) == text:
                return (LexicalEditReport(refused=False, reasons=["Link already present"], matched=1, changed=False, diff=None), before)
        if node.get("type") == "paragraph":
            for _, sub in _iter_nodes(node):
                if isinstance(sub, dict) and sub.get("type") == "link" and (sub.get("url") or "").strip() == link_url:
                    if " ".join(_extract_text(sub).strip().split()) == text:
                        return (
                            LexicalEditReport(refused=False, reasons=["Link already present"], matched=1, changed=False, diff=None),
                            before,
                        )

    link_node = {
        "type": "link",
        "version": 1,
        "direction": None,
        "format": "",
        "indent": 0,
        "rel": None,
        "target": None,
        "title": None,
        "url": link_url,
        "children": [{"type": "extended-text", "version": 1, "text": text, "format": 0, "detail": 0, "mode": "normal", "style": ""}],
    }
    paragraph_node = {
        "type": "paragraph",
        "version": 1,
        "direction": None,
        "format": "",
        "indent": 0,
        "children": [link_node],
    }

    out_children.insert(insert_idx, paragraph_node)
    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[f"Inserted link paragraph after {h} section"], matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def move_top_level_image_before_heading(
    lexical_obj: dict[str, Any],
    *,
    src: str,
    heading: str,
    heading_occurrence: int | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Moves a top-level Lexical image node (root.children) to immediately *before* a heading.

    Safety:
    - Refuses unless the image is a top-level card (root.children).
    - Refuses unless the src matches exactly one top-level image.
    - Refuses on ambiguous headings unless heading_occurrence is provided.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    target_heading = _normalize_heading(heading)
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == target_heading:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )
    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"--heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    heading_idx = heading_idxs[occ - 1]

    image_idxs = [
        i for i, node in enumerate(out_children) if isinstance(node, dict) and _is_image_node(node) and node.get("src") == src
    ]
    if not image_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No image matched src"], matched=0, changed=False, diff=None),
            before,
        )
    if len(image_idxs) > 1:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: src matched multiple images ({len(image_idxs)})"],
                matched=len(image_idxs),
                changed=False,
                diff=None,
            ),
            before,
        )

    image_idx = image_idxs[0]
    # Already immediately before the heading.
    if image_idx == heading_idx - 1:
        changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
        return (
            LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
            out if changed else before,
        )

    node = out_children.pop(image_idx)
    # If we removed an element before the heading, the heading index shifts left by one.
    if image_idx < heading_idx:
        heading_idx -= 1
    out_children.insert(heading_idx, node)

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def fix_numbered_list_split_by_html_ol_after_heading(
    lexical_obj: dict[str, Any],
    *,
    heading: str,
    heading_occurrence: int | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Fixes common importer artifacts where numbered list steps are split across:
    - a Lexical list node for step 1, and then either:
      - multiple HTML cards that each contain a single-item <ol start=\"N\"><li>...</li></ol>, and/or
      - multiple Lexical list nodes, each containing a single list item with start=N.

    This converts those extra nodes into proper Lexical list items in the first list node and removes the redundant cards/nodes.

    Safety:
    - Operates only on root.children (top-level cards).
    - Only merges immediately-adjacent HTML cards after the first numbered list node.
    - Refuses if an encountered HTML card doesn't match the expected single-item <ol>/<li> pattern.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    target_heading = _normalize_heading(heading)
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == target_heading:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )
    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"--heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    heading_idx = heading_idxs[occ - 1]
    scan_idx = heading_idx + 1
    # Skip over empty paragraphs (rare, but safe).
    while scan_idx < len(out_children):
        node = out_children[scan_idx]
        if isinstance(node, dict) and node.get("type") == "paragraph" and not _extract_text(node).strip():
            scan_idx += 1
            continue
        break

    if scan_idx >= len(out_children):
        return (
            LexicalEditReport(refused=False, reasons=["No content after heading"], matched=0, changed=False, diff=None),
            before,
        )

    first = out_children[scan_idx]
    if not (isinstance(first, dict) and first.get("type") == "list" and first.get("listType") == "number"):
        return (
            LexicalEditReport(refused=True, reasons=["Refused: expected a numbered list immediately after heading"], matched=0, changed=False, diff=None),
            before,
        )

    list_items = first.get("children")
    if not (isinstance(list_items, list) and list_items):
        return (
            LexicalEditReport(refused=True, reasons=["Refused: numbered list has no items"], matched=0, changed=False, diff=None),
            before,
        )

    template_item = list_items[0]
    if not isinstance(template_item, dict) or template_item.get("type") != "listitem":
        return (
            LexicalEditReport(refused=True, reasons=["Refused: unsupported list item shape"], matched=0, changed=False, diff=None),
            before,
        )

    # Collect consecutive list nodes (single-item) and/or HTML ol/li cards until the next heading
    # (or first non-list/non-html card).
    parsed_steps: list[str] = []
    to_delete: list[int] = []
    # Continue numbering from the first list.
    expected = len(list_items) + 1
    j = scan_idx + 1
    while j < len(out_children):
        node = out_children[j]
        if isinstance(node, dict) and _is_heading_node(node):
            break

        # Merge consecutive single-item Lexical list nodes with start=N and value=N.
        if isinstance(node, dict) and node.get("type") == "list" and node.get("listType") == "number":
            if node.get("start") != expected:
                break
            node_items = node.get("children")
            if not (isinstance(node_items, list) and len(node_items) == 1):
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: encountered unsupported numbered list shape while fixing list"], matched=0, changed=False, diff=None),
                    before,
                )
            item = node_items[0]
            if not (isinstance(item, dict) and item.get("type") == "listitem" and item.get("value") == expected):
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: encountered unexpected list item numbering while fixing list"], matched=0, changed=False, diff=None),
                    before,
                )
            # Convert list item to text and treat it as a parsed step (keeps behavior consistent).
            li_text = _extract_text(item).strip()
            if not li_text:
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: extracted empty list item text while fixing list"], matched=0, changed=False, diff=None),
                    before,
                )
            parsed_steps.append(li_text)
            to_delete.append(j)
            expected += 1
            j += 1
            continue

        if not (isinstance(node, dict) and node.get("type") == "html"):
            break
        html_str = node.get("html")
        if not isinstance(html_str, str) or not html_str.strip():
            # Empty HTML card: treat as unsafe noise.
            return (
                LexicalEditReport(refused=True, reasons=["Refused: encountered empty HTML card while fixing list"], matched=0, changed=False, diff=None),
                before,
            )
        m = _HTML_OL_LI_RE.search(html_str)
        if not m:
            return (
                LexicalEditReport(refused=True, reasons=["Refused: HTML card did not match expected <ol>/<li> pattern"], matched=0, changed=False, diff=None),
                before,
            )
        li_html = _HTML_COMMENT_RE.sub("", m.group("li"))
        li_text = html.unescape(_TAG_RE.sub("", li_html)).strip()
        if not li_text:
            return (
                LexicalEditReport(refused=True, reasons=["Refused: extracted empty <li> text from HTML card"], matched=0, changed=False, diff=None),
                before,
            )
        parsed_steps.append(li_text)
        to_delete.append(j)
        expected += 1
        j += 1

    if not parsed_steps:
        # Nothing to fix.
        changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
        return (
            LexicalEditReport(refused=False, reasons=[], matched=0, changed=changed, diff=diff),
            out if changed else before,
        )

    # Append parsed steps as new list items. Prefer sequential values starting at current length + 1.
    next_value = len(list_items) + 1
    for text in parsed_steps:
        new_item = deepcopy(template_item)
        new_item["value"] = next_value
        # Keep the child's node type (Ghost uses extended-text in some list shapes).
        child_nodes = new_item.get("children")
        if isinstance(child_nodes, list) and child_nodes and isinstance(child_nodes[0], dict) and "text" in child_nodes[0]:
            child_nodes[0]["text"] = text
        else:
            # Fall back to a safe minimal list item shape.
            new_item["children"] = [{"type": "extended-text", "version": 1, "text": text}]
        list_items.append(new_item)
        next_value += 1

    # Delete HTML cards from end to preserve indices.
    for idx in sorted(to_delete, reverse=True):
        del out_children[idx]

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=len(parsed_steps), changed=changed, diff=diff),
        out if changed else before,
    )


def _make_extended_text_node(text: str, *, template: dict[str, Any] | None, format_override: int | None) -> dict[str, Any]:
    if template is not None:
        node: dict[str, Any] = deepcopy(template)
    else:
        node = {"type": "extended-text", "version": 1, "text": "", "format": 0, "detail": 0, "mode": "normal", "style": ""}
    node["type"] = node.get("type") or "extended-text"
    node["version"] = node.get("version") or 1
    node["text"] = text
    if format_override is not None:
        node["format"] = format_override
    return node


_STRONG_AT_START_RE = re.compile(r"^\s*<strong\b[^>]*>(?P<strong>.*?)</strong>(?P<rest>.*)$", re.IGNORECASE | re.DOTALL)


def _parse_simple_wp_li_html(li_html: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    """
    Parse a WordPress importer list-item HTML snippet into a small Lexical inline shape.

    Supported shapes (fail-closed):
    - <strong>Title</strong> — rest (no other tags)
    - plain text (no tags)
    """
    raw = _HTML_COMMENT_RE.sub("", li_html).strip()
    if not raw:
        return None, ["Refused: extracted empty <li> HTML"]

    m = _STRONG_AT_START_RE.match(raw)
    if m:
        strong_html = m.group("strong").strip()
        rest_html = m.group("rest")
        if "<" in strong_html:
            return None, ["Refused: <strong> content contains nested tags (unsupported)"]
        if "<" in rest_html:
            return None, ["Refused: list item contains unsupported HTML tags"]
        strong_text = html.unescape(strong_html).strip()
        # Preserve leading whitespace (commonly: " — ...") but trim trailing whitespace/newlines.
        rest_text = html.unescape(rest_html).rstrip()
        if not strong_text and not rest_text:
            return None, ["Refused: extracted empty <li> text from HTML card"]
        # Preserve the common "bold title + normal rest" shape.
        nodes: list[dict[str, Any]] = []
        if strong_text:
            nodes.append({"type": "extended-text", "version": 1, "text": strong_text, "format": 1, "detail": 0, "mode": "normal", "style": ""})
        if rest_text:
            nodes.append({"type": "extended-text", "version": 1, "text": rest_text, "format": 0, "detail": 0, "mode": "normal", "style": ""})
        return nodes, []

    if "<" in raw:
        return None, ["Refused: list item contains unsupported HTML tags"]
    text = html.unescape(raw).strip()
    if not text:
        return None, ["Refused: extracted empty <li> text from HTML card"]
    return [{"type": "extended-text", "version": 1, "text": text, "format": 0, "detail": 0, "mode": "normal", "style": ""}], []


def fix_bullet_lists_split_by_html_ul_cards(
    lexical_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Fixes a WordPress importer artifact where bullet list items are split across:
    - a Lexical bullet list node, and
    - multiple HTML cards that each contain a single-item <ul start=\"N\"><li>...</li></ul>.

    This converts those HTML ul cards into proper Lexical list items in the preceding list node
    and removes the HTML cards.

    Safety:
    - Operates only on root.children (top-level cards).
    - Only merges immediately-adjacent HTML cards after a bullet list node.
    - Requires a sequential start= attribute (e.g. 2,3,4...) to reduce false positives.
    - Refuses if the <li> contains unsupported nested tags beyond a simple leading <strong>.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children: list[Any] = out["root"]["children"]

    matched_total = 0
    i = 0
    while i < len(out_children):
        node = out_children[i]
        if not (isinstance(node, dict) and node.get("type") == "list" and node.get("listType") == "bullet"):
            i += 1
            continue

        list_items = node.get("children")
        if not (isinstance(list_items, list) and list_items):
            i += 1
            continue

        template_item = list_items[0]
        if not isinstance(template_item, dict) or template_item.get("type") != "listitem":
            return (
                LexicalEditReport(refused=True, reasons=["Refused: unsupported list item shape"], matched=0, changed=False, diff=None),
                before,
            )

        template_children = template_item.get("children")
        template_text_nodes: list[dict[str, Any]] = []
        if isinstance(template_children, list):
            for ch in template_children:
                if isinstance(ch, dict) and isinstance(ch.get("text"), str):
                    template_text_nodes.append(ch)
                else:
                    # Fail closed: we only know how to build plain inline text nodes.
                    return (
                        LexicalEditReport(
                            refused=True,
                            reasons=["Refused: unsupported list item inline shape (non-text child)"],
                            matched=0,
                            changed=False,
                            diff=None,
                        ),
                        before,
                    )

        j = i + 1
        parsed_items: list[list[dict[str, Any]]] = []
        to_delete: list[int] = []
        expected_start = len(list_items) + 1

        while j < len(out_children):
            nxt = out_children[j]
            if isinstance(nxt, dict) and _is_heading_node(nxt):
                break
            if not (isinstance(nxt, dict) and nxt.get("type") == "html"):
                break
            html_str = nxt.get("html")
            if not isinstance(html_str, str) or not html_str.strip():
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: encountered empty HTML card while fixing list"], matched=0, changed=False, diff=None),
                    before,
                )

            m = _HTML_UL_LI_RE.search(html_str)
            if not m:
                # If the first HTML card doesn't look like a single-item ul/li list, treat it as unrelated and stop.
                if not parsed_items:
                    break
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: HTML card did not match expected <ul>/<li> pattern"], matched=0, changed=False, diff=None),
                    before,
                )

            # Require a sequential start= attribute to reduce false positives.
            attrs = m.group("ul_attrs") or ""
            start_m = _HTML_START_ATTR_RE.search(attrs)
            if not start_m:
                if not parsed_items:
                    break
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: HTML <ul> missing start= attribute"], matched=0, changed=False, diff=None),
                    before,
                )
            start_val = int(start_m.group("start"))
            if start_val != expected_start:
                return (
                    LexicalEditReport(
                        refused=True,
                        reasons=[f"Refused: HTML <ul> start={start_val} but expected {expected_start}"],
                        matched=0,
                        changed=False,
                        diff=None,
                    ),
                    before,
                )

            # Ensure the card is a single-item list.
            lower = html_str.lower()
            if lower.count("<li") != 1:
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: HTML <ul> card contains multiple <li> items"], matched=0, changed=False, diff=None),
                    before,
                )

            li_html = _HTML_COMMENT_RE.sub("", m.group("li"))
            li_nodes, li_reasons = _parse_simple_wp_li_html(li_html)
            if li_nodes is None:
                return (
                    LexicalEditReport(refused=True, reasons=li_reasons, matched=0, changed=False, diff=None),
                    before,
                )

            # Map parsed nodes onto the template shape (preserve editor-specific fields where possible).
            mapped_nodes: list[dict[str, Any]] = []
            for idx, pn in enumerate(li_nodes):
                template = template_text_nodes[idx] if idx < len(template_text_nodes) else (template_text_nodes[-1] if template_text_nodes else None)
                fmt = pn.get("format") if isinstance(pn.get("format"), int) else None
                if fmt == 1 and template is not None and isinstance(template.get("format"), int) and template.get("format") != 0:
                    fmt = int(template["format"])
                mapped_nodes.append(_make_extended_text_node(str(pn.get("text") or ""), template=template, format_override=fmt))

            parsed_items.append(mapped_nodes)
            to_delete.append(j)
            expected_start += 1
            j += 1

        if not parsed_items:
            i += 1
            continue

        next_value = len(list_items) + 1
        for nodes_inline in parsed_items:
            new_item = deepcopy(template_item)
            new_item["value"] = next_value
            new_item["children"] = nodes_inline
            list_items.append(new_item)
            next_value += 1

        for idx in sorted(to_delete, reverse=True):
            del out_children[idx]

        matched_total += len(parsed_items)
        i += 1

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched_total, changed=changed, diff=diff),
        out if changed else before,
    )


def _last_list_value(list_node: dict[str, Any]) -> int | None:
    items = list_node.get("children")
    if not isinstance(items, list) or not items:
        return None
    last = items[-1]
    if isinstance(last, dict) and isinstance(last.get("value"), int):
        return int(last["value"])
    return None


def _make_list_node(
    *,
    list_type: str,
    start: int | None,
    value: int,
    inline_children: list[dict[str, Any]],
) -> dict[str, Any]:
    node: dict[str, Any] = {"type": "list", "version": 1, "listType": list_type, "children": []}
    if list_type == "number":
        node["tag"] = "ol"
        if start is not None:
            node["start"] = int(start)
    else:
        node["tag"] = "ul"
    node["children"] = [{"type": "listitem", "version": 1, "value": int(value), "children": inline_children}]
    return node


def _extract_first_list_block(html_str: str) -> tuple[str, str]:
    """
    Returns (tag, full_html) for the first <ul> or <ol> block in html_str, including nested list tags.
    """
    low = html_str.lower()
    ul_i = low.find("<ul")
    ol_i = low.find("<ol")
    if ul_i == -1 and ol_i == -1:
        raise ValueError("No <ul> or <ol> tag found")
    if ul_i == -1 or (ol_i != -1 and ol_i < ul_i):
        start = ol_i
        tag = "ol"
    else:
        start = ul_i
        tag = "ul"

    depth = 0
    end = None
    for m in _HTML_LIST_TAG_RE.finditer(html_str, pos=start):
        t = (m.group("tag") or "").lower()
        if t not in ("ul", "ol"):
            continue
        is_close = bool(m.group("close"))
        if not is_close:
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = m.end()
                break
        if depth < 0:
            raise ValueError("Unbalanced list tags")
    if end is None:
        raise ValueError("Unbalanced list tags (no closing tag found)")
    return tag, html_str[start:end]


def _extract_direct_li_inner_html(list_html: str) -> list[str]:
    """
    Extracts direct <li> inner HTML strings from a list HTML block (<ul>...</ul> or <ol>...</ol>),
    ignoring nested list items (they are included inside the parent's inner HTML).
    """
    list_depth = 0
    li_depth = 0
    capturing = False
    cursor = 0
    buf: list[str] = []
    out: list[str] = []

    for m in _HTML_LIST_TAG_RE.finditer(list_html):
        close = bool(m.group("close"))
        tag = (m.group("tag") or "").lower()

        if capturing:
            if tag == "li" and close:
                li_depth -= 1
                if li_depth == 0:
                    buf.append(list_html[cursor : m.start()])
                    out.append("".join(buf))
                    buf = []
                    capturing = False
                    cursor = m.end()
                    continue
                buf.append(list_html[cursor : m.start()])
                buf.append(m.group(0))
                cursor = m.end()
            else:
                buf.append(list_html[cursor : m.start()])
                buf.append(m.group(0))
                cursor = m.end()
                if tag in ("ul", "ol"):
                    list_depth += -1 if close else 1
                elif tag == "li" and not close:
                    li_depth += 1
            continue

        # Not capturing yet.
        if tag in ("ul", "ol"):
            list_depth += -1 if close else 1
            continue
        if tag == "li" and not close and list_depth == 1 and li_depth == 0:
            capturing = True
            li_depth = 1
            cursor = m.end()
            buf = []
            continue

    return out


def _strip_html_comments_and_ws(s: str) -> str:
    return _HTML_COMMENT_RE.sub("", s).strip()


def _split_li_on_nested_list(li_inner_html: str) -> tuple[str, str | None, str]:
    """
    Splits a list item's inner HTML into (prefix_html, nested_list_html_or_none, suffix_html).
    """
    cleaned = li_inner_html
    m = re.search(r"<\s*(ul|ol)\b", cleaned, flags=re.IGNORECASE)
    if not m:
        return li_inner_html, None, ""
    nested_start = m.start()
    tag, block = _extract_first_list_block(cleaned[nested_start:])
    prefix = cleaned[:nested_start]
    suffix = cleaned[nested_start + len(block) :]
    return prefix, block, suffix


def convert_html_list_cards_to_native_lists(
    lexical_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Converts WordPress-imported HTML list cards into native Lexical list nodes.

    This targets *top-level* Lexical `html` cards that look like Gutenberg list items, such as:
      - <ol start="2"><!-- wp:list-item --><li>...</li><!-- /wp:list-item --></ol>
      - <ul><!-- wp:list-item --><li>...</li><!-- /wp:list-item --></ul>

    Behavior:
    - Replaces each matching HTML card with a native Lexical list block.
    - If the HTML card is immediately after a compatible Lexical list block, it appends into that list instead.

    Safety (fail-closed):
    - Operates only on root.children.
    - Only converts HTML cards that contain either `wp:list-item` comments OR a `start=` attribute.
    - Refuses if list item HTML contains unsupported nested tags beyond a simple leading <strong>.
    - Refuses if converting an <ol> card without a `start=` attribute (to avoid changing numbering semantics).
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children: list[Any] = out["root"]["children"]

    matched_total = 0
    i = 0
    while i < len(out_children):
        node = out_children[i]
        if not (isinstance(node, dict) and node.get("type") == "html" and isinstance(node.get("html"), str)):
            i += 1
            continue

        html_str = node["html"]
        low = html_str.lower()
        if "<li" not in low or ("<ul" not in low and "<ol" not in low):
            i += 1
            continue

        # Only target likely WP importer artifacts.
        is_wp_hint = ("wp:list-item" in low) or (" start=" in low)
        if not is_wp_hint:
            i += 1
            continue

        try:
            tag, list_block = _extract_first_list_block(html_str)
        except Exception as e:  # noqa: BLE001
            return (LexicalEditReport(refused=True, reasons=[f"Refused: cannot parse list HTML card: {e}"], matched=0, changed=False, diff=None), before)

        # Parse the outer list's direct <li> items.
        li_inners = _extract_direct_li_inner_html(list_block)
        if not li_inners:
            return (LexicalEditReport(refused=True, reasons=["Refused: HTML list card has no <li> items"], matched=0, changed=False, diff=None), before)

        if tag == "ol":
            m = _HTML_OL_OPEN_RE.search(list_block)
            attrs = m.group("attrs") if m else ""
            start_m = _HTML_START_ATTR_RE.search(attrs or "")
            if not start_m:
                return (LexicalEditReport(refused=True, reasons=["Refused: HTML <ol> missing start= attribute"], matched=0, changed=False, diff=None), before)
            start_val = int(start_m.group("start"))
            values = list(range(start_val, start_val + len(li_inners)))
            list_items: list[dict[str, Any]] = []
            for val, li_inner in zip(values, li_inners, strict=True):
                li_clean = _strip_html_comments_and_ws(li_inner)
                if re.search(r"<\s*(ul|ol)\b", li_clean, flags=re.IGNORECASE):
                    return (LexicalEditReport(refused=True, reasons=["Refused: nested lists inside <ol> list items are unsupported"], matched=0, changed=False, diff=None), before)
                li_nodes, li_reasons = _parse_simple_wp_li_html(li_clean)
                if li_nodes is None:
                    return (LexicalEditReport(refused=True, reasons=li_reasons, matched=0, changed=False, diff=None), before)
                list_items.append({"type": "listitem", "version": 1, "value": int(val), "children": li_nodes})

            prev = out_children[i - 1] if i - 1 >= 0 else None
            if isinstance(prev, dict) and prev.get("type") == "list" and prev.get("listType") == "number":
                prev_items = prev.get("children")
                if isinstance(prev_items, list) and prev_items:
                    last_val = _last_list_value(prev) or len(prev_items)
                    if last_val + 1 == start_val:
                        prev_items.extend(list_items)
                        del out_children[i]
                        matched_total += 1
                        continue

            new_list = {"type": "list", "version": 1, "listType": "number", "tag": "ol", "start": int(start_val), "children": list_items}
            out_children[i] = new_list
            matched_total += 1
            i += 1
            continue

        # tag == "ul"
        list_items: list[dict[str, Any]] = []
        next_val = 1
        for li_inner in li_inners:
            li_clean = _strip_html_comments_and_ws(li_inner)
            prefix, nested_list, suffix = _split_li_on_nested_list(li_clean)
            suffix_clean = _strip_html_comments_and_ws(suffix) if suffix else ""
            if nested_list is not None and suffix_clean:
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: unsupported content after nested list inside <li>"], matched=0, changed=False, diff=None),
                    before,
                )

            if nested_list is None:
                li_nodes, li_reasons = _parse_simple_wp_li_html(li_clean)
                if li_nodes is None:
                    return (LexicalEditReport(refused=True, reasons=li_reasons, matched=0, changed=False, diff=None), before)
                list_items.append({"type": "listitem", "version": 1, "value": int(next_val), "children": li_nodes, "indent": 0})
                next_val += 1
                continue

            # One-level nested list support (converted to indent=1 listitems).
            prefix_clean = _strip_html_comments_and_ws(prefix)
            if not prefix_clean:
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: nested list <li> is missing prefix text"], matched=0, changed=False, diff=None),
                    before,
                )
            prefix_nodes, prefix_reasons = _parse_simple_wp_li_html(prefix_clean)
            if prefix_nodes is None:
                return (LexicalEditReport(refused=True, reasons=prefix_reasons, matched=0, changed=False, diff=None), before)
            list_items.append({"type": "listitem", "version": 1, "value": int(next_val), "children": prefix_nodes, "indent": 0})
            next_val += 1

            try:
                nested_tag, nested_block = _extract_first_list_block(nested_list)
            except Exception as e:  # noqa: BLE001
                return (
                    LexicalEditReport(refused=True, reasons=[f"Refused: cannot parse nested list inside <li>: {e}"], matched=0, changed=False, diff=None),
                    before,
                )
            if nested_tag != "ul":
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: only nested <ul> is supported"], matched=0, changed=False, diff=None),
                    before,
                )
            nested_li_inners = _extract_direct_li_inner_html(nested_block)
            if not nested_li_inners:
                return (
                    LexicalEditReport(refused=True, reasons=["Refused: nested <ul> has no <li> items"], matched=0, changed=False, diff=None),
                    before,
                )
            for sub_li in nested_li_inners:
                sub_clean = _strip_html_comments_and_ws(sub_li)
                if re.search(r"<\s*(ul|ol)\b", sub_clean, flags=re.IGNORECASE):
                    return (
                        LexicalEditReport(refused=True, reasons=["Refused: nested lists deeper than 1 level are unsupported"], matched=0, changed=False, diff=None),
                        before,
                    )
                sub_nodes, sub_reasons = _parse_simple_wp_li_html(sub_clean)
                if sub_nodes is None:
                    return (LexicalEditReport(refused=True, reasons=sub_reasons, matched=0, changed=False, diff=None), before)
                list_items.append({"type": "listitem", "version": 1, "value": int(next_val), "children": sub_nodes, "indent": 1})
                next_val += 1

        prev = out_children[i - 1] if i - 1 >= 0 else None
        if isinstance(prev, dict) and prev.get("type") == "list" and prev.get("listType") == "bullet":
            prev_items = prev.get("children")
            if isinstance(prev_items, list) and prev_items:
                base_val = (_last_list_value(prev) or len(prev_items))
                for it in list_items:
                    base_val += 1
                    it["value"] = base_val
                prev_items.extend(list_items)
                del out_children[i]
                matched_total += 1
                continue

        new_list = {"type": "list", "version": 1, "listType": "bullet", "tag": "ul", "children": list_items}
        out_children[i] = new_list
        matched_total += 1
        i += 1

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=matched_total, changed=changed, diff=diff),
        out if changed else before,
    )


_NUMBERED_PREFIX_RE = re.compile(r"^(?P<num>\d+)\.\s+")


def fix_numbered_paragraphs_to_list_after_heading(
    lexical_obj: dict[str, Any],
    *,
    heading: str,
    heading_occurrence: int | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Converts consecutive numbered paragraphs ("1. ...", "2. ...") immediately after a heading
    into a proper ordered list.

    Safety:
    - Operates only on root.children (top-level cards).
    - Refuses on ambiguous headings unless heading_occurrence is provided.
    - Refuses unless the content immediately after the heading is a strict consecutive numbering
      sequence starting at 1.
    - Refuses unless the numeric prefix lives entirely in the first text-bearing child (so we can
      strip it without losing formatting).
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    target_heading = _normalize_heading(heading)
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            if _normalize_heading(_extract_text(node)) == target_heading:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )
    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"--heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    heading_idx = heading_idxs[occ - 1]
    scan_idx = heading_idx + 1
    if scan_idx >= len(out_children):
        return (
            LexicalEditReport(refused=False, reasons=["No content after heading"], matched=0, changed=False, diff=None),
            before,
        )

    numbered_nodes: list[dict[str, Any]] = []
    expected = 1
    while scan_idx < len(out_children):
        node = out_children[scan_idx]
        if isinstance(node, dict) and _is_heading_node(node):
            break
        if not (isinstance(node, dict) and node.get("type") == "paragraph"):
            break

        raw = " ".join(_extract_text(node).strip().split())
        m = _NUMBERED_PREFIX_RE.match(raw)
        if not m:
            break
        num = int(m.group("num"))
        if num != expected:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"Refused: expected step #{expected} but saw #{num}"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )

        node_children = node.get("children")
        if not isinstance(node_children, list) or not node_children:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=["Refused: numbered paragraph missing children"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )
        first = node_children[0]
        if not (isinstance(first, dict) and isinstance(first.get("text"), str)):
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=["Refused: expected first child to contain text"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )

        prefix = raw[: m.end()]
        if not first["text"].startswith(prefix):
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=["Refused: numbered prefix is not contained in the first text node"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )

        numbered_nodes.append(node)
        expected += 1
        scan_idx += 1

    if not numbered_nodes:
        changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
        return (
            LexicalEditReport(refused=False, reasons=["No numbered paragraphs after heading"], matched=0, changed=changed, diff=diff),
            out if changed else before,
        )

    start_idx = heading_idx + 1
    end_idx = start_idx + len(numbered_nodes)

    list_items: list[dict[str, Any]] = []
    for i, para in enumerate(numbered_nodes, start=1):
        para_children = deepcopy(para.get("children"))
        assert isinstance(para_children, list) and para_children
        raw = " ".join(_extract_text(para).strip().split())
        m = _NUMBERED_PREFIX_RE.match(raw)
        assert m is not None
        prefix = raw[: m.end()]
        first = para_children[0]
        assert isinstance(first, dict) and isinstance(first.get("text"), str)
        first["text"] = first["text"][len(prefix) :]

        list_items.append(
            {
                "children": para_children,
                "direction": None,
                "format": "",
                "indent": 0,
                "type": "listitem",
                "version": 1,
                "value": i,
            }
        )

    list_node: dict[str, Any] = {
        "children": list_items,
        "direction": None,
        "format": "",
        "indent": 0,
        "listType": "number",
        "start": 1,
        "tag": "ol",
        "type": "list",
        "version": 1,
    }

    out_children[start_idx:end_idx] = [list_node]

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=len(numbered_nodes), changed=changed, diff=diff),
        out if changed else before,
    )


def list_images(lexical_obj: dict[str, Any]) -> list[LexicalImage]:
    """
    Returns images in depth-first order.
    context_heading is best-effort: last seen heading in the same traversal.
    """
    images: list[LexicalImage] = []
    last_heading: str | None = None
    idx = 0
    for path, node in _iter_nodes(lexical_obj):
        if _is_heading_node(node):
            text = _extract_text(node)
            if text.strip():
                last_heading = " ".join(text.strip().split())
        if _is_image_node(node):
            caption = node.get("caption")
            caption_s = caption if isinstance(caption, str) else None
            caption_text = _strip_caption_html(caption_s) if caption_s else None
            images.append(
                LexicalImage(
                    index=idx,
                    path=_to_path(path),
                    src=str(node["src"]),
                    alt=str(node["alt"]) if isinstance(node.get("alt"), str) else None,
                    title=str(node["title"]) if isinstance(node.get("title"), str) else None,
                    caption=caption_s,
                    caption_text=caption_text,
                    context_heading=last_heading,
                )
            )
            idx += 1
    return images


def replace_image_src(
    lexical_obj: dict[str, Any],
    *,
    old_src: str,
    new_src: str,
    alt: str | None,
    caption: str | None,
    title: str | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    before = lexical_obj
    out = deepcopy(lexical_obj)

    matches_old: list[tuple[list[str | int], dict[str, Any]]] = []
    for path, node in _iter_nodes(out):
        if _is_image_node(node) and node.get("src") == old_src:
            matches_old.append((path, node))

    reasons: list[str] = []
    if not matches_old:
        matches_new: list[tuple[list[str | int], dict[str, Any]]] = []
        for path, node in _iter_nodes(out):
            if _is_image_node(node) and node.get("src") == new_src:
                matches_new.append((path, node))
        if len(matches_new) == 1:
            reasons.append("No old-src match; new-src already present (treating as already replaced)")
            _, node = matches_new[0]
            if alt is not None:
                node["alt"] = alt
            if title is not None:
                node["title"] = title
            if caption is not None:
                node["caption"] = _normalize_caption_input(caption)

            changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
            return (
                LexicalEditReport(
                    refused=False,
                    reasons=reasons,
                    matched=1,
                    changed=changed,
                    diff=diff,
                ),
                out if changed else before,
            )

        if len(matches_new) > 1:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"Refused: old-src not found and new-src matched multiple images ({len(matches_new)})"],
                    matched=len(matches_new),
                    changed=False,
                    diff=None,
                ),
                before,
            )

        return (
            LexicalEditReport(
                refused=True,
                reasons=["No image node matched old-src, and new-src was not found"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    if len(matches_old) > 1:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: old-src matched multiple images ({len(matches_old)})"],
                matched=len(matches_old),
                changed=False,
                diff=None,
            ),
            before,
        )

    _, node = matches_old[0]
    node["src"] = new_src
    if alt is not None:
        node["alt"] = alt
    if title is not None:
        node["title"] = title
    if caption is not None:
        node["caption"] = _normalize_caption_input(caption)

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=reasons, matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def set_image_meta_by_src(
    lexical_obj: dict[str, Any],
    *,
    src: str,
    alt: str | None,
    caption: str | None,
    title: str | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    before = lexical_obj
    out = deepcopy(lexical_obj)

    matches: list[dict[str, Any]] = []
    for _, node in _iter_nodes(out):
        if _is_image_node(node) and node.get("src") == src:
            matches.append(node)
    if not matches:
        return (
            LexicalEditReport(
                refused=True,
                reasons=["No image node matched src"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    if len(matches) > 1:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: src matched multiple images ({len(matches)})"],
                matched=len(matches),
                changed=False,
                diff=None,
            ),
            before,
        )
    node = matches[0]
    if alt is not None:
        node["alt"] = alt
    if title is not None:
        node["title"] = title
    if caption is not None:
        node["caption"] = _normalize_caption_input(caption)

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def replace_first_image_after_heading(
    lexical_obj: dict[str, Any],
    *,
    heading: str,
    new_src: str,
    expect_old_src: str | None,
    alt: str | None,
    caption: str | None,
    title: str | None,
    nth_after_heading: int,
    heading_occurrence: int | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    if nth_after_heading < 1:
        raise RuntimeError("--nth-after-heading must be >= 1")

    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root.children is missing or not a list"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    target = _normalize_heading(heading)
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            text = _normalize_heading(_extract_text(node))
            if text == target:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )

    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"--heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    start_i = heading_idxs[occ - 1]
    seen = 0
    for i in range(start_i + 1, len(out_children)):
        node = out_children[i]
        if isinstance(node, dict) and _is_image_node(node):
            seen += 1
            if seen == nth_after_heading:
                if expect_old_src is not None and node.get("src") != expect_old_src:
                    # Idempotence: if the targeted image is already at new_src, treat as already replaced.
                    if node.get("src") == new_src:
                        reasons = ["expected-old-src mismatch, but image is already at new-src (treating as applied)"]
                        if alt is not None:
                            node["alt"] = alt
                        if title is not None:
                            node["title"] = title
                        if caption is not None:
                            node["caption"] = _normalize_caption_input(caption)
                        changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
                        return (
                            LexicalEditReport(refused=False, reasons=reasons, matched=1, changed=changed, diff=diff),
                            out if changed else before,
                        )
                    return (
                        LexicalEditReport(
                            refused=True,
                            reasons=[
                                "Refused: expected-old-src did not match the targeted image",
                                f"expected: {expect_old_src}",
                                f"got: {node.get('src')}",
                            ],
                            matched=1,
                            changed=False,
                            diff=None,
                        ),
                        before,
                    )
                node["src"] = new_src
                if alt is not None:
                    node["alt"] = alt
                if title is not None:
                    node["title"] = title
                if caption is not None:
                    node["caption"] = _normalize_caption_input(caption)
                changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
                return (
                    LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
                    out if changed else before,
                )

    return (
        LexicalEditReport(
            refused=True,
            reasons=[f"No image found after heading (needed image #{nth_after_heading} after match)"],
            matched=0,
            changed=False,
            diff=None,
        ),
        before,
    )


def insert_image_after_heading(
    lexical_obj: dict[str, Any],
    *,
    heading: str,
    src: str,
    alt: str | None,
    caption: str | None,
    title: str | None,
    template_src: str | None,
    heading_occurrence: int | None,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root.children is missing or not a list"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    target = _normalize_heading(heading)
    heading_idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_heading_node(node):
            text = _normalize_heading(_extract_text(node))
            if text == target:
                heading_idxs.append(i)

    if not heading_idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No heading matched"], matched=0, changed=False, diff=None),
            before,
        )
    if len(heading_idxs) > 1 and heading_occurrence is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass --heading-occurrence"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )
    occ = heading_occurrence or 1
    if occ < 1 or occ > len(heading_idxs):
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"--heading-occurrence out of range (1..{len(heading_idxs)})"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    insert_at = heading_idxs[occ - 1] + 1

    # Idempotence: if the immediately-next node is already the desired image, do not insert again.
    if insert_at < len(out_children):
        existing = out_children[insert_at]
        if isinstance(existing, dict) and _is_image_node(existing) and existing.get("src") == src:
            if alt is not None:
                existing["alt"] = alt
            if title is not None:
                existing["title"] = title
            if caption is not None:
                existing["caption"] = _normalize_caption_input(caption)
            changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
            return (
                LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
                out if changed else before,
            )

    template_node: dict[str, Any] | None = None
    if template_src is not None:
        matches = []
        for _, node in _iter_nodes(out):
            if _is_image_node(node) and node.get("src") == template_src:
                matches.append(node)
        if not matches:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=["template-src did not match any image"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )
        if len(matches) > 1:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"template-src matched multiple images ({len(matches)})"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                before,
            )
        template_node = deepcopy(matches[0])

    if template_node is None:
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Refused: inserting an image requires --template-src for a safe node shape"],
                matched=0,
                changed=False,
                diff=None,
            ),
            before,
        )

    template_node["src"] = src
    if alt is not None:
        template_node["alt"] = alt
    if title is not None:
        template_node["title"] = title
    if caption is not None:
        template_node["caption"] = _normalize_caption_input(caption)

    out_children.insert(insert_at, template_node)

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=1, changed=changed, diff=diff),
        out if changed else before,
    )


def delete_images_by_src(
    lexical_obj: dict[str, Any],
    *,
    src: str,
    allow_multiple: bool,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Deletes Lexical image nodes that match the exact src.

    Safety:
    - Refuses if multiple matches exist unless allow_multiple is True.
    - Only deletes nodes from root.children (top-level cards); refuses otherwise.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root is missing root object"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(
                refused=True,
                reasons=["Lexical root.children is missing or not a list"],
                matched=0,
                changed=False,
                diff=None,
            ),
            lexical_obj,
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children = out["root"]["children"]

    idxs: list[int] = []
    for i, node in enumerate(out_children):
        if isinstance(node, dict) and _is_image_node(node) and node.get("src") == src:
            idxs.append(i)

    if not idxs:
        return (
            LexicalEditReport(refused=True, reasons=["No image matched src"], matched=0, changed=False, diff=None),
            before,
        )
    if len(idxs) > 1 and not allow_multiple:
        return (
            LexicalEditReport(
                refused=True,
                reasons=[f"Refused: src matched multiple images ({len(idxs)}); pass --all to delete all"],
                matched=len(idxs),
                changed=False,
                diff=None,
            ),
            before,
        )

    # Delete from end to preserve indices.
    for i in sorted(idxs, reverse=True):
        del out_children[i]

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=len(idxs), changed=changed, diff=diff),
        out if changed else before,
    )


def sync_top_level_images_before_headings(
    lexical_obj: dict[str, Any],
    *,
    placements: list[dict[str, Any]],
    fix_split_numbered_lists: bool,
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any]]:
    """
    Removes all top-level images (root.children) and inserts the provided images immediately
    before the specified headings (also top-level).

    Safety:
    - Operates only on root.children.
    - Refuses if placements are invalid.
    - Refuses on ambiguous headings unless heading_occurrence is provided.
    - Uses an existing image node as a template for safe node shape; refuses if none exist.
    - If an HTML card contains <img>, it is removed only when it matches a standalone <img> pattern.
    - Optional: fixes split numbered lists (HTML <ol> cards) when the safe pattern is detected.
    """
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root is missing root object"], matched=0, changed=False, diff=None),
            lexical_obj,
        )
    children = root.get("children")
    if not isinstance(children, list):
        return (
            LexicalEditReport(refused=True, reasons=["Lexical root.children is missing or not a list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    if not isinstance(placements, list):
        return (
            LexicalEditReport(refused=True, reasons=["Refused: placements must be a JSON list"], matched=0, changed=False, diff=None),
            lexical_obj,
        )

    normalized: list[dict[str, Any]] = []
    for i, p in enumerate(placements):
        if not isinstance(p, dict):
            return (
                LexicalEditReport(refused=True, reasons=[f"Refused: placement #{i+1} is not an object"], matched=0, changed=False, diff=None),
                lexical_obj,
            )
        heading = p.get("heading")
        src = p.get("src")
        if not (isinstance(heading, str) and heading.strip()):
            return (
                LexicalEditReport(refused=True, reasons=[f"Refused: placement #{i+1} missing heading"], matched=0, changed=False, diff=None),
                lexical_obj,
            )
        if not (isinstance(src, str) and src.startswith("http")):
            return (
                LexicalEditReport(refused=True, reasons=[f"Refused: placement #{i+1} missing valid src"], matched=0, changed=False, diff=None),
                lexical_obj,
            )
        occ = p.get("heading_occurrence")
        if occ is not None and not isinstance(occ, int):
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"Refused: placement #{i+1} heading_occurrence must be an integer"],
                    matched=0,
                    changed=False,
                    diff=None,
                ),
                lexical_obj,
            )
        normalized.append(
            {
                "heading": heading,
                "heading_occurrence": occ,
                "src": src,
                "alt": p.get("alt"),
                "caption": p.get("caption"),
                "title": p.get("title"),
            }
        )

    before = lexical_obj
    out = deepcopy(lexical_obj)
    out_children: list[Any] = out["root"]["children"]

    template: dict[str, Any] | None = None
    if normalized:
        for node in out_children:
            if isinstance(node, dict) and _is_image_node(node):
                template = deepcopy(node)
                break
        if template is None:
            template = _default_image_template()

    # Remove all top-level image cards and safe standalone HTML <img> cards.
    removed = 0
    kept: list[Any] = []
    for node in out_children:
        if isinstance(node, dict) and _is_image_node(node):
            removed += 1
            continue
        if isinstance(node, dict) and node.get("type") == "html" and isinstance(node.get("html"), str):
            html_str = node["html"]
            if "<img" in html_str.lower():
                if not _HTML_STANDALONE_IMG_RE.search(html_str):
                    return (
                        LexicalEditReport(
                            refused=True,
                            reasons=["Refused: encountered HTML card with <img> that was not a standalone image card"],
                            matched=0,
                            changed=False,
                            diff=None,
                        ),
                        before,
                    )
                removed += 1
                continue
        kept.append(node)
    out["root"]["children"] = kept
    out_children = out["root"]["children"]

    # Optional safe auto-fix for split numbered lists after headings.
    if fix_split_numbered_lists:
        seen_occ: dict[str, int] = {}
        i = 0
        while i < len(out_children):
            node = out_children[i]
            if not (isinstance(node, dict) and _is_heading_node(node)):
                i += 1
                continue
            h_text = _extract_text(node).strip()
            h_norm = _normalize_heading(h_text)
            seen_occ[h_norm] = seen_occ.get(h_norm, 0) + 1

            scan_idx = i + 1
            while scan_idx < len(out_children):
                n = out_children[scan_idx]
                if isinstance(n, dict) and n.get("type") == "paragraph" and not _extract_text(n).strip():
                    scan_idx += 1
                    continue
                break
            if scan_idx + 1 < len(out_children):
                first = out_children[scan_idx]
                nxt = out_children[scan_idx + 1]
                if (
                    isinstance(first, dict)
                    and first.get("type") == "list"
                    and first.get("listType") == "number"
                    and isinstance(nxt, dict)
                    and nxt.get("type") == "html"
                    and isinstance(nxt.get("html"), str)
                    and _HTML_OL_LI_RE.search(nxt["html"])
                ):
                    rep, new_out = fix_numbered_list_split_by_html_ol_after_heading(
                        out,
                        heading=h_text,
                        heading_occurrence=seen_occ[h_norm],
                        include_diff=False,
                    )
                    if rep.refused:
                        return (
                            LexicalEditReport(
                                refused=True,
                                reasons=["Refused: split-list fixer refused unexpectedly", *rep.reasons],
                                matched=0,
                                changed=False,
                                diff=None,
                            ),
                            before,
                        )
                    out = new_out
                    out_children = out["root"]["children"]
                    continue
            i += 1

    matched = 0
    for p in normalized:
        heading = str(p["heading"])
        heading_occurrence = p.get("heading_occurrence")
        target = _normalize_heading(heading)
        heading_idxs: list[int] = []
        for idx, node in enumerate(out_children):
            if isinstance(node, dict) and _is_heading_node(node):
                if _normalize_heading(_extract_text(node)) == target:
                    heading_idxs.append(idx)
        if not heading_idxs:
            return (
                LexicalEditReport(refused=True, reasons=[f"No heading matched: {heading}"], matched=matched, changed=False, diff=None),
                before,
            )
        if len(heading_idxs) > 1 and heading_occurrence is None:
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"Refused: heading matched multiple times ({len(heading_idxs)}); pass heading_occurrence"],
                    matched=matched,
                    changed=False,
                    diff=None,
                ),
                before,
            )
        occ = int(heading_occurrence or 1)
        if occ < 1 or occ > len(heading_idxs):
            return (
                LexicalEditReport(
                    refused=True,
                    reasons=[f"heading_occurrence out of range (1..{len(heading_idxs)}) for heading {heading}"],
                    matched=matched,
                    changed=False,
                    diff=None,
                ),
                before,
            )
        insert_at = heading_idxs[occ - 1]
        desired_src = str(p["src"])

        # Idempotence: if the immediate previous node is already this image, just ensure meta fields.
        if insert_at > 0:
            prev = out_children[insert_at - 1]
            if isinstance(prev, dict) and _is_image_node(prev) and prev.get("src") == desired_src:
                if isinstance(p.get("alt"), str):
                    prev["alt"] = p["alt"]
                if isinstance(p.get("title"), str):
                    prev["title"] = p["title"]
                if isinstance(p.get("caption"), str):
                    prev["caption"] = _normalize_caption_input(p["caption"])
                matched += 1
                continue

        node = deepcopy(template)
        node["src"] = desired_src
        if isinstance(p.get("alt"), str):
            node["alt"] = p["alt"]
        if isinstance(p.get("title"), str):
            node["title"] = p["title"]
        if isinstance(p.get("caption"), str):
            node["caption"] = _normalize_caption_input(p["caption"])

        out_children.insert(insert_at, node)
        matched += 1

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    reasons: list[str] = []
    if removed:
        reasons.append(f"Removed {removed} existing image card(s)")
    return (
        LexicalEditReport(refused=False, reasons=reasons, matched=matched, changed=changed, diff=diff),
        out if changed else before,
    )


def replace_images_by_src_map(
    lexical_obj: dict[str, Any],
    *,
    mapping: dict[str, Any],
    include_diff: bool,
) -> tuple[LexicalEditReport, dict[str, Any], list[ReplaceManyItemResult]]:
    """
    Replace multiple image src values in one pass (one deep copy).

    mapping formats supported:
    - { "old_src": "new_src", ... }
    - { "old_src": {"new_src": "...", "alt": "...", "caption": "...", "title": "..."}, ... }

    Safety:
    - Refuses if any old_src matches multiple images.
    - Refuses if old_src is missing and new_src matches multiple images.
    - If old_src is missing and new_src matches exactly one image, treats it as already replaced and applies meta.
    """
    before = lexical_obj
    if not isinstance(mapping, dict) or not mapping:
        return (
            LexicalEditReport(refused=True, reasons=["Mapping must be a non-empty JSON object"], matched=0, changed=False, diff=None),
            before,
            [],
        )

    out = deepcopy(lexical_obj)
    item_results: list[ReplaceManyItemResult] = []
    refused_reasons: list[str] = []

    for old_src, spec in mapping.items():
        if not isinstance(old_src, str) or not old_src.strip():
            refused_reasons.append("Mapping key (old_src) must be a non-empty string")
            continue

        new_src: str | None = None
        alt: str | None = None
        caption: str | None = None
        title: str | None = None

        if isinstance(spec, str):
            new_src = spec
        elif isinstance(spec, dict):
            ns = spec.get("new_src")
            if isinstance(ns, str):
                new_src = ns
            alt = spec.get("alt") if isinstance(spec.get("alt"), str) else None
            caption = spec.get("caption") if isinstance(spec.get("caption"), str) else None
            title = spec.get("title") if isinstance(spec.get("title"), str) else None
        else:
            refused_reasons.append(f"Mapping value for {old_src!r} must be a string or object")
            continue

        if not isinstance(new_src, str) or not new_src.strip():
            refused_reasons.append(f"Mapping for {old_src!r} must include new_src")
            continue
        new_src = new_src.strip()

        matches_old: list[dict[str, Any]] = []
        for _, node in _iter_nodes(out):
            if _is_image_node(node) and node.get("src") == old_src:
                matches_old.append(node)

        reasons: list[str] = []
        if not matches_old:
            matches_new: list[dict[str, Any]] = []
            for _, node in _iter_nodes(out):
                if _is_image_node(node) and node.get("src") == new_src:
                    matches_new.append(node)
            if len(matches_new) == 1:
                node = matches_new[0]
                reasons.append("No old-src match; new-src already present (treating as already replaced)")
                item_changed = False
                if alt is not None:
                    item_changed = item_changed or node.get("alt") != alt
                    node["alt"] = alt
                if title is not None:
                    item_changed = item_changed or node.get("title") != title
                    node["title"] = title
                if caption is not None:
                    norm_cap = _normalize_caption_input(caption)
                    item_changed = item_changed or node.get("caption") != norm_cap
                    node["caption"] = norm_cap
                item_results.append(
                    ReplaceManyItemResult(
                        old_src=old_src,
                        new_src=new_src,
                        matched=1,
                        changed=item_changed,
                        reasons=reasons,
                    )
                )
                continue
            if len(matches_new) > 1:
                refused_reasons.append(
                    f"Refused: old-src {old_src!r} not found and new-src matched multiple images ({len(matches_new)})"
                )
                item_results.append(
                    ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=len(matches_new), changed=False, reasons=["refused"])
                )
                continue
            refused_reasons.append(f"No image node matched old-src {old_src!r} (and new-src not found)")
            item_results.append(
                ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=0, changed=False, reasons=["refused"])
            )
            continue

        if len(matches_old) > 1:
            refused_reasons.append(f"Refused: old-src {old_src!r} matched multiple images ({len(matches_old)})")
            item_results.append(
                ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=len(matches_old), changed=False, reasons=["refused"])
            )
            continue

        node = matches_old[0]
        item_changed = node.get("src") != new_src
        node["src"] = new_src
        if alt is not None:
            item_changed = item_changed or node.get("alt") != alt
            node["alt"] = alt
        if title is not None:
            item_changed = item_changed or node.get("title") != title
            node["title"] = title
        if caption is not None:
            norm_cap = _normalize_caption_input(caption)
            item_changed = item_changed or node.get("caption") != norm_cap
            node["caption"] = norm_cap
        item_results.append(
            ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=1, changed=item_changed, reasons=[])
        )

    if refused_reasons:
        # Refuse the whole operation (no partial apply).
        return (
            LexicalEditReport(refused=True, reasons=refused_reasons, matched=0, changed=False, diff=None),
            before,
            item_results,
        )

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        LexicalEditReport(refused=False, reasons=[], matched=len(mapping), changed=changed, diff=diff),
        out if changed else before,
        item_results,
    )


def build_replace_many_map_for_missing_captions(
    lexical_obj: dict[str, Any],
    *,
    include_all: bool,
) -> dict[str, dict[str, str]]:
    """
    Builds a mapping file compatible with `post bodylex image replace-many`.

    Default use-case:
    - select only images that are missing captions
    - prefill new_src with the same src (no rehosting)
    - prefill alt with the current alt (or empty)
    - leave caption empty for the human to fill

    If include_all=True, includes all images and pre-fills caption with the current caption text (best-effort).
    """
    out: dict[str, dict[str, str]] = {}
    for img in list_images(lexical_obj):
        caption_text = img.caption_text or ""
        has_caption = bool(caption_text.strip())
        if not include_all and has_caption:
            continue
        out[img.src] = {
            "new_src": img.src,
            "alt": img.alt or "",
            "caption": caption_text if include_all and has_caption else "",
        }
        if img.title and img.title.strip():
            out[img.src]["title"] = img.title
    return out
