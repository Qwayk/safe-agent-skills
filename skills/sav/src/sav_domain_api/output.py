from __future__ import annotations

import json
import sys
from typing import Any


class Output:
    def __init__(self, *, mode: str = "json") -> None:
        self._mode = mode
        self.last: Any | None = None

    def emit(self, obj: Any) -> None:
        self.last = obj
        payload = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
        if self._mode == "json":
            sys.stdout.write(payload)
            sys.stdout.write("\n")
            return
        sys.stdout.write(payload)
        sys.stdout.write("\n")
