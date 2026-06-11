from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qwayk_reddit_safe_agent_cli.cli import main


class TestApiCommands(unittest.TestCase):
    def test_api_mod_conversation_id_path_param_is_filled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "api", "get-api-mod-conversations-conversation-id", "--path", "conversation_id=abc-123"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["operation"]["path_filled"], "/api/mod/conversations/abc-123")
            self.assertEqual(payload["plan"]["operation"]["url"], "https://oauth.reddit.com/api/mod/conversations/abc-123")

    def test_api_file_arg_validates_bad_file_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "api", "post-api-vote", "--file", "avatar"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Invalid file pair", payload["error"])

    def test_api_plan_env_fingerprint_rejects_plan_in_from_different_client(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path_a = Path(temp_dir) / ".env-a"
            env_path_b = Path(temp_dir) / ".env-b"
            plan_path = Path(temp_dir) / "plan.json"
            env_path_a.write_text("REDDIT_CLIENT_ID=client-a\n", encoding="utf-8")
            env_path_b.write_text("REDDIT_CLIENT_ID=client-b\n", encoding="utf-8")

            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc = main(["--output", "json", "--env-file", str(env_path_a), "--plan-out", str(plan_path), "api", "get-api-v1-me"])
            self.assertEqual(rc, 0)
            self.assertTrue(plan_path.exists())

            buf_apply = io.StringIO()
            with redirect_stdout(buf_apply):
                rc2 = main(["--output", "json", "--env-file", str(env_path_b), "--live", "--apply", "--plan-in", str(plan_path), "api", "get-api-v1-me"])
            self.assertEqual(rc2, 0)
            payload = json.loads(buf_apply.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("env_fingerprint", payload["reasons"][0])
    def test_api_ops_list_returns_inventory_rows(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "ops", "list", "--method", "GET", "--section", "account"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["count"], 0)
        for row in payload["ops"]:
            self.assertEqual(row["method"], "GET")
            self.assertEqual(row["section"], "account")

    def test_api_read_operation_live_without_credentials_is_safe_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--live", "api", "get-api-v1-me"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_api_write_operation_requires_apply(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "post-api-vote", "--body", "dir=1", "--body", "id=t3_abc123"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["operation"]["operation_command"], "post-api-vote")

    def test_api_write_plan_exposes_irreversible_contract(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "post-api-vote", "--body", "dir=1", "--body", "id=t3_abc123"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        plan = payload["plan"]
        self.assertEqual(plan["risk_level"], "high")
        self.assertEqual(plan["before_state"]["status"], "no_snapshot_available")
        self.assertFalse(plan["before_state"]["supported"])
        self.assertEqual(plan["verification_plan"]["status"], "best_effort_after_apply")
        self.assertEqual(plan["legacy_verification_plan"]["type"], "response-only")
        self.assertEqual(plan["rollback"]["mode"], "irreversible_and_clearly_labeled")
        self.assertFalse(plan["rollback"]["automatic_rollback"])
        self.assertFalse(plan["rollback"]["requires_ack_irreversible"])

    def test_api_write_apply_refuses_before_credentials_or_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            receipt_path = Path(temp_dir) / "receipt.json"
            env_path.write_text("", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--live",
                        "--apply",
                        "--receipt-out",
                        str(receipt_path),
                        "api",
                        "post-api-announcements-v1-read",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertFalse(receipt_path.exists())
