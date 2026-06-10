from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text("WOOCOMMERCE_STORE_URL=https://shop.example.com\n", encoding="utf-8")
        return env_path

    def test_dry_run_write_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            run_id = "2026-05-25T010203Z_abc123"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)
            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            runs_index = Path(payload["runs_index"])
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            run_id = "2026-05-25T040506Z_runs01"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )

            buffer2 = io.StringIO()
            with redirect_stdout(buffer2):
                rc2 = main(["--env-file", str(env_path), "--output", "json", "runs", "list", "--limit", "5"])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buffer2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

            buffer3 = io.StringIO()
            with redirect_stdout(buffer3):
                rc3 = main(["--env-file", str(env_path), "--output", "json", "runs", "show", "--run-id", run_id])
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buffer3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertEqual(payload3["run"]["run_id"], run_id)
            self.assertIn("Run summary", payload3["summary_md"])

    def test_apply_without_plan_in_refuses_and_keeps_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            run_id = "2026-05-25T070809Z_refuse1"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "--apply",
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertIn(run_id, Path(payload["runs_index"]).read_text(encoding="utf-8"))
