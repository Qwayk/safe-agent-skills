from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from ..errors import ToolError


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd: int | None = None
    tmp_path: str | None = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
        with os.fdopen(tmp_fd, "wb") as f:
            tmp_fd = None
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Failed writing file: {path}: {e}") from e
    finally:
        if tmp_fd is not None:
            try:
                os.close(tmp_fd)
            except Exception:
                pass
        if tmp_path is not None:
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass


def write_json(path: Path, obj: dict[str, Any]) -> None:
    payload = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    _atomic_write_bytes(path, payload)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    buf: list[str] = []
    n = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        buf.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
        n += 1
    payload = ("\n".join(buf) + ("\n" if buf else "")).encode("utf-8")
    _atomic_write_bytes(path, payload)
    return n

