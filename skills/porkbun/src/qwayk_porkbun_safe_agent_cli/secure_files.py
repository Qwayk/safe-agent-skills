from __future__ import annotations

import json
import os
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ValidationError


def _raise_unsafe(path: Path, reason: str) -> None:
    raise ValidationError(f"Unsafe local file target {path}: {reason}")


def _create_private_parents(path: Path) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent

    if current.is_symlink() or not current.is_dir():
        _raise_unsafe(path, "parent must be a real directory")

    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            if directory.is_symlink() or not directory.is_dir():
                _raise_unsafe(directory, "concurrent parent must be a real directory")
        except OSError as exc:
            raise ValidationError(f"Cannot create private directory {directory}") from exc
        try:
            directory.chmod(0o700)
        except OSError as exc:
            raise ValidationError(f"Cannot make directory owner-only: {directory}") from exc


def ensure_private_directory(path: Path) -> Path:
    if path.is_symlink():
        _raise_unsafe(path, "symbolic links are not allowed")
    if path.exists() and not path.is_dir():
        _raise_unsafe(path, "expected a directory")
    if not path.exists():
        _create_private_parents(path)
    try:
        path.chmod(0o700)
    except OSError as exc:
        raise ValidationError(f"Cannot make directory owner-only: {path}") from exc
    return path


def _prepare_parent(path: Path, *, private_parent: bool) -> None:
    parent = path.parent
    if not parent.exists():
        _create_private_parents(parent)
    if parent.is_symlink() or not parent.is_dir():
        _raise_unsafe(path, "parent must be a real directory")
    if private_parent:
        ensure_private_directory(parent)
    mode = stat.S_IMODE(parent.stat().st_mode)
    if mode & 0o222 == 0:
        _raise_unsafe(path, "parent directory is not writable")


def _validate_destination(path: Path) -> None:
    if path.is_symlink():
        _raise_unsafe(path, "symbolic links are not allowed")
    if path.exists() and not path.is_file():
        _raise_unsafe(path, "expected a regular file")


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_private_bytes(fd: int, data: bytes) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        view = view[written:]
    os.fchmod(fd, 0o600)
    os.fsync(fd)


@dataclass
class AtomicFileReservation:
    destination: Path
    temporary: Path
    fd: int
    _committed: bool = False

    def commit_bytes(self, data: bytes) -> str:
        try:
            _write_private_bytes(self.fd, data)
            os.close(self.fd)
            self.fd = -1
            _validate_destination(self.destination)
            os.replace(self.temporary, self.destination)
            _fsync_directory(self.destination.parent)
            self._committed = True
            return str(self.destination)
        except Exception:
            self.cleanup()
            raise

    def commit_text(self, text: str) -> str:
        return self.commit_bytes(text.encode("utf-8"))

    def commit_json(self, payload: dict[str, Any]) -> str:
        data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        return self.commit_text(data)

    def cleanup(self) -> None:
        if self.fd >= 0:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = -1
        if not self._committed:
            try:
                self.temporary.unlink()
            except FileNotFoundError:
                pass


def reserve_atomic_file(
    path: str | Path,
    *,
    private_parent: bool = False,
    _allow_plan_signing_key: bool = False,
) -> AtomicFileReservation:
    destination = Path(path)
    is_plan_signing_key = destination.resolve(strict=False) == Path(
        ".state/plan-signing.key"
    ).resolve(strict=False)
    if is_plan_signing_key and not _allow_plan_signing_key:
        _raise_unsafe(destination, "the plan signing key is a protected tool file")
    _prepare_parent(destination, private_parent=private_parent)
    _validate_destination(destination)

    temporary = destination.parent / f".{destination.name}.{secrets.token_hex(8)}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(temporary, flags, 0o600)
        os.fchmod(fd, 0o600)
    except OSError as exc:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise ValidationError(f"Cannot reserve owner-only output file: {destination}") from exc
    return AtomicFileReservation(destination=destination, temporary=temporary, fd=fd)


def create_private_bytes_if_absent(
    path: str | Path,
    data: bytes,
    *,
    private_parent: bool = False,
    allow_plan_signing_key: bool = False,
) -> bool:
    reservation = reserve_atomic_file(
        path,
        private_parent=private_parent,
        _allow_plan_signing_key=allow_plan_signing_key,
    )
    try:
        _write_private_bytes(reservation.fd, data)
        os.close(reservation.fd)
        reservation.fd = -1
        try:
            os.link(
                reservation.temporary,
                reservation.destination,
                follow_symlinks=False,
            )
        except FileExistsError:
            reservation.cleanup()
            _validate_destination(reservation.destination)
            return False
        _fsync_directory(reservation.destination.parent)
        reservation.cleanup()
        return True
    except Exception:
        reservation.cleanup()
        raise


def file_paths_alias(left: str | Path, right: str | Path) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    try:
        if left_path.resolve(strict=False) == right_path.resolve(strict=False):
            return True
        if left_path.exists() and right_path.exists():
            return os.path.samefile(left_path, right_path)
    except OSError as exc:
        raise ValidationError("Cannot safely resolve local file roles") from exc
    return False


def atomic_write_bytes(
    path: str | Path,
    data: bytes,
    *,
    private_parent: bool = False,
    allow_plan_signing_key: bool = False,
) -> str:
    reservation = reserve_atomic_file(
        path,
        private_parent=private_parent,
        _allow_plan_signing_key=allow_plan_signing_key,
    )
    return reservation.commit_bytes(data)


def atomic_write_text(
    path: str | Path,
    text: str,
    *,
    private_parent: bool = False,
) -> str:
    reservation = reserve_atomic_file(path, private_parent=private_parent)
    return reservation.commit_text(text)


def atomic_write_json(
    path: str | Path,
    payload: dict[str, Any],
    *,
    private_parent: bool = False,
) -> str:
    reservation = reserve_atomic_file(path, private_parent=private_parent)
    return reservation.commit_json(payload)
