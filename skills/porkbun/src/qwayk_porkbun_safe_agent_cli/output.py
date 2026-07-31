from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from .privacy import sanitize


class Output:
    """Serialize tool output in the required JSON/text modes."""

    def __init__(self, mode: str = "json", sensitive_values: Iterable[str] = ()):
        self.mode = "json" if str(mode or "json").lower() == "json" else "text"
        self.last: Any = None
        self._sensitive_values = {str(value) for value in sensitive_values if str(value)}

    def add_sensitive_values(self, values: Iterable[str]) -> None:
        self._sensitive_values.update(str(value) for value in values if str(value))

    def emit(self, obj: Any) -> None:
        obj = sanitize(obj, self._sensitive_values)
        self.last = obj
        if self.mode == "text":
            if isinstance(obj, str):
                print(obj)
                return
            print(json.dumps(obj, indent=2, sort_keys=False))
            return

        payload = json.dumps(obj, indent=2, sort_keys=True)
        print(payload)
