from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from requests import ReadTimeout

from qdrant_cloud_api_tool.cli import main
from qdrant_cloud_api_tool.operations_v1 import OPERATIONS


def _argv_for_op(*, env_file: str, op, extra: list[str] | None = None) -> list[str]:
    argv: list[str] = ["--output", "json", "--env-file", env_file, op.domain, op.command_name]
    for _tpl, arg in op.path_params:
        argv.extend([f"--{arg.replace('_', '-')}", "dummy"])
    if extra:
        argv = extra + argv
    return argv


class TestPlanApplyGates(unittest.TestCase):
    def test_write_like_defaults_to_plan(self) -> None:
        # create-account is POST but should not call HTTP without --apply (plan-only).
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "account-v1", "create-account"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)

    def test_delete_requires_yes_ack_and_plan_in(self) -> None:
        delete_op = next(op for op in OPERATIONS if op.http_verb.upper() == "DELETE")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n", encoding="utf-8")

            # Missing --yes
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(_argv_for_op(env_file=str(env_path), op=delete_op, extra=["--apply"]))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("--yes", " ".join(payload.get("reasons") or []))

            # Missing --ack-irreversible
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(_argv_for_op(env_file=str(env_path), op=delete_op, extra=["--apply", "--yes"]))
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertIn("--ack-irreversible", " ".join(payload2.get("reasons") or []))

            # Missing --plan-in
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(_argv_for_op(env_file=str(env_path), op=delete_op, extra=["--apply", "--yes", "--ack-irreversible"]))
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["refused"])
            self.assertIn("--plan-in", " ".join(payload3.get("reasons") or []))

    def test_payment_requires_ack_spend_money_and_plan_in(self) -> None:
        payment_op = next(op for op in OPERATIONS if "payment" in op.domain.lower())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n", encoding="utf-8")

            # Missing --ack-spend-money
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(_argv_for_op(env_file=str(env_path), op=payment_op, extra=["--apply", "--yes"]))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-spend-money", " ".join(payload.get("reasons") or []))

            # Still requires plan-in when ack is present
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(_argv_for_op(env_file=str(env_path), op=payment_op, extra=["--apply", "--yes", "--ack-spend-money"]))
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertIn("--plan-in", " ".join(payload2.get("reasons") or []))

            # Provide a reviewed plan file to get past plan-in gate; then refusal should be about --live.
            plan_path = root / "plan.json"
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(_argv_for_op(env_file=str(env_path), op=payment_op, extra=["--plan-out", str(plan_path)]))
            self.assertEqual(rc3, 0)

            buf4 = io.StringIO()
            with redirect_stdout(buf4):
                rc4 = main(
                    _argv_for_op(
                        env_file=str(env_path),
                        op=payment_op,
                        extra=["--apply", "--yes", "--ack-spend-money", "--plan-in", str(plan_path)],
                    )
                )
            self.assertEqual(rc4, 0)
            payload4 = json.loads(buf4.getvalue())
            self.assertTrue(payload4["refused"])
            self.assertIn("--live", " ".join(payload4.get("reasons") or []))



class TestReviewedRequests(unittest.TestCase):
    restore = [
        "cluster-backup-v1", "restore-backup",
        "--account-id", "example-account", "--backup-id", "example-backup",
    ]

    def run_cli(self, root: Path, flags: list[str], command: list[str]) -> tuple[int, dict]:
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main([
                "--output", "json", "--env-file", str(root / "test.env"),
                "--no-artifacts", *flags, *command,
            ])
        return rc, json.loads(out.getvalue())

    def reply(self, status: int) -> Mock:
        response = Mock()
        response.status_code = status
        response.headers = {}
        response.content = b"{}"
        response.url = "https://api.cloud.qdrant.io/test"
        return response

    @patch.dict("os.environ", {}, clear=True)
    def test_saved_delete_cannot_change_target_key_or_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env_file = root / "test.env"
            env_file.write_text("QDRANT_CLOUD_API_KEY=test-key\n")
            body = root / "request.json"
            body.write_text('{"deleteBackups":false}')
            command = [
                "cluster-v1", "delete-cluster", "--account-id", "example-account",
                "--cluster-id", "example-cluster", "--request-json", str(body),
            ]
            plan = root / "plan.json"
            _, preview = self.run_cli(root, ["--plan-out", str(plan)], command)
            self.assertEqual("example-cluster", preview["plan"]["operation"]["path_params"]["cluster_id"])
            self.assertNotIn("test-key", plan.read_text())
            flags = ["--live", "--apply", "--yes", "--ack-irreversible", "--ack-no-snapshot", "--plan-in", str(plan)]
            with patch("qdrant_cloud_api_tool.http.requests.Session.request", return_value=self.reply(204)) as send:
                changed_target = [*command[:5], "other-cluster", *command[6:]]
                _, result = self.run_cli(root, flags, changed_target)
                self.assertIn("target changed", result["reasons"][0])

                env_file.write_text("QDRANT_CLOUD_API_KEY=other-key\n")
                _, result = self.run_cli(root, flags, command)
                self.assertIn("API key", result["reasons"][0])

                env_file.write_text("QDRANT_CLOUD_API_KEY=test-key\n")
                body.write_text('{"deleteBackups":true}')
                _, result = self.run_cli(root, flags, command)
                self.assertIn("request changed", result["reasons"][0])
                send.assert_not_called()

                body.write_text('{"deleteBackups":false}')
                _, result = self.run_cli(root, flags, command)
                self.assertTrue(result["ok"])
                send.assert_called_once()

    @patch.dict("os.environ", {"QDRANT_CLOUD_API_KEY": "test-key"}, clear=True)
    def test_restore_needs_plan_irreversible_and_spend_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "plan.json"
            _, preview = self.run_cli(root, ["--plan-out", str(plan)], self.restore)
            self.assertEqual("restore_history", preview["plan"]["verification_plan"]["type"])
            flags = ["--live", "--apply", "--yes"]
            with patch("qdrant_cloud_api_tool.http.requests.Session.request", return_value=self.reply(202)) as send:
                for extras, expected in (
                    (["--plan-in", str(plan), "--ack-spend-money"], "--ack-irreversible"),
                    (["--plan-in", str(plan), "--ack-irreversible"], "--ack-spend-money"),
                    (["--ack-irreversible", "--ack-spend-money"], "--plan-in"),
                ):
                    _, result = self.run_cli(root, flags + extras, self.restore)
                    self.assertIn(expected, result["reasons"][0])
                send.assert_not_called()
                code, result = self.run_cli(root, [
                    *flags, "--ack-irreversible", "--ack-spend-money", "--plan-in", str(plan),
                ], self.restore)
                self.assertEqual(0, code)
                send.assert_called_once()
                verification = result["receipt"]["verification"]
                self.assertIsNone(verification["ok"])
                self.assertIn("list-backup-restores", verification["command"])
                self.assertEqual("example-backup", verification["backup_id"])

    @patch.dict("os.environ", {"QDRANT_CLOUD_API_KEY": "test-key"}, clear=True)
    def test_failed_restore_sends_only_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "plan.json"
            self.run_cli(root, ["--plan-out", str(plan)], self.restore)
            flags = [
                "--live", "--apply", "--yes", "--ack-irreversible",
                "--ack-spend-money", "--plan-in", str(plan),
            ]
            for reply in (self.reply(503), self.reply(307), ReadTimeout()):
                with patch("qdrant_cloud_api_tool.http.requests.Session.request", side_effect=[reply]) as send:
                    rc, result = self.run_cli(root, flags, self.restore)
                    self.assertEqual(1, rc)
                    send.assert_called_once()
                    self.assertFalse(send.call_args.kwargs["allow_redirects"])
                    self.assertIn("list-backup-restores", result["receipt"]["verification"]["command"])

    @patch.dict("os.environ", {"QDRANT_CLOUD_API_KEY": "test-key"}, clear=True)
    def test_cluster_provisioning_cannot_run_without_spend_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "plan.json"
            command = ["cluster-v1", "create-cluster", "--cluster-account-id", "example-account"]
            self.run_cli(root, ["--plan-out", str(plan)], command)
            with patch("qdrant_cloud_api_tool.http.requests.Session.request") as send:
                _, result = self.run_cli(root, [
                    "--live", "--apply", "--yes", "--ack-no-snapshot", "--plan-in", str(plan),
                ], command)
                self.assertIn("--ack-spend-money", result["reasons"][0])
                send.assert_not_called()

    @patch.dict("os.environ", {"QDRANT_CLOUD_API_KEY": "test-key"}, clear=True)
    def test_quote_is_a_read_and_keeps_the_request_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            body = root / "quote.json"
            body.write_text('{"regionId":"example"}')
            command = [
                "booking-v1", "get-quote", "--account-id", "example-account",
                "--request-json", str(body),
            ]
            with patch("qdrant_cloud_api_tool.http.requests.Session.request", return_value=self.reply(200)) as send:
                _, preview = self.run_cli(root, [], command)
                self.assertTrue(preview["dry_run"])
                send.assert_not_called()
                _, result = self.run_cli(root, ["--live"], command)
                self.assertTrue(result["read"])
                send.assert_called_once()
                self.assertEqual({"regionId": "example"}, send.call_args.kwargs["json"])
