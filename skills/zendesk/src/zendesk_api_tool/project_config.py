from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _resolve_path_value(*, base_dir: Path, value: str) -> str:
    v = value.strip()
    if not v:
        return v
    if v.startswith("~"):
        v = os.path.expanduser(v)
    p = Path(v)
    if not p.is_absolute():
        p = base_dir / p
    return str(p)


def load_project_config(config_path: str | None) -> tuple[dict[str, Any], Path | None]:
    """
    Load a non-secret project config JSON file.

    - Intended for project defaults (paths/domains/output dirs), not credentials.
    - Relative paths inside the JSON are resolved relative to the JSON file's directory.
    """
    if not config_path:
        return {}, None
    p = Path(config_path)
    if not p.exists():
        raise RuntimeError(f"Project config not found: {config_path}")
    base_dir = p.resolve().parent
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("Project config must be a JSON object")

    out: dict[str, Any] = {}
    for k, v in obj.items():
        if isinstance(v, str) and (k.endswith("_dir") or k.endswith("_path") or k.endswith("_file") or k.endswith("_csv")):
            out[k] = _resolve_path_value(base_dir=base_dir, value=v)
        else:
            out[k] = v
    return out, base_dir


# Pinned OpenAPI snapshot + canonical inventories (tool-root relative paths).
#
# These files are committed so the tool can prove “100% coverage” offline:
# - the snapshot itself is the canonical source of truth
# - inventories are derived deterministically and enforced by unit tests
OPENAPI_SNAPSHOT_FILENAME = "docs/official_openapi_ticketing_2026-03-05.yaml"
OPENAPI_OPERATIONS_FILENAME = "docs/official_operations_ticketing_2026-03-05.txt"
OPENAPI_COMMANDS_FILENAME = "docs/official_commands_ticketing_2026-03-05.txt"
