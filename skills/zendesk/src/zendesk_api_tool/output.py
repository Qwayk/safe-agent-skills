from __future__ import annotations

import json
import sys
from typing import Any


class Output:
    def __init__(self, *, mode: str):
        self._mode = mode
        self._provenance: dict[str, Any] = {}
        self.last: Any | None = None

    def set_provenance(self, provenance: dict[str, Any]) -> None:
        self._provenance = dict(provenance or {})

    def _with_provenance(self, obj: Any) -> Any:
        if self._mode != "json":
            return obj
        if not isinstance(obj, dict):
            return obj
        if not self._provenance:
            return obj
        merged = dict(obj)
        for k, v in self._provenance.items():
            if k not in merged:
                merged[k] = v
        return merged

    def emit(self, obj: Any) -> None:
        obj = self._with_provenance(obj)
        self.last = obj
        try:
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
        except BrokenPipeError:
            try:
                sys.stdout.close()
            except Exception:
                pass
            raise SystemExit(0) from None
