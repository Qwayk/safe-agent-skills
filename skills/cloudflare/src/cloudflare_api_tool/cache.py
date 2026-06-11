from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _stable_params(params: dict[str, Any] | None) -> str:
    if not params:
        return ""
    try:
        return json.dumps(params, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except Exception:
        # Best-effort; cache is only an optimization.
        return str(params)


@dataclasses.dataclass(frozen=True)
class CacheKey:
    key_hex: str


class ShortTtlCache:
    """
    A short-TTL cache for safe GET reads.

    Design constraints:
    - Never stores tokens (keys use a non-secret fingerprint).
    - Lives under `.state/cache/` next to the env file (gitignored).
    - Best-effort only: failures must not break the command.
    """

    def __init__(self, *, cache_dir: Path, fingerprint: str, ttl_s: float) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._fingerprint = str(fingerprint or "").strip()
        self._ttl_s = float(ttl_s)

    def _key_for(self, *, url: str, params: dict[str, Any] | None) -> CacheKey:
        material = "\n".join([self._fingerprint, str(url), _stable_params(params)])
        return CacheKey(key_hex=_sha256_hex(material))

    def _path_for(self, key: CacheKey) -> Path:
        return self._cache_dir / f"{key.key_hex}.json"

    def get(self, *, url: str, params: dict[str, Any] | None) -> dict[str, Any] | None:
        if self._ttl_s <= 0:
            return None
        p = self._path_for(self._key_for(url=url, params=params))
        if not p.exists():
            return None
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(obj, dict):
            return None
        saved_at = float(obj.get("saved_at_epoch") or 0.0)
        if not saved_at:
            return None
        if (time.time() - saved_at) > self._ttl_s:
            return None
        v = obj.get("value")
        return v if isinstance(v, dict) else None

    def set(self, *, url: str, params: dict[str, Any] | None, value: dict[str, Any]) -> None:
        if self._ttl_s <= 0:
            return
        if not isinstance(value, dict):
            return
        p = self._path_for(self._key_for(url=url, params=params))
        payload = {
            "saved_at_utc": _utc_now(),
            "saved_at_epoch": time.time(),
            "ttl_s": self._ttl_s,
            "value": value,
        }
        try:
            p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except Exception:
            return

