from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_external_calendars_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsExternalCalendarsV2Parser(unittest.TestCase):
    def test_parser_recognizes_external_calendar_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-external-calendars-v2", "list-providers"])
        self.assertEqual(read_args.bookings_external_calendars_v2_cmd, "list-providers")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_list_providers)

        write_args = parser.parse_args(
            [
                "bookings-external-calendars-v2",
                "connect-by-credentials",
                "--request-json",
                '{"scheduleId":"schedule-1","providerId":"google","email":"owner@example.com","password":"secret"}',
                "--ack-external-credentials",
            ]
        )
        self.assertEqual(write_args.bookings_external_calendars_v2_cmd, "connect-by-credentials")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_connect_by_credentials)

        expected = {
            "list-providers",
            "connect-by-credentials",
            "connect-by-oauth",
            "list-connections",
            "get-connection",
            "update-sync-config",
            "list-calendars",
            "list-events",
            "disconnect",
        }
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-external-calendars-v2"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsExternalCalendarsV2Commands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_external_calendars_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_external_calendars_v2.resolve_auth_mode")
    def test_list_providers_uses_official_path(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"providers": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_list_providers(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-external-calendars-v2.list-providers")
        self.assertEqual(payload["request"]["path"], "/bookings/v2/external-calendars/providers")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.bookings_external_calendars_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_external_calendars_v2.resolve_auth_mode")
    def test_list_events_requires_date_range_unless_cursor_and_passes_params(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"events": []})

        missing = io.StringIO()
        with redirect_stdout(missing):
            rc_missing = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_list_events(
                SimpleNamespace(query_json=None, from_=None, to=None, cursor=None, limit=None, schedule_ids=None, user_ids=None, fieldsets=None, partial_failure=False),
                self._ctx(),
            )
        missing_payload = json.loads(missing.getvalue())

        ok = io.StringIO()
        with redirect_stdout(ok):
            rc_ok = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_list_events(
                SimpleNamespace(
                    query_json=None,
                    from_="2026-06-01T00:00:00Z",
                    to="2026-06-30T23:59:59Z",
                    cursor=None,
                    limit=50,
                    schedule_ids="schedule-1,schedule-2",
                    user_ids=None,
                    fieldsets="OWN_PI",
                    partial_failure=True,
                ),
                self._ctx(),
            )
        payload = json.loads(ok.getvalue())

        self.assertEqual(rc_missing, 1)
        self.assertIn("requires both --from and --to", missing_payload["error"])
        self.assertEqual(rc_ok, 0)
        self.assertEqual(payload["request"]["path"], "/bookings/v2/external-calendars/events")
        self.assertEqual(payload["request"]["params"]["scheduleIds"], ["schedule-1", "schedule-2"])
        self.assertEqual(payload["request"]["params"]["fieldsets"], "OWN_PI")
        self.assertTrue(payload["request"]["params"]["partialFailure"])
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"]["cursorPaging"]["limit"], 50)

    def test_connect_by_credentials_requires_ack_and_redacts_password(self) -> None:
        request_json = '{"scheduleId":"schedule-1","providerId":"google","email":"owner@example.com","password":"secret-value"}'

        refused = io.StringIO()
        with redirect_stdout(refused):
            rc_refused = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_connect_by_credentials(
                SimpleNamespace(request_json=request_json, ack_external_credentials=False),
                self._ctx(),
            )
        refused_payload = json.loads(refused.getvalue())

        ok = io.StringIO()
        with redirect_stdout(ok):
            rc_ok = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_connect_by_credentials(
                SimpleNamespace(request_json=request_json, ack_external_credentials=True),
                self._ctx(),
            )
        payload = json.loads(ok.getvalue())

        self.assertEqual(rc_refused, 0)
        self.assertTrue(refused_payload["refused"])
        self.assertIn("--ack-external-credentials", refused_payload["reasons"][0])
        self.assertEqual(rc_ok, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/external-calendars/connections:connectByCredentials")
        self.assertEqual(payload["plan"]["request"]["body"]["password"], "[REDACTED]")
        self.assertNotIn("secret-value", json.dumps(payload))

    def test_update_sync_config_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_update_sync_config(
                SimpleNamespace(connection_id="connection-1", request_json='{"syncConfig":{"import":true,"export":false}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/external-calendars/connections/connection-1/sync-config")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_disconnect_builds_irreversible_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_external_calendars_v2.cmd_bookings_external_calendars_v2_disconnect(
                SimpleNamespace(connection_id="connection-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/external-calendars/connections/connection-1/disconnect")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])


if __name__ == "__main__":
    unittest.main()
