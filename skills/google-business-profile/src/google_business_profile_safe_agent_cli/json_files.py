from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationError


def read_json_file(path: str | Path) -> Any:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON file: {p}: {type(e).__name__}: {e}") from None


def write_json_file(path: str | Path, obj: Any) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(p)
