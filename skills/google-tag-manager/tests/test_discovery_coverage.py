from __future__ import annotations

import unittest
from pathlib import Path

from gtm_api_tool.method_inventory import official_commands, official_method_ids


def _read_lines(path: Path) -> list[str]:
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


class TestDiscoveryCoverage(unittest.TestCase):
    def test_official_method_list_matches_vendored_snapshot(self) -> None:
        root = Path(__file__).resolve().parents[1]
        canonical = _read_lines(root / "docs" / "official_methods_v2.txt")
        snapshot = official_method_ids()
        self.assertEqual(snapshot, canonical)
        self.assertEqual(len(snapshot), len(set(snapshot)))
        self.assertGreater(len(snapshot), 0)

    def test_official_command_list_is_deterministic(self) -> None:
        root = Path(__file__).resolve().parents[1]
        canonical = _read_lines(root / "docs" / "official_commands_v2.txt")
        derived = official_commands()
        self.assertEqual(derived, canonical)
        self.assertEqual(len(derived), len(set(derived)))
        self.assertGreater(len(derived), 0)

