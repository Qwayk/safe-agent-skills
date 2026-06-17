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


def _api_response(*, status: int, path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestEmployees(unittest.TestCase):
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
        first_name: str = "Ada",
        last_name: str = "Lovelace",
    ) -> None:
        payload = {
            "Employee": {
                "EmployeeId": employee_id,
                "FirstName": first_name,
                "LastName": last_name,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_employees_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/employees",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Employees": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "employees", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/employees")

    def test_employees_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/employees/E-100",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Employee": {"EmployeeId": "E-100"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "employees",
                            "get",
                            "--employee-id",
                            "E-100",
                        ]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/employees/E-100")

    def test_employees_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, employee_id="E-100")
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["employees", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_employees_create_rejects_missing_top_level_wrapper(self) -> None:
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
                args=["employees", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("top-level Employee object", payload["error"])

    def test_employees_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, employee_id="E-100")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {"Employee": {"EmployeeId": "E-100", "FirstName": "Updated"}},
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_employees_create_apply_performs_post_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, employee_id="E-100")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/employees", body={"Employee": {"EmployeeId": "E-100"}}),
                    _api_response(
                        status=200,
                        path="/employees/E-100",
                        body={"Employee": {"EmployeeId": "E-100"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/employees")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/employees/E-100")

    def test_employees_create_apply_uses_response_employee_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"Employee": {"FirstName": "Ada"}}, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/employees", body={"Employee": {"EmployeeId": "E-200"}}),
                    _api_response(status=200, path="/employees/E-200", body={"Employee": {"EmployeeId": "E-200"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/employees/E-200")

    def test_employees_create_apply_fails_without_employee_id_on_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"Employee": {"FirstName": "Ada"}}, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [_api_response(status=201, path="/employees", body={"Employee": {}})]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply["ok"])
        self.assertEqual(payload_apply["error_type"], "ValidationError")
        self.assertIn("EmployeeId", payload_apply["error"])

    def test_employees_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, employee_id="E-100")
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["employees", "update", "--employee-id", "E-100", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_employees_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, employee_id="E-200")

            rc, payload = self._run(
                env_path=env_path,
                args=["employees", "update", "--employee-id", "E-100", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Employee.EmployeeId", payload["error"])

    def test_employees_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, employee_id="E-100")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "update", "--employee-id", "E-100", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {"Employee": {"EmployeeId": "E-100", "FirstName": "Updated"}},
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "update",
                        "--employee-id",
                        "E-100",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_employees_update_apply_performs_put_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, employee_id="E-100")

            with patch("fortnox_api_tool.commands.employees.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["employees", "update", "--employee-id", "E-100", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/employees/E-100", body={"Employee": {"EmployeeId": "E-100"}}),
                    _api_response(status=200, path="/employees/E-100", body={"Employee": {"EmployeeId": "E-100"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "employees",
                        "update",
                        "--employee-id",
                        "E-100",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/employees/E-100")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/employees/E-100")

