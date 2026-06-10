from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qdrant_cloud_api_tool.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_write_like_operation_creates_run_folder_and_index(self) -> None:
        # Non-GET operations are write-capable and should create a run folder/index even in dry-run.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "QDRANT_CLOUD_API_BASE_URL=http://example.invalid",
                        "QDRANT_CLOUD_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_id = "2026-03-14T000000Z_deadbe"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--run-id", run_id, "account-v1", "create-account"])
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            self.assertEqual(payload["plan"]["safety"]["recovery"]["contract"], "no-recovery")
            self.assertTrue(payload["plan"]["safety"]["before_state"]["required"])
            self.assertFalse(payload["plan"]["safety"]["before_state"]["supported"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            plan_obj = json.loads((artifacts_dir / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan_obj["safety"]["recovery"]["contract"], "no-recovery")
            self.assertEqual(plan_obj["safety"]["before_state"]["status"], "no_snapshot_available")
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            run_id = "2026-03-14T000500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(["--env-file", str(env_path), "--run-id", run_id, "account-v1", "create-account"])

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
            env_path.write_text(
                "QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            run_id = "2026-03-14T001000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "account-v1",
                        "delete-account",
                        "--account-id",
                        "00000000-0000-0000-0000-000000000000",
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
