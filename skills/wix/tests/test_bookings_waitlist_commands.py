from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_waitlist
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsWaitlistParser(unittest.TestCase):
    def test_parser_recognizes_waitlist_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-waitlist", "list", "--waiting-resources", "session-1"])
        self.assertEqual(read_args.bookings_waitlist_cmd, "list")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_waitlist.cmd_bookings_waitlist_list)

        write_args = parser.parse_args(["bookings-waitlist", "register", "--request-json", '{"waitingResource":"session-1","formInfo":{}}', "--ack-event-session"])
        self.assertEqual(write_args.bookings_waitlist_cmd, "register")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_waitlist.cmd_bookings_waitlist_register)

        expected = {"list", "register", "leave", "book"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-waitlist"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsWaitlistCommands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_waitlist.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_waitlist.resolve_auth_mode")
    def test_list_uses_official_path_and_waiting_resources_query(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"list": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_waitlist.cmd_bookings_waitlist_list(SimpleNamespace(waiting_resources="session-1, session-2"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-waitlist.list")
        self.assertEqual(payload["request"]["path"], "/bookings/v1/waitlist/list")
        self.assertEqual(payload["request"]["params"], {"waitingResources": ["session-1", "session-2"]})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"waitingResources": ["session-1", "session-2"]})

    def test_register_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_waitlist.cmd_bookings_waitlist_register(
                SimpleNamespace(
                    request_json='{"waitingResource":"session-1","formInfo":{"paymentSelection":[{"rateLabel":"general","numberOfParticipants":1}]}}',
                    ack_event_session=True,
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v1/waitlist/register")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_leave_and_book_require_irreversible_ack(self) -> None:
        leave_buf = io.StringIO()
        with redirect_stdout(leave_buf):
            rc_leave = bookings_waitlist.cmd_bookings_waitlist_leave(
                SimpleNamespace(request_json='{"registrationId":"reg-1","waitingResource":"session-1"}', ack_event_session=True),
                self._ctx(),
            )
        leave_payload = json.loads(leave_buf.getvalue())

        book_buf = io.StringIO()
        with redirect_stdout(book_buf):
            rc_book = bookings_waitlist.cmd_bookings_waitlist_book(
                SimpleNamespace(request_json='{"registrationId":"reg-1"}', ack_event_session=True),
                self._ctx(),
            )
        book_payload = json.loads(book_buf.getvalue())

        self.assertEqual(rc_leave, 0)
        self.assertEqual(leave_payload["plan"]["request"]["path"], "/bookings/v1/waitlist/leave")
        self.assertIn("apply also requires --ack-irreversible", leave_payload["plan"]["preconditions"])
        self.assertEqual(rc_book, 0)
        self.assertEqual(book_payload["plan"]["request"]["path"], "/bookings/v1/waitlist/enroll")
        self.assertIn("apply also requires --ack-irreversible", book_payload["plan"]["preconditions"])

    def test_empty_waiting_resources_is_rejected_before_http(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_waitlist.cmd_bookings_waitlist_list(SimpleNamespace(waiting_resources=" "), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("waiting-resources cannot be empty", payload["error"])

    def test_waitlist_writes_require_event_session_ack(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_waitlist.cmd_bookings_waitlist_register(
                SimpleNamespace(request_json='{"waitingResource":"session-1","formInfo":{}}', ack_event_session=False),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("ack-event-session", payload["reasons"][0])


if __name__ == "__main__":
    unittest.main()
