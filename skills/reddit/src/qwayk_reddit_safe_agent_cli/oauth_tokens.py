from __future__ import annotations

import datetime
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TokenStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]
    has_refresh_token: bool | None
    expires_at_utc: str | None


def token_path_for_env_file(env_file: str) -> Path:
    """
    Store OAuth tokens next to the env file (per-environment), under `.state/token.json`.
    """
    root = Path(env_file).resolve().parent
    return root / ".state" / "token.json"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _parse_expiry_timestamp(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        value_f = float(value)
        if value_f < 0:
            return None
        if value_f > 10_000_000_000:
            value_f /= 1000
        return value_f
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            value_f = float(raw)
            if value_f < 0:
                return None
            if value_f > 10_000_000_000:
                value_f /= 1000
            return value_f
        except ValueError:
            pass
        try:
            dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                return dt.timestamp()
            return time.mktime(dt.timetuple())
        except ValueError:
            return None
    return None


def _extract_expiry_time(data: dict[str, Any]) -> float | None:
    for key in ("expires_at", "expiry", "expires", "expiration"):
        if key in data:
            ts = _parse_expiry_timestamp(data.get(key))
            if ts is not None:
                return ts

    expires_in = data.get("expires_in")
    if isinstance(expires_in, (int, float, str)):
        value = _parse_expiry_timestamp(expires_in)
        if value is not None:
            return time.time() + value
    return None


def read_token_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")
    return data


def write_token_from_file(*, src_file: Path, dest_file: Path) -> TokenStatus:
    if not src_file.exists():
        raise RuntimeError(f"Token file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return get_token_status(dest_file)


def get_token_status(path: Path) -> TokenStatus:
    if not path.exists():
        return TokenStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
            has_refresh_token=None,
            expires_at_utc=None,
        )

    data = read_token_json(path) or {}
    fields = sorted([k for k in data.keys() if isinstance(k, str)])
    has_refresh_token = None
    if "refresh_token" in data:
        has_refresh_token = bool(data.get("refresh_token"))

    # Best-effort: many OAuth tokens store unix (`expires_at`, `expires_in`) or iso (`expiry`) values.
    expires_at_utc = None
    expires_at = _extract_expiry_time(data)
    if expires_at is not None:
        expires_at_utc = _utc(expires_at)

    st = path.stat()
    return TokenStatus(
        exists=True,
        path=str(path),
        updated_at_utc=_utc(st.st_mtime),
        fields=fields,
        has_refresh_token=has_refresh_token,
        expires_at_utc=expires_at_utc,
    )


def redact_token_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a safe view of a token dict (no secrets).
    """
    out: dict[str, Any] = {}
    for k, v in data.items():
        lk = str(k).lower()
        if lk in {"access_token", "refresh_token", "id_token", "client_secret", "token"} or lk.endswith("_token"):
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out
