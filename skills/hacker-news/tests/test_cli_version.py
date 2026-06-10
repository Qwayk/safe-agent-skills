from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from hacker_news_api_tool.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "hacker-news-api-tool")
        self.assertIn("version", payload)
