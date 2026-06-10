from __future__ import annotations

import unittest
from pathlib import Path

from x_api_tool.openapi_inventory import (
    extract_operations,
    load_openapi_snapshot,
    official_operations_lines,
    parse_official_operations_text,
)


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_api_coverage_operation_ids(md: str) -> list[str]:
    ids: list[str] = []
    for raw in md.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("| operationId "):
            continue
        if line.startswith("|---"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if not cols:
            continue
        op_id = cols[0]
        if op_id:
            ids.append(op_id)
    return ids


def _parse_api_coverage_primary_cli(md: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in md.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("| operationId "):
            continue
        if line.startswith("|---"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        op_id = cols[0]
        primary = cols[-1]
        primary = primary.strip().strip("`").strip()
        if op_id:
            out[op_id] = primary
    return out


class TestOpenApiInventory(unittest.TestCase):
    def test_official_operations_matches_snapshot(self) -> None:
        root = _tool_root()
        snap = root / "docs" / "official_openapi_x_api_v2.json"
        committed = root / "docs" / "official_operations.txt"
        self.assertTrue(snap.exists(), "Missing pinned OpenAPI snapshot")
        self.assertTrue(committed.exists(), "Missing committed official_operations.txt")

        obj = load_openapi_snapshot(snap)
        ops = extract_operations(obj)
        expected_lines = official_operations_lines(ops)

        got_lines = parse_official_operations_text(_read_text(committed))
        self.assertEqual(got_lines, expected_lines)

    def test_api_coverage_has_one_row_per_operation(self) -> None:
        root = _tool_root()
        snap = root / "docs" / "official_openapi_x_api_v2.json"
        coverage = root / "docs" / "api_coverage.md"
        self.assertTrue(snap.exists(), "Missing pinned OpenAPI snapshot")
        self.assertTrue(coverage.exists(), "Missing docs/api_coverage.md")

        obj = load_openapi_snapshot(snap)
        ops = extract_operations(obj)
        expected_ids = [o.operation_id for o in ops]

        got_ids = _parse_api_coverage_operation_ids(_read_text(coverage))
        self.assertEqual(got_ids, expected_ids)

    def test_api_coverage_primary_cli_is_explicit_operation(self) -> None:
        root = _tool_root()
        coverage = root / "docs" / "api_coverage.md"
        self.assertTrue(coverage.exists(), "Missing docs/api_coverage.md")

        got = _parse_api_coverage_primary_cli(_read_text(coverage))
        self.assertTrue(got, "Expected at least one row in api_coverage.md")
        for op_id, primary_cli in got.items():
            self.assertEqual(primary_cli, f"x-api-tool api {op_id}")
            self.assertNotIn("--op", primary_cli)
