from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from stripe_api_tool.cli import main


def _write_env(tmpdir: str, *, api_key: str) -> str:
    p = Path(tmpdir) / ".env"
    p.write_text("\n".join([f"STRIPE_API_KEY={api_key}", "STRIPE_TIMEOUT_S=30"]) + "\n", encoding="utf-8")
    return str(p)


class TestRiskAndDriftRegressions(unittest.TestCase):
    def test_invoice_pay_is_money_moving_high_risk(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _write_env(td, api_key="sk_test_dummy_123")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "api",
                        "post-invoices-invoice-pay",
                        "--invoice",
                        "in_123",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            plan = payload.get("plan") or {}
            risk = plan.get("risk") or {}
            req = (risk.get("requirements") or {}) if isinstance(risk, dict) else {}
            self.assertEqual(risk.get("level"), "high")
            self.assertTrue(bool(req.get("ack_spend_money")))
            self.assertTrue(bool(req.get("yes")))
            self.assertTrue(bool(req.get("plan_in")))

    def test_plan_in_refuses_idempotency_drift_before_live_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _write_env(td, api_key="sk_test_dummy_123")
            plan_path = Path(td) / "plan.json"

            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "post-customers",
                        "--data",
                        "name=Alice",
                        "--idempotency-key",
                        "foo",
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            buf_apply = io.StringIO()
            with redirect_stdout(buf_apply):
                rc_apply = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "post-customers",
                        "--data",
                        "name=Alice",
                        "--idempotency-key",
                        "bar",
                    ]
                )
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf_apply.getvalue())
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("refused"))
            reason = " ".join(payload.get("reasons") or []).lower()
            self.assertIn("idempotency", reason)
            self.assertNotIn("--live", reason)

    def test_api_plan_marks_before_state_and_live_apply_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _write_env(td, api_key="sk_test_dummy_123")
            plan_path = Path(td) / "plan.json"
            receipt_path = Path(td) / "receipt.json"

            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "post-customers",
                        "--data",
                        "name=Alice",
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())
            plan_payload = json.loads(buf_plan.getvalue())
            plan = plan_payload.get("plan") or {}
            rollback = plan.get("rollback") or {}
            self.assertEqual(rollback.get("supported"), False)
            self.assertEqual(
                rollback.get("notes"),
                "No before-state snapshot is taken; no automatic rollback is available from this plan.",
            )
            before_state = plan.get("before_state") or {}
            self.assertTrue(before_state.get("required"))
            self.assertEqual(before_state.get("supported"), False)

            with patch("stripe_api_tool.commands_api._execute_live") as execute_live:
                buf_apply = io.StringIO()
                with redirect_stdout(buf_apply):
                    rc_apply = main(
                        [
                            "--output",
                            "json",
                        "--env-file",
                        env_file,
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "--receipt-out",
                        str(receipt_path),
                        "api",
                        "--live",
                        "post-customers",
                        "--data",
                        "name=Alice",
                        ]
                    )
            self.assertEqual(rc_apply, 0)
            self.assertFalse(receipt_path.exists())
            execute_live.assert_not_called()
            apply_payload = json.loads(buf_apply.getvalue())
            self.assertTrue(apply_payload.get("ok"))
            self.assertTrue(apply_payload.get("refused"))
            reason = " ".join(apply_payload.get("reasons") or [])
            self.assertIn("before-state", reason)
            self.assertIn("ack-no-snapshot", reason)
