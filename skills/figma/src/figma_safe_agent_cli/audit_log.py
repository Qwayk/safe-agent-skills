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

_REDACT_KEY_PATTERNS = ("token", "access_token", "x-figma-token", "x_figma_token", "api-key", "api_key", "secret")


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if (
                lk in _REDACT_KEYS
                or lk in {"x-figma-token", "x_figma_token"}
                or any(p in lk for p in _REDACT_KEY_PATTERNS)
                or lk.startswith("bearer ")
                or lk.endswith("_token")
                or lk.endswith("_secret")
                or lk.endswith("_api_key")
                or lk.endswith("_api-key")
            ):
                out[k] = "***REDACTED***"
            else:
                out[k] = _sanitize(v)
        return out
    if isinstance(obj, list):
        return [_sanitize(x) for x in obj]
    return obj


class AuditLogger:
    def __init__(self, *, path: str | None, enabled: bool):
        self._enabled = enabled and bool(path)
        self._fh: TextIO | None = None
        self._context: dict[str, Any] = {}
        if self._enabled:
            assert path is not None
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

    def bind_context(self, context: dict[str, Any]) -> None:
        """
        Attach standard v2 fields that should appear on every audit row.

        Keep this context non-secret. Never include tokens.
        """
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
