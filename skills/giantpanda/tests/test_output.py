from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from giantpanda_api_tool.output import Output


class TestOutput(unittest.TestCase):
    def test_json_emits_single_object(self) -> None:
        out = Output(mode="json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            out.emit({"ok": True, "value": 1})
        raw = buf.getvalue()
        self.assertTrue(raw.startswith("{"))
        # one object, not a bare stream of text
        self.assertTrue(raw.strip().endswith("}"))

    def test_json_wraps_non_mapping(self) -> None:
        out = Output(mode="json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            out.emit("hello")
        self.assertIn("\"data\": \"hello\"", buf.getvalue())

    def test_json_wraps_list_as_object(self) -> None:
        out = Output(mode="json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            out.emit(["alpha", "beta"])
        payload = json.loads(buf.getvalue())
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("data"), ["alpha", "beta"])
