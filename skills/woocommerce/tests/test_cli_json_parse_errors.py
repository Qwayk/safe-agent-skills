from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = main(["--output", "json"])
        self.assertEqual(rc, 1)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_subcommand_is_json_error(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
