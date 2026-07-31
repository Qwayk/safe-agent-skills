from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, TextIO

from .redaction import redact_object

_REDACT_KEYS = {
    "authorization",
    "accesstoken",
    "authtoken",
    "authcode",
    "clientsecret",
    "token",
    "tokens",
    "accountbalance",
    "verification",
    "verificationcode",
    "verificationcodefile",
    "linkauthcode",
    "linkauthcodefile",
}



def _sanitize(obj: Any) -> Any:
    # Reuse the project-wide redaction map, then enforce shared secret keys used by this module.
    sanitized = redact_object(obj, redact_pii=True)
    if isinstance(sanitized, dict):
        out: dict[str, Any] = {}
        for key, value in sanitized.items():
            norm = str(key).lower().replace("_", "").replace("-", "").replace(" ", "")
            if norm in _REDACT_KEYS:
                out[key] = "***REDACTED***"
            else:
                out[key] = value
        return out
    return sanitized


class AuditLogger:
    def __init__(self, *, path: str | None, enabled: bool):
        self._enabled = enabled and bool(path)
        self._fh: TextIO | None = None
        self._context: dict[str, Any] = {}
        if self._enabled:
            assert path is not None
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            try:
                p.parent.chmod(0o700)
            except OSError:
                pass
            self._fh = open(p, "a", encoding="utf-8")  # noqa: SIM115
            try:
                os.chmod(p, 0o600)
            except OSError:
                pass

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
        for logger in self._loggers:
            logger.bind_context(context)

    def write(self, event: str, payload: dict[str, Any]) -> None:
        for logger in self._loggers:
            logger.write(event, payload)

    def close(self) -> None:
        for logger in self._loggers:
            logger.close()


def sanitize_payload(payload: Any) -> Any:
    """Shared redaction helper for local run artifacts."""
    return _sanitize(payload)
