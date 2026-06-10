from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestSmoke(unittest.TestCase):
    def test_operations_list_cli_smoke(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = main(["--output", "json", "operations", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["count"], 139)
