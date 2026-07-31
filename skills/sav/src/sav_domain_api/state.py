from __future__ import annotations

import contextlib
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any

from .errors import StateError


def _is_private_dir_mode(mode: int) -> bool:
    return stat.S_ISDIR(mode) and stat.S_IMODE(mode) == 0o700


def ensure_private_directory(path: Path, *, stop_at: Path) -> None:
    target = Path(os.path.abspath(path))
    stop = Path(os.path.abspath(stop_at))
    if target != stop and not target.is_relative_to(stop):
        raise StateError("Invalid state path")

    chain: list[Path] = [target] if target == stop else []
    if target != stop:
        cursor = target
        while cursor != stop:
            chain.append(cursor)
            cursor = cursor.parent

    for directory in reversed(chain):
        try:
            if not directory.exists():
                directory.mkdir(mode=0o700)
                os.chmod(directory, 0o700)
                continue

            if directory.is_symlink():
                raise StateError("State path must not be a symlink")

            st_mode = directory.stat().st_mode
            if not _is_private_dir_mode(st_mode):
                raise StateError("State directory must be private (0o700)")
        except OSError as exc:
            raise StateError("Unable to prepare state directory") from exc


def _fsync_directory(directory: Path) -> None:
    try:
        fd = os.open(str(directory), os.O_RDONLY)
    except OSError as exc:
        raise StateError("Unable to flush state") from exc

    try:
        os.fsync(fd)
    finally:
        with contextlib.suppress(OSError):
            os.close(fd)


def _write_bytes(path: Path, payload: bytes, *, stop_at: Path) -> None:
    ensure_private_directory(path.parent, stop_at=stop_at)

    target = path
    tmp_file: str | None = None
    fd = -1
    try:
        fd, tmp_file = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.")
        os.fchmod(fd, 0o600)
        remaining = memoryview(payload)
        while remaining:
            written = os.write(fd, remaining)
            if written == 0:
                raise OSError("short state write")
            remaining = remaining[written:]
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(tmp_file, target)
        _fsync_directory(target.parent)
    except OSError as exc:
        if tmp_file is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmp_file)
        raise StateError("Unable to write state file") from exc
    finally:
        if fd >= 0:
            with contextlib.suppress(OSError):
                os.close(fd)


def write_private_json(path: Path, payload: dict[str, Any], *, stop_at: Path) -> None:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    _write_bytes(path, encoded, stop_at=stop_at)


def write_private_bytes(path: Path, payload: bytes, *, stop_at: Path) -> None:
    _write_bytes(path, payload, stop_at=stop_at)


def read_plan_key(path: Path) -> bytes:
    try:
        ensure_private_directory(path.parent, stop_at=path.parent.parent)
    except OSError as exc:
        raise StateError("Signing key directory is not safe") from exc

    try:
        if path.is_symlink():
            raise StateError("Signing key must not be a symlink")

        if not path.is_file():
            raise StateError("Signing key file is invalid")

        st = path.stat()
        if stat.S_IMODE(st.st_mode) != 0o600:
            raise StateError("Signing key must be private (0o600)")

        value = path.read_bytes()
    except OSError as exc:
        raise StateError("Unable to read signing key") from exc

    if len(value) != 32:
        raise StateError("Signing key is malformed")
    return value
