from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from amazon_pa_api_tool import __version__
from amazon_pa_api_tool.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = int(main(["--output", "json", "--version"]))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload.get("ok"), True)
        self.assertEqual(payload.get("tool"), "amazon-pa-api-tool")
        self.assertEqual(payload.get("version"), __version__)

