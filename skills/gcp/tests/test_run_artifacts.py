from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gcp_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def _write_delete_input(self, root: Path) -> Path:
        input_path = root / "input.json"
        input_path.write_text(
            json.dumps(
                {
                    "path": {
                        "project": "proj-a",
                        "zone": "us-central1-a",
                        "instance": "instance-a",
                    }
                }
            ),
            encoding="utf-8",
        )
        return input_path

    def test_generated_write_plan_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = self._write_delete_input(root)
            run_id = "2026-01-19T120000Z_deadbe"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "compute",
                        "instances-delete",
                        "--input-json",
                        str(input_path),
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            self.assertFalse(Path(payload["artifacts_dir"]).is_absolute())
            self.assertFalse(Path(payload["runs_index"]).is_absolute())
            self.assertFalse(Path(payload["audit_log"]).is_absolute())

            artifacts_dir = root / payload["artifacts_dir"]
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = root / payload["runs_index"]
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
            row = json.loads(runs_index.read_text(encoding="utf-8").splitlines()[-1])
            self.assertFalse(Path(row["artifacts_dir"]).is_absolute())
            summary_text = (artifacts_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn(".state/runs/index.jsonl", summary_text)
            self.assertNotIn(str(root), summary_text)

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = self._write_delete_input(root)
            run_id = "2026-01-19T120500Z_c0ffee"

            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "compute",
                        "instances-delete",
                        "--input-json",
                        str(input_path),
                    ]
                )

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
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = self._write_delete_input(root)
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
                        "compute",
                        "instances-delete",
                        "--input-json",
                        str(input_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            self.assertFalse(Path(payload["artifacts_dir"]).is_absolute())
            self.assertFalse(Path(payload["runs_index"]).is_absolute())
            artifacts_dir = root / payload["artifacts_dir"]
            self.assertTrue((artifacts_dir / "summary.md").exists())
            runs_index = root / payload["runs_index"]
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_equals_style_path_args_are_shortened_in_command_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = self._write_delete_input(root)
            run_id = "2026-01-19T121500Z_eqpath"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        f"--env-file={env_path}",
                        "--run-id",
                        run_id,
                        "compute",
                        "instances-delete",
                        f"--input-json={input_path}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            artifacts_dir = root / payload["artifacts_dir"]
            summary_text = (artifacts_dir / "summary.md").read_text(encoding="utf-8")
            plan_text = (artifacts_dir / "plan.json").read_text(encoding="utf-8")
            self.assertIn("--env-file=.env", summary_text)
            self.assertIn("--input-json=input.json", summary_text)
            self.assertNotIn(str(root), summary_text)
            self.assertNotIn(str(root), plan_text)
