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


def _api_response(*, status: int, path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestScheduleTimes(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, employee_id: str = "E-100", date: str = "2026-06-15") -> None:
        path.write_text(
            json.dumps(
                {
                    "ScheduleTime": {
                        "EmployeeId": employee_id,
                        "Date": date,
                        "Hours": "8",
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_schedule_times_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/scheduletimes/E-100/2026-06-15",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"ScheduleTime": {"EmployeeId": "E-100", "Date": "2026-06-15"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "schedule-times",
                            "get",
                            "--employee-id",
                            "E-100",
                            "--date",
                            "2026-06-15",
                        ]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/scheduletimes/E-100/2026-06-15")

    def test_schedule_times_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "payload.json"
            self._make_payload_file(payload_path, employee_id="E-101")
            rc, payload = self._run(
                env_path=env_path,
                args=["schedule-times", "update", "--employee-id", "E-100", "--date", "2026-06-15", "--json-file", str(payload_path)],
            )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("ScheduleTime.EmployeeId", payload["error"])

    def test_schedule_times_update_and_reset_day_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "payload.json"
            self._make_payload_file(payload_path)
            with patch("fortnox_api_tool.commands.schedule_times.request_json") as request_json:
                rc, update_plan_payload = self._run(
                    env_path=env_path,
                    args=["schedule-times", "update", "--employee-id", "E-100", "--date", "2026-06-15", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                update_plan_path = Path(td) / "update-plan.json"
                update_plan_path.write_text(json.dumps(self._plan_from_output(update_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=200, path="/scheduletimes/E-100/2026-06-15", body={"ScheduleTime": {"EmployeeId": "E-100", "Date": "2026-06-15"}}),
                    _api_response(status=200, path="/scheduletimes/E-100/2026-06-15", body={"ScheduleTime": {"EmployeeId": "E-100", "Date": "2026-06-15"}}),
                ]
                rc_update_apply, update_apply = self._run(
                    env_path=env_path,
                    args=[
                        "schedule-times",
                        "update",
                        "--employee-id",
                        "E-100",
                        "--date",
                        "2026-06-15",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(update_plan_path),
                    ],
                )
                self.assertEqual(rc_update_apply, 0)
                self.assertTrue(update_apply["ok"])

                request_json.reset_mock()
                rc, reset_plan_payload = self._run(
                    env_path=env_path,
                    args=["schedule-times", "reset-day", "--employee-id", "E-100", "--date", "2026-06-15", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                reset_plan_path = Path(td) / "reset-plan.json"
                reset_plan_path.write_text(json.dumps(self._plan_from_output(reset_plan_payload), indent=2), encoding="utf-8")
                request_json.side_effect = [
                    _api_response(status=200, path="/scheduletimes/E-100/2026-06-15/resetday", body={"ScheduleTime": {"EmployeeId": "E-100", "Date": "2026-06-15"}}),
                    _api_response(status=200, path="/scheduletimes/E-100/2026-06-15", body={"ScheduleTime": {"EmployeeId": "E-100", "Date": "2026-06-15"}}),
                ]
                rc_reset_apply, reset_apply = self._run(
                    env_path=env_path,
                    args=[
                        "schedule-times",
                        "reset-day",
                        "--employee-id",
                        "E-100",
                        "--date",
                        "2026-06-15",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(reset_plan_path),
                    ],
                )
                self.assertEqual(rc_reset_apply, 0)
                self.assertTrue(reset_apply["ok"])
