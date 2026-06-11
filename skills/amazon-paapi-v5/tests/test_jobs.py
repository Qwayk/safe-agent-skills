from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import amazon_pa_api_tool.commands.jobs as jobs_mod
from amazon_pa_api_tool.output import Output


class TestJobs(unittest.TestCase):
    def test_unknown_action_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["nope.nope"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = {"apply": False, "yes": False, "out": Output(mode="json")}
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = jobs_mod.cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["errors"], 1)

    def test_emits_one_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["read.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = {"apply": False, "yes": False, "out": Output(mode="json")}
            buf = io.StringIO()
            original_actions = jobs_mod._ACTIONS
            try:
                jobs_mod._ACTIONS = {
                    "read.ping": jobs_mod.ActionSpec(
                        name="read.ping",
                        handler=lambda row, _ctx: {"ok": True, "row": row},
                    )
                }
                with redirect_stdout(buf):
                    rc = jobs_mod.cmd_jobs_run(args, ctx)
            finally:
                jobs_mod._ACTIONS = original_actions
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 1)
