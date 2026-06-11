from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def webhooks_index_path_for_env_file(env_file: str) -> Path:
    tool_root = Path(env_file).expanduser().resolve().parent
    return tool_root / ".state" / "webhooks" / "index.jsonl"


def append_webhook_row(index_path: Path, row: dict[str, Any]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**row, "ts": _utc_now()}, ensure_ascii=False) + "\n")


def iter_webhook_rows(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with index_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows

