from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from ..errors import SafetyError, ValidationError


@dataclass(frozen=True)
class PackPaths:
    out_dir: Path
    manifest_json: Path
    tables_dir: Path
    queries_json: Path
    errors_jsonl: Path


def build_pack_paths(out_dir: Path) -> PackPaths:
    out_dir = out_dir.expanduser().resolve()
    return PackPaths(
        out_dir=out_dir,
        manifest_json=out_dir / "manifest.json",
        tables_dir=out_dir / "tables",
        queries_json=out_dir / "queries" / "queries.json",
        errors_jsonl=out_dir / "errors" / "errors.jsonl",
    )


class PackWriter:
    def __init__(self, *, out_dir: Path, overwrite: bool):
        self.paths = build_pack_paths(out_dir)
        self._overwrite = bool(overwrite)

    def ensure_empty_dir(self) -> None:
        p = self.paths.out_dir
        if p.exists():
            if not self._overwrite:
                raise SafetyError(f"Refusing to overwrite existing out dir without --overwrite: {p}")
            if not p.is_dir():
                raise ValidationError(f"--out-dir exists but is not a directory: {p}")
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)

    def create_layout(self) -> None:
        self.ensure_empty_dir()
        self.paths.tables_dir.mkdir(parents=True, exist_ok=True)
        self.paths.queries_json.parent.mkdir(parents=True, exist_ok=True)
        self.paths.errors_jsonl.parent.mkdir(parents=True, exist_ok=True)
        # Always create the errors file for stable layout, even if it's empty.
        self.paths.errors_jsonl.write_text("", encoding="utf-8")

    def open_table_for_write(self, filename: str) -> tuple[Path, TextIO]:
        if "/" in filename or "\\" in filename or ".." in filename:
            raise ValidationError(f"Unsafe table filename: {filename}")
        if not filename.endswith(".jsonl"):
            raise ValidationError(f"Table filename must end with .jsonl: {filename}")
        path = self.paths.tables_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path, path.open("w", encoding="utf-8")

    def append_error(self, obj: dict[str, Any]) -> None:
        with self.paths.errors_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def write_queries(self, obj: Any) -> None:
        self.paths.queries_json.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def write_manifest(self, obj: Any) -> None:
        self.paths.manifest_json.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

