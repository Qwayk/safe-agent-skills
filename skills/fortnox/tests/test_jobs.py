from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from fortnox_api_tool.commands.jobs import cmd_jobs_run
from fortnox_api_tool.output import Output


class TestJobs(unittest.TestCase):
    def _ctx(self, **overrides):
        ctx = {
            "cfg": SimpleNamespace(base_url="http://example.invalid"),
            "tool": "fortnox-api-tool",
            "tool_version": "0.0.0",
            "command_str": "fortnox-api-tool jobs run",
            "apply": False,
            "yes": False,
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def test_jobs_run_is_honestly_marked_unsupported(self) -> None:
        args = SimpleNamespace(file="jobs.csv", limit=None)
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_jobs_run(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["supported"])
        self.assertEqual(payload["error_type"], "NotSupportedError")
        self.assertIn("registry-backed", payload["error"])
