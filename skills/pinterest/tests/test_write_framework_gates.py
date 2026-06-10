from __future__ import annotations

import unittest

from pinterest_api_tool.write_framework import build_plan, build_receipt, require_write_allowed


class TestWriteFrameworkGates(unittest.TestCase):
    def test_refuses_without_apply(self) -> None:
        ctx = {"apply": False, "yes": True}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx)
        self.assertIn("--apply", str(cm.exception))

    def test_refuses_without_yes(self) -> None:
        ctx = {"apply": True, "yes": False}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx)
        self.assertIn("--yes", str(cm.exception))

    def test_refuses_without_ack_irreversible(self) -> None:
        ctx = {"apply": True, "yes": True, "ack_irreversible": False}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx, acks_required=["ack-irreversible"])
        self.assertIn("--ack-irreversible", str(cm.exception))

    def test_refuses_without_ack_spend(self) -> None:
        ctx = {"apply": True, "yes": True, "ack_spend": False}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx, acks_required=["ack-spend"])
        self.assertIn("--ack-spend", str(cm.exception))

    def test_refuses_without_ack_volume(self) -> None:
        ctx = {"apply": True, "yes": True, "ack_volume": False}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx, acks_required=["ack-volume"])
        self.assertIn("--ack-volume", str(cm.exception))

    def test_confirmed_apply_requires_no_snapshot_ack(self) -> None:
        ctx = {"apply": True, "yes": True}
        with self.assertRaises(RuntimeError) as cm:
            require_write_allowed(ctx)
        self.assertIn("--ack-no-snapshot", str(cm.exception))

    def test_plan_and_receipt_shape(self) -> None:
        plan = build_plan(
            action="boards.delete",
            operations=[{"method": "GET", "path": "/boards/123"}],
            acks_required=["ack-volume", "ack-irreversible"],
            request={"board_id": "123"},
            warnings=["manual"],
        )
        receipt = build_receipt(
            action="boards.delete",
            changed=True,
            operations=[{"method": "GET", "path": "/boards/123"}],
            acks_required=["ack-volume", "ack-irreversible"],
            request={"board_id": "123"},
            before={"id": "123"},
            write_result={"deleted": True},
            after={"status": 404},
            warnings=[],
        )

        self.assertEqual(
            ["--apply", "--yes"],
            plan["apply_requires"],
            "plan should keep current apply flag contract",
        )
        self.assertEqual(
            ["--apply", "--yes"],
            receipt["apply_requires"],
            "receipt should keep current apply flag contract",
        )
        self.assertEqual(plan["acks_required"], ["ack-irreversible", "ack-volume"])
        self.assertEqual(receipt["acks_required"], ["ack-irreversible", "ack-volume"])
        self.assertTrue(plan["dry_run"])
        self.assertFalse(receipt["dry_run"])
        self.assertTrue(receipt["changed"])
        self.assertIn("before", receipt)
        self.assertIn("after", receipt)
        self.assertIn("warnings", plan)
        self.assertEqual(plan["before_state"]["status"], "no_snapshot_available")
        self.assertEqual(plan["verification_plan"]["status"], "best_effort_after_apply")
        self.assertFalse(plan["rollback"]["supported"])
        self.assertEqual(plan["acks_required"], sorted(plan["acks_required"]))
