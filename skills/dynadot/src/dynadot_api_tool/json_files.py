from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, TextIO

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
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=p.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(obj, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        temporary.replace(p)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return str(p)


@contextmanager
def new_private_file(path: str | Path) -> Iterator[TextIO]:
    """Reserve a new private destination before a sensitive request."""
    p = Path(path)
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as exc:
        raise ValidationError(f"Choose a new writable file: {p}") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            yield stream
    except BaseException:
        p.unlink(missing_ok=True)
        raise
