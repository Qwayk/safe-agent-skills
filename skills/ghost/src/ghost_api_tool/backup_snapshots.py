from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _safe_part(value: str, *, max_len: int = 80) -> str:
    v = value.strip()
    v = re.sub(r"[^a-zA-Z0-9._-]+", "_", v)
    v = v.strip("._-") or "x"
    return v[:max_len]


def domain_from_admin_api_url(admin_api_url: str) -> str:
    parsed = urlparse(admin_api_url)
    host = parsed.hostname or ""
    if not host:
        return "unknown-domain"
    return _safe_part(host, max_len=120)


@dataclass(frozen=True)
class SnapshotPaths:
    before: str | None
    after: str | None
    meta: str


class SnapshotWriter:
    """
    Writes before/after snapshots for Ghost resources (posts/pages/tags).

    Default location is derived from --env-file:
      <env-file directory>/backup-snapshots/<domain>/YYYY-MM-DD/

    Snapshots are intentionally plain JSON for manual restore/debugging.
    """

    def __init__(self, *, root_dir: Path, domain: str, enabled: bool):
        self._root_dir = root_dir
        self._domain = domain
        self._enabled = enabled
        self._records: list[dict[str, Any]] = []

    def _dir_for_today(self) -> Path:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._root_dir / self._domain / day

    def _ts_prefix(self) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"

    def _write_json(self, path: Path, obj: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")

    def write_before_after(
        self,
        *,
        kind: str,
        resource_id: str,
        slug: str | None,
        action: str,
        before: Any | None,
        after: Any | None,
        meta: dict[str, Any],
    ) -> SnapshotPaths | None:
        if not self._enabled:
            return None

        ts = self._ts_prefix()
        slug_part = _safe_part(slug or "no-slug", max_len=80)
        action_part = _safe_part(action, max_len=80)
        base = f"{ts}__{_safe_part(kind)}__{_safe_part(str(resource_id))}__{slug_part}__{action_part}"

        out_dir = self._dir_for_today()
        before_path = out_dir / f"{base}__before.json" if before is not None else None
        after_path = out_dir / f"{base}__after.json" if after is not None else None
        meta_path = out_dir / f"{base}__meta.json"

        if before_path is not None:
            self._write_json(before_path, before)
        if after_path is not None:
            self._write_json(after_path, after)

        meta_row = {
            "ts": time.time(),
            "domain": self._domain,
            "kind": kind,
            "resource_id": str(resource_id),
            "slug": slug,
            "action": action,
            "paths": {
                "before": str(before_path) if before_path is not None else None,
                "after": str(after_path) if after_path is not None else None,
            },
            **meta,
        }
        self._write_json(meta_path, meta_row)

        self._records.append(
            {
                "kind": kind,
                "resource_id": str(resource_id),
                "slug": slug,
                "action": action,
                "before": str(before_path) if before_path is not None else None,
                "after": str(after_path) if after_path is not None else None,
                "meta": str(meta_path),
            }
        )

        return SnapshotPaths(
            before=str(before_path) if before_path is not None else None,
            after=str(after_path) if after_path is not None else None,
            meta=str(meta_path),
        )

    def records(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._records]
