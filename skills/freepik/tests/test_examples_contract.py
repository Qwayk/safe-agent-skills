from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestExamplesContract(unittest.TestCase):
    def test_plan_example_matches_current_no_snapshot_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "docs" / "examples" / "plan.example.json").read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        before_state = payload["plan"]["before_state"]
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertEqual(before_state["approval_required"], "--ack-no-snapshot")
        self.assertEqual(payload["plan"]["verification_plan"]["status"], "best_effort_after_apply")

    def test_receipt_example_matches_current_approved_apply_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "docs" / "examples" / "receipt.example.json").read_text(encoding="utf-8"))

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["no_snapshot_approval"]["acknowledged"])
        self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
        self.assertEqual(payload["verification"]["mode"], "download-and-inventory")
        self.assertEqual(payload["rows"][0]["file_name"], "123456--file.jpg")
