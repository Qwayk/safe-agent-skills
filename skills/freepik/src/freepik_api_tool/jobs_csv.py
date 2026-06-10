from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class JobsCsvWriteResult:
    path: str
    rows: int
    columns: list[str]


def write_jobs_csv(
    path: Path,
    *,
    resource_ids: Iterable[str],
    fmt: str,
    image_size: str | None = None,
) -> JobsCsvWriteResult:
    """
    Write a deterministic CSV compatible with `freepik-api-tool jobs run`.

    Determinism rules:
    - Deduplicate resource ids.
    - Sort rows by resource_id (string).
    - Stable header and column ordering.
    """
    fmt = str(fmt or "").strip()
    if not fmt:
        raise RuntimeError("Refused: missing job format")

    clean_ids: set[str] = set()
    for rid in resource_ids:
        s = str(rid or "").strip()
        if s:
            clean_ids.add(s)

    ordered_ids = sorted(clean_ids)
    columns = ["resource_id", "format"]
    if image_size:
        columns.append("image_size")

    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for rid in ordered_ids:
            row: dict[str, str] = {"resource_id": rid, "format": fmt}
            if image_size:
                row["image_size"] = str(image_size)
            w.writerow(row)

    return JobsCsvWriteResult(path=str(path), rows=len(ordered_ids), columns=columns)

