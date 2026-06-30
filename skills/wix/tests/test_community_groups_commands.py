from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_groups
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityGroupsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli community-groups",
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

    def test_parser_exposes_community_groups_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-groups", "list"], "list", False),
            (["community-groups", "get", "--group-id", "group-1"], "get", False),
            (["community-groups", "get-by-slug", "--slug", "my-group"], "get-by-slug", False),
            (["community-groups", "query", "--query-json", '{"filter":{"title":{"$contains":"Test"}}}'], "query", False),
            (["community-groups", "create", "--group-json", '{"group":{"name":"My Group"}}'], "create", True),
            (["community-groups", "update", "--group-json", '{"group":{"id":"group-1","name":"New"}}'], "update", True),
            (["community-groups", "delete", "--group-id", "group-1"], "delete", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_groups_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_community_groups_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        read_cases = [
            (
                community_groups.cmd_community_groups_list,
                SimpleNamespace(params_json='{"limit":10}'),
                "GET",
                "/social-groups-proxy/groups/v2/groups",
            ),
            (
                community_groups.cmd_community_groups_get,
                SimpleNamespace(group_id="group-1"),
                "GET",
                "/social-groups-proxy/groups/v2/groups/group-1",
            ),
            (
                community_groups.cmd_community_groups_get_by_slug,
                SimpleNamespace(slug="my-group"),
                "GET",
                "/social-groups-proxy/groups/v2/groups/slugs/my-group",
            ),
            (
                community_groups.cmd_community_groups_query,
                SimpleNamespace(query_json='{"filter":{"title":{"$contains":"Test"}}}'),
                "POST",
                "/social-groups-proxy/groups/v2/groups/query",
            ),
        ]
        for func, args, http_method, path in read_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                self.assertEqual(rc, 0)
                self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], http_method)
                self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith(path))

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_community_groups_writes_are_plan_first_with_expected_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        write_cases = [
            (
                community_groups.cmd_community_groups_create,
                SimpleNamespace(group_json='{"group":{"name":"My Group"}}'),
                "POST",
                "/social-groups-proxy/groups/v2/groups",
                False,
            ),
            (
                community_groups.cmd_community_groups_update,
                SimpleNamespace(group_json='{"group":{"id":"group-1","name":"New"}}'),
                "PATCH",
                "/social-groups-proxy/groups/v2/groups/group-1",
                False,
            ),
            (
                community_groups.cmd_community_groups_delete,
                SimpleNamespace(group_id="group-1"),
                "DELETE",
                "/social-groups-proxy/groups/v2/groups/group-1",
                True,
            ),
        ]
        for func, args, http_method, path, requires_ack in write_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                preconditions = payload["plan"]["preconditions"]
                self.assertEqual("apply also requires --ack-irreversible" in preconditions, requires_ack)
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_community_groups_update_requires_group_id(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_groups.cmd_community_groups_update(
                SimpleNamespace(group_json='{"group":{"name":"New"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
