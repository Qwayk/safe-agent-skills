from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_writer_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsWriterV2Parser(unittest.TestCase):
    def test_parser_recognizes_writer_v2_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-writer-v2", "get-multi-service", "--multi-service-booking-id", "ms-1"])
        self.assertEqual(read_args.bookings_writer_v2_cmd, "get-multi-service")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_writer_v2.cmd_bookings_writer_v2_get_multi_service)

        write_args = parser.parse_args(["bookings-writer-v2", "create", "--booking-json", '{"contactDetails":{"email":"a@example.com"}}'])
        self.assertEqual(write_args.bookings_writer_v2_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_writer_v2.cmd_bookings_writer_v2_create)

        expected = {
            "create",
            "bulk-create",
            "bulk-calculate-allowed-actions",
            "bulk-confirm-or-decline",
            "confirm-or-decline",
            "confirm",
            "decline",
            "cancel",
            "reschedule",
            "mark-pending",
            "set-submission-id",
            "update-extended-fields",
            "update-participants",
            "create-multi-service",
            "get-multi-service",
            "get-multi-service-availability",
            "add-to-multi-service",
            "remove-from-multi-service",
            "cancel-multi-service",
            "confirm-multi-service",
            "decline-multi-service",
            "reschedule-multi-service",
            "mark-multi-service-pending",
            "bulk-get-multi-service-allowed-actions",
            "get-anonymous-action-token",
            "get-anonymous",
            "get-service-anonymous",
            "cancel-anonymous",
            "reschedule-anonymous",
        }
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-writer-v2"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsWriterV2Commands(unittest.TestCase):
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

    def test_create_dry_run_uses_official_path_and_wraps_booking_body(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_writer_v2.cmd_bookings_writer_v2_create(
                SimpleNamespace(booking_json='{"contactDetails":{"email":"a@example.com"},"totalParticipants":1}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-writer-v2.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/bookings-service/v2/bookings")
        self.assertIn("booking", payload["plan"]["request"]["body"])

    def test_bulk_create_enforces_official_twelve_booking_cap(self) -> None:
        body = {"createBookingsInfo": [{"booking": {"id": str(i)}} for i in range(13)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_writer_v2.cmd_bookings_writer_v2_bulk_create(
                SimpleNamespace(bookings_json=json.dumps(body)),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("cannot include more than 12 bookings", payload["error"])

    def test_destructive_lifecycle_methods_require_irreversible_ack(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_writer_v2.cmd_bookings_writer_v2_cancel(
                SimpleNamespace(booking_id="booking-1", request_json='{"reason":"customer asked"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/bookings-service/v2/bookings/booking-1/cancel")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.bookings_writer_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_writer_v2.resolve_auth_mode")
    def test_read_methods_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"multiServiceBooking": {"id": "ms-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_writer_v2.cmd_bookings_writer_v2_get_multi_service(
                SimpleNamespace(multi_service_booking_id="ms-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/_api/bookings-service/v2/multi_service_bookings/ms-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/_api/bookings-service/v2/multi_service_bookings/ms-1"))

    @patch("wix_safe_agent_cli.commands.bookings_writer_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_writer_v2.resolve_auth_mode")
    def test_anonymous_reads_do_not_use_normal_auth(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"booking": {"id": "booking-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_writer_v2.cmd_bookings_writer_v2_get_anonymous(SimpleNamespace(token="secret-token"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "anonymous_token")
        self.assertEqual(payload["request"]["path"], "/v1/anonymous-bookings/<redacted-token>")
        mock_auth.assert_not_called()
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["headers"], {})
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/v1/anonymous-bookings/secret-token"))
