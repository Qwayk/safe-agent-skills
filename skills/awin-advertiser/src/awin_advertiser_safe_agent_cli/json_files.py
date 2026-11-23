from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .errors import ValidationError


def read_json_file(path: str | Path) -> Any:
    return read_json_input(path)[0]


def read_json_input(path: str | Path) -> tuple[Any, str]:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"JSON file not found: {p}")
    try:
        contents = p.read_bytes()
        return json.loads(contents.decode("utf-8")), sha256(contents).hexdigest()
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON file: {p}: {type(e).__name__}: {e}") from None


def write_json_file(path: str | Path, obj: Any) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(p)

