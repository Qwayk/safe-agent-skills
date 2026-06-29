from __future__ import annotations

import json
import unittest
from pathlib import Path

from zapier_safe_agent_cli.cli import get_registered_operation_commands


class TestCommandInventory(unittest.TestCase):
    def test_inventory_matches_operation_table(self) -> None:
        root = Path(__file__).resolve().parents[1]
        raw = json.loads((root / "src/zapier_safe_agent_cli/operations_data.json").read_text(encoding="utf-8"))

        expected = sorted([f"{op['group']} {op['command']}" for op in raw])

        self.assertEqual(len(expected), 62)
        self.assertEqual(expected, get_registered_operation_commands())
