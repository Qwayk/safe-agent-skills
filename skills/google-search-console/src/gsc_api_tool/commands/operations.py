from __future__ import annotations

from pathlib import Path

from ..command_naming import method_id_to_command_str
from ..discovery import DEFAULT_DISCOVERY_SNAPSHOT, list_method_ids, load_discovery_snapshot, load_methods
from ..errors import ValidationError


def _official_methods_path() -> Path:
    return DEFAULT_DISCOVERY_SNAPSHOT.parent / "official_methods_searchconsole_v1_2026-03-05.txt"


def _official_commands_path() -> Path:
    return DEFAULT_DISCOVERY_SNAPSHOT.parent / "official_commands_searchconsole_v1_2026-03-05.txt"


def cmd_operations_list(args, ctx) -> int:
    _ = args
    discovery = load_discovery_snapshot()
    methods = load_methods(discovery=discovery)
    ops = []
    for mid, spec in methods.items():
        ops.append(
            {
                "method_id": mid,
                "command": "gsc-api-tool " + method_id_to_command_str(mid),
                "http_method": spec.http_method,
                "path": spec.path,
                "has_request_body": spec.has_request_body,
            }
        )
    out = {"ok": True, "count": len(ops), "operations": ops}
    ctx["audit"].write("operations.list", {"count": len(ops)})
    ctx["out"].emit(out)
    return 0


def cmd_operations_validate(args, ctx) -> int:
    _ = args
    discovery = load_discovery_snapshot()
    snapshot_method_ids = list_method_ids(discovery)
    if len(snapshot_method_ids) != 11:
        raise ValidationError(f"Discovery snapshot method count changed: expected 11, got {len(snapshot_method_ids)}")

    official_methods_path = _official_methods_path()
    official_commands_path = _official_commands_path()
    official_method_ids = [ln.strip() for ln in official_methods_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    official_commands = [ln.strip() for ln in official_commands_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    computed_commands = [method_id_to_command_str(mid) for mid in snapshot_method_ids]

    ok = True
    reasons: list[str] = []

    if official_method_ids != snapshot_method_ids:
        ok = False
        reasons.append("official_methods file does not match discovery snapshot")
    if official_commands != computed_commands:
        ok = False
        reasons.append("official_commands file does not match naming rule for snapshot")

    registered = sorted(list(ctx.get("registered_method_ids") or []))
    if registered != snapshot_method_ids:
        ok = False
        reasons.append("registered CLI method commands do not match discovery snapshot")

    out = {
        "ok": ok,
        "expected_method_count": 11,
        "snapshot_method_count": len(snapshot_method_ids),
        "official_methods_path": str(official_methods_path),
        "official_commands_path": str(official_commands_path),
        "registered_method_count": len(registered),
        "reasons": reasons,
    }
    ctx["audit"].write("operations.validate", {"ok": ok, "reasons": reasons})
    ctx["out"].emit(out)
    return 0 if ok else 1

