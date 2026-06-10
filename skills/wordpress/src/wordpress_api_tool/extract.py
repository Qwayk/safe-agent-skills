from __future__ import annotations

import dataclasses
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin


@dataclasses.dataclass(frozen=True)
class ExtractedImage:
    attachment_id: int | None
    sources: tuple[str, ...]


IMG_CLASS_ID_RE = re.compile(r"\bwp-image-(\d+)\b")


def _scan_wp_image_blocks(raw: str) -> set[int]:
    """
    Safe extraction from Gutenberg image blocks:
    - Find <!-- wp:image ... --> and parse JSON attrs.
    - Only accept integer "id".
    """
    ids: set[int] = set()
    idx = 0
    while True:
        start = raw.find("<!-- wp:image", idx)
        if start == -1:
            break
        end = raw.find("-->", start)
        if end == -1:
            break
        header = raw[start + len("<!-- wp:image") : end].strip()
        idx = end + 3
        if not header.startswith("{"):
            continue
        try:
            attrs = json.loads(header)
        except Exception:
            continue
        block_id = attrs.get("id")
        if isinstance(block_id, int):
            ids.add(block_id)
    return ids


def extract_attachment_ids_from_post_content(raw_html: str) -> list[ExtractedImage]:
    """
    Extract attachment IDs from:
    - <img class="... wp-image-123 ...">
    - Gutenberg image blocks (attrs JSON contains "id")
    """
    found: dict[int, set[str]] = {}

    for m in IMG_CLASS_ID_RE.finditer(raw_html):
        aid = int(m.group(1))
        found.setdefault(aid, set()).add("img_class")

    for aid in _scan_wp_image_blocks(raw_html):
        found.setdefault(aid, set()).add("wp_image_block")

    out: list[ExtractedImage] = []
    for aid in sorted(found.keys()):
        out.append(ExtractedImage(attachment_id=aid, sources=tuple(sorted(found[aid]))))
    return out


class _ImgSrcParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.srcs: list[str] = []
        self._base_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "base":
            href = dict(attrs).get("href")
            if isinstance(href, str) and href.strip():
                self._base_href = href.strip()
            return

        if tag != "img":
            return
        d = dict(attrs)
        src = d.get("src")
        if isinstance(src, str) and src.strip():
            self.srcs.append(self._abs(src.strip()))
        srcset = d.get("srcset")
        if isinstance(srcset, str) and srcset.strip():
            for part in srcset.split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.srcs.append(self._abs(url))

    def _abs(self, u: str) -> str:
        if self._base_href:
            return urljoin(self._base_href, u)
        return u


def extract_img_srcs_from_html(html: str) -> list[str]:
    """
    Extracts image URLs from rendered HTML:
    - <img src="...">
    - <img srcset="..."> (all URLs)

    Returns a de-duplicated list in first-seen order.
    """
    p = _ImgSrcParser()
    try:
        p.feed(html)
    except Exception:
        # HTML can be malformed; best effort only.
        return []
    seen: set[str] = set()
    out: list[str] = []
    for s in p.srcs:
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out
