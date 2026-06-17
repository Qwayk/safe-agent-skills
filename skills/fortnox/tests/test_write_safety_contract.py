from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main
from fortnox_api_tool.write_safety import normalize_plan, normalize_receipt


class TestWriteSafetyContract(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
        return env_path

    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        return rc, json.loads(buf.getvalue())

    def test_normalize_plan_adds_snapshot_and_recovery_fields(self) -> None:
        plan = normalize_plan(
            {
                "selector": {"kind": "unit", "value": "PCS"},
                "risk_level": "high",
                "proposed_changes": [{"field": "Description", "from": "Old", "to": "New"}],
                "verification_plan": {"type": "read-after-write"},
                "rollback": {"supported": False, "notes": "No rollback in current runtime."},
            }
        )
        self.assertEqual(plan["snapshot_status"], "no_snapshot_available")
        self.assertIn("recovery_notes", plan)
        self.assertIn("recovery", plan)
        self.assertIn("before_state", plan)

    def test_normalize_receipt_adds_snapshot_and_recovery_fields(self) -> None:
        plan = normalize_plan(
            {
                "selector": {"kind": "unit", "value": "PCS"},
                "risk_level": "medium",
                "proposed_changes": [{"field": "Description", "from": "Old", "to": "New"}],
                "verification_plan": {"type": "read-after-write"},
            }
        )
        receipt = normalize_receipt(
            {
                "selector": {"kind": "unit", "value": "PCS"},
                "changed": True,
                "verification": {"ok": True},
                "diff_applied": plan["proposed_changes"],
                "rollback_plan": None,
            },
            plan=plan,
        )
        self.assertEqual(receipt["snapshot_status"], "no_snapshot_available")
        self.assertIn("recovery_notes", receipt)
        self.assertIn("recovery", receipt)
        self.assertIn("before_state", receipt)

    def test_high_risk_apply_without_plan_in_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = self._write_env(root)

            with patch("fortnox_api_tool.api_runtime.HttpClient.request") as request:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "units",
                        "remove",
                        "--code",
                        "PCS",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", " ".join(payload["reasons"]))
        self.assertEqual(request.call_count, 0)

    def test_high_risk_no_snapshot_apply_without_ack_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = self._write_env(root)

            rc_plan, plan_payload = self._run(env_path=env_path, args=["units", "remove", "--code", "PCS"])
            self.assertEqual(rc_plan, 0)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan_payload["plan"], indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.api_runtime.HttpClient.request") as request:
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "units",
                        "remove",
                        "--code",
                        "PCS",
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["refused"])
        joined = " ".join(payload_apply["reasons"])
        self.assertIn("no before-state snapshot", joined)
        self.assertIn("--ack-no-snapshot", joined)
        self.assertEqual(request.call_count, 0)
