from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from google_merchant_api_tool.cli import build_parser, main


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
        # `auth` requires a subcommand.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_removed_demo_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "demo", "read"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_removed_jobs_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "jobs", "run", "--file", "jobs.csv"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_plan_in_flag_is_accepted(self) -> None:
        self.assertIn("--plan-in", build_parser().format_help())
        args = build_parser().parse_args(["--output", "json", "--plan-in", "legacy-plan.json", "auth", "check"])
        self.assertEqual(args.plan_in, "legacy-plan.json")
