from __future__ import annotations

from typing import Any


def _as_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _get_str(d: dict[str, Any], k: str) -> str | None:
    return _as_str(d.get(k))


def _best_preview_url(item: dict[str, Any]) -> str | None:
    direct = (
        _get_str(item, "preview_url")
        or _get_str(item, "previewUrl")
        or _get_str(item, "thumbnail_url")
        or _get_str(item, "thumbnailUrl")
    )
    if direct:
        return direct

    preview = item.get("preview")
    if isinstance(preview, dict):
        for k in ("url", "href", "src"):
            s = _get_str(preview, k)
            if s:
                return s

    image = item.get("image")
    if isinstance(image, dict):
        for k in ("url", "href", "src"):
            s = _get_str(image, k)
            if s:
                return s
        source = image.get("source")
        if isinstance(source, dict):
            for k in ("url", "href", "src"):
                s = _get_str(source, k)
                if s:
                    return s

    thumbs = item.get("thumbnails")
    if isinstance(thumbs, list) and thumbs:
        best_url: str | None = None
        best_score = -1
        for t in thumbs:
            if not isinstance(t, dict):
                continue
            url = _get_str(t, "url") or _get_str(t, "src") or _get_str(t, "href")
            if not url:
                continue
            w = t.get("width")
            h = t.get("height")
            score = 0
            try:
                if w is not None:
                    score += int(w)
                if h is not None:
                    score += int(h)
            except Exception:
                score = 0
            if score >= best_score:
                best_score = score
                best_url = url
        if best_url:
            return best_url

    return None


def _author_str(item: dict[str, Any]) -> str | None:
    a = item.get("author")
    if isinstance(a, dict):
        return _as_str(a.get("name") or a.get("username") or a.get("id"))
    return _as_str(a)


def shape_search_shortlist(*, items: list[Any]) -> dict[str, Any]:
    shaped: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue

        rid = _as_str(raw.get("id") or raw.get("resource_id") or raw.get("resourceId"))
        title = _as_str(raw.get("title") or raw.get("name"))
        license_url = _as_str(raw.get("license_url") or raw.get("licenseUrl"))
        orientation = _as_str(raw.get("orientation"))
        resource_url = _as_str(raw.get("resource_url") or raw.get("resourceUrl") or raw.get("url") or raw.get("link"))

        shaped.append(
            {
                "id": rid,
                "title": title,
                "preview_url": _best_preview_url(raw),
                "license_url": license_url,
                "author": _author_str(raw),
                "orientation": orientation,
                "resource_url": resource_url,
            }
        )

    return {"items": shaped}

