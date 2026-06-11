from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


def _tool_root_from_env_file(env_file: str) -> Path:
    return Path(env_file).expanduser().resolve().parent


def _utc_now_compact() -> str:
    return time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def write_sensitive_json(
    *,
    env_file: str,
    kind: str,
    obj: Any,
) -> tuple[str, str]:
    """
    Write secret-bearing JSON to a gitignored path under `.state/` next to `--env-file`.

    Returns:
        (path, sha256_fingerprint)
    """
    root = _tool_root_from_env_file(env_file)
    out_dir = root / ".state" / "sensitive"
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_kind = "".join([c if c.isalnum() or c in {"-", "_"} else "-" for c in str(kind or "sensitive")])[:64]
    path = out_dir / f"{_utc_now_compact()}_{safe_kind}.json"

    payload_bytes = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    path.write_bytes(payload_bytes)
    try:
        os.chmod(path, 0o600)
    except Exception:  # noqa: BLE001
        pass

    return str(path), _sha256_bytes(payload_bytes)

