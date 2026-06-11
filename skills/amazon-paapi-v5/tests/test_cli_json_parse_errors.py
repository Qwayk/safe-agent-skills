from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from amazon_pa_api_tool.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = int(main(argv))
        payload = json.loads(buf.getvalue())
        self.assertIsInstance(payload, dict)
        return rc, payload

    def test_missing_command_returns_json_error(self) -> None:
        rc, payload = self._run(["--output", "json"])
        self.assertEqual(rc, 1)
        self.assertEqual(payload.get("ok"), False)
        self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_missing_subcommand_returns_json_error(self) -> None:
        rc, payload = self._run(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        self.assertEqual(payload.get("ok"), False)
        self.assertEqual(payload.get("error_type"), "ValidationError")

