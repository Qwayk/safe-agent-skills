from __future__ import annotations

import json
import sys
from typing import Any

from .before_state import augment_output_with_before_state
from .redaction import sanitize


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
        if isinstance(obj, str):
            s = obj.lstrip()
            if s.startswith("{") or s.startswith("["):
                try:
                    obj = json.loads(obj)
                except json.JSONDecodeError:
                    pass
        obj = augment_output_with_before_state(obj)
        obj = sanitize(obj)
        self.last = obj
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
