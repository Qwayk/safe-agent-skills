from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from zendesk_api_tool.cli import main


class TestCliInventoryValidate(unittest.TestCase):
    def test_inventory_validate_ok_offline(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "inventory", "validate"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0, payload)
        self.assertTrue(payload["ok"])
        self.assertGreater(int(payload["operation_count"]), 0)
        self.assertEqual(int(payload["command_count"]), int(payload["operation_count"]))

