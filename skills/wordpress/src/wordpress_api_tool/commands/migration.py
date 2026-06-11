from __future__ import annotations

import csv
import re
from pathlib import Path

from ..wp_xml import parse_wordpress_export_xml

_TRACKING_HEADER = [
    "wp_post_id",
    "wp_slug",
    "wp_title",
    "wp_status",
    "wp_date",
    "wp_modified",
    "wp_author",
    "wp_tags",
    "wp_categories",
    "ghost_id",
    "ghost_edit_url",
    "ghost_slug_imported",
    "ghost_slug_final",
    "ghost_status",
    "ghost_editor_format",
    "migration_status",
    "notes",
    "last_updated",
    "tags_final",
    "meta_description_final",
]


_SLUG_SAFE_RE = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = _SLUG_SAFE_RE.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def _blank_tracking_row(*, r) -> dict[str, str]:
    slug = r.wp_slug
    note_prefix = ""
    if not slug:
        guessed = _slugify(r.wp_title) or f"wp-{r.wp_post_id}"
        slug = guessed
        note_prefix = f"wp_slug_missing_in_xml; guessed_slug={guessed}"
    return {
        "wp_post_id": str(r.wp_post_id),
        "wp_slug": slug,
        "wp_title": r.wp_title,
        "wp_status": r.wp_status,
        "wp_date": r.wp_date or "",
        "wp_modified": r.wp_modified or "",
        "wp_author": r.wp_author or "",
        "wp_tags": "; ".join(r.wp_tags),
        "wp_categories": "; ".join(r.wp_categories),
        "ghost_id": "",
        "ghost_edit_url": "",
        "ghost_slug_imported": "",
        "ghost_slug_final": "",
        "ghost_status": "",
        "ghost_editor_format": "",
        "migration_status": "todo",
        "notes": note_prefix,
        "last_updated": "",
        "tags_final": "",
        "meta_description_final": "",
    }


def cmd_tracking_from_xml(args, ctx) -> int:
    xml_files: list[str] = list(args.xml or [])
    if not xml_files:
        raise RuntimeError("Refused: provide at least one --xml file")

    all_rows = []
    for xml_path in xml_files:
        all_rows.extend(parse_wordpress_export_xml(xml_path))

    # De-dupe by post id, keep first occurrence.
    seen: set[int] = set()
    uniq = []
    for r in all_rows:
        if r.wp_post_id in seen:
            continue
        seen.add(r.wp_post_id)
        uniq.append(r)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    existing_rows: list[dict[str, str]] = []
    fieldnames = list(_TRACKING_HEADER)
    existing_ids: set[int] = set()

    if bool(getattr(args, "append", False)) and out_path.exists():
        with out_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise RuntimeError(f"Refused: existing CSV has no header: {out_path}")
            for col in _TRACKING_HEADER:
                if col not in reader.fieldnames:
                    raise RuntimeError(
                        f"Refused: existing CSV missing required column {col!r}: {out_path}"
                    )
            fieldnames = list(reader.fieldnames)
            existing_rows = list(reader)
        for row in existing_rows:
            raw = (row.get("wp_post_id") or "").strip()
            if raw.isdigit():
                existing_ids.add(int(raw))

    added = 0
    skipped_existing = 0

    out_rows: list[dict[str, str]] = []
    if existing_rows:
        out_rows.extend(existing_rows)

    for r in sorted(uniq, key=lambda x: x.wp_post_id):
        if r.wp_post_id in existing_ids:
            skipped_existing += 1
            continue
        new_row = _blank_tracking_row(r=r)
        # Ensure we can write into whatever existing schema we have.
        for col in fieldnames:
            if col not in new_row:
                new_row[col] = ""
        out_rows.append({k: new_row.get(k, "") for k in fieldnames})
        added += 1

    with out_path.open("w", encoding="utf-8", newline="") as out_f:
        w = csv.DictWriter(out_f, fieldnames=fieldnames, lineterminator="\r\n")
        w.writeheader()
        w.writerows(out_rows)

    ctx["out"].emit(
        {
            "written": str(out_path),
            "count_total": len(out_rows),
            "count_from_xml": len(uniq),
            "added": added,
            "skipped_existing": skipped_existing,
            "append": bool(getattr(args, "append", False)) and bool(existing_rows),
        }
    )
    return 0
