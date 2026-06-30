from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_guests
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsGuestsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli events-guests",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.events_guests.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_guests.HttpClient")
    def test_query_uses_expected_path_and_body(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"guests": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_guests.cmd_events_guests_query(
                SimpleNamespace(query_json='{"query":{"filter":{"eventId":"event-1"}},"fieldsets":["guestDetails"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-guests.query")
        self.assertEqual(payload["request"]["path"], "/events/v2/guests/query")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"eventId": "event-1"}}, "fieldsets": ["guestDetails"]})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-guests")

    @patch("wix_safe_agent_cli.commands.events_guests.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_guests.HttpClient")
    def test_query_defaults_to_empty_request_body(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"guests": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_guests.cmd_events_guests_query(SimpleNamespace(query_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["body"], {})

    def test_parser_exposes_events_guests_query_as_read_only(self) -> None:
        args = build_parser().parse_args(["events-guests", "query", "--query-json", "{}"])

        self.assertIs(args.func, events_guests.cmd_events_guests_query)
        self.assertFalse(args.write_capable)
