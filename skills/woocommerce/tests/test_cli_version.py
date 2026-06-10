from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "qwayk-woocommerce-safe-agent-cli")
        self.assertEqual(payload["version"], "0.1.0")
