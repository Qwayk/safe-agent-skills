from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from x_api_tool.commands.jobs import cmd_jobs_run
from x_api_tool.output import Output


class TestJobs(unittest.TestCase):
    def _ctx(self, **overrides):
        ctx = {
            "cfg": SimpleNamespace(base_url="http://example.invalid"),
            "tool": "x-api-tool",
            "tool_version": "0.0.0",
            "command_str": "x-api-tool jobs run",
            "apply": False,
            "yes": False,
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def test_write_action_requires_apply_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=True, yes=False, command_str="x-api-tool --apply jobs run")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("reasons", payload)
            self.assertEqual(payload["errors"], 0)

    def test_emits_one_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["read.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=False, yes=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["count"], 1)

    def test_write_action_is_planned_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=False, yes=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["results"][0]["action"], "write.ping")
            self.assertTrue(payload["results"][0]["result"]["dry_run"])
            self.assertIn("plan", payload["results"][0]["result"])

    def test_plan_out_and_plan_in_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job_path = Path(d) / "jobs.csv"
            with job_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            plan_path = Path(d) / "plan.json"
            receipt_path = Path(d) / "receipt.json"

            # Dry-run with plan-out.
            args = SimpleNamespace(file=str(job_path), limit=None)
            ctx_plan = self._ctx(apply=False, yes=False, plan_out=str(plan_path))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx_plan)
            self.assertEqual(rc, 0)
            self.assertTrue(plan_path.exists())

            # Apply from plan-in.
            args_apply = SimpleNamespace(file=str(job_path), limit=None)
            ctx_apply = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                command_str="x-api-tool --apply --yes --plan-in plan.json --file jobs.csv jobs run",
            )
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_jobs_run(args_apply, ctx_apply)
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertFalse(receipt_path.exists())

    def test_jobs_apply_refusal_includes_before_state_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx_plan = self._ctx(apply=False, yes=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx_plan)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            rollback = payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertEqual(rollback["automatic_rollback"], False)
            self.assertIn("no built-in rollback", rollback["notes"].lower())
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")

            ctx_apply = self._ctx(apply=True, yes=True, command_str="x-api-tool --apply --yes jobs run")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_jobs_run(args, ctx_apply)
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
