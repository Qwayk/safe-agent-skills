from __future__ import annotations

from typing import Any

from ..errors import NotFound, ValidationError
from ..presets import PresetLoader
from ..presets.validate import validate_preset_dict


def cmd_presets_list(args: Any, ctx: dict[str, Any]) -> int:  # noqa: ARG001
    loader = PresetLoader()
    presets = loader.list_presets()
    ctx["audit"].write("presets_list", {"ok": True, "count": len(presets)})
    ctx["out"].emit({"ok": True, "presets": presets, "count": len(presets)})
    return 0


def cmd_presets_show(args: Any, ctx: dict[str, Any]) -> int:
    name = str(getattr(args, "preset", "") or "").strip()
    if not name:
        raise ValidationError("Missing --preset")
    loader = PresetLoader()
    try:
        preset = loader.load_preset(name)
    except NotFound as e:
        ctx["out"].emit({"ok": False, "error": str(e), "error_type": "NotFound"})
        return 1
    ctx["audit"].write("presets_show", {"ok": True, "preset": name})
    ctx["out"].emit({"ok": True, "preset": preset})
    return 0


def cmd_presets_validate(args: Any, ctx: dict[str, Any]) -> int:
    name = str(getattr(args, "preset", "") or "").strip()
    loader = PresetLoader()
    names: list[str]
    if name:
        names = [name]
    else:
        names = [p["name"] for p in loader.list_presets() if isinstance(p, dict) and p.get("name")]
        if not names:
            ctx["out"].emit({"ok": False, "error": "No presets found", "error_type": "NotFound"})
            return 1

    results: list[dict[str, Any]] = []
    had_errors = False
    for n in names:
        try:
            preset = loader.load_preset(n)
        except NotFound as e:
            had_errors = True
            results.append({"name": n, "ok": False, "errors": [str(e)], "error_type": "NotFound"})
            continue

        r = validate_preset_dict(preset, source=f"{n}.json")
        if not r.ok:
            had_errors = True
        results.append({"name": n, "ok": r.ok, "errors": list(r.errors)})

    ctx["audit"].write("presets_validate", {"ok": not had_errors, "count": len(results)})
    if had_errors:
        ctx["out"].emit(
            {
                "ok": False,
                "error": "Preset validation failed",
                "error_type": "ValidationError",
                "results": results,
            }
        )
        return 1
    ctx["out"].emit({"ok": True, "results": results})
    return 0

