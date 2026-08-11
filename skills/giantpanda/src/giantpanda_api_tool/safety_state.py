from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import uuid4

from .errors import ValidationError


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def plan_id(
    operation: str,
    host: str,
    endpoint: str,
    normalized_domains: list[str],
    safety: Mapping[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "operation": operation,
        "host": host,
        "endpoint": endpoint,
        "domains": normalized_domains,
    }
    if safety is not None:
        payload["safety"] = safety
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _state_root(env_file: str | Path = ".env") -> Path:
    env_path = Path(env_file or ".env")
    if not env_path.is_absolute():
        env_path = Path.cwd() / env_path
    return env_path.parent


def default_plan_path(plan_id: str, env_file: str | Path = ".env") -> str:
    root = _state_root(env_file)
    return str(root / ".state" / "plans" / f"{plan_id}.json")


def default_receipt_path(
    plan_id: str,
    env_file: str | Path = ".env",
    *,
    unique: bool = False,
) -> str:
    suffix = f"-{uuid4().hex}" if unique else ""
    root = _state_root(env_file)
    return str(root / ".state" / "receipts" / f"{plan_id}{suffix}.json")


def write_private_json(path: str | Path, obj: Any) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    fd = os.open(str(p), os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
    try:
        os.write(fd, data.encode("utf-8"))
    finally:
        os.close(fd)
    os.chmod(str(p), 0o600)
    return str(p)


def read_json_file(path: str | Path) -> Any:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON in {p}: {type(exc).__name__}: {exc}") from exc
