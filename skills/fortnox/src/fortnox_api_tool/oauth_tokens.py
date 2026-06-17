from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TokenStatus:
    exists: bool
    path: str
    updated_at_utc: str | None
    fields: list[str]
    has_access_token: bool | None
    has_refresh_token: bool | None
    expires_at_utc: str | None
    token_source: str | None
    grant_type: str | None
    tenant_id: str | None


def token_path_for_env_file(env_file: str, override: str | None = None) -> Path:
    root = Path(env_file).resolve().parent
    if override:
        p = Path(override)
        return p if p.is_absolute() else (root / p)
    return root / ".state" / "token.json"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _coerce_epoch(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except Exception:
            pass
        try:
            normalized = raw.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    return None


def read_token_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")
    return data


def token_expires_at_epoch(data: dict[str, Any]) -> float | None:
    direct = _coerce_epoch(data.get("expires_at"))
    if direct is not None:
        return direct
    expiry = _coerce_epoch(data.get("expiry"))
    if expiry is not None:
        return expiry
    expires_in = data.get("expires_in")
    saved_at = _coerce_epoch(data.get("saved_at"))
    if isinstance(expires_in, (int, float)) and saved_at is not None:
        return saved_at + float(expires_in)
    return None


def token_expires_at_utc(data: dict[str, Any]) -> str | None:
    ts = token_expires_at_epoch(data)
    if ts is None:
        return None
    return _utc(ts)


def token_is_expired(data: dict[str, Any], *, skew_s: int = 60) -> bool | None:
    ts = token_expires_at_epoch(data)
    if ts is None:
        return None
    return ts <= (time.time() + float(skew_s))


def access_token_from_dict(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    raw = data.get("access_token")
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def refresh_token_from_dict(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    raw = data.get("refresh_token")
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def normalize_token_dict(
    data: dict[str, Any],
    *,
    existing: dict[str, Any] | None = None,
    token_source: str | None = None,
    grant_type: str | None = None,
    tenant_id: str | None = None,
    preserve_refresh_token: bool = False,
    saved_at: int | None = None,
) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RuntimeError("Token data must be a JSON object")

    now = int(saved_at if saved_at is not None else time.time())
    out = dict(existing or {})
    out.update(data)

    if preserve_refresh_token:
        existing_refresh = refresh_token_from_dict(existing)
        new_refresh = refresh_token_from_dict(out)
        if existing_refresh and not new_refresh:
            out["refresh_token"] = existing_refresh

    if "expires_in" in data:
        try:
            out["expires_at"] = int(now + float(data["expires_in"]))
        except Exception:
            pass
    elif "expires_at" in data:
        direct = _coerce_epoch(data.get("expires_at"))
        if direct is not None:
            out["expires_at"] = int(direct)
    elif "expiry" in data:
        expiry = _coerce_epoch(data.get("expiry"))
        if expiry is not None:
            out["expires_at"] = int(expiry)

    out["saved_at"] = now
    if token_source:
        out["token_source"] = token_source
    if grant_type:
        out["grant_type"] = grant_type
    if tenant_id:
        out["tenant_id"] = str(tenant_id)
    return out


def write_token_from_file(*, src_file: Path, dest_file: Path) -> TokenStatus:
    if not src_file.exists():
        raise RuntimeError(f"Token file not found: {src_file}")
    data = json.loads(src_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Token file must be a JSON object")

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_token_dict(data)
    dest_file.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return get_token_status(dest_file)


def write_token_dict(
    *,
    data: dict[str, Any],
    dest_file: Path,
    existing: dict[str, Any] | None = None,
    token_source: str | None = None,
    grant_type: str | None = None,
    tenant_id: str | None = None,
    preserve_refresh_token: bool = False,
) -> TokenStatus:
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_token_dict(
        data,
        existing=existing,
        token_source=token_source,
        grant_type=grant_type,
        tenant_id=tenant_id,
        preserve_refresh_token=preserve_refresh_token,
    )
    dest_file.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return get_token_status(dest_file)


def get_token_status(path: Path) -> TokenStatus:
    if not path.exists():
        return TokenStatus(
            exists=False,
            path=str(path),
            updated_at_utc=None,
            fields=[],
            has_access_token=None,
            has_refresh_token=None,
            expires_at_utc=None,
            token_source=None,
            grant_type=None,
            tenant_id=None,
        )

    data = read_token_json(path) or {}
    fields = sorted([k for k in data.keys() if isinstance(k, str)])
    st = path.stat()
    return TokenStatus(
        exists=True,
        path=str(path),
        updated_at_utc=_utc(st.st_mtime),
        fields=fields,
        has_access_token=bool(access_token_from_dict(data)),
        has_refresh_token=bool(refresh_token_from_dict(data)) if "refresh_token" in data else None,
        expires_at_utc=token_expires_at_utc(data),
        token_source=str(data.get("token_source") or "").strip() or None,
        grant_type=str(data.get("grant_type") or "").strip() or None,
        tenant_id=str(data.get("tenant_id") or "").strip() or None,
    )


def redact_token_dict(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in data.items():
        lk = str(k).lower()
        if lk in {"access_token", "refresh_token", "id_token", "client_secret", "token"} or lk.endswith("_token"):
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out
