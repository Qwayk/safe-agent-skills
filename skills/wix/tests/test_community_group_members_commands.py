from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_group_members
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityGroupMembersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-group-members",
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

    def test_parser_exposes_community_group_members_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-group-members", "list", "--group-id", "group-1"], "list", False),
            (["community-group-members", "list-memberships", "--member-id", "member-1"], "list-memberships", False),
            (["community-group-members", "query", "--group-id", "group-1"], "query", False),
            (["community-group-members", "query-memberships", "--member-id", "member-1"], "query-memberships", False),
            (["community-group-members", "add", "--group-id", "group-1", "--members-json", '{"memberIds":["member-1"]}'], "add", True),
            (
                ["community-group-members", "remove", "--group-id", "group-1", "--members-json", '{"memberIds":["member-1"]}'],
                "remove",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_group_members_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_uses_official_path_and_params(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"members": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_list(
                SimpleNamespace(group_id="group-1", params_json='{"paging.limit":50}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/members/v2/groups/group-1/members"
            )
        )
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"paging.limit": 50})

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_memberships_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"memberships": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_list_memberships(
                SimpleNamespace(member_id="member-1", params_json="{}"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/members/v2/members/member-1/memberships"
            )
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_query_uses_official_path_and_wraps_query(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"members": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_query(
                SimpleNamespace(group_id="group-1", query_json='{"filter":{"role":"MEMBER"}}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/members/v2/groups/group-1/members/query"
            )
        )
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["json_body"],
            {"query": {"filter": {"role": "MEMBER"}}},
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_query_memberships_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"memberships": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_query_memberships(
                SimpleNamespace(member_id="member-1", query_json='{"filter":{"status":"ACTIVE"}}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/members/v2/members/member-1/memberships/query"
            )
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_add_is_plan_first_and_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_add(
                SimpleNamespace(group_id="group-1", members_json='{"memberIds":["member-1"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups-proxy/members/v2/groups/group-1/members")
        self.assertIn("add-community-group-members", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_remove_is_plan_first_and_preserves_delete_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_remove(
                SimpleNamespace(group_id="group-1", members_json='{"memberIds":["member-1"]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups-proxy/members/v2/groups/group-1/members")
        self.assertEqual(payload["plan"]["request"]["body"], {"memberIds": ["member-1"]})
        self.assertIn("remove-community-group-members", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_members_json_must_be_non_empty(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_group_members.cmd_community_group_members_add(
                SimpleNamespace(group_id="group-1", members_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
