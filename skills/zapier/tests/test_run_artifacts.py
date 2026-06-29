from __future__ import annotations

import io
import json
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from pathlib import Path

from zapier_safe_agent_cli.cli import main
from zapier_safe_agent_cli.http import HttpResponse


class TestRunArtifacts(unittest.TestCase):
    def _write_env(self, path: Path) -> None:
        path.write_text(
            "\n".join(
                [
                    "ZAPIER_BASE_URL=https://api.zapier.com",
                    "ZAPIER_AI_ACTIONS_BASE_URL=https://actions.zapier.com",
                    "ZAPIER_TRIGGER_INBOX_BASE_URL=https://api.zapier.com",
                    "ZAPIER_ACCESS_TOKEN=token",
                    "ZAPIER_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def test_dry_run_operations_create_run_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env = root / ".env"
            self._write_env(env)

            run_id = "2026-06-29T120000Z_test"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "--plan-out",
                        str(root / "plan.json"),
                        "partner",
                        "post-zaps",
                        "--body-json",
                        '{"name":"plan"}',
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))

    def test_runs_list_and_show(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env = root / ".env"
            self._write_env(env)
            run_id = "2026-06-29T120500Z_list"

            with redirect_stdout(io.StringIO()):
                main(
                    [
                        "--env-file",
                        str(env),
                        "--run-id",
                        run_id,
                        "--output",
                        "json",
                        "partner",
                        "post-zaps",
                        "--body-json",
                        '{"name":"x"}',
                    ]
                )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc1 = main(["--env-file", str(env), "--output", "json", "runs", "list", "--limit", "5"])
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf.getvalue())
            self.assertTrue(payload1["ok"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--env-file", str(env), "--output", "json", "runs", "show", "--run-id", run_id])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])

    def test_private_body_values_are_redacted_in_artifacts_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env = root / ".env"
            self._write_env(env)

            secret = "PRIVATE_ACTION_PAYLOAD_SEED_123"
            body = {"name": "private-run-test", "details": {"secret_token": secret}}


            plan_run_id = "2026-06-29T125000Z_plan_redact"
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                plan_rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--run-id",
                        plan_run_id,
                        "--output",
                        "json",
                        "--plan-out",
                        str(root / "dryrun_plan.json"),
                        "partner",
                        "post-zaps",
                        "--body-json",
                        json.dumps(body),
                    ]
                )

            self.assertEqual(plan_rc, 0)
            plan_output = json.loads(buf_plan.getvalue())
            self.assertTrue(plan_output["dry_run"])
            plan_file = Path(plan_output["plan_out"])
            self.assertTrue(plan_file.exists())
            self.assertIn("<redacted-body-json>", str(plan_output.get("command", "")))
            self.assertNotIn(secret, buf_plan.getvalue())
            self.assertNotIn(secret, plan_file.read_text(encoding="utf-8"))

            summary = Path(plan_output["artifacts_dir"]) / "summary.md"
            self.assertNotIn(secret, summary.read_text(encoding="utf-8"))

            runs_index = Path(plan_output["runs_index"])
            self.assertTrue(runs_index.exists())
            plan_index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(plan_run_id, plan_index_text)
            self.assertNotIn(secret, plan_index_text)

            audit_file = Path(plan_output["artifacts_dir"]) / "audit.jsonl"
            self.assertTrue(audit_file.exists())
            audit_payload = audit_file.read_text(encoding="utf-8")
            self.assertNotIn(secret, audit_payload)

            with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                req.return_value = HttpResponse(
                    status=201,
                    headers={},
                    body=b'{"ok":true}',
                    url="https://api.zapier.com/v2/zaps",
                )
                run_id = "2026-06-29T125100Z_apply_redact"
                buf = io.StringIO()
                with redirect_stdout(buf):
                    apply_rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--run-id",
                            run_id,
                            "--output",
                            "json",
                            "--apply",
                            "--plan-in",
                            str(plan_file),
                            "--yes",
                            "partner",
                            "post-zaps",
                            "--body-json",
                            json.dumps(body),
                        ]
                    )

            self.assertEqual(apply_rc, 0)
            req.assert_called_once()
            apply_output = json.loads(buf.getvalue())
            self.assertTrue(apply_output["ok"])
            self.assertNotIn(secret, buf.getvalue())
            self.assertNotIn("<body-json>", str(apply_output.get("command", "")))
            self.assertIn("<redacted-body-json>", str(apply_output.get("command", "")))

            receipt_file = Path(apply_output["receipt_out"])
            self.assertTrue(receipt_file.exists())
            self.assertNotIn(secret, receipt_file.read_text(encoding="utf-8"))

            apply_summary = Path(apply_output["artifacts_dir"]) / "summary.md"
            self.assertNotIn(secret, apply_summary.read_text(encoding="utf-8"))

            apply_index_text = Path(apply_output["runs_index"]).read_text(encoding="utf-8")
            self.assertIn(run_id, apply_index_text)
            self.assertNotIn(secret, apply_index_text)

            apply_audit_payload = (Path(apply_output["artifacts_dir"]) / "audit.jsonl").read_text(encoding="utf-8")
            self.assertNotIn(secret, apply_audit_payload)

            for line in apply_audit_payload.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self.assertIn("event", row)
                self.assertIn("payload", row)

            for line in audit_payload.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self.assertIn("event", row)
                self.assertIn("payload", row)
