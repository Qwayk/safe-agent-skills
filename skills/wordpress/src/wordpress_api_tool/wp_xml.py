from __future__ import annotations

import dataclasses
import datetime as dt
import xml.etree.ElementTree as ET
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class WpXmlPostRow:
    wp_post_id: int
    wp_slug: str
    wp_title: str
    wp_status: str
    wp_date: str | None
    wp_modified: str | None
    wp_author: str | None
    wp_tags: list[str]
    wp_categories: list[str]


_NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def _text(el: ET.Element | None) -> str | None:
    if el is None:
        return None
    if el.text is None:
        return None
    t = el.text.strip()
    return t if t else None


def _parse_wp_datetime(s: str | None) -> str | None:
    if not s:
        return None
    # WordPress exports in "YYYY-MM-DD HH:MM:SS" (local blog time).
    try:
        dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return s
    return s


def parse_wordpress_export_xml(path: str | Path) -> list[WpXmlPostRow]:
    p = Path(path)
    rows: list[WpXmlPostRow] = []

    # Use iterparse so we can handle large exports without loading the entire tree into memory.
    # We process <item> elements as they close and clear them immediately.
    for _, item in ET.iterparse(p, events=("end",)):
        if item.tag != "item":
            continue
        post_type = _text(item.find("wp:post_type", _NS)) or ""
        if post_type != "post":
            item.clear()
            continue

        post_id_raw = _text(item.find("wp:post_id", _NS))
        slug = _text(item.find("wp:post_name", _NS))
        title = _text(item.find("title")) or ""
        status = _text(item.find("wp:status", _NS)) or ""
        author = _text(item.find("dc:creator", _NS))
        date = _parse_wp_datetime(_text(item.find("wp:post_date", _NS)))
        modified = _parse_wp_datetime(_text(item.find("wp:post_modified", _NS)))

        if not post_id_raw or not post_id_raw.isdigit():
            item.clear()
            continue
        if not slug:
            # Some posts may have empty slug; keep them but with a placeholder.
            slug = ""

        tags: list[str] = []
        cats: list[str] = []
        for cat in item.findall("category"):
            domain = cat.attrib.get("domain", "")
            name = (cat.text or "").strip()
            if not name:
                continue
            if domain == "post_tag":
                tags.append(name)
            elif domain == "category":
                cats.append(name)

        rows.append(
            WpXmlPostRow(
                wp_post_id=int(post_id_raw),
                wp_slug=slug,
                wp_title=title,
                wp_status=status,
                wp_date=date,
                wp_modified=modified,
                wp_author=author,
                wp_tags=sorted(set(tags)),
                wp_categories=sorted(set(cats)),
            )
        )
        item.clear()
    return rows
