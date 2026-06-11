from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import NotFound, ValidationError
from .validate import PresetValidationResult, validate_preset_dict


@dataclass(frozen=True)
class PresetRef:
    name: str
    path: Path
    builtin: bool


class PresetLoader:
    def __init__(self, *, extra_search_paths: list[Path] | None = None):
        self._builtin_dir = Path(__file__).resolve().parent / "builtin"
        self._extra = [p for p in (extra_search_paths or []) if isinstance(p, Path)]

    def _search_dirs(self) -> list[PresetRef]:
        refs: list[PresetRef] = []
        if self._builtin_dir.exists():
            for p in sorted(self._builtin_dir.glob("*.json")):
                refs.append(PresetRef(name=p.stem, path=p, builtin=True))
        for d in self._extra:
            if not d.exists() or not d.is_dir():
                continue
            for p in sorted(d.glob("*.json")):
                refs.append(PresetRef(name=p.stem, path=p, builtin=False))
        # De-dupe by name preferring extra paths first (so local overrides can exist).
        by_name: dict[str, PresetRef] = {}
        for r in refs:
            by_name[r.name] = r
        return [by_name[k] for k in sorted(by_name.keys())]

    def list_presets(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for r in self._search_dirs():
            out.append({"name": r.name, "builtin": r.builtin, "path": str(r.path)})
        return out

    def load_preset(self, name: str) -> dict[str, Any]:
        n = str(name or "").strip()
        if not n:
            raise ValidationError("Missing preset name")
        for r in self._search_dirs():
            if r.name == n:
                try:
                    obj = json.loads(r.path.read_text(encoding="utf-8"))
                except Exception as e:  # noqa: BLE001
                    raise ValidationError(f"Invalid preset JSON: {r.path}: {type(e).__name__}: {e}") from None
                if not isinstance(obj, dict):
                    raise ValidationError(f"Preset must be a JSON object: {r.path}")
                return obj
        raise NotFound(f"Preset not found: {n}")

    def validate_preset(self, name: str) -> PresetValidationResult:
        preset = self.load_preset(name)
        return validate_preset_dict(preset, source=f"{name}.json")

