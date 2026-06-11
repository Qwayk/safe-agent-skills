from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from plausible_api_tool.cli import main


class TestCliVersionOutput(unittest.TestCase):
    def test_version_respects_output_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = int(main(["--output", "json", "--version"]))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "plausible-api-tool")
        self.assertIn("version", payload)

