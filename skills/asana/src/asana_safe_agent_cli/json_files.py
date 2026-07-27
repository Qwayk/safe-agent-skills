from __future__ import annotations

import json
import os
import stat
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
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON file: {p}: {type(e).__name__}: {e}") from None


def ensure_private_directory(path: str | Path) -> Path:
    target = Path(path)
    missing: list[Path] = []
    cursor = target
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
    return target


def atomic_write_bytes(path: str | Path, data: bytes) -> str:
    target = Path(path)
    ensure_private_directory(target.parent)
    existing_mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else None
    final_mode = 0o600 if existing_mode is None else existing_mode & 0o600
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, final_mode)
        offset = 0
        while offset < len(data):
            offset += os.write(descriptor, data[offset:])
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, target)
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists():
            temporary.unlink()
    return str(target)


def atomic_append_text(path: str | Path, text: str) -> str:
    target = Path(path)
    previous = target.read_bytes() if target.exists() else b""
    return atomic_write_bytes(target, previous + text.encode("utf-8"))


def get_or_create_private_bytes(path: str | Path, new_data: bytes) -> bytes:
    target = Path(path)
    ensure_private_directory(target.parent)
    if target.exists():
        current_mode = stat.S_IMODE(target.stat().st_mode)
        target.chmod(current_mode & 0o600)
        return target.read_bytes()
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        offset = 0
        while offset < len(new_data):
            offset += os.write(descriptor, new_data[offset:])
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        try:
            os.link(temporary, target)
        except FileExistsError:
            pass
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists():
            temporary.unlink()
    current_mode = stat.S_IMODE(target.stat().st_mode)
    target.chmod(current_mode & 0o600)
    return target.read_bytes()


def write_json_file(path: str | Path, obj: Any) -> str:
    rendered = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return atomic_write_bytes(path, rendered.encode("utf-8"))
