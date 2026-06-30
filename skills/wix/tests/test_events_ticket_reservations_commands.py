from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_ticket_reservations
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsTicketReservationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-ticket-reservations",
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

    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ticketReservation": {"id": "res-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_ticket_reservations.cmd_events_ticket_reservations_get(SimpleNamespace(ticket_reservation_id="res-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-ticket-reservations.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/events/v1/ticket-reservations/res-1")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-ticket-reservations")

    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.HttpClient")
    def test_create_and_bulk_update_tags_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        create_buf = io.StringIO()
        with redirect_stdout(create_buf):
            rc_create = events_ticket_reservations.cmd_events_ticket_reservations_create(
                SimpleNamespace(reservation_json='{"ticketReservation":{"tickets":[{"ticketDefinitionId":"td-1","quantity":1}]}}'),
                self._ctx(),
            )
        create_payload = json.loads(create_buf.getvalue())

        tags_buf = io.StringIO()
        with redirect_stdout(tags_buf):
            rc_tags = events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags(
                SimpleNamespace(tags_json='{"ids":["res-1"],"assign":["vip"]}'),
                self._ctx(),
            )
        tags_payload = json.loads(tags_buf.getvalue())

        self.assertEqual(rc_create, 0)
        self.assertTrue(create_payload["dry_run"])
        self.assertEqual(create_payload["plan"]["request"]["path"], "/events/v1/ticket-reservations")
        self.assertEqual(rc_tags, 0)
        self.assertTrue(tags_payload["dry_run"])
        self.assertEqual(tags_payload["plan"]["request"]["path"], "/events/v1/bulk/ticket-reservations/update-tags")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.HttpClient")
    def test_destructive_and_broad_writes_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")

        for label, func, args in [
            ("delete", events_ticket_reservations.cmd_events_ticket_reservations_delete, SimpleNamespace(ticket_reservation_id="res-1")),
            ("bulk-update-tags-by-filter", events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"eventId":"event-1"},"assign":["vip"]}')),
            ("cancel", events_ticket_reservations.cmd_events_ticket_reservations_cancel, SimpleNamespace(ticket_reservation_id="res-1")),
        ]:
            with self.subTest(label=label):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, ctx)
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.HttpClient")
    def test_ticket_and_bulk_tag_limits_are_enforced(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        reservation_json = json.dumps({"ticketReservation": {"tickets": [{"ticketDefinitionId": str(i), "quantity": 1} for i in range(51)]}})
        tags_json = json.dumps({"ids": [f"res-{i}" for i in range(101)], "assign": ["vip"]})

        reservation_buf = io.StringIO()
        with redirect_stdout(reservation_buf):
            rc_reservation = events_ticket_reservations.cmd_events_ticket_reservations_create(
                SimpleNamespace(reservation_json=reservation_json),
                self._ctx(),
            )
        reservation_payload = json.loads(reservation_buf.getvalue())

        tags_buf = io.StringIO()
        with redirect_stdout(tags_buf):
            rc_tags = events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags(
                SimpleNamespace(tags_json=tags_json),
                self._ctx(),
            )
        tags_payload = json.loads(tags_buf.getvalue())

        self.assertEqual(rc_reservation, 1)
        self.assertIn("at most 50 line items", reservation_payload["error"])
        self.assertEqual(rc_tags, 1)
        self.assertIn("at most 100 ticket reservations", tags_payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_reservations.HttpClient")
    def test_bulk_update_tags_requires_ids(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags(SimpleNamespace(tags_json='{"assign":["vip"]}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("non-empty ids array", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_ticket_reservation_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-ticket-reservations", "create", "--reservation-json", "{}"], events_ticket_reservations.cmd_events_ticket_reservations_create, True),
            (["events-ticket-reservations", "get", "--ticket-reservation-id", "res-1"], events_ticket_reservations.cmd_events_ticket_reservations_get, False),
            (["events-ticket-reservations", "delete", "--ticket-reservation-id", "res-1"], events_ticket_reservations.cmd_events_ticket_reservations_delete, True),
            (["events-ticket-reservations", "bulk-update-tags", "--tags-json", "{}"], events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags, True),
            (["events-ticket-reservations", "bulk-update-tags-by-filter", "--filter-json", "{}"], events_ticket_reservations.cmd_events_ticket_reservations_bulk_update_tags_by_filter, True),
            (["events-ticket-reservations", "cancel", "--ticket-reservation-id", "res-1"], events_ticket_reservations.cmd_events_ticket_reservations_cancel, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
