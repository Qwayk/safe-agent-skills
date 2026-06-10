from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import jobs as jobs_cmd
from pinterest_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestJobsRunner(unittest.TestCase):
    def _ctx(self, *, apply: bool, yes: bool, ack_volume: bool, ack_no_snapshot: bool = False) -> dict:
        return {
            "out": Output(mode="json"),
            "audit": _Audit(),
            "apply": bool(apply),
            "yes": bool(yes),
            "ack_volume": bool(ack_volume),
            "ack_no_snapshot": bool(ack_no_snapshot),
        }

    def test_refuses_without_apply_yes_ack_volume_for_ads_reports_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            jobs_file = os.path.join(td, "jobs.json")
            with open(jobs_file, "w", encoding="utf-8") as f:
                json.dump([{"action": "ads.reports.run", "ad_account_id": "123", "body_file": "req.json"}], f)

            out_dir = os.path.join(td, "out")
            args = SimpleNamespace(file=jobs_file, out_dir=out_dir, limit=None)
            ctx = self._ctx(apply=False, yes=False, ack_volume=False)
            with self.assertRaises(RuntimeError) as e:
                jobs_cmd.cmd_jobs_run(args, ctx)
            self.assertIn("--apply", str(e.exception))
            self.assertIn("--yes", str(e.exception))
            self.assertIn("--ack-volume", str(e.exception))

    def test_remote_write_batch_requires_no_snapshot_ack_before_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            jobs_file = os.path.join(td, "jobs.json")
            with open(jobs_file, "w", encoding="utf-8") as f:
                json.dump(
                    [
                        {"action": "unknown.action", "foo": "bar"},
                        {"action": "ads.reports.run", "ad_account_id": "123", "body_file": "req.json"},
                    ],
                    f,
                )

            out_dir = os.path.join(td, "out")
            args = SimpleNamespace(file=jobs_file, out_dir=out_dir, limit=None)
            ctx = self._ctx(apply=True, yes=True, ack_volume=True)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                jobs_cmd.cmd_jobs_run(args, ctx)
            self.assertFalse(os.path.exists(out_dir))

    def test_deterministic_outputs_written(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            jobs_file = os.path.join(td, "jobs.json")
            with open(jobs_file, "w", encoding="utf-8") as f:
                json.dump([{"action": "unknown.action"}], f)

            out_dir = os.path.join(td, "out")
            args = SimpleNamespace(file=jobs_file, out_dir=out_dir, limit=None)
            ctx = self._ctx(apply=True, yes=True, ack_volume=True)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = jobs_cmd.cmd_jobs_run(args, ctx)
            self.assertEqual(rc, 1)

            payload = json.loads(buf.getvalue())
            self.assertIn("summary_path", payload)
            self.assertTrue(os.path.exists(payload["summary_path"]))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "receipts", "row-0001.json")))
