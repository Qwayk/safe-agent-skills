from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from x_api_tool.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_demo_write_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "X_API_BASE_URL=http://example.invalid",
                        "X_API_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_deadbe"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--run-id", run_id, "demo", "write", "--selector", "x"])
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            rollback = payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertEqual(rollback["automatic_rollback"], False)
            self.assertIn("no built-in rollback", rollback["notes"].lower())
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)

    def test_demo_write_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("X_API_BASE_URL=http://example.invalid\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--apply", "demo", "write", "--selector", "x"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("reasons", payload)
            self.assertIn("Refused: demo write requires --apply --yes", payload["reasons"])

    def test_demo_write_apply_refuses_before_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("X_API_BASE_URL=http://example.invalid\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--apply", "--yes", "demo", "write", "--selector", "x"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertFalse(payload["dry_run"])
            rollback = payload["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertEqual(rollback["automatic_rollback"], False)
            self.assertIn("no built-in rollback", rollback["notes"].lower())
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertFalse((root / ".state" / "runs" / payload["run_id"] / "receipt.json").exists())

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("X_API_BASE_URL=http://example.invalid\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-01-19T120500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(["--env-file", str(env_path), "--run-id", run_id, "demo", "write", "--selector", "x"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(["--env-file", str(env_path), "runs", "show", "--run-id", run_id])
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertEqual(payload3["run"]["run_id"], run_id)
            self.assertIsNotNone(payload3["summary_md"])

    def test_refusal_still_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("X_API_BASE_URL=http://example.invalid\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            job_csv = root / "jobs.csv"
            job_csv.write_text("action\nwrite.ping\n", encoding="utf-8")

            run_id = "2026-01-19T121000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "jobs",
                        "run",
                        "--file",
                        str(job_csv),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "summary.md").exists())
            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
