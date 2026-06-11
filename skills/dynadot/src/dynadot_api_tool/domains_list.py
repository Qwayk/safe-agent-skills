from __future__ import annotations

import re
from pathlib import Path

from .errors import ValidationError


_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)


def parse_domains_from_args(*, domains: list[str] | None, domains_file: str | None) -> list[str]:
    items: list[str] = []
    if domains:
        items.extend(domains)
    if domains_file:
        p = Path(domains_file)
        if not p.exists():
            raise ValidationError(f"Domains file not found: {p}")
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            items.append(line)

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in items:
        d = str(item or "").strip().lower().rstrip(".")
        if not d:
            continue
        if d in seen:
            continue
        if not _DOMAIN_RE.match(d):
            raise ValidationError(f"Invalid domain: {d}")
        seen.add(d)
        cleaned.append(d)

    if not cleaned:
        raise ValidationError("No domains provided (use --domain or --domains-file)")
    return cleaned


def chunk(items: list[str], size: int) -> list[list[str]]:
    if size <= 0:
        raise ValidationError("Internal error: chunk size must be > 0")
    return [items[i : i + size] for i in range(0, len(items), size)]

