from __future__ import annotations

import dataclasses
import json
from copy import deepcopy
from typing import Any

from .diffutil import stable_json, unified_diff


@dataclasses.dataclass(frozen=True)
class MobiledocImage:
    index: int
    card_index: int
    src: str
    alt: str | None
    title: str | None
    caption: str | None


@dataclasses.dataclass(frozen=True)
class MobiledocEditReport:
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


@dataclasses.dataclass(frozen=True)
class DedupeImagesResult:
    removed: int
    duplicates: list[dict[str, Any]]


def parse_mobiledoc_field(mobiledoc: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if mobiledoc is None:
        return None, ["Missing mobiledoc field"]
    if isinstance(mobiledoc, str):
        try:
            obj = json.loads(mobiledoc)
        except json.JSONDecodeError as e:
            return None, [f"Mobiledoc JSON decode failed: {e}"]
        if not isinstance(obj, dict):
            return None, ["Mobiledoc root must be a JSON object"]
        return obj, []
    if isinstance(mobiledoc, dict):
        return mobiledoc, []
    return None, [f"Unsupported mobiledoc type: {type(mobiledoc).__name__}"]


def dump_mobiledoc_field(obj: dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _changed_and_diff(before_obj: dict[str, Any], after_obj: dict[str, Any], *, include_diff: bool) -> tuple[bool, str | None]:
    before_s = stable_json(before_obj)
    after_s = stable_json(after_obj)
    changed = before_s != after_s
    diff = unified_diff(before_s, after_s) if include_diff and changed else None
    return changed, diff


def list_images(mobiledoc_obj: dict[str, Any]) -> tuple[list[MobiledocImage], list[str]]:
    cards = mobiledoc_obj.get("cards")
    if not isinstance(cards, list):
        return [], ["Mobiledoc cards is missing or not a list"]

    images: list[MobiledocImage] = []
    idx = 0
    for card_index, card in enumerate(cards):
        if not (isinstance(card, list) and len(card) >= 2 and isinstance(card[0], str) and isinstance(card[1], dict)):
            continue
        if card[0] != "image":
            continue
        payload = card[1]
        src = payload.get("src")
        if not isinstance(src, str) or not src.strip():
            continue
        images.append(
            MobiledocImage(
                index=idx,
                card_index=card_index,
                src=src,
                alt=payload.get("alt") if isinstance(payload.get("alt"), str) else None,
                title=payload.get("title") if isinstance(payload.get("title"), str) else None,
                caption=payload.get("caption") if isinstance(payload.get("caption"), str) else None,
            )
        )
        idx += 1
    return images, []


def build_replace_many_map_for_missing_captions(
    mobiledoc_obj: dict[str, Any],
    *,
    include_all: bool,
) -> tuple[dict[str, dict[str, str]], list[str]]:
    imgs, reasons = list_images(mobiledoc_obj)
    if reasons:
        return {}, reasons
    out: dict[str, dict[str, str]] = {}
    for img in imgs:
        cap = img.caption or ""
        has_cap = bool(cap.strip())
        if not include_all and has_cap:
            continue
        out[img.src] = {
            "new_src": img.src,
            "alt": img.alt or "",
            "caption": cap if include_all and has_cap else "",
        }
        if img.title and img.title.strip():
            out[img.src]["title"] = img.title
    return out, []


def replace_images_by_src_map(
    mobiledoc_obj: dict[str, Any],
    *,
    mapping: dict[str, Any],
    include_diff: bool,
) -> tuple[MobiledocEditReport, dict[str, Any], list[ReplaceManyItemResult]]:
    """
    Replace multiple mobiledoc image card src values and/or set meta in one pass.

    mapping formats supported:
    - { "old_src": "new_src", ... }
    - { "old_src": {"new_src": "...", "alt": "...", "caption": "...", "title": "..."}, ... }

    Safety:
    - Refuses if any old_src matches multiple images.
    - Refuses if old_src is missing and new_src matches multiple images.
    - If old_src is missing and new_src matches exactly one image, treats it as already replaced and applies meta.
    """
    before = mobiledoc_obj
    if not isinstance(mapping, dict) or not mapping:
        return (
            MobiledocEditReport(refused=True, reasons=["Mapping must be a non-empty JSON object"], matched=0, changed=False, diff=None),
            before,
            [],
        )

    out = deepcopy(mobiledoc_obj)
    cards = out.get("cards")
    if not isinstance(cards, list):
        return (
            MobiledocEditReport(refused=True, reasons=["Mobiledoc cards is missing or not a list"], matched=0, changed=False, diff=None),
            before,
            [],
        )

    item_results: list[ReplaceManyItemResult] = []
    refused_reasons: list[str] = []

    def _iter_image_payloads():
        for card in cards:
            if not (isinstance(card, list) and len(card) >= 2 and card[0] == "image" and isinstance(card[1], dict)):
                continue
            payload = card[1]
            src = payload.get("src")
            if isinstance(src, str):
                yield payload

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

        matches_old: list[dict[str, Any]] = [p for p in _iter_image_payloads() if p.get("src") == old_src]
        reasons: list[str] = []

        if not matches_old:
            matches_new: list[dict[str, Any]] = [p for p in _iter_image_payloads() if p.get("src") == new_src]
            if len(matches_new) == 1:
                payload = matches_new[0]
                reasons.append("No old-src match; new-src already present (treating as already replaced)")
                item_changed = False
                if alt is not None:
                    item_changed = item_changed or payload.get("alt") != alt
                    payload["alt"] = alt
                if title is not None:
                    item_changed = item_changed or payload.get("title") != title
                    payload["title"] = title
                if caption is not None:
                    item_changed = item_changed or payload.get("caption") != caption
                    payload["caption"] = caption
                item_results.append(ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=1, changed=item_changed, reasons=reasons))
                continue
            if len(matches_new) > 1:
                refused_reasons.append(f"Refused: old-src {old_src!r} not found and new-src matched multiple images ({len(matches_new)})")
                item_results.append(ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=len(matches_new), changed=False, reasons=["refused"]))
                continue
            refused_reasons.append(f"No image card matched old-src {old_src!r} (and new-src not found)")
            item_results.append(ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=0, changed=False, reasons=["refused"]))
            continue

        if len(matches_old) > 1:
            refused_reasons.append(f"Refused: old-src {old_src!r} matched multiple images ({len(matches_old)})")
            item_results.append(ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=len(matches_old), changed=False, reasons=["refused"]))
            continue

        payload = matches_old[0]
        item_changed = payload.get("src") != new_src
        payload["src"] = new_src
        if alt is not None:
            item_changed = item_changed or payload.get("alt") != alt
            payload["alt"] = alt
        if title is not None:
            item_changed = item_changed or payload.get("title") != title
            payload["title"] = title
        if caption is not None:
            item_changed = item_changed or payload.get("caption") != caption
            payload["caption"] = caption
        item_results.append(ReplaceManyItemResult(old_src=old_src, new_src=new_src, matched=1, changed=item_changed, reasons=[]))

    if refused_reasons:
        return (
            MobiledocEditReport(refused=True, reasons=refused_reasons, matched=0, changed=False, diff=None),
            before,
            item_results,
        )

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    return (
        MobiledocEditReport(refused=False, reasons=[], matched=len(mapping), changed=changed, diff=diff),
        out if changed else before,
        item_results,
    )


def dedupe_image_cards(
    mobiledoc_obj: dict[str, Any],
    *,
    include_diff: bool,
) -> tuple[MobiledocEditReport, dict[str, Any], DedupeImagesResult]:
    """
    Remove duplicate mobiledoc image cards by exact src match, keeping the first occurrence.

    This is a structural cleanup to make downstream operations (like replace-many) safe, because
    replace-many refuses when the same old-src matches multiple images.
    """
    before = mobiledoc_obj
    cards = mobiledoc_obj.get("cards")
    sections = mobiledoc_obj.get("sections")
    if not isinstance(cards, list):
        return (
            MobiledocEditReport(refused=True, reasons=["Mobiledoc cards is missing or not a list"], matched=0, changed=False, diff=None),
            before,
            DedupeImagesResult(removed=0, duplicates=[]),
        )
    if not isinstance(sections, list):
        return (
            MobiledocEditReport(refused=True, reasons=["Mobiledoc sections is missing or not a list"], matched=0, changed=False, diff=None),
            before,
            DedupeImagesResult(removed=0, duplicates=[]),
        )

    # Identify duplicate *image cards* by src, removing later card indices.
    first_by_src: dict[str, int] = {}
    by_src: dict[str, int] = {}
    remove_card_indices: set[int] = set()
    for idx, card in enumerate(cards):
        if not (isinstance(card, list) and len(card) >= 2 and card[0] == "image" and isinstance(card[1], dict)):
            continue
        payload = card[1]
        src = payload.get("src")
        if not isinstance(src, str) or not src.strip():
            continue
        src = src.strip()
        by_src[src] = by_src.get(src, 0) + 1
        if src not in first_by_src:
            first_by_src[src] = idx
            continue
        remove_card_indices.add(idx)

    duplicates = [{"src": s, "count": c} for s, c in by_src.items() if c > 1]
    if not remove_card_indices:
        return (
            MobiledocEditReport(refused=False, reasons=[], matched=0, changed=False, diff=None),
            before,
            DedupeImagesResult(removed=0, duplicates=duplicates),
        )

    # Rebuild cards array and keep mapping old -> new indices for section updates.
    old_to_new: dict[int, int] = {}
    new_cards: list[Any] = []
    for old_idx, card in enumerate(cards):
        if old_idx in remove_card_indices:
            continue
        old_to_new[old_idx] = len(new_cards)
        new_cards.append(card)

    # Update sections:
    # - Card sections are of the form [10, card_index]
    # - Drop sections referencing removed cards (this removes the duplicate rendered images)
    # - Re-index remaining card references to the new cards array
    new_sections: list[Any] = []
    dropped_sections = 0
    for sec in sections:
        if not (isinstance(sec, list) and len(sec) >= 2 and isinstance(sec[0], int)):
            new_sections.append(sec)
            continue
        if sec[0] != 10:
            new_sections.append(sec)
            continue
        card_index = sec[1]
        if not isinstance(card_index, int):
            new_sections.append(sec)
            continue
        if card_index in remove_card_indices:
            dropped_sections += 1
            continue
        new_idx = old_to_new.get(card_index)
        if new_idx is None:
            # Should not happen; keep original to avoid corrupting structure.
            new_sections.append(sec)
            continue
        new_sec = list(sec)
        new_sec[1] = new_idx
        new_sections.append(new_sec)

    out = deepcopy(mobiledoc_obj)
    out["cards"] = new_cards
    out["sections"] = new_sections

    changed, diff = _changed_and_diff(before, out, include_diff=include_diff)
    removed_cards = len(remove_card_indices)
    removed_total = removed_cards  # card count removed is the primary metric
    if dropped_sections:
        # Still keep `removed` as number of removed cards (stable); sections dropped is implied by diff.
        pass
    return (
        MobiledocEditReport(refused=False, reasons=[], matched=removed_total, changed=changed, diff=diff),
        out if changed else before,
        DedupeImagesResult(removed=removed_cards, duplicates=duplicates),
    )
