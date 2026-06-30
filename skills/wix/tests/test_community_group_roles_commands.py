from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_group_roles
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityGroupRolesCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli community-group-roles",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_exposes_community_group_roles_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["community-group-roles", "assign", "--group-id", "group-1", "--role-json", '{"memberIds":["member-1"],"role":{"value":"ADMIN"}}'],
                "assign",
            ),
            (
                ["community-group-roles", "unassign", "--group-id", "group-1", "--role-json", '{"memberIds":["member-1"],"role":{"value":"ADMIN"}}'],
                "unassign",
            ),
        ]
        for argv, command in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_group_roles_cmd, command)
                self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_assign_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_roles.cmd_community_group_roles_assign(
                SimpleNamespace(
                    group_id="group-1",
                    role_json='{"memberIds":["member-1"],"role":{"value":"ADMIN"}}',
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups-proxy/roles/v2/groups/group-1/roles/assign")
        self.assertIn("assign-community-group-role", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_unassign_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_roles.cmd_community_group_roles_unassign(
                SimpleNamespace(
                    group_id="group-1",
                    role_json='{"memberIds":["member-1"],"role":{"value":"ADMIN"}}',
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups-proxy/roles/v2/groups/group-1/roles/unassign")
        self.assertIn("unassign-community-group-role", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_role_json_must_be_non_empty(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_roles.cmd_community_group_roles_assign(
                SimpleNamespace(group_id="group-1", role_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
