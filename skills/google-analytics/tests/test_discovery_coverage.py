from __future__ import annotations

import unittest
from pathlib import Path

from ga4_api_tool.method_inventory import official_commands, official_method_ids, snapshots


def _read_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


class TestDiscoveryCoverage(unittest.TestCase):
    def test_method_ids_match_committed_snapshots(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        docs_dir = tool_root / "docs"

        expected_files = {
            ("admin", "v1alpha"): docs_dir / "official_methods_admin_v1alpha.txt",
            ("data", "v1beta"): docs_dir / "official_methods_data_v1beta.txt",
            ("data", "v1alpha"): docs_dir / "official_methods_data_v1alpha.txt",
        }

        for spec in snapshots():
            key = (spec.service_token, spec.version_token)
            self.assertIn(key, expected_files)
            expected = _read_lines(expected_files[key])
            got = official_method_ids(spec)
            self.assertTrue(got)
            self.assertEqual(len(got), len(set(got)), "Derived method ids must be unique")
            self.assertEqual(expected, got)

    def test_commands_match_committed_snapshot(self) -> None:
        tool_root = Path(__file__).resolve().parents[1]
        expected_path = tool_root / "docs" / "official_commands.txt"

        expected = _read_lines(expected_path)
        got = official_commands()
        self.assertTrue(got)
        self.assertEqual(len(got), len(set(got)), "Derived commands must be unique")
        self.assertEqual(expected, got)

