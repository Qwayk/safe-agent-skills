from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestWriteSafety(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text("WOOCOMMERCE_STORE_URL=https://shop.example.com\n", encoding="utf-8")
        return env_path

    def _write_env_with_credentials(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "WOOCOMMERCE_STORE_URL=https://shop.example.com",
                    "WOOCOMMERCE_CONSUMER_KEY=dummy_key",
                    "WOOCOMMERCE_CONSUMER_SECRET=dummy_secret",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env_path

    def test_high_risk_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            plan_path = root / "delete-plan.json"

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
                        "products",
                        "delete",
                        "--id",
                        "123",
                        "--params-json",
                        '{"force": true}',
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_path.exists())

            buffer2 = io.StringIO()
            with redirect_stdout(buffer2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "products",
                        "delete",
                        "--id",
                        "123",
                        "--params-json",
                        '{"force": true}',
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buffer2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertIn("--yes", " ".join(payload2["reasons"]))

    def test_high_risk_apply_with_yes_refuses_before_provider_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            plan_path = root / "delete-plan.json"

            with redirect_stdout(io.StringIO()):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "products",
                        "delete",
                        "--id",
                        "123",
                        "--params-json",
                        '{"force": true}',
                    ]
                )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "products",
                        "delete",
                        "--id",
                        "123",
                        "--params-json",
                        '{"force": true}',
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("before-state snapshot", payload["reasons"][0])
            self.assertIn("ack-no-snapshot", payload["reasons"][0])

    def test_plan_rollback_note_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env_with_credentials(root)
            plan_path = root / "coupon-plan.json"

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
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )
            self.assertEqual(rc, 0)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertTrue(plan["before_state"]["required"])
            self.assertFalse(plan["before_state"]["supported"])
            self.assertEqual(plan["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")
            self.assertIn("No WooCommerce snapshots", plan["rollback"]["notes"])
            self.assertIn("provider backups", plan["rollback"]["notes"])
            self.assertIn("machine rollback plans", plan["rollback"]["notes"])

    def test_apply_refuses_before_provider_request_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env_with_credentials(root)
            plan_path = root / "coupon-plan.json"
            receipt_path = root / "coupon-receipt.json"

            with redirect_stdout(io.StringIO()):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )

            with patch("qwayk_woocommerce_safe_agent_cli.commands.operations.WooCommerceClient.request_json") as request_mock:
                buffer2 = io.StringIO()
                with redirect_stdout(buffer2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "coupons",
                            "create",
                            "--body-json",
                            '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                        ]
                    )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buffer2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertIn("before-state snapshot", payload2["reasons"][0])
            self.assertIn("ack-no-snapshot", payload2["reasons"][0])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(receipt_path.exists())
            request_mock.assert_not_called()

    def test_apply_refuses_when_plan_body_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = self._write_env(root)
            plan_path = root / "coupon-plan.json"

            with redirect_stdout(io.StringIO()):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE10","discount_type":"percent","amount":"10"}',
                    ]
                )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "coupons",
                        "create",
                        "--body-json",
                        '{"code":"SAVE20","discount_type":"percent","amount":"20"}',
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan body", " ".join(payload["reasons"]))
