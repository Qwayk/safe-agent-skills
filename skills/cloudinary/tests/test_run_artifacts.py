from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ._helpers import assert_blocked_before_state, run_cli, write_env


class TestRunArtifacts(unittest.TestCase):
    def test_write_plan_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            run_id = "2026-05-25T120000Z_cloudi1"
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--run-id",
                    run_id,
                    "operations",
                    "upload",
                    "text",
                    "--form-field",
                    "sample=value",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            assert_blocked_before_state(self, payload["plan"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            run_id = "2026-05-25T120500Z_cloudi2"
            _ = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--run-id",
                    run_id,
                    "operations",
                    "upload",
                    "text",
                    "--form-field",
                    "sample=value",
                ]
            )

            rc_list, payload_list = run_cli(
                ["--output", "json", "--env-file", str(env_path), "runs", "list", "--limit", "5"]
            )
            self.assertEqual(rc_list, 0)
            self.assertTrue(payload_list["ok"])
            self.assertGreaterEqual(payload_list["count"], 1)

            rc_show, payload_show = run_cli(
                ["--output", "json", "--env-file", str(env_path), "runs", "show", "--run-id", run_id]
            )
            self.assertEqual(rc_show, 0)
            self.assertTrue(payload_show["ok"])
            self.assertEqual(payload_show["run"]["run_id"], run_id)
            self.assertIsNotNone(payload_show["summary_md"])

    def test_refusal_still_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            run_id = "2026-05-25T121000Z_cloudi3"
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--run-id",
                        run_id,
                        "--apply",
                        "--yes",
                        "operations",
                        "upload",
                        "text",
                    "--form-field",
                    "sample=value",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            assert_blocked_before_state(self, payload["plan"])
            self.assertFalse((Path(payload["artifacts_dir"]) / "receipt.json").exists())
            self.assertTrue((Path(payload["artifacts_dir"]) / "summary.md").exists())
            self.assertIn(run_id, Path(payload["runs_index"]).read_text(encoding="utf-8"))
