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

        merged = dict(obj)

        postprocess = self._provenance.get("_postprocess")
        if callable(postprocess):
            merged = postprocess(merged)
            if not isinstance(merged, dict):
                return merged

        # Heuristics to make outputs more v2-friendly without rewriting every command.
        if "ok" not in merged:
            merged["ok"] = True
        if "apply" in merged and "dry_run" not in merged and isinstance(merged.get("apply"), bool):
            merged["dry_run"] = not bool(merged.get("apply"))

        for k, v in self._provenance.items():
            if str(k).startswith("_"):
                continue
            if k not in merged:
                merged[k] = v
        return merged

    def emit(self, obj: Any) -> None:
        obj = self._with_provenance(obj)
        self.last = obj
        if self._mode == "json":
            json.dump(obj, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return
        # text
        if isinstance(obj, str):
            sys.stdout.write(obj)
            if not obj.endswith("\n"):
                sys.stdout.write("\n")
            return
        sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n")

    # Backwards-compatible alias (internal code historically used `print`).
    def print(self, obj: Any) -> None:
        self.emit(obj)
