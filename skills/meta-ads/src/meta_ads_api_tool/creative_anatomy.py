from __future__ import annotations

import hashlib
import re
from typing import Any

from .http import HttpClient


def extract_creative_anatomy(creative: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a Graph `adcreative` payload into a normalized, analysis-friendly object.

    This is intentionally permissive: Meta creative shapes vary widely by objective,
    placement, and creative type. Callers should treat missing fields as expected.
    """
    cid = str(creative.get("id") or "").strip() or None

    oss = creative.get("object_story_spec") if isinstance(creative.get("object_story_spec"), dict) else {}
    afs = creative.get("asset_feed_spec") if isinstance(creative.get("asset_feed_spec"), dict) else {}

    link_data = oss.get("link_data") if isinstance(oss.get("link_data"), dict) else {}
    video_data = oss.get("video_data") if isinstance(oss.get("video_data"), dict) else {}
    template_data = oss.get("template_data") if isinstance(oss.get("template_data"), dict) else {}

    primary_texts: list[str] = []
    headlines: list[str] = []
    descriptions: list[str] = []
    cta_types: list[str] = []
    urls: list[str] = []
    image_urls: list[str] = []
    video_ids: list[str] = []

    def add_str(lst: list[str], v: Any) -> None:
        s = str(v or "").strip()
        if s and s not in lst:
            lst.append(s)

    def add_url(v: Any) -> None:
        s = str(v or "").strip()
        if s and re.match(r"^https?://", s, flags=re.IGNORECASE):
            s2 = HttpClient.redact_url(s)
            if s2 not in urls:
                urls.append(s2)

    def add_image_url(v: Any) -> None:
        s = str(v or "").strip()
        if s and re.match(r"^https?://", s, flags=re.IGNORECASE):
            s2 = HttpClient.redact_url(s)
            if s2 not in image_urls:
                image_urls.append(s2)

    for k in ("name", "title", "body", "message", "link_description", "description"):
        if k in creative:
            add_str(primary_texts, creative.get(k))

    for v in (creative.get("image_url"), creative.get("thumbnail_url")):
        add_image_url(v)
        add_url(v)

    # object_story_spec: link_data
    add_str(primary_texts, link_data.get("message"))
    add_str(headlines, link_data.get("name"))
    add_str(descriptions, link_data.get("description"))
    add_url(link_data.get("link"))
    if isinstance(link_data.get("call_to_action"), dict):
        add_str(cta_types, link_data.get("call_to_action", {}).get("type"))
        value = link_data.get("call_to_action", {}).get("value")
        if isinstance(value, dict):
            add_url(value.get("link"))
    add_image_url(link_data.get("picture"))
    for ca in link_data.get("child_attachments") if isinstance(link_data.get("child_attachments"), list) else []:
        if isinstance(ca, dict):
            add_image_url(ca.get("picture"))
            add_url(ca.get("link"))
            add_str(headlines, ca.get("name"))
            add_str(descriptions, ca.get("description"))

    # object_story_spec: video_data
    add_str(primary_texts, video_data.get("message"))
    add_str(headlines, video_data.get("title"))
    add_str(descriptions, video_data.get("description"))
    if "video_id" in video_data:
        add_str(video_ids, video_data.get("video_id"))
    add_image_url(video_data.get("image_url"))
    add_url(video_data.get("link_description"))

    # object_story_spec: template_data (common for some formats)
    add_str(primary_texts, template_data.get("message"))
    add_str(headlines, template_data.get("name"))
    add_str(descriptions, template_data.get("description"))
    add_url(template_data.get("link"))
    add_image_url(template_data.get("picture"))
    if isinstance(template_data.get("call_to_action_type"), str):
        add_str(cta_types, template_data.get("call_to_action_type"))

    # asset_feed_spec: dynamic creative
    for t in afs.get("bodies") if isinstance(afs.get("bodies"), list) else []:
        if isinstance(t, dict):
            add_str(primary_texts, t.get("text"))
    for t in afs.get("titles") if isinstance(afs.get("titles"), list) else []:
        if isinstance(t, dict):
            add_str(headlines, t.get("text"))
    for t in afs.get("descriptions") if isinstance(afs.get("descriptions"), list) else []:
        if isinstance(t, dict):
            add_str(descriptions, t.get("text"))
    for i in afs.get("images") if isinstance(afs.get("images"), list) else []:
        if isinstance(i, dict):
            add_image_url(i.get("url"))
            add_url(i.get("url"))
    for v in afs.get("videos") if isinstance(afs.get("videos"), list) else []:
        if isinstance(v, dict):
            add_str(video_ids, v.get("video_id"))

    if cid:
        return {
            "creative_id": cid,
            "text": {"primary": primary_texts, "headlines": headlines, "descriptions": descriptions},
            "cta_types": cta_types,
            "urls": urls,
            "image_urls": image_urls,
            "video_ids": video_ids,
            "actors": {
                "page_id": str(oss.get("page_id") or "").strip() or None,
                "instagram_actor_id": str(oss.get("instagram_actor_id") or "").strip() or None,
            },
        }
    return {
        "creative_id": None,
        "text": {"primary": primary_texts, "headlines": headlines, "descriptions": descriptions},
        "cta_types": cta_types,
        "urls": urls,
        "image_urls": image_urls,
        "video_ids": video_ids,
        "actors": {
            "page_id": str(oss.get("page_id") or "").strip() or None,
            "instagram_actor_id": str(oss.get("instagram_actor_id") or "").strip() or None,
        },
    }


def extract_asset_urls(creative: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract candidate asset URLs from a creative payload.

    Returns a list of items with at minimum:
      - creative_id
      - url
      - kind
      - url_sha256
    """
    anatomy = extract_creative_anatomy(creative)
    cid = anatomy.get("creative_id")
    out: list[dict[str, Any]] = []

    def add(url: str, kind: str) -> None:
        u = str(url or "").strip()
        if not u or not re.match(r"^https?://", u, flags=re.IGNORECASE):
            return
        h = hashlib.sha256(u.encode("utf-8")).hexdigest()
        out.append({"creative_id": cid, "url": u, "kind": kind, "url_sha256": h})

    for u in anatomy.get("image_urls") or []:
        add(str(u), "image_url")
    for u in anatomy.get("urls") or []:
        add(str(u), "landing_url")
    return _dedupe_assets(out)


def _dedupe_assets(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for it in items:
        u = str(it.get("url") or "").strip()
        k = str(it.get("kind") or "").strip()
        if not u or not k:
            continue
        key = (k, u)
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
