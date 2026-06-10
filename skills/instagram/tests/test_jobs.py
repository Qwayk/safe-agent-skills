from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from instagram_api_tool.commands.write_utils import build_write_plan, run_write_command
from instagram_api_tool.errors import SafetyError


class TestWriteUtils(unittest.TestCase):
    def _ctx(self, **overrides):
        ctx = {
            "cfg": SimpleNamespace(base_url="https://graph.instagram.com"),
            "tool": "instagram-api-tool",
            "tool_version": "0.1.0",
            "command_str": "instagram-api-tool media publish",
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
        }
        ctx.update(overrides)
        return ctx

    def test_dry_run_can_write_plan_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            out = run_write_command(
                ctx=self._ctx(plan_out=str(plan_path)),
                selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                command="media.publish",
                proposed_changes=[{"action": "publish_container"}],
                requires_yes=True,
                risk_level="high",
                execute=lambda: {"id": "ignored"},
            )
            self.assertTrue(out["ok"])
            self.assertTrue(out["dry_run"])
            self.assertEqual(out["plan_out"], str(plan_path))
            self.assertTrue(plan_path.exists())

    def test_dry_run_before_state_contract_requires_no_snapshot_ack(self) -> None:
        out = run_write_command(
            ctx=self._ctx(),
            selector={"kind": "media.publish", "creation_id": "17890000000000000"},
            command="media.publish",
            proposed_changes=[{"action": "publish_container"}],
            requires_yes=True,
            risk_level="high",
            execute=lambda: {"id": "ignored"},
        )
        before_state = out["plan"]["before_state"]
        self.assertTrue(before_state["required"])
        self.assertFalse(before_state["supported"])
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertEqual(out["plan"]["verification_plan"]["status"], "best_effort_after_apply")
        rollback = out["plan"]["rollback"]
        self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
        self.assertFalse(rollback["supported"])
        self.assertFalse(rollback["automatic_rollback"])
        self.assertIn("No built-in rollback", rollback["notes"])

    def test_apply_requires_yes_when_requested(self) -> None:
        with self.assertRaises(SafetyError):
            run_write_command(
                ctx=self._ctx(apply=True, yes=False),
                selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                command="media.publish",
                proposed_changes=[{"action": "publish_container"}],
                requires_yes=True,
                risk_level="high",
                execute=lambda: {"id": "ignored"},
            )

    def test_apply_requires_no_snapshot_ack_before_execute_or_receipt(self) -> None:
        calls: list[str] = []
        with tempfile.TemporaryDirectory() as d:
            receipt_path = Path(d) / "receipt.json"
            out = run_write_command(
                ctx=self._ctx(apply=True, yes=True, receipt_out=str(receipt_path)),
                selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                command="media.publish",
                proposed_changes=[{"action": "publish_container"}],
                requires_yes=True,
                risk_level="high",
                execute=lambda: calls.append("called"),
            )
            self.assertFalse(receipt_path.exists())
        self.assertTrue(out["ok"])
        self.assertTrue(out["refused"])
        self.assertEqual(calls, [])
        self.assertNotIn("receipt", out)
        rollback = out["plan"]["rollback"]
        self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
        self.assertFalse(rollback["supported"])
        self.assertIn("No built-in rollback", rollback["notes"])

    def test_apply_with_no_snapshot_ack_executes_and_writes_receipt(self) -> None:
        calls: list[str] = []
        with tempfile.TemporaryDirectory() as d:
            receipt_path = Path(d) / "receipt.json"
            out = run_write_command(
                ctx=self._ctx(apply=True, yes=True, ack_no_snapshot=True, receipt_out=str(receipt_path)),
                selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                command="media.publish",
                proposed_changes=[{"action": "publish_container"}],
                requires_yes=True,
                risk_level="high",
                execute=lambda: calls.append("called") or {"id": "17890000000000000"},
            )
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(out["ok"])
        self.assertFalse(out["dry_run"])
        self.assertEqual(calls, ["called"])
        self.assertEqual(out["receipt"]["write_result"], {"id": "17890000000000000"})
        self.assertTrue(out["receipt"]["no_snapshot_approval"]["acknowledged"])
        self.assertEqual(receipt["no_snapshot_approval"]["flag"], "--ack-no-snapshot")

    def test_apply_requires_ack_when_requested(self) -> None:
        with self.assertRaises(SafetyError):
            run_write_command(
                ctx=self._ctx(apply=True, yes=True, ack_irreversible=False),
                selector={"kind": "comments.delete", "comment_id": "18000000000000000"},
                command="comments.delete",
                proposed_changes=[{"action": "delete_comment"}],
                requires_yes=True,
                requires_ack=True,
                risk_level="high",
                execute=lambda: {"success": True},
            )

    def test_plan_in_rejects_wrong_selector(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan = build_write_plan(
                ctx=self._ctx(),
                command="media.publish",
                selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                proposed_changes=[{"action": "publish_container"}],
                risk_level="high",
            )
            bad_plan = deepcopy(plan)
            bad_plan["selector"] = {"kind": "media.publish", "creation_id": "DIFFERENT"}
            plan_path.write_text(
                json.dumps(bad_plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(SafetyError):
                run_write_command(
                    ctx=self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                    selector={"kind": "media.publish", "creation_id": "17890000000000000"},
                    command="media.publish",
                    proposed_changes=[{"action": "publish_container"}],
                    requires_yes=True,
                    risk_level="high",
                    execute=lambda: {"id": "ignored"},
                )
