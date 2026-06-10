from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from .caption_policy import caption_matches_expected, guess_caption_policy
from .content_lexical import LexicalImage, list_images, parse_lexical_field
from .content_mobiledoc import parse_mobiledoc_field

_TRAILING_MONGOID_RE = re.compile(r"-[0-9a-f]{24}$")
_TRAILING_LONG_DIGITS_RE = re.compile(r"-\d{5,}$")

_HTML_LIST_CARD_HINT_RE = re.compile(r"<(?:ul|ol)\b", re.IGNORECASE)


def _is_legacy_wp_upload(url: str, *, legacy_hosts: list[str]) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False
    host = (p.hostname or "").lower()
    if not host:
        return False
    if host not in {h.lower() for h in legacy_hosts}:
        return False
    return "/wp-content/uploads/" in (p.path or "")


def _extract_text(obj: Any) -> str:
    if isinstance(obj, dict):
        if isinstance(obj.get("text"), str):
            return obj["text"]
        return "".join(_extract_text(v) for v in obj.values() if isinstance(v, (dict, list)))
    if isinstance(obj, list):
        return "".join(_extract_text(v) for v in obj)
    return ""


def _list_root_html_list_cards(lexical_obj: dict[str, Any]) -> list[dict[str, Any]]:
    root = lexical_obj.get("root")
    if not isinstance(root, dict):
        return []
    children = root.get("children")
    if not isinstance(children, list):
        return []

    out: list[dict[str, Any]] = []
    current_heading: str | None = None
    for idx, node in enumerate(children):
        if isinstance(node, dict) and node.get("type") in ("extended-heading", "heading"):
            heading_text = " ".join(_extract_text(node).strip().split())
            current_heading = heading_text if heading_text else None
            continue
        if not (isinstance(node, dict) and node.get("type") == "html"):
            continue
        html_str = node.get("html")
        if not (isinstance(html_str, str) and html_str.strip()):
            continue
        low = html_str.lower()
        if not _HTML_LIST_CARD_HINT_RE.search(low):
            continue
        # Heuristic: most WP importer artifacts include `start=` and/or Gutenberg comments.
        if "<li" not in low:
            continue
        if (" start=" not in low) and ("wp:list-item" not in low):
            continue
        out.append(
            {
                "path": f"root.children[{idx}]",
                "heading": current_heading,
                "html_preview": html_str[:140],
            }
        )
    return out


def audit_post(
    post: dict[str, Any],
    *,
    legacy_hosts: list[str],
    enforce_caption_policy: bool = False,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    slug = post.get("slug") if isinstance(post.get("slug"), str) else ""
    if slug:
        if _TRAILING_MONGOID_RE.search(slug) or _TRAILING_LONG_DIGITS_RE.search(slug):
            issues.append({"type": "slug", "message": "Slug looks auto-suffixed (ID-like).", "slug": slug})

    meta_description = post.get("meta_description")
    if not isinstance(meta_description, str) or not meta_description.strip():
        issues.append({"type": "meta", "message": "Missing meta_description."})

    feature_image = post.get("feature_image")
    if isinstance(feature_image, str) and feature_image.strip():
        alt = post.get("feature_image_alt")
        cap = post.get("feature_image_caption")
        if not (isinstance(alt, str) and alt.strip()):
            issues.append({"type": "feature_image", "message": "Feature image is missing alt text."})
        if not (isinstance(cap, str) and cap.strip()):
            issues.append({"type": "feature_image", "message": "Feature image is missing caption."})
        if enforce_caption_policy:
            exp = guess_caption_policy(feature_image, alt=alt if isinstance(alt, str) else None, title=None, caption_text=cap if isinstance(cap, str) else None)
            if not caption_matches_expected(cap if isinstance(cap, str) else None, expected_suffix=exp.expected_suffix):
                issues.append(
                    {
                        "type": "caption_policy",
                        "message": "Feature image caption does not match the caption policy.",
                        "feature_image": {
                            "src": feature_image,
                            "kind": exp.kind,
                            "expected_suffix": exp.expected_suffix,
                            "caption_text": cap if isinstance(cap, str) else None,
                        },
                    }
                )

    # Prefer Lexical if available; otherwise support mobiledoc (older imports).
    lexical_obj, reasons = parse_lexical_field(post.get("lexical"))
    imgs: list[LexicalImage] = []
    if lexical_obj is None:
        mob_obj, mob_reasons = parse_mobiledoc_field(post.get("mobiledoc"))
        if mob_obj is None:
            issues.append(
                {
                    "type": "content",
                    "message": "Cannot parse lexical or mobiledoc field.",
                    "reasons": {"lexical": reasons, "mobiledoc": mob_reasons},
                }
            )
            return {"issues": issues, "ready_to_publish": False}
        from .content_mobiledoc import list_images as list_mobiledoc_images

        mob_imgs, mob_list_reasons = list_mobiledoc_images(mob_obj)
        if mob_list_reasons:
            issues.append({"type": "mobiledoc", "message": "Cannot list mobiledoc images.", "reasons": mob_list_reasons})
            return {"issues": issues, "ready_to_publish": False}
        # Normalize into LexicalImage-like objects for downstream checks.
        for mi in mob_imgs:
            imgs.append(
                LexicalImage(
                    index=mi.index,
                    path=f"mobiledoc.cards[{mi.card_index}]",
                    src=mi.src,
                    alt=mi.alt,
                    title=mi.title,
                    caption=mi.caption,
                    caption_text=mi.caption,
                    context_heading=None,
                )
            )
    else:
        html_list_cards = _list_root_html_list_cards(lexical_obj)
        if html_list_cards:
            issues.append(
                {
                    "type": "content_structure",
                    "message": "Found HTML list cards (WordPress importer artifact). Convert them to native Ghost lists.",
                    "count": len(html_list_cards),
                    "cards_sample": html_list_cards[:10],
                }
            )
        imgs = list_images(lexical_obj)
    by_src: dict[str, int] = {}
    legacy: list[dict[str, Any]] = []
    missing_alt: list[dict[str, Any]] = []
    missing_caption: list[dict[str, Any]] = []
    caption_mismatch: list[dict[str, Any]] = []
    for im in imgs:
        by_src[im.src] = by_src.get(im.src, 0) + 1
        if _is_legacy_wp_upload(im.src, legacy_hosts=legacy_hosts):
            legacy.append({"src": im.src, "heading": im.context_heading, "path": im.path})
        if not (isinstance(im.alt, str) and im.alt.strip()):
            missing_alt.append({"src": im.src, "heading": im.context_heading, "path": im.path})
        if not (isinstance(im.caption_text, str) and im.caption_text.strip()):
            missing_caption.append({"src": im.src, "heading": im.context_heading, "path": im.path})
        if enforce_caption_policy:
            exp = guess_caption_policy(im.src, alt=im.alt, title=im.title, caption_text=im.caption_text)
            if not caption_matches_expected(im.caption_text, expected_suffix=exp.expected_suffix):
                caption_mismatch.append(
                    {
                        "src": im.src,
                        "heading": im.context_heading,
                        "path": im.path,
                        "kind": exp.kind,
                        "expected_suffix": exp.expected_suffix,
                        "caption_text": im.caption_text,
                    }
                )

    duplicates = [{"src": s, "count": c} for s, c in by_src.items() if c > 1]
    if duplicates:
        issues.append({"type": "body_images", "message": "Duplicate body images found.", "duplicates": duplicates})
    if legacy:
        issues.append({"type": "body_images", "message": "Body images still reference WordPress uploads.", "images": legacy})
    if missing_alt:
        issues.append({"type": "body_images", "message": "Body images missing alt text.", "images": missing_alt})
    if missing_caption:
        issues.append({"type": "body_images", "message": "Body images missing caption.", "images": missing_caption})
    if caption_mismatch:
        issues.append(
            {
                "type": "caption_policy",
                "message": "Body image captions do not match the caption policy.",
                "images": caption_mismatch,
            }
        )

    return {"issues": issues, "ready_to_publish": len(issues) == 0, "image_count": len(imgs)}
