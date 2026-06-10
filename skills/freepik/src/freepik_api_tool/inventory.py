from __future__ import annotations

import csv
import hashlib
import time
from pathlib import Path
from typing import Any

INVENTORY_FIELDS = [
    "downloaded_at_utc",
    "resource_id",
    "resource_type",
    "title",
    "author",
    "resource_url",
    "preview_url",
    "download_url",
    "license_url",
    "download_id",
    "format",
    "image_size",
    "file_name",
    "file_path",
    "sha256",
    "keywords",
    "post_slug",
    "ghost_id",
    "usage_role",
    "tags",
    "notes",
]


def ensure_inventory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INVENTORY_FIELDS)
        w.writeheader()


def read_inventory_index(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    idx: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rid = (row.get("resource_id") or "").strip()
            fmt = (row.get("format") or "").strip()
            if rid and fmt:
                idx[(rid, fmt)] = dict(row)
    return idx


def append_inventory_row(path: Path, row: dict[str, Any]) -> None:
    ensure_inventory(path)
    out: dict[str, str] = {k: "" for k in INVENTORY_FIELDS}
    for k, v in row.items():
        if k in out:
            out[k] = "" if v is None else str(v)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INVENTORY_FIELDS)
        w.writerow(out)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def now_utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
