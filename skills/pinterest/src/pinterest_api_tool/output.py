from __future__ import annotations

import json
import sys
from typing import Any


class Output:
    def __init__(self, *, mode: str):
        self._mode = mode

    def emit(self, obj: Any) -> None:
        if self._mode == "json":
            json.dump(obj, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return
        if isinstance(obj, str):
            sys.stdout.write(obj)
            if not obj.endswith("\n"):
                sys.stdout.write("\n")
            return
        sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n")

