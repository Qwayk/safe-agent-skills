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


class TestSalaryTransactions(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, salary_row: int | None = None) -> None:
        payload: dict[str, Any] = {
            "SalaryTransaction": {
                "EmployeeId": "E-100",
                "Date": "2026-06-15",
                "SalaryCode": "100",
            }
        }
        if salary_row is not None:
            payload["SalaryTransaction"]["SalaryRow"] = salary_row
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_salary_transactions_reads_are_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            for args, expected_path, body in [
                (["salary-transactions", "list"], "/salarytransactions", {"SalaryTransactions": []}),
                (["salary-transactions", "get", "--salary-row", "10"], "/salarytransactions/10", {"SalaryTransaction": {"SalaryRow": 10}}),
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

    def test_salary_transactions_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "payload.json"
            self._make_payload_file(payload_path, salary_row=11)
            rc, payload = self._run(
                env_path=env_path,
                args=["salary-transactions", "update", "--salary-row", "10", "--json-file", str(payload_path)],
            )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("SalaryTransaction.SalaryRow", payload["error"])

    def test_salary_transactions_create_update_and_delete_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "payload.json"
            self._make_payload_file(payload_path)
            with patch("fortnox_api_tool.commands.salary_transactions.request_json") as request_json:
                rc, create_plan_payload = self._run(
                    env_path=env_path,
                    args=["salary-transactions", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                create_plan_path = Path(td) / "create-plan.json"
                create_plan_path.write_text(json.dumps(self._plan_from_output(create_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=201, path="/salarytransactions", body={"SalaryTransaction": {"SalaryRow": 10}}),
                    _api_response(status=200, path="/salarytransactions/10", body={"SalaryTransaction": {"SalaryRow": 10}}),
                ]
                rc_create_apply, create_apply = self._run(
                    env_path=env_path,
                    args=["salary-transactions", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(create_plan_path)],
                )
                self.assertEqual(rc_create_apply, 0)
                self.assertTrue(create_apply["ok"])

                self._make_payload_file(payload_path, salary_row=10)
                request_json.reset_mock()
                rc, update_plan_payload = self._run(
                    env_path=env_path,
                    args=["salary-transactions", "update", "--salary-row", "10", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                update_plan_path = Path(td) / "update-plan.json"
                update_plan_path.write_text(json.dumps(self._plan_from_output(update_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=200, path="/salarytransactions/10", body={"SalaryTransaction": {"SalaryRow": 10}}),
                    _api_response(status=200, path="/salarytransactions/10", body={"SalaryTransaction": {"SalaryRow": 10}}),
                ]
                rc_update_apply, update_apply = self._run(
                    env_path=env_path,
                    args=["salary-transactions", "update", "--salary-row", "10", "--json-file", str(payload_path), "--apply", "--plan-in", str(update_plan_path)],
                )
                self.assertEqual(rc_update_apply, 0)
                self.assertTrue(update_apply["ok"])

                request_json.reset_mock()
                rc, delete_plan_payload = self._run(
                    env_path=env_path,
                    args=["salary-transactions", "delete", "--salary-row", "10"],
                )
                self.assertEqual(rc, 0)
                delete_plan_path = Path(td) / "delete-plan.json"
                delete_plan_path.write_text(json.dumps(self._plan_from_output(delete_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=204, path="/salarytransactions/10", body=None),
                    RuntimeError("HTTP 404 for GET /salarytransactions/10"),
                ]
                rc_delete_apply, delete_apply = self._run(
                    env_path=env_path,
                    args=[
                        "salary-transactions",
                        "delete",
                        "--salary-row",
                        "10",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(delete_plan_path),
                    ],
                )
                self.assertEqual(rc_delete_apply, 0)
                self.assertTrue(delete_apply["ok"])
