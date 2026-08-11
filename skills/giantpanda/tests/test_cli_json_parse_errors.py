from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from giantpanda_api_tool.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_subcommand_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_invalid_date_format_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    "/tmp/giantpanda-missing.env",
                    "domains",
                    "stats",
                    "--start-date",
                    "bad-date",
                    "--end-date",
                    "2026-08-01",
                ]
            )
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertIn("strict", payload["error"])

    def test_non_padded_date_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    "/tmp/giantpanda-missing.env",
                    "domains",
                    "stats",
                    "--start-date",
                    "2026-8-1",
                    "--end-date",
                    "2026-8-07",
                ]
            )
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertIn("strict", payload["error"])

    def test_json_help_is_single_json_object(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["--output", "json", "--help"])
        self.assertEqual(rc, 1)
        payload = json.loads(out.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "HelpRequested")
        self.assertFalse(err.getvalue())

    def test_top_level_exception_hides_token(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            with patch(
                "giantpanda_api_tool.cli.load_config",
                side_effect=RuntimeError("boom with token=sentinel_token"),
            ):
                rc = main(["--output", "json", "--env-file", "/tmp/giantpanda-missing.env", "auth", "check"])
        payload = json.loads(out.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "RuntimeError")
        self.assertNotIn("sentinel_token", out.getvalue())
