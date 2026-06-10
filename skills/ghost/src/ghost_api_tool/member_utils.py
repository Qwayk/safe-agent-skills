from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def slugify_label(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def parse_delimited_list(value: str | None, *, seps: str = ",;|") -> list[str]:
    if value is None:
        return []
    raw = value.strip()
    if not raw:
        return []
    parts = [raw]
    for sep in seps:
        next_parts: list[str] = []
        for p in parts:
            next_parts.extend(p.split(sep))
        parts = next_parts
    items: list[str] = []
    seen: set[str] = set()
    for p in parts:
        item = p.strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def redact_email(email: str) -> str:
    s = email.strip()
    if "@" not in s:
        return "***"
    local, _, domain = s.partition("@")
    if not local:
        return "***@" + (domain[:1] + "***" if domain else "***")
    return (local[:1] + "***") + "@" + (domain[:1] + "***" if domain else "***")


@dataclass(frozen=True)
class MemberCsvRow:
    email: str
    name: str | None
    note: str | None
    labels: list[str]
    newsletters: list[str]


def read_member_csv(path: str) -> list[MemberCsvRow]:
    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"CSV file not found: {path}")
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("CSV has no header row")
        rows: list[MemberCsvRow] = []
        for i, row in enumerate(reader, start=2):
            email = (row.get("email") or "").strip()
            if not email:
                raise RuntimeError(f"CSV missing email at line {i}")
            name = (row.get("name") or row.get("firstName") or "").strip() or None
            note = (row.get("note") or "").strip() or None
            labels = parse_delimited_list(row.get("labels"))
            newsletters = parse_delimited_list(row.get("newsletters"))
            rows.append(MemberCsvRow(email=email, name=name, note=note, labels=labels, newsletters=newsletters))
        return rows


def labels_to_objects(labels: Iterable[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for label in labels:
        name = label.strip()
        if not name:
            continue
        out.append({"name": name, "slug": slugify_label(name)})
    return out


def normalize_member_labels(labels: Any) -> list[dict[str, Any]]:
    if not isinstance(labels, list):
        return []
    out: list[dict[str, Any]] = []
    for item in labels:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        slug = item.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            if isinstance(name, str) and name.strip():
                slug = slugify_label(name)
            else:
                continue
        out.append({k: v for k, v in item.items() if k in ("id", "name", "slug", "created_at", "updated_at")})
    return out


def merge_labels(
    *,
    existing: Any,
    add: Iterable[str] = (),
    remove: Iterable[str] = (),
    replace: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    if replace is not None:
        return labels_to_objects(replace)
    current = normalize_member_labels(existing)
    by_slug: dict[str, dict[str, Any]] = {}
    for item in current:
        slug = item.get("slug")
        if isinstance(slug, str) and slug:
            by_slug[slug] = item
    for label in add:
        slug = slugify_label(label)
        if slug in by_slug:
            continue
        by_slug[slug] = {"name": label.strip(), "slug": slug}
    for label in remove:
        slug = slugify_label(label)
        by_slug.pop(slug, None)
    return list(by_slug.values())


def newsletters_to_refs(ids: Iterable[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for nid in ids:
        s = nid.strip()
        if not s:
            continue
        out.append({"id": s})
    return out

