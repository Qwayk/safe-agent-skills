from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class FieldDiff:
    field: str
    before: Any
    after: Any


def diff_fields(before: dict[str, Any], after: dict[str, Any], *, fields: list[str]) -> list[FieldDiff]:
    out: list[FieldDiff] = []
    for f in fields:
        b = before.get(f)
        a = after.get(f)
        if a is not None and a != b:
            out.append(FieldDiff(field=f, before=b, after=a))
    return out


def caption_text_from_media(media: dict[str, Any]) -> str:
    cap = media.get("caption")
    if isinstance(cap, dict):
        return cap.get("raw") or cap.get("rendered") or ""
    if isinstance(cap, str):
        return cap
    return ""


def title_text_from_media(media: dict[str, Any]) -> str:
    title = media.get("title")
    if isinstance(title, dict):
        return title.get("raw") or title.get("rendered") or ""
    if isinstance(title, str):
        return title
    return ""


def source_url_from_media(media: dict[str, Any]) -> str:
    return media.get("source_url") or ""

