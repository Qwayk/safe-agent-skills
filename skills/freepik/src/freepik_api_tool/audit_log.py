from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, TextIO


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if (
                lk in {"authorization", "password", "token", "secret", "api_key"}
                or lk.endswith("_token")
                or lk.endswith("_secret")
                or lk.endswith("_api_key")
                or lk.endswith("_password")
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
        if self._enabled:
            assert path is not None
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

    def write(self, event: str, payload: dict[str, Any]) -> None:
        if not self._enabled or not self._fh:
            return
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            "payload": _sanitize(payload),
        }
        self._fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None
