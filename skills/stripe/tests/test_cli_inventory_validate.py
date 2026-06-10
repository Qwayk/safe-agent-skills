from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from stripe_api_tool.cli import main


class TestCliInventoryValidate(unittest.TestCase):
    def _run(self, argv: list[str]) -> dict:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        self.assertEqual(rc, 0, msg=f"non-zero exit for argv={argv!r}: {buf.getvalue()!r}")
        return json.loads(buf.getvalue())

    def test_inventory_validate_top_level(self) -> None:
        payload = self._run(["--output", "json", "inventory", "validate"])
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["operation_count"], 0)
        self.assertEqual(payload["command_count"], payload["operation_count"])

    def test_inventory_validate_operations_alias(self) -> None:
        payload = self._run(["--output", "json", "inventory", "operations", "validate"])
        self.assertTrue(payload["ok"])

    def test_inventory_validate_commands_alias(self) -> None:
        payload = self._run(["--output", "json", "inventory", "commands", "validate"])
        self.assertTrue(payload["ok"])

