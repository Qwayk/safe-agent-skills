from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestAbsenceTransactions(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        plan_out = payload.get("plan_out") or payload.get("plan_path")
        self.assertTrue(plan_out)
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _make_payload_file(
        self,
        path: Path,
        *,
        employee_id: str = "E-100",
        date: str = "2026-06-15",
        code: str = "SEM",
    ) -> None:
        payload = {
            "AbsenceTransaction": {
                "EmployeeId": employee_id,
                "Date": date,
                "CauseCode": code,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_absence_transactions_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/absencetransactions",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"AbsenceTransactions": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "absence-transactions", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/absencetransactions")

    def test_absence_transactions_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/absencetransactions/a-1",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"AbsenceTransaction": {"id": "a-1"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        ["--output", "json", "--env-file", str(env_path), "absence-transactions", "get", "--id", "a-1"]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/absencetransactions/a-1")

    def test_absence_transactions_get_by_employee_date_code_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/absencetransactions/E-100/2026-06-15/SEM",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"AbsenceTransactions": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "absence-transactions",
                            "get-by-employee-date-code",
                            "--employee-id",
                            "E-100",
                            "--date",
                            "2026-06-15",
                            "--code",
                            "SEM",
                        ]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/absencetransactions/E-100/2026-06-15/SEM")

    def test_absence_transactions_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["absence-transactions", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_absence_transactions_create_rejects_missing_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"EmployeeId": "E-100"}, indent=2), encoding="utf-8")

            rc, payload = self._run(
                env_path=env_path,
                args=["absence-transactions", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("top-level AbsenceTransaction object", payload["error"])

    def test_absence_transactions_create_apply_verifies_by_response_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.absence_transactions.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["absence-transactions", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/absencetransactions", body={"AbsenceTransaction": {"id": "a-1"}}),
                    _api_response(status=200, path="/absencetransactions/a-1", body={"AbsenceTransaction": {"id": "a-1"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "absence-transactions",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/absencetransactions/a-1")

    def test_absence_transactions_update_apply_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.absence_transactions.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["absence-transactions", "update", "--id", "a-1", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=200, path="/absencetransactions/a-1", body={"AbsenceTransaction": {"id": "a-1"}}),
                    _api_response(status=200, path="/absencetransactions/a-1", body={"AbsenceTransaction": {"id": "a-1"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "absence-transactions",
                        "update",
                        "--id",
                        "a-1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])

    def test_absence_transactions_delete_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            rc, plan_payload = self._run(env_path=env_path, args=["absence-transactions", "delete", "--id", "a-1"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=["absence-transactions", "delete", "--id", "a-1", "--apply", "--plan-in", str(plan_path)],
            )
        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["refused"])
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_absence_transactions_delete_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.absence_transactions.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["absence-transactions", "delete", "--id", "a-1"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=204, path="/absencetransactions/a-1", body=None),
                    RuntimeError("HTTP 404 for GET /absencetransactions/a-1"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "absence-transactions",
                        "delete",
                        "--id",
                        "a-1",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
