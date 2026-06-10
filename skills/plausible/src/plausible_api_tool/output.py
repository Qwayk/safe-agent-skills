from __future__ import annotations

import json
import sys
from pathlib import Path
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


def write_json_file(path: str, obj: Any) -> str:
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return str(p)
