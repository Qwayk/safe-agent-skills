from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestSavedExamples(unittest.TestCase):
    def test_discovery_example_lists_active_operations(self) -> None:
        folder = Path(__file__).resolve().parents[1] / "docs" / "examples" / "outputs"
        sample = json.loads((folder / "api_ops_list.json").read_text())
        self.assertEqual(sample["count"], len(sample["ops"]))
        self.assertEqual(sample["retired_count"], 23)
        self.assertTrue(all(row["path"].split("/")[1] not in {"assistants", "threads"} for row in sample["ops"]))

    def test_paid_plan_and_receipt_example_match(self) -> None:
        folder = Path(__file__).resolve().parents[1] / "docs" / "examples"
        plan = json.loads((folder / "plan_spend_money.example.json").read_text())
        receipt = json.loads((folder / "receipt.example.json").read_text())
        self.assertEqual(plan["plan_hash"], receipt["plan_hash"])
        self.assertEqual(plan["operation"], receipt["operation"])
        self.assertTrue(plan["classification"]["gates"]["ack_spend_money"])
        self.assertTrue(receipt["no_snapshot_approval"]["approved"])
