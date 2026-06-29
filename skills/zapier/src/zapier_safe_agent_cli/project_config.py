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

