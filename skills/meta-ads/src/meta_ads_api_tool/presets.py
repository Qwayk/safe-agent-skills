from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .errors import ValidationError


@dataclass(frozen=True)
class Preset:
    preset_id: str
    label: str
    description: str
    use_case_tags: tuple[str, ...]
    surfaces: dict[str, Any]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.preset_id,
            "label": self.label,
            "description": self.description,
            "use_case_tags": list(self.use_case_tags),
            "surfaces": self.surfaces,
        }


def _require_str(obj: dict[str, Any], key: str) -> str:
    val = obj.get(key, None)
    if not isinstance(val, str) or not val.strip():
        raise ValidationError(f"Invalid presets data: missing/invalid '{key}'")
    return val


def _require_list_of_str(obj: dict[str, Any], key: str) -> list[str]:
    val = obj.get(key, None)
    if not isinstance(val, list) or not all(isinstance(x, str) and x.strip() for x in val):
        raise ValidationError(f"Invalid presets data: missing/invalid '{key}'")
    return val


def _require_dict(obj: dict[str, Any], key: str) -> dict[str, Any]:
    val = obj.get(key, None)
    if not isinstance(val, dict):
        raise ValidationError(f"Invalid presets data: missing/invalid '{key}'")
    return val


def _load_builtin_presets_payload() -> dict[str, Any]:
    try:
        from importlib.resources import files  # py311
    except Exception as e:  # pragma: no cover
        raise ValidationError(f"Unable to load presets data (importlib.resources unavailable): {e}") from e

    try:
        raw = (files("meta_ads_api_tool.data") / "presets.json").read_text(encoding="utf-8")
    except Exception as e:
        raise ValidationError(f"Unable to load presets data (presets.json not found): {e}") from e

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid presets data (presets.json is not valid JSON): {e}") from e

    if not isinstance(payload, dict):
        raise ValidationError("Invalid presets data: expected a top-level JSON object")
    return payload


def load_builtin_presets() -> tuple[str, dict[str, Preset]]:
    """
    Load built-in, packaged presets.

    Returns:
      (schema_version, presets_by_id)
    """
    payload = _load_builtin_presets_payload()
    schema_version = _require_str(payload, "schema_version")
    presets_raw = payload.get("presets", None)
    if not isinstance(presets_raw, list):
        raise ValidationError("Invalid presets data: missing/invalid 'presets'")

    presets: dict[str, Preset] = {}
    for i, item in enumerate(presets_raw):
        if not isinstance(item, dict):
            raise ValidationError(f"Invalid presets data: presets[{i}] must be an object")
        preset_id = _require_str(item, "id")
        if preset_id in presets:
            raise ValidationError(f"Invalid presets data: duplicate preset id '{preset_id}'")
        label = _require_str(item, "label")
        description = _require_str(item, "description")
        use_case_tags = tuple(_require_list_of_str(item, "use_case_tags"))
        surfaces = _require_dict(item, "surfaces")
        presets[preset_id] = Preset(
            preset_id=preset_id,
            label=label,
            description=description,
            use_case_tags=use_case_tags,
            surfaces=surfaces,
        )
    return schema_version, presets


def list_presets() -> dict[str, Any]:
    schema_version, presets_by_id = load_builtin_presets()
    items = []
    for preset_id in sorted(presets_by_id.keys()):
        p = presets_by_id[preset_id]
        items.append(
            {
                "id": p.preset_id,
                "label": p.label,
                "description": p.description,
                "use_case_tags": list(p.use_case_tags),
            }
        )
    return {"schema_version": schema_version, "presets": items}


def get_preset(preset_id: str) -> dict[str, Any]:
    preset_id = str(preset_id or "").strip()
    if not preset_id:
        raise ValidationError("Missing --preset")
    schema_version, presets_by_id = load_builtin_presets()
    if preset_id not in presets_by_id:
        raise ValidationError(f"Unknown preset '{preset_id}'")
    return {"schema_version": schema_version, "preset": presets_by_id[preset_id].to_public_dict()}

