from __future__ import annotations

from ..presets import get_preset, list_presets


def cmd_presets_list(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]

    payload = list_presets()
    presets = payload["presets"]
    out_obj = {
        "ok": True,
        "presets_list": {"schema_version": payload["schema_version"], "count": len(presets)},
        "presets": presets,
    }
    audit.write("presets.list", {"count": len(presets)})
    out.emit(out_obj)
    return 0


def cmd_presets_show(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]

    payload = get_preset(getattr(args, "preset", None))
    preset = payload["preset"]
    out_obj = {
        "ok": True,
        "presets_show": {"schema_version": payload["schema_version"], "preset_id": preset["id"]},
        "preset": preset,
    }
    audit.write("presets.show", {"preset_id": str(preset.get("id", ""))})
    out.emit(out_obj)
    return 0

