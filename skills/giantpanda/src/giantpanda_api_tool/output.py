from __future__ import annotations

import json
import sys
from typing import Any


class Output:
    """Emission helper with JSON/text mode parity."""

    def __init__(self, *, mode: str) -> None:
        self.mode = "json" if str(mode) != "text" else "text"

    def emit(self, obj: Any) -> None:
        if self.mode == "json":
            if not isinstance(obj, dict):
                obj = {"ok": True, "data": obj}
            json.dump(obj, sys.stdout, ensure_ascii=False, sort_keys=True)
            sys.stdout.write("\n")
            return
        if isinstance(obj, str):
            sys.stdout.write(obj)
            if not obj.endswith("\n"):
                sys.stdout.write("\n")
            return
        sys.stdout.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")
