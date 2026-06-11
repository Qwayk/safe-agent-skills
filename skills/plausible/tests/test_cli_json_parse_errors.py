from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from plausible_api_tool.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = int(main(argv))
        payload = json.loads(buf.getvalue())
        return rc, payload

    def test_unknown_command_is_single_json_object(self) -> None:
        rc, payload = self._run(["--output", "json", "nope"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_command_is_single_json_object(self) -> None:
        rc, payload = self._run(["--output", "json"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_arg_is_single_json_object(self) -> None:
        rc, payload = self._run(["--output", "json", "stats", "validate"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

