import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dynadot_api_tool.commands.api3 import cmd_api3_call
from dynadot_api_tool.commands.domains import cmd_domains_push
from dynadot_api_tool.commands.jobs import cmd_jobs_run
from dynadot_api_tool.config import Config
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.json_files import read_json_file
from dynadot_api_tool.output import Output
from dynadot_api_tool.audit_log import AuditLogger


class WriteRecoveryContractTests(unittest.TestCase):
    def _ctx(self, *, cfg: Config, apply: bool, yes: bool, plan_out=None, plan_in=None, receipt_out=None, api=None, command_str="dynadot-api-tool write") -> dict:
        return {
            "cfg": cfg,
            "out": Output(mode="json"),
            "audit": AuditLogger(path=None, enabled=False),
            "tool": "dynadot-api-tool",
            "tool_version": "0.5.0",
            "command_str": command_str,
            "timeout_s": 30.0,
            "verbose": False,
            "apply": apply,
            "yes": yes,
            "plan_out": plan_out,
            "plan_in": plan_in,
            "receipt_out": receipt_out,
            "ack_irreversible": False,
            "api": api,
        }

    def _assert_no_recovery(self, payload: dict) -> None:
        recovery = payload["recovery"]
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertEqual(recovery["strategy"], "no_inverse")
        self.assertFalse(recovery["rollback_ready"])
        self.assertEqual(recovery["backups"], [])
        self.assertEqual(recovery["snapshots"], [])
        self.assertIsNone(recovery["rollback_plan"])

    def _assert_before_state_blocked(self, payload: dict) -> None:
        before_state = payload["before_state"]
        self.assertTrue(before_state["required"])
        self.assertFalse(before_state["supported"])
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertIsNone(before_state["storage"])
        self.assertEqual(payload["verification_plan"]["type"], "best_effort_after_apply")

    def test_api3_plan_and_receipt_include_no_recovery_contract(self) -> None:
        class _Args:
            api3_command = "set_note"
            domain = "example.com"
            note = "hello"

        class _FakeApi:
            def __init__(self) -> None:
                self.calls = []

            def call(self, *, command: str, params=None) -> DynadotApiResult:
                params = dict(params or {})
                self.calls.append((command, params))
                if command == "set_note":
                    return DynadotApiResult(command=command, response={"Status": "success", "ResponseCode": "0"})
                if command == "domain_info":
                    return DynadotApiResult(command=command, response={"Status": "success", "ResponseCode": "0"})
                raise AssertionError(command)

        cfg = Config(base_url="http://example.invalid/api3.json", api_key="K", timeout_s=30.0)
        api = _FakeApi()

        with tempfile.TemporaryDirectory() as td:
            plan_path = str(Path(td) / "plan.json")
            receipt_path = str(Path(td) / "receipt.json")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_api3_call(
                    _Args(),
                    self._ctx(cfg=cfg, apply=False, yes=False, plan_out=plan_path, api=api, command_str="dynadot-api-tool api3 set-note --domain example.com --note hello"),
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self._assert_no_recovery(payload["plan"])
            self._assert_before_state_blocked(payload["plan"])
            plan_obj = read_json_file(plan_path)
            self._assert_no_recovery(plan_obj)
            self._assert_before_state_blocked(plan_obj)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_api3_call(
                    _Args(),
                    self._ctx(
                        cfg=cfg,
                        apply=True,
                        yes=True,
                        plan_in=plan_path,
                        receipt_out=receipt_path,
                        api=api,
                        command_str="dynadot-api-tool --apply --yes --plan-in plan.json api3 set-note --domain example.com --note hello",
                    ),
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(Path(receipt_path).exists())
            self._assert_before_state_blocked(payload2["plan"])
            self.assertEqual(api.calls, [])

    def test_jobs_plan_and_receipt_include_no_recovery_contract(self) -> None:
        cfg = Config(base_url="http://example.invalid/api3.json", api_key="K", timeout_s=30.0)

        class _Args:
            def __init__(self, file_path: str) -> None:
                self.file = file_path
                self.limit = None

        with tempfile.TemporaryDirectory() as td:
            job_file = Path(td) / "jobs.csv"
            with job_file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["action"])
                writer.writeheader()
                writer.writerow({"action": "write.ping"})

            plan_path = str(Path(td) / "plan.json")
            receipt_path = str(Path(td) / "receipt.json")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_jobs_run(
                    _Args(str(job_file)),
                    self._ctx(cfg=cfg, apply=False, yes=False, plan_out=plan_path, command_str="dynadot-api-tool jobs run --file jobs.csv"),
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self._assert_no_recovery(payload["plan"])
            self._assert_before_state_blocked(payload["plan"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_jobs_run(
                    _Args(str(job_file)),
                    self._ctx(
                        cfg=cfg,
                        apply=True,
                        yes=True,
                        plan_in=plan_path,
                        receipt_out=receipt_path,
                        command_str="dynadot-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv",
                    ),
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(Path(receipt_path).exists())
            self._assert_before_state_blocked(payload2["plan"])

    def test_domains_push_plan_and_receipt_include_no_recovery_contract(self) -> None:
        cfg = Config(base_url="http://example.invalid/api3.json", api_key="K", timeout_s=30.0)

        class _Args:
            def __init__(self, domains_file: str) -> None:
                self.to_username = "receiver_user"
                self.no_unlock = False
                self.sleep_between_batches_s = 0.0
                self.max_batches = None
                self.domain = None
                self.domains_file = domains_file
                self.resume_from_receipt = None

        class _FakeApi:
            def call(self, *, command: str, params=None) -> DynadotApiResult:
                self.last = (command, dict(params or {}))
                if command == "push":
                    return DynadotApiResult(command=command, response={"Status": "success", "ResponseCode": "0"})
                raise AssertionError(command)

        with tempfile.TemporaryDirectory() as td:
            domains_file = Path(td) / "domains.txt"
            domains_file.write_text("example.com\n", encoding="utf-8")
            plan_path = str(Path(td) / "plan.json")
            receipt_path = str(Path(td) / "receipt.json")
            api = _FakeApi()

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_push(
                    _Args(str(domains_file)),
                    self._ctx(cfg=cfg, apply=False, yes=False, plan_out=plan_path, api=api, command_str="dynadot-api-tool domains push --to-username receiver_user --domains-file domains.txt"),
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self._assert_no_recovery(payload["plan"])
            self._assert_before_state_blocked(payload["plan"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cmd_domains_push(
                    _Args(str(domains_file)),
                    self._ctx(
                        cfg=cfg,
                        apply=True,
                        yes=True,
                        plan_in=plan_path,
                        receipt_out=receipt_path,
                        api=api,
                        command_str="dynadot-api-tool --apply --yes --plan-in plan.json domains push --to-username receiver_user --domains-file domains.txt",
                    ),
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["refused"])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(Path(receipt_path).exists())
            self._assert_before_state_blocked(payload2["plan"])
            self.assertFalse(hasattr(api, "last"))
