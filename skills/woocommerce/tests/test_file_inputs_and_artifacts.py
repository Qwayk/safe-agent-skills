from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestFileInputsAndArtifacts(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text("WOOCOMMERCE_STORE_URL=https://shop.example.com\n", encoding="utf-8")
        return env_path

    def test_body_file_and_params_file_are_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            body_path = root / "body.json"
            params_path = root / "params.json"
            plan_path = root / "plan.json"
            body_path.write_text(
                '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                encoding="utf-8",
            )
            params_path.write_text('{"search":"coupon","page":2}', encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "coupons",
                        "create",
                        "--body-file",
                        str(body_path),
                        "--params-file",
                        str(params_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            self.assertEqual(payload["plan"]["request"]["query"]["search"], "coupon")
            self.assertEqual(payload["plan"]["request"]["query"]["page"], 2)
            self.assertEqual(payload["plan"]["request"]["body"]["code"], "SAVE10")

    def test_artifacts_dir_and_log_file_create_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            body_path = root / "body.json"
            body_path.write_text(
                '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                encoding="utf-8",
            )
            artifacts_dir = root / "run-artifacts"
            log_file = root / "run.jsonl"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--run-id",
                        "run-123",
                        "--artifacts-dir",
                        str(artifacts_dir),
                        "--log-file",
                        str(log_file),
                        "coupons",
                        "create",
                        "--body-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())

            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], "run-123")
            self.assertEqual(payload["artifacts_dir"], str(artifacts_dir.resolve()))
            self.assertEqual(payload["audit_log"], str((artifacts_dir / "audit.jsonl").resolve()))
            self.assertEqual(payload["audit_log_global"], str(log_file))

            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            self.assertTrue(log_file.exists())
            log_rows = log_file.read_text(encoding="utf-8").splitlines()
            self.assertTrue(any("operation.plan" in row for row in log_rows))

    def test_no_artifacts_disables_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--no-artifacts",
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
            self.assertIsNone(payload["run_id"])
            self.assertIsNone(payload["artifacts_dir"])
            self.assertEqual(payload["audit_log"], None)
            self.assertEqual(payload["audit_log_global"], None)
            self.assertFalse((root / ".state").exists())
