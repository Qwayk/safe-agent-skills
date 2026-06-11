from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from stripe_api_tool.cli import main
from stripe_api_tool.inventory import canonical_commands, canonical_operation_ids, pinned_commands_path, pinned_operations_path


class TestOpenApiCoverage(unittest.TestCase):
    def test_operations_and_commands_are_one_to_one(self) -> None:
        ops = canonical_operation_ids()
        cmds = canonical_commands()
        self.assertGreater(len(ops), 0)
        self.assertEqual(len(cmds), len(ops))
        self.assertEqual(len(set(ops)), len(ops))
        self.assertEqual(len(set(cmds)), len(cmds))

    def test_pinned_commands_file_matches_registry(self) -> None:
        pinned = pinned_commands_path()
        self.assertTrue(pinned.exists())
        pinned_lines = [ln for ln in pinned.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(pinned_lines, canonical_commands())

    def test_pinned_operations_file_matches_registry(self) -> None:
        pinned = pinned_operations_path()
        self.assertTrue(pinned.exists())
        pinned_lines = [ln for ln in pinned.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(pinned_lines, canonical_operation_ids())

    def test_inventory_validate_includes_commands(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "inventory", "validate"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0, payload)
        self.assertTrue(payload["ok"])
        self.assertGreater(int(payload["operation_count"]), 0)
        self.assertEqual(int(payload["command_count"]), int(payload["operation_count"]))
