from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import NotFound, SafetyError, ValidationError


@dataclass(frozen=True)
class CompareArgs:
    pack_a: Path
    pack_b: Path
    out_dir: Path
    overwrite: bool


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_manifest(pack_dir: Path) -> dict[str, Any]:
    p = pack_dir / "manifest.json"
    if not p.exists():
        raise NotFound(f"Missing manifest.json: {p}")
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid manifest.json: {p}: {type(e).__name__}: {e}") from None
    if not isinstance(obj, dict):
        raise ValidationError(f"manifest.json must be a JSON object: {p}")
    if int(obj.get("schema_version") or 0) != 1:
        raise ValidationError(f"Unsupported schema_version in {p}: {obj.get('schema_version')}")
    return obj


def _ensure_empty_dir(out_dir: Path, overwrite: bool) -> None:
    d = out_dir.expanduser().resolve()
    if d.exists():
        if not overwrite:
            raise SafetyError(f"Refusing to overwrite existing out dir without --overwrite: {d}")
        if not d.is_dir():
            raise ValidationError(f"--out-dir exists but is not a directory: {d}")
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=True)


def _table_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for t in manifest.get("tables") or []:
        if not isinstance(t, dict):
            continue
        name = str(t.get("name") or "").strip()
        if not name:
            continue
        out[name] = t
    return out


def compare_packs(*, a: CompareArgs) -> dict[str, Any]:
    ma = _read_manifest(a.pack_a)
    mb = _read_manifest(a.pack_b)

    ta = _table_map(ma)
    tb = _table_map(mb)
    names_a = set(ta.keys())
    names_b = set(tb.keys())

    added = sorted(list(names_b - names_a))
    removed = sorted(list(names_a - names_b))
    common = sorted(list(names_a & names_b))

    changed_counts: list[dict[str, Any]] = []
    for n in common:
        ra = int((ta.get(n) or {}).get("row_count") or 0)
        rb = int((tb.get(n) or {}).get("row_count") or 0)
        if ra != rb:
            changed_counts.append({"table": n, "rows_a": ra, "rows_b": rb, "delta": rb - ra})

    warnings: list[str] = []
    ja = ma.get("join_map") or {}
    jb = mb.get("join_map") or {}
    if isinstance(ja, dict) and isinstance(jb, dict):
        ka = set(ja.keys())
        kb = set(jb.keys())
        if ka != kb:
            warnings.append("join_map differs between packs; joins may not be compatible")
    else:
        warnings.append("join_map missing or invalid in one or both packs")

    return {
        "schema_version": 1,
        "generated_at_utc": _utc_now(),
        "pack_a": {"dir": str(a.pack_a), "preset": ma.get("preset"), "since": ma.get("since"), "until": ma.get("until")},
        "pack_b": {"dir": str(a.pack_b), "preset": mb.get("preset"), "since": mb.get("since"), "until": mb.get("until")},
        "diff": {
            "tables": {"added": added, "removed": removed, "changed_row_counts": changed_counts},
            "group_failures": {
                "a_failed_groups": [
                    g.get("group_id")
                    for g in (ma.get("groups") or [])
                    if isinstance(g, dict) and str(g.get("status") or "") == "failed"
                ],
                "b_failed_groups": [
                    g.get("group_id")
                    for g in (mb.get("groups") or [])
                    if isinstance(g, dict) and str(g.get("status") or "") == "failed"
                ],
            },
        },
        "warnings": warnings,
        "notes": ["Descriptive only. This compare does not make causal claims."],
    }


def run_compare(*, a: CompareArgs, apply: bool) -> tuple[int, dict[str, Any]]:
    summary = compare_packs(a=a)
    if not apply:
        return 0, {"ok": True, "dry_run": True, "out_dir": str(a.out_dir), "planned_file": "compare_summary.json"}

    _ensure_empty_dir(a.out_dir, overwrite=a.overwrite)
    out_path = a.out_dir / "compare_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0, {"ok": True, "dry_run": False, "out_dir": str(a.out_dir), "compare_summary_path": str(out_path)}

