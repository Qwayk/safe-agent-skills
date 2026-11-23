from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .errors import ValidationError


def plan_id(
    operation: str,
    host: str,
    endpoint: str,
    normalized_domains: list[str],
    *,
    safety: Mapping[str, Any],
    nonce: str,
    token: str | None,
    env_file: str,
) -> str:
    payload = {
        "operation": operation,
        "host": host,
        "endpoint": endpoint,
        "domains": normalized_domains,
        "safety": safety,
        "nonce": nonce,
        "state_root": str(Path(env_file).parent.resolve()),
    }
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if token:
        return hmac.new(token.encode("utf-8"), data, "sha256").hexdigest()
    return hashlib.sha256(data).hexdigest()


def default_plan_path(plan_id: str, env_file: str | Path = ".env") -> str:
    return str(Path(env_file).parent.resolve() / ".state" / "plans" / f"{plan_id}.json")


def default_receipt_path(plan_id: str, env_file: str | Path = ".env") -> str:
    return str(Path(env_file).parent.resolve() / ".state" / "receipts" / f"{plan_id}.json")


def write_private_json(path: str | Path, obj: Any, *, exclusive: bool = False) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    fd, temp_path = tempfile.mkstemp(dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if exclusive:
            os.link(temp_path, target)
        else:
            os.replace(temp_path, target)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def read_json_file(path: str | Path) -> Any:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValidationError(f"Could not read a JSON plan from {p}") from exc
