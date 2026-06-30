from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_staff_members
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsStaffMembersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-staff-members",
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

    @patch("wix_safe_agent_cli.commands.events_staff_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_staff_members.HttpClient")
    def test_get_uses_expected_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"staffMember": {"id": "staff-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_staff_members.cmd_events_staff_members_get(SimpleNamespace(staff_member_id="staff-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-staff-members.get")
        self.assertEqual(payload["request"]["path"], "/events/v1/staff-members/staff-1")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-staff-members")

    @patch("wix_safe_agent_cli.commands.events_staff_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_staff_members.HttpClient")
    def test_create_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_staff_members.cmd_events_staff_members_create(
                SimpleNamespace(staff_member_json='{"staffMember":{"name":"Ada","assignedEvents":"ALL_EVENTS"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/events/v1/staff-members")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_staff_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_staff_members.HttpClient")
    def test_delete_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json")
        with redirect_stdout(buf):
            rc = events_staff_members.cmd_events_staff_members_delete(SimpleNamespace(staff_member_id="staff-1"), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/events/v1/staff-members/staff-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_staff_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_staff_members.HttpClient")
    def test_update_requires_staff_member_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_staff_members.cmd_events_staff_members_update(
                SimpleNamespace(staff_member_id="staff-1", staff_member_json='{"staffMember":{"name":"Updated"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("staffMember.revision", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_staff_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_staff_members.HttpClient")
    def test_query_posts_query_body(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"staffMembers": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_staff_members.cmd_events_staff_members_query(
                SimpleNamespace(query_json='{"query":{"filter":{"id":"staff-1"}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/events/v1/staff-members/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"id": "staff-1"}}})

    def test_parser_exposes_all_events_staff_members_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-staff-members", "create", "--staff-member-json", "{}"], events_staff_members.cmd_events_staff_members_create, True),
            (["events-staff-members", "get", "--staff-member-id", "staff-1"], events_staff_members.cmd_events_staff_members_get, False),
            (["events-staff-members", "update", "--staff-member-id", "staff-1", "--staff-member-json", "{}"], events_staff_members.cmd_events_staff_members_update, True),
            (["events-staff-members", "delete", "--staff-member-id", "staff-1"], events_staff_members.cmd_events_staff_members_delete, True),
            (["events-staff-members", "query"], events_staff_members.cmd_events_staff_members_query, False),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)
