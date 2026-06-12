from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jobber_safe_agent_cli.commands.jobs import cmd_jobs_run
from jobber_safe_agent_cli.output import Output


class _FakeJobsClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def execute(self, query: str, variables=None) -> dict:
        return {"data": {"ok": True, "query": query}, "variables": variables}


class TestJobs(unittest.TestCase):
    def _high_risk_row_action(self) -> str:
        return "write.clientDelete"

    def _ctx(self, **overrides):
        ctx = {
            "cfg": SimpleNamespace(
                base_url="http://example.invalid",
                graphql_url="http://example.invalid/api/graphql",
                token="token",
                graphql_version="2025-04-16",
            ),
            "tool": "qwayk-jobber-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "qwayk-jobber-safe-agent-cli jobs run",
            "apply": False,
            "yes": False,
            "timeout_s": 30,
            "verbose": False,
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def test_write_action_requires_plan_in_before_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "args_json", "selection"])
                w.writerow(["write.clientCreate", '{"input":{"firstName":"Sample","lastName":"Client"}}', "client { id name }"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=True, yes=False, command_str="qwayk-jobber-safe-agent-cli --apply jobs run")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("reasons", payload)
            self.assertIn("require --plan-in", payload["reasons"][0])
            self.assertEqual(payload["errors"], 0)

    def test_emits_one_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "selection", "limit"])
                w.writerow(["read.clients", "nodes { id name } totalCount", "5"])

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

    def test_registry_read_action_is_planned_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "selection", "limit"])
                w.writerow(["read.clients", "nodes { id name } totalCount", "5"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=False, yes=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["results"][0]["action"], "read.clients")
            self.assertIn("clients", payload["results"][0]["result"]["plan"]["graphql"]["document"])

    def test_registry_write_action_is_planned_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "args_json", "selection"])
                w.writerow(["write.clientCreate", '{"input":{"firstName":"Sample","lastName":"Client"}}', "client { id name }"])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx = self._ctx(apply=False, yes=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["results"][0]["action"], "write.clientCreate")
            self.assertEqual(payload["results"][0]["result"]["plan"]["mutation"], "clientCreate")

    def test_registry_write_action_is_planned_in_dry_run_with_minimal_columns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "args_json", "selection"])
                w.writerow(["write.clientCreate", '{"input":{"firstName":"Sample","lastName":"Client"}}', "client { id name }"])

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
            self.assertEqual(payload["results"][0]["action"], "write.clientCreate")
            self.assertTrue(payload["results"][0]["result"]["dry_run"])
            self.assertIn("plan", payload["results"][0]["result"])

    def test_plan_out_and_plan_in_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job_path = Path(d) / "jobs.csv"
            with job_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "args_json", "selection"])
                w.writerow(["write.clientCreate", '{"input":{"firstName":"Sample","lastName":"Client"}}', "client { id name }"])

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
                command_str="qwayk-jobber-safe-agent-cli --apply --yes --plan-in plan.json --file jobs.csv jobs run",
            )
            buf2 = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.jobs.GraphQLClient", _FakeJobsClient):
                with redirect_stdout(buf2):
                    rc2 = cmd_jobs_run(args_apply, ctx_apply)
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertTrue(receipt_path.exists())
            self.assertEqual(payload2["receipt"]["snapshot_status"], "No snapshot available")
            self.assertIn("recovery_notes", payload2["receipt"])

    def test_jobs_apply_refuses_high_risk_write_without_ack_no_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action", "args_json", "selection"])
                w.writerow([self._high_risk_row_action(), "{}", ""])

            args = SimpleNamespace(file=str(path), limit=None)
            ctx_plan = self._ctx(apply=False, yes=False, plan_out=str(path.with_suffix(".plan.json")))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(args, ctx_plan)
            self.assertEqual(rc, 0)
            plan_path = Path(path.with_suffix(".plan.json"))
            self.assertTrue(plan_path.exists())

            args_apply = SimpleNamespace(file=str(path), limit=None)
            ctx_apply = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                command_str="qwayk-jobber-safe-agent-cli --apply --yes --plan-in jobs-plan.json jobs run",
            )
            buf2 = io.StringIO()
            with patch("jobber_safe_agent_cli.commands.jobs.GraphQLClient", _FakeJobsClient):
                with redirect_stdout(buf2):
                    rc2 = cmd_jobs_run(args_apply, ctx_apply)
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertIn("ack-no-snapshot", payload2["reasons"][0])
