from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .errors import ValidationError


def read_json_file(path: str | Path) -> Any:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ValidationError(f"Could not read JSON from {p}") from None


def write_json_file(path: str | Path, obj: Any, *, exclusive: bool = False) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    contents = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        if exclusive:
            os.link(temporary, p)
        else:
            os.replace(temporary, p)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return str(p)
