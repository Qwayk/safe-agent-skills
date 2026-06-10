from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from freepik_api_tool.commands.jobs import cmd_jobs_run
from freepik_api_tool.output import Output


class TestJobsRequireYes(unittest.TestCase):
    def test_requires_apply_and_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job = Path(d) / "jobs.csv"
            job.write_text("resource_id,format\n123,jpg\n", encoding="utf-8")

            a = SimpleNamespace(
                file=str(job),
                out_dir=str(Path(d) / "out"),
                inventory=str(Path(d) / "inv.csv"),
                limit=None,
            )

            ctx = {"apply": True, "yes": False}
            with self.assertRaises(RuntimeError):
                cmd_jobs_run(a, ctx)

    def test_emits_single_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job = Path(d) / "jobs.csv"
            job.write_text("resource_id,format\n123,jpg\n", encoding="utf-8")

            a = SimpleNamespace(
                file=str(job),
                out_dir=str(Path(d) / "out"),
                inventory=str(Path(d) / "inv.csv"),
                limit=None,
            )

            ctx = {"apply": True, "yes": True, "out": Output(mode="json")}
            with mock.patch(
                "freepik_api_tool.commands.jobs.run_download",
                return_value={"ok": True, "rows": [{"file_path": str(Path(d) / "out" / "x.jpg")}]},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    cmd_jobs_run(a, ctx)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["errors"], 0)
            recovery = payload["recovery"]
            self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(recovery["strategy"], "no_inverse")
            self.assertFalse(recovery["rollback_ready"])
            self.assertFalse(recovery["automatic_rollback"])
            self.assertIsInstance(recovery["backups"], list)
            self.assertIsInstance(recovery["snapshots"], list)
            self.assertIsNone(recovery["rollback_plan"])
            self.assertIn("Licensed batch downloads", recovery["restore_note"])

    def test_refused_download_row_makes_batch_summary_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job = Path(d) / "jobs.csv"
            job.write_text("resource_id,format\n123,jpg\n", encoding="utf-8")

            a = SimpleNamespace(
                file=str(job),
                out_dir=str(Path(d) / "out"),
                inventory=str(Path(d) / "inv.csv"),
                limit=None,
            )

            ctx = {"apply": True, "yes": True, "out": Output(mode="json")}
            refused = {
                "ok": False,
                "refused": True,
                "reasons": ["Refused: before-state missing"],
                "plan": {"before_state": {"status": "no_snapshot_available"}},
            }
            with mock.patch("freepik_api_tool.commands.jobs.run_download", return_value=refused):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_jobs_run(a, ctx)

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["errors"], 1)
            self.assertTrue(payload["results"][0]["refused"])
            self.assertEqual(payload["results"][0]["result"]["plan"]["before_state"]["status"], "no_snapshot_available")
