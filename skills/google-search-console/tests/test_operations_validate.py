from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from gsc_api_tool.cli import main


class TestOperationsValidate(unittest.TestCase):
    def test_operations_validate_passes_offline(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "operations", "validate"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])

