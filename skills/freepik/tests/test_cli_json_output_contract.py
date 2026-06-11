from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from freepik_api_tool.cli import main


class TestCliJsonOutputContract(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            rc = main(argv)
        return rc, stdout.getvalue(), stderr.getvalue()

    def test_invalid_args_in_json_mode_prints_one_json_object(self) -> None:
        rc, out, _err = self._run(["--output", "json", "download", "--format", "jpg", "--out-dir", "x", "--inventory", "y"])
        self.assertEqual(rc, 2)
        payload = json.loads(out)
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("ok"), False)
        self.assertEqual(payload.get("error_type"), "UsageError")
        self.assertIsInstance(payload.get("error"), str)

    def test_invalid_subcommand_in_json_mode_prints_one_json_object(self) -> None:
        rc, out, _err = self._run(["--output", "json", "nope"])
        self.assertEqual(rc, 2)
        payload = json.loads(out)
        self.assertEqual(payload.get("ok"), False)
        self.assertEqual(payload.get("error_type"), "UsageError")

    def test_help_in_json_mode_is_json(self) -> None:
        rc, out, _err = self._run(["--output", "json", "--help"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload.get("ok"), True)
        self.assertIn("help", payload)
        self.assertIsInstance(payload.get("help"), str)

    def test_version_in_json_mode_is_json(self) -> None:
        rc, out, _err = self._run(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload.get("ok"), True)
        self.assertEqual(payload.get("tool"), "freepik-api-tool")
        self.assertIsInstance(payload.get("version"), str)

    def test_invalid_args_in_text_mode_raises_systemexit(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                main(["--output", "text", "download"])
