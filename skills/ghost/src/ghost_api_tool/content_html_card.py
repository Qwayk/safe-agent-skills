from __future__ import annotations

import dataclasses
import re

from .diffutil import unified_diff

_KG_HTML_CARD_RE = re.compile(
    r"<!--kg-card-begin:\s*html\s*-->(?P<html>.*?)<!--kg-card-end:\s*html\s*-->",
    flags=re.I | re.S,
)
_IMG_RE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*(?P<q>['\"])(?P<src>.*?)(?P=q)[^>]*>", flags=re.I)
_FIGURE_RE = re.compile(r"<figure\b[^>]*>(?P<body>.*?)</figure>", flags=re.I | re.S)
_FIGCAPTION_RE = re.compile(
    r"<figcaption\b(?P<attrs>[^>]*)>(?P<cap>.*?)</figcaption>", flags=re.I | re.S
)


@dataclasses.dataclass(frozen=True)
class HtmlCardEditReport:
    matched_images: int
    updated_figcaptions: int
    refused: bool
    reasons: list[str]
    diff: str | None


def extract_html_card(post_html: str) -> str | None:
    matches = list(_KG_HTML_CARD_RE.finditer(post_html or ""))
    if len(matches) != 1:
        return None
    return matches[0].group("html")


def list_images_in_html_card(card_html: str) -> list[dict]:
    out = []
    for m in _IMG_RE.finditer(card_html):
        out.append({"src": m.group("src")})
    return out


def set_figcaptions_by_src(
    post_html: str,
    *,
    captions_by_src: dict[str, str],
    include_diff: bool,
) -> tuple[HtmlCardEditReport, str]:
    """
    Updates figcaptions inside a single HTML card.
    Matching key: <img src="..."> URL (exact string).
    """
    reasons: list[str] = []
    matches = list(_KG_HTML_CARD_RE.finditer(post_html or ""))
    if len(matches) != 1:
        return (
            HtmlCardEditReport(
                matched_images=0,
                updated_figcaptions=0,
                refused=True,
                reasons=["Refused: post html is not a single HTML card (kg html)"],
                diff=None,
            ),
            post_html,
        )
    m = matches[0]
    card = m.group("html")

    matched = 0
    updated = 0
    new_card = card

    # Iterate figures, find first img src inside, update/insert figcaption.
    def _update_figure(match: re.Match) -> str:
        nonlocal matched, updated
        figure_html = match.group(0)
        body = match.group("body")
        img_m = _IMG_RE.search(body)
        if not img_m:
            return figure_html
        src = img_m.group("src")
        if src not in captions_by_src:
            return figure_html
        matched += 1
        new_caption = captions_by_src[src]
        cap_m = _FIGCAPTION_RE.search(body)
        if cap_m:
            attrs = cap_m.group("attrs") or ""
            replacement = f"<figcaption{attrs}>{_escape_html(new_caption)}</figcaption>"
            after_cap = re.sub(_FIGCAPTION_RE, replacement, body, count=1)
            if after_cap != body:
                updated += 1
            return figure_html.replace(body, after_cap, 1)
        # Insert before </figure>
        insert = f"{body}<figcaption>{_escape_html(new_caption)}</figcaption>"
        updated += 1
        return figure_html.replace(body, insert, 1)

    new_card = _FIGURE_RE.sub(_update_figure, new_card)
    if matched == 0:
        reasons.append("No matching <figure><img src=...> found for provided captions")

    new_post_html = post_html[: m.start("html")] + new_card + post_html[m.end("html") :]

    diff = None
    if include_diff and new_post_html != post_html:
        diff = unified_diff(post_html, new_post_html)
    return (
        HtmlCardEditReport(
            matched_images=matched,
            updated_figcaptions=updated,
            refused=False,
            reasons=reasons,
            diff=diff,
        ),
        new_post_html,
    )


def _escape_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
