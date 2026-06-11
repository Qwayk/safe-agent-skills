from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

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

