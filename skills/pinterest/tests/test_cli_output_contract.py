from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from pinterest_api_tool import __version__
from pinterest_api_tool.cli import main


class TestCliOutputContract(unittest.TestCase):
    def test_version_json_mode_emits_one_object(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["tool"], "pinterest-api-tool")
        self.assertEqual(payload["version"], __version__)
        self.assertEqual(err.getvalue(), "")

    def test_parse_error_json_mode_emits_one_object(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main([])
        self.assertEqual(rc, 2)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("required", payload["error"])
        self.assertEqual(err.getvalue(), "")

    def test_unknown_arg_json_mode_emits_one_object(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["auth", "check", "--nope"])
        self.assertEqual(rc, 2)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("unrecognized arguments", payload["error"])
        self.assertEqual(err.getvalue(), "")

    def test_runtime_error_debug_json_mode_emits_one_object_and_stderr(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["--debug", "boards", "list"])
        self.assertEqual(rc, 1)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error_type"], "RuntimeError")
        self.assertIn("No usable access token found", payload["error"])
        self.assertNotEqual(err.getvalue(), "")
