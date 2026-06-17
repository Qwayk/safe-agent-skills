from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _api_response(*, status: int, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestAttendanceTransactions(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text)
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        return json.loads(Path(payload["plan_out"]).read_text(encoding="utf-8"))

    def _make_payload_file(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "AttendanceTransaction": {
                        "EmployeeId": "E-100",
                        "Date": "2026-06-15",
                        "CauseCode": "TID",
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_attendance_transactions_reads_are_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            for args, expected_path, body in [
                (["attendance-transactions", "list"], "/attendancetransactions", {"AttendanceTransactions": []}),
                (["attendance-transactions", "get", "--id", "t-1"], "/attendancetransactions/t-1", {"AttendanceTransaction": {"id": "t-1"}}),
                (
                    ["attendance-transactions", "get-by-employee-date-code", "--employee-id", "E-100", "--date", "2026-06-15", "--code", "TID"],
                    "/attendancetransactions/E-100/2026-06-15/TID",
                    {"AttendanceTransactions": []},
                ),
            ]:
                buf = io.StringIO()
                with patch(
                    "fortnox_api_tool.commands.accounting_reads.get_json",
                    return_value={
                        "status": 200,
                        "url": f"https://api.fortnox.se/3{expected_path}",
                        "token_source": "env",
                        "token_expired": None,
                        "body": body,
                    },
                ):
                    with redirect_stdout(buf):
                        rc = main(["--output", "json", "--env-file", str(env_path), *args])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertEqual(payload["path"], expected_path)

    def test_attendance_transactions_create_wrapper_validation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "bad.json"
            payload_path.write_text(json.dumps({"EmployeeId": "E-100"}, indent=2), encoding="utf-8")
            rc, payload = self._run(
                env_path=env_path,
                args=["attendance-transactions", "create", "--json-file", str(payload_path)],
            )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_attendance_transactions_create_update_and_delete_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "payload.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.attendance_transactions.request_json") as request_json:
                rc, create_plan_payload = self._run(
                    env_path=env_path,
                    args=["attendance-transactions", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                create_plan = self._plan_from_output(create_plan_payload)
                create_plan_path = Path(td) / "create-plan.json"
                create_plan_path.write_text(json.dumps(create_plan, indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=201, path="/attendancetransactions", body={"AttendanceTransaction": {"id": "t-1"}}),
                    _api_response(status=200, path="/attendancetransactions/t-1", body={"AttendanceTransaction": {"id": "t-1"}}),
                ]
                rc_create_apply, create_apply = self._run(
                    env_path=env_path,
                    args=["attendance-transactions", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(create_plan_path)],
                )
                self.assertEqual(rc_create_apply, 0)
                self.assertTrue(create_apply["ok"])

                request_json.reset_mock()
                rc, update_plan_payload = self._run(
                    env_path=env_path,
                    args=["attendance-transactions", "update", "--id", "t-1", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                update_plan_path = Path(td) / "update-plan.json"
                update_plan_path.write_text(json.dumps(self._plan_from_output(update_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=200, path="/attendancetransactions/t-1", body={"AttendanceTransaction": {"id": "t-1"}}),
                    _api_response(status=200, path="/attendancetransactions/t-1", body={"AttendanceTransaction": {"id": "t-1"}}),
                ]
                rc_update_apply, update_apply = self._run(
                    env_path=env_path,
                    args=["attendance-transactions", "update", "--id", "t-1", "--json-file", str(payload_path), "--apply", "--plan-in", str(update_plan_path)],
                )
                self.assertEqual(rc_update_apply, 0)
                self.assertTrue(update_apply["ok"])

                request_json.reset_mock()
                rc, delete_plan_payload = self._run(
                    env_path=env_path,
                    args=["attendance-transactions", "delete", "--id", "t-1"],
                )
                self.assertEqual(rc, 0)
                delete_plan_path = Path(td) / "delete-plan.json"
                delete_plan_path.write_text(json.dumps(self._plan_from_output(delete_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=204, path="/attendancetransactions/t-1", body=None),
                    RuntimeError("HTTP 404 for GET /attendancetransactions/t-1"),
                ]
                rc_delete_apply, delete_apply = self._run(
                    env_path=env_path,
                    args=[
                        "attendance-transactions",
                        "delete",
                        "--id",
                        "t-1",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(delete_plan_path),
                    ],
                )
                self.assertEqual(rc_delete_apply, 0)
                self.assertTrue(delete_apply["ok"])
