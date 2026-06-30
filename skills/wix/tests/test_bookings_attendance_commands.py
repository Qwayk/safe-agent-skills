from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_attendance
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsAttendanceParser(unittest.TestCase):
    def test_parser_recognizes_attendance_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-attendance", "get", "--attendance-id", "att-1"])
        self.assertEqual(read_args.bookings_attendance_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_attendance.cmd_bookings_attendance_get)

        write_args = parser.parse_args(["bookings-attendance", "set", "--attendance-json", '{"attendance":{"status":"ATTENDED"}}'])
        self.assertEqual(write_args.bookings_attendance_cmd, "set")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_attendance.cmd_bookings_attendance_set)

        expected = {"get", "query", "count", "set", "bulk-set", "delete", "bulk-delete"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-attendance"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsAttendanceCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.bookings_attendance.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_attendance.resolve_auth_mode")
    def test_get_uses_official_path(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"attendance": {"id": "att-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_attendance.cmd_bookings_attendance_get(SimpleNamespace(attendance_id="att-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-attendance.get")
        self.assertEqual(payload["request"]["path"], "/bookings/bookings-attendance/att-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/bookings/bookings-attendance/att-1"))

    @patch("wix_safe_agent_cli.commands.bookings_attendance.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_attendance.resolve_auth_mode")
    def test_query_and_count_normalize_bodies(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"attendance": []})

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_attendance.cmd_bookings_attendance_query(
                SimpleNamespace(query_json='{"filter":{"bookingId":{"$eq":"booking-1"}}}'),
                self._ctx(),
            )
        query_payload = json.loads(query_buf.getvalue())

        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_attendance.cmd_bookings_attendance_count(
                SimpleNamespace(filter_json='{"status":"ATTENDED"}'),
                self._ctx(),
            )
        count_payload = json.loads(count_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/bookings/bookings-attendance/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"bookingId": {"$eq": "booking-1"}}}})
        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/bookings/bookings-attendance/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"status": "ATTENDED"}})

    def test_set_and_bulk_set_build_reviewed_plans(self) -> None:
        set_buf = io.StringIO()
        with redirect_stdout(set_buf):
            rc_set = bookings_attendance.cmd_bookings_attendance_set(
                SimpleNamespace(attendance_json='{"attendance":{"bookingId":"booking-1","sessionId":"session-1","status":"ATTENDED"}}'),
                self._ctx(),
            )
        set_payload = json.loads(set_buf.getvalue())

        bulk_buf = io.StringIO()
        with redirect_stdout(bulk_buf):
            rc_bulk = bookings_attendance.cmd_bookings_attendance_bulk_set(
                SimpleNamespace(attendance_json='{"attendanceDetails":[{"bookingId":"booking-1","sessionId":"session-1","status":"ATTENDED"}]}'),
                self._ctx(),
            )
        bulk_payload = json.loads(bulk_buf.getvalue())

        self.assertEqual(rc_set, 0)
        self.assertTrue(set_payload["dry_run"])
        self.assertEqual(set_payload["plan"]["request"]["path"], "/bookings/bookings-attendance/set")
        self.assertEqual(rc_bulk, 0)
        self.assertTrue(bulk_payload["dry_run"])
        self.assertEqual(bulk_payload["plan"]["request"]["path"], "/bookings/v2/bulk/attendance/set")

    def test_delete_and_bulk_delete_require_irreversible_ack(self) -> None:
        delete_buf = io.StringIO()
        with redirect_stdout(delete_buf):
            rc_delete = bookings_attendance.cmd_bookings_attendance_delete(SimpleNamespace(attendance_id="att-1"), self._ctx())
        delete_payload = json.loads(delete_buf.getvalue())

        bulk_delete_buf = io.StringIO()
        with redirect_stdout(bulk_delete_buf):
            rc_bulk_delete = bookings_attendance.cmd_bookings_attendance_bulk_delete(
                SimpleNamespace(attendance_json='{"attendanceIds":["att-1","att-2"]}'),
                self._ctx(),
            )
        bulk_delete_payload = json.loads(bulk_delete_buf.getvalue())

        self.assertEqual(rc_delete, 0)
        self.assertEqual(delete_payload["plan"]["request"]["path"], "/bookings/bookings-attendance/att-1")
        self.assertIn("apply also requires --ack-irreversible", delete_payload["plan"]["preconditions"])
        self.assertEqual(rc_bulk_delete, 0)
        self.assertEqual(bulk_delete_payload["plan"]["request"]["path"], "/bookings/v2/bulk/attendance/delete")
        self.assertIn("apply also requires --ack-irreversible", bulk_delete_payload["plan"]["preconditions"])

    def test_empty_attendance_id_is_rejected_before_http(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_attendance.cmd_bookings_attendance_get(SimpleNamespace(attendance_id=" "), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("attendance-id cannot be empty", payload["error"])


if __name__ == "__main__":
    unittest.main()
