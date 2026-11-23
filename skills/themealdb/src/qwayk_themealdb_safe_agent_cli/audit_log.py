from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, TextIO
from urllib.parse import quote, quote_plus


_REDACT_KEYS = {
    "authorization",
    "password",
    "secret",
    "token",
    "api_key",
}


def key_redactions(key: str) -> tuple[str, ...]:
    if not key or key == "1":
        return ()
    return tuple(sorted({key, quote(key, safe=""), quote_plus(key, safe="")}, key=len, reverse=True))


def redact_text(text: str, values: tuple[str, ...]) -> str:
    for value in values:
        text = text.replace(value, "***REDACTED***")
    return text


def sanitize(obj: Any, values: tuple[str, ...], *, mask_fields: bool = False) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            name = str(k)
            key = redact_text(name, values)
            lowered = name.lower()
            if mask_fields and (lowered in _REDACT_KEYS or lowered.endswith(("_token", "_secret", "_api_key"))):
                out[key] = "***REDACTED***"
            else:
                out[key] = sanitize(v, values, mask_fields=mask_fields)
        return out
    if isinstance(obj, list):
        return [sanitize(value, values, mask_fields=mask_fields) for value in obj]
    if isinstance(obj, str):
        return redact_text(obj, values)
    return obj


class AuditLogger:
    def __init__(self, *, path: str | None, enabled: bool, redacted_values: tuple[str, ...] = ()):
        self._enabled = enabled and bool(path)
        self._fh: TextIO | None = None
        self._context: dict[str, Any] = {}
        self._redacted_values = redacted_values
        if self._enabled:
            assert path is not None
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

    def bind_context(self, context: dict[str, Any]) -> None:
        """
        Attach standard v2 fields that should appear on every audit row.

        Keep this context non-secret. Never include tokens.
        """
        self._context = sanitize(context, self._redacted_values, mask_fields=True)

    def write(self, event: str, payload: dict[str, Any]) -> None:
        if not self._enabled or not self._fh:
            return
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **self._context,
            "event": event,
            "payload": sanitize(payload, self._redacted_values, mask_fields=True),
        }
        self._fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None


class CompositeAuditLogger:
    """
    Write the same audit events to multiple AuditLogger sinks.

    Used so a tool can write a per-run audit log under `.state/runs/<run_id>/audit.jsonl`
    while also optionally writing to a user-specified `--log-file`.
    """

    def __init__(self, loggers: list[AuditLogger]):
        self._loggers = list(loggers)

    def bind_context(self, context: dict[str, Any]) -> None:
        for lg in self._loggers:
            lg.bind_context(context)

    def write(self, event: str, payload: dict[str, Any]) -> None:
        for lg in self._loggers:
            lg.write(event, payload)

    def close(self) -> None:
        for lg in self._loggers:
            lg.close()
