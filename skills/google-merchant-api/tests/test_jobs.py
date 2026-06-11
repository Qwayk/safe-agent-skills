from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from google_merchant_api_tool.commands.demo import cmd_demo_read, cmd_demo_write
from google_merchant_api_tool.commands.jobs import cmd_jobs_run
from google_merchant_api_tool.output import Output


class TestJobs(unittest.TestCase):
    def _ctx(self, **overrides):
        ctx = {
            "tool": "google-merchant-api-tool",
            "tool_version": "0.0.0",
            "command_str": "google-merchant-api-tool jobs run",
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def test_jobs_is_legacy_guard(self) -> None:
        args = SimpleNamespace(file=str(Path("examples/jobs.csv")), limit=None)
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_jobs_run(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["legacy"])
        self.assertEqual(payload["error_type"], "LegacyCommandError")
        self.assertIn("legacy", payload["error"].lower())

    def test_demo_read_is_legacy_guard(self) -> None:
        args = SimpleNamespace()
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_demo_read(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["legacy"])
        self.assertEqual(payload["command"], "demo read")

    def test_demo_write_is_legacy_guard(self) -> None:
        args = SimpleNamespace()
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_demo_write(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["legacy"])
        self.assertEqual(payload["command"], "demo write")
