from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, TextIO


_REDACT_KEYS = {"authorization", "password", "secret", "token", "api_key"}


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        clean: dict[str, Any] = {}
        for key, value in obj.items():
            key_text = str(key).lower()
            if key_text in _REDACT_KEYS or key_text.endswith("_token") or key_text.endswith("_secret"):
                clean[key] = "***REDACTED***"
            else:
                clean[key] = _sanitize(value)
        return clean
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    return obj


class AuditLogger:
    def __init__(self, *, path: str | None, enabled: bool):
        self._enabled = enabled and bool(path)
        self._fh: TextIO | None = None
        self._context: dict[str, Any] = {}
        if self._enabled and path:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            self._fh = target.open("a", encoding="utf-8")  # noqa: SIM115

    def bind_context(self, context: dict[str, Any]) -> None:
        self._context = _sanitize(context)

    def write(self, event: str, payload: dict[str, Any]) -> None:
        if not self._enabled or self._fh is None:
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
        if self._fh is not None:
            self._fh.close()
            self._fh = None
