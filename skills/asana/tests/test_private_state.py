from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from asana_safe_agent_cli.audit_log import AuditLogger
from asana_safe_agent_cli.commands.asana import cmd_api
from asana_safe_agent_cli.json_files import write_json_file

from .helpers import FakeClient, args, context, response


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


class TestPrivateStateFiles(unittest.TestCase):
    def _plan(self, td: str, *, plan_out: Path | None = None) -> tuple[Path, dict[str, object]]:
        ctx, out, _ = context(td, FakeClient([]))
        cmd_api(
            args(
                operation="create-task",
                data_json='{"data":{"name":"private task"}}',
                plan_out=str(plan_out) if plan_out else None,
            ),
            ctx,
        )
        path = Path(out.last["plan_out"])
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_default_and_custom_plans_and_signing_state_are_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            default_plan, _ = self._plan(td)
            custom_plan, _ = self._plan(td, plan_out=Path(td) / "custom" / "plan.json")
            state = Path(td) / ".state"
            key = state / "plan-signing.key"

            self.assertEqual(_mode(state), 0o700)
            self.assertEqual(_mode(state / "plans"), 0o700)
            self.assertEqual(_mode(default_plan), 0o600)
            self.assertEqual(_mode(custom_plan), 0o600)
            self.assertEqual(_mode(custom_plan.parent), 0o700)
            self.assertEqual(_mode(key), 0o600)

    def test_default_and_custom_receipts_are_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            for name, receipt_out in (
                ("default", None),
                ("custom", Path(td) / "custom" / "receipt.json"),
            ):
                with self.subTest(layout=name):
                    case_dir = Path(td) / name
                    case_dir.mkdir()
                    plan_path, plan = self._plan(str(case_dir))
                    apply_ctx, apply_out, _ = context(
                        str(case_dir), FakeClient([response(200, {"data": {"gid": "1"}})])
                    )
                    cmd_api(
                        args(
                            operation="create-task",
                            apply=True,
                            plan_in=str(plan_path),
                            approve=str(plan["plan_id"]),
                            acknowledge_no_snapshot=True,
                            receipt_out=str(receipt_out) if receipt_out else None,
                        ),
                        apply_ctx,
                    )
                    saved = Path(apply_out.last["receipt_out"])
                    self.assertEqual(_mode(saved), 0o600)
                    if receipt_out is None:
                        self.assertEqual(_mode(case_dir / ".state" / "receipts"), 0o700)

    def test_default_and_custom_audit_logs_are_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            for path in (
                Path(td) / ".state" / "runs" / "run-1" / "audit.jsonl",
                Path(td) / "custom" / "audit.jsonl",
            ):
                with self.subTest(path=path):
                    audit = AuditLogger(path=str(path), enabled=True)
                    audit.bind_context({"tool": "test"})
                    audit.write("test.event", {"value": "private"})
                    audit.close()
                    self.assertEqual(_mode(path), 0o600)
                    self.assertEqual(_mode(path.parent), 0o700)

    def test_atomic_json_replacement_never_widens_existing_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "existing.json"
            path.write_text('{"old":true}\n', encoding="utf-8")
            path.chmod(0o400)
            write_json_file(path, {"new": True})
            self.assertEqual(_mode(path), 0o400)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"new": True})


if __name__ == "__main__":
    unittest.main()
