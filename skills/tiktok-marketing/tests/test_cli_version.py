from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from tiktok_marketing_safe_agent_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "tiktok-marketing-api-tool")
        self.assertIn("version", payload)

