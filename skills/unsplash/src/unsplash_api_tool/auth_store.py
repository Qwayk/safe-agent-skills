from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuthStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]


def auth_path_for_env_file(env_file: str) -> Path:
    """
    Store auth secrets next to the env file (per-environment), under `.state/auth.json`.

    This file is gitignored and must never be printed.
    """
    root = Path(env_file).resolve().parent
    return root / ".state" / "auth.json"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def read_auth_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Auth file must be a JSON object")
    return data


def write_auth_from_file(*, src_file: Path, dest_file: Path) -> AuthStatus:
    if not src_file.exists():
        raise RuntimeError(f"Auth file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Auth file must be a JSON object")

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return get_auth_status(dest_file)


def get_auth_status(path: Path) -> AuthStatus:
    if not path.exists():
        return AuthStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
        )

    data = read_auth_json(path) or {}
    fields = sorted([k for k in data.keys() if isinstance(k, str)])

    st = path.stat()
    return AuthStatus(
        exists=True,
        path=str(path),
        updated_at_utc=_utc(st.st_mtime),
        fields=fields,
    )


def redact_auth_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a safe view of an auth dict (no secrets).
    """
    out: dict[str, Any] = {}
    for k, v in data.items():
        lk = str(k).lower()
        if lk in {
            "access_key",
            "api_key",
            "token",
            "access_token",
            "refresh_token",
            "id_token",
            "client_secret",
        } or lk.endswith("_token") or lk.endswith("_key"):
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


def get_access_key_from_store(path: Path) -> str | None:
    data = read_auth_json(path) or {}
    raw = data.get("access_key")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None
