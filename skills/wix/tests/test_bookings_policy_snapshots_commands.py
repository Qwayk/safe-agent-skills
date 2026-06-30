from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_policy_snapshots
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsPolicySnapshotsParser(unittest.TestCase):
    def test_parser_recognizes_list_command(self) -> None:
        parser = build_parser()

        args = parser.parse_args(["bookings-policy-snapshots", "list", "--booking-ids", "booking-1,booking-2"])

        self.assertEqual(args.bookings_policy_snapshots_cmd, "list")
        self.assertFalse(args.write_capable)
        self.assertIs(args.func, bookings_policy_snapshots.cmd_bookings_policy_snapshots_list)


class TestBookingsPolicySnapshotsCommands(unittest.TestCase):
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
        }

    @patch("wix_safe_agent_cli.commands.bookings_policy_snapshots.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_policy_snapshots.resolve_auth_mode")
    def test_list_uses_official_path_and_booking_ids_param(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"bookingPolicySnapshots": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_policy_snapshots.cmd_bookings_policy_snapshots_list(
                SimpleNamespace(booking_ids=" booking-1,booking-2 "),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-policy-snapshots.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/booking-policy-snapshots/v1/policy-snapshots")
        self.assertEqual(payload["request"]["params"], {"bookingIds": ["booking-1", "booking-2"]})
        call = mock_client.return_value.request.call_args
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/booking-policy-snapshots/v1/policy-snapshots"))
        self.assertEqual(call.kwargs["params"], {"bookingIds": ["booking-1", "booking-2"]})
        mock_auth.assert_called_once()
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "bookings-policy-snapshots")

    @patch("wix_safe_agent_cli.commands.bookings_policy_snapshots.HttpClient")
    def test_list_requires_at_least_one_booking_id(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_policy_snapshots.cmd_bookings_policy_snapshots_list(
                SimpleNamespace(booking_ids=" , "),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("--booking-ids cannot be empty", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)
