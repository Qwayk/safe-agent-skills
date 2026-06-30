from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_tickets
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsTicketsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-tickets",
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

    @patch("wix_safe_agent_cli.commands.events_tickets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_tickets.HttpClient")
    def test_get_and_list_use_expected_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ticket": {"ticketNumber": "AAAA-1"}})

        get_buf = io.StringIO()
        with redirect_stdout(get_buf):
            rc_get = events_tickets.cmd_events_tickets_get(SimpleNamespace(ticket_number="AAAA-1"), self._ctx())
        get_payload = json.loads(get_buf.getvalue())

        list_buf = io.StringIO()
        with redirect_stdout(list_buf):
            rc_list = events_tickets.cmd_events_tickets_list(SimpleNamespace(params_json='{"paging.limit": 25, "eventId": "event-1"}'), self._ctx())
        list_payload = json.loads(list_buf.getvalue())

        self.assertEqual(rc_get, 0)
        self.assertEqual(get_payload["method"], "events-tickets.get")
        self.assertEqual(get_payload["request"]["method"], "GET")
        self.assertEqual(get_payload["request"]["path"], "/events/v1/tickets/AAAA-1")
        self.assertEqual(rc_list, 0)
        self.assertEqual(list_payload["method"], "events-tickets.list")
        self.assertEqual(list_payload["request"]["path"], "/events/v1/tickets")
        self.assertEqual(list_payload["request"]["params"], {"paging.limit": 25, "eventId": "event-1"})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-tickets")

    @patch("wix_safe_agent_cli.commands.events_tickets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_tickets.HttpClient")
    def test_update_bulk_update_and_check_in_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                events_tickets.cmd_events_tickets_update,
                SimpleNamespace(ticket_number="AAAA-1", ticket_json='{"ticket":{"guestDetails":{"firstName":"Ada"}}}'),
                "/events/v1/tickets/AAAA-1",
            ),
            (
                events_tickets.cmd_events_tickets_bulk_update,
                SimpleNamespace(tickets_json='{"tickets":[{"ticketNumber":"AAAA-1","archived":true}]}'),
                "/events/v1/tickets",
            ),
            (
                events_tickets.cmd_events_tickets_check_in,
                SimpleNamespace(request_json='{"ticketNumber":["AAAA-1"],"eventId":"event-1"}'),
                "/events/v1/tickets/check-in",
            ),
        ]

        for func, args, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_tickets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_tickets.HttpClient")
    def test_delete_check_in_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_tickets.cmd_events_tickets_delete_check_in(
                SimpleNamespace(request_json='{"ticketNumber":["AAAA-1"],"eventId":"event-1"}'),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_tickets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_tickets.HttpClient")
    def test_bulk_and_check_in_limits_are_enforced(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        tickets_json = json.dumps({"tickets": [{"ticketNumber": f"ticket-{i}", "archived": True} for i in range(101)]})
        check_in_json = json.dumps({"ticketNumber": [f"ticket-{i}" for i in range(101)], "eventId": "event-1"})

        tickets_buf = io.StringIO()
        with redirect_stdout(tickets_buf):
            rc_tickets = events_tickets.cmd_events_tickets_bulk_update(SimpleNamespace(tickets_json=tickets_json), self._ctx())
        tickets_payload = json.loads(tickets_buf.getvalue())

        check_in_buf = io.StringIO()
        with redirect_stdout(check_in_buf):
            rc_check_in = events_tickets.cmd_events_tickets_check_in(SimpleNamespace(request_json=check_in_json), self._ctx())
        check_in_payload = json.loads(check_in_buf.getvalue())

        self.assertEqual(rc_tickets, 1)
        self.assertIn("at most 100 tickets", tickets_payload["error"])
        self.assertEqual(rc_check_in, 1)
        self.assertIn("at most 100 tickets", check_in_payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_tickets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_tickets.HttpClient")
    def test_check_in_requires_ticket_numbers(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_tickets.cmd_events_tickets_check_in(SimpleNamespace(request_json='{"eventId":"event-1"}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("non-empty ticketNumber array", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_ticket_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-tickets", "get", "--ticket-number", "AAAA-1"], events_tickets.cmd_events_tickets_get, False),
            (["events-tickets", "list"], events_tickets.cmd_events_tickets_list, False),
            (["events-tickets", "update", "--ticket-number", "AAAA-1", "--ticket-json", "{}"], events_tickets.cmd_events_tickets_update, True),
            (["events-tickets", "bulk-update", "--tickets-json", "{}"], events_tickets.cmd_events_tickets_bulk_update, True),
            (["events-tickets", "check-in", "--request-json", "{}"], events_tickets.cmd_events_tickets_check_in, True),
            (["events-tickets", "delete-check-in", "--request-json", "{}"], events_tickets.cmd_events_tickets_delete_check_in, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
