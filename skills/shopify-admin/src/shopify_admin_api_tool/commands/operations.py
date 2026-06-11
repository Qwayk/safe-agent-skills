from __future__ import annotations

from ..official import load_official_manifest, load_official_operations_list, validate_manifest_matches_operations


def cmd_operations_list(args, ctx) -> int:
    _ = args
    ops = load_official_operations_list()
    ctx["out"].emit({"ok": True, "count": len(ops), "operations": ops})
    return 0


def cmd_operations_validate(args, ctx) -> int:
    _ = args
    manifest = load_official_manifest()
    ops = load_official_operations_list()
    validate_manifest_matches_operations(manifest, ops)
    ctx["out"].emit(
        {
            "ok": True,
            "api_version": manifest.api_version,
            "generated_at_utc": manifest.generated_at_utc,
            "operations_count": len(ops),
        }
    )
    return 0

