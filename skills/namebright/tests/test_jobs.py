from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from namebright_safe_cli.cli import main


class TestJobsAndDemoAreNotExposed(unittest.TestCase):
    def test_jobs_command_is_not_supported(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "jobs", "run", "--file", "jobs.csv"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_demo_read_is_not_supported(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "demo", "read"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_demo_write_is_not_supported(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "demo", "write", "--selector", "x"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")
