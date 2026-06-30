from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_ticket_definitions_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsTicketDefinitionsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-ticket-definitions-v3",
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

    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ticketDefinition": {"id": "td-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_get(
                SimpleNamespace(ticket_definition_id="td-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-ticket-definitions-v3.get")
        self.assertEqual(payload["request"]["path"], "/events-ticket-definitions/v3/ticket-definitions/td-1")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-ticket-definitions-v3")

    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.resolve_auth_mode")
    def test_update_requires_matching_id_and_revision(self, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mismatch_ctx = self._ctx()
        mismatch_buf = io.StringIO()
        with redirect_stdout(mismatch_buf):
            rc_mismatch = events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_update(
                SimpleNamespace(ticket_definition_id="td-1", ticket_definition_json='{"ticketDefinition":{"id":"td-2","revision":"1"}}'),
                mismatch_ctx,
            )
        mismatch_payload = json.loads(mismatch_buf.getvalue())

        missing_revision_buf = io.StringIO()
        with redirect_stdout(missing_revision_buf):
            rc_missing = events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_update(
                SimpleNamespace(ticket_definition_id="td-1", ticket_definition_json='{"ticketDefinition":{"id":"td-1","name":"General"}}'),
                self._ctx(),
            )
        missing_revision_payload = json.loads(missing_revision_buf.getvalue())

        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --ticket-definition-id", mismatch_payload["reasons"][0])
        self.assertEqual(rc_missing, 1)
        self.assertIn("ticketDefinition.revision is required for update", missing_revision_payload["error"])

    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.HttpClient")
    def test_delete_without_irreversible_ack_stays_dry_run(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json", ack_irreversible=False)
        with redirect_stdout(buf):
            rc = events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_delete(
                SimpleNamespace(ticket_definition_id="td-1"),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["method"], "events-ticket-definitions-v3.delete")
        self.assertEqual(payload["plan"]["request"]["path"], "/events-ticket-definitions/v3/ticket-definitions/td-1")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_ticket_definitions_v3.HttpClient")
    def test_bulk_delete_by_filter_uses_official_bulk_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        ctx = self._ctx()
        with redirect_stdout(buf):
            rc = events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_bulk_delete_by_filter(
                SimpleNamespace(filter_json='{"filter":{"eventId":"event-1"}}'),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/events-ticket-definitions/v3/bulk/ticket-definitions/delete-by-filter",
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_ticket_definitions_v3_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-ticket-definitions-v3", "create", "--ticket-definition-json", "{}"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_create, True),
            (["events-ticket-definitions-v3", "get", "--ticket-definition-id", "td-1"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_get, False),
            (["events-ticket-definitions-v3", "update", "--ticket-definition-id", "td-1", "--ticket-definition-json", "{}"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_update, True),
            (["events-ticket-definitions-v3", "delete", "--ticket-definition-id", "td-1"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_delete, True),
            (["events-ticket-definitions-v3", "query"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_query, False),
            (["events-ticket-definitions-v3", "bulk-delete-by-filter", "--filter-json", "{}"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_bulk_delete_by_filter, True),
            (["events-ticket-definitions-v3", "change-currency", "--request-json", "{}"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_change_currency, True),
            (["events-ticket-definitions-v3", "count"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_count, False),
            (["events-ticket-definitions-v3", "reorder", "--request-json", "{}"], events_ticket_definitions_v3.cmd_events_ticket_definitions_v3_reorder, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
