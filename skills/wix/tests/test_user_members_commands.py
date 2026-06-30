from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import user_members
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestUserMembersCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(base_url="https://www.wixapis.com", timeout_s=30.0, access_token="token-abc")
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli user-members",
        }

    @patch("wix_safe_agent_cli.commands.user_members.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.user_members.HttpClient")
    def test_query_uses_official_path_and_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"userMembers": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = user_members.cmd_user_members_query(
                SimpleNamespace(query_json='{"query":{"filter":{"userId":{"$eq":"user-1"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/members/v1/user-members/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"userId": {"$eq": "user-1"}}}})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "user-members")

    def test_parser_exposes_user_members_query(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["user-members", "query", "--query-json", "{}"])
        self.assertIs(args.func, user_members.cmd_user_members_query)
        self.assertFalse(args.write_capable)
