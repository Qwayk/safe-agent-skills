from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, TextIO


_REDACT_KEYS = {
    "authorization",
    "password",
    "secret",
    "token",
    "api_key",
}


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            lk = str(key).lower()
            if lk in _REDACT_KEYS or lk.endswith("_token") or lk.endswith("_secret") or lk.endswith("_api_key"):
                out[key] = "***REDACTED***"
            else:
                out[key] = _sanitize(value)
        return out
    if isinstance(obj, list):
        return [_sanitize(value) for value in obj]
    return obj


class AuditLogger:
    def __init__(self, *, path: str | None, enabled: bool):
        self._enabled = bool(enabled) and bool(path)
        self._fh: TextIO | None = None
        self._context: dict[str, Any] = {}
        if self._enabled:
            assert path is not None
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

    def bind_context(self, context: dict[str, Any]) -> None:
        """Attach shared non-secret fields to every audit row."""
        self._context = _sanitize(context)

    def write(self, event: str, payload: dict[str, Any]) -> None:
        if not self._enabled or not self._fh:
            return
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **self._context,
            "event": event,
            "payload": _sanitize(payload),
        }
        self._fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None
