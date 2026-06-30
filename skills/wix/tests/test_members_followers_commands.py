from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import members_followers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMembersFollowersCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(base_url="https://www.wixapis.com", timeout_s=30.0, access_token="token-abc")
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli members-followers",
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

    @patch("wix_safe_agent_cli.commands.members_followers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.members_followers.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"members": []})

        cases = [
            (members_followers.cmd_members_followers_list_followers, SimpleNamespace(member_id="member-1"), "GET", "/members/v3/followers/member-1", None),
            (members_followers.cmd_members_followers_list_following, SimpleNamespace(member_id="member-1"), "GET", "/members/v3/followers/member-1/following", None),
            (members_followers.cmd_members_followers_list_my_followers, SimpleNamespace(), "GET", "/members/v3/followers/my", None),
            (members_followers.cmd_members_followers_list_my_following, SimpleNamespace(), "GET", "/members/v3/followers/my/following", None),
            (
                members_followers.cmd_members_followers_query_connections,
                SimpleNamespace(member_id="member-1", query_json='{"connectedMemberIds":["member-2"]}'),
                "POST",
                "/members/v3/followers/member-1/connections",
                {"connectedMemberIds": ["member-2"]},
            ),
            (
                members_followers.cmd_members_followers_query_my_connections,
                SimpleNamespace(query_json='{"connectedMemberIds":["member-2"]}'),
                "POST",
                "/members/v3/followers/my/connections",
                {"connectedMemberIds": ["member-2"]},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "members-followers")

    @patch("wix_safe_agent_cli.commands.members_followers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.members_followers.HttpClient")
    def test_follow_is_plan_first_and_unfollow_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        follow_buf = io.StringIO()
        with redirect_stdout(follow_buf):
            follow_rc = members_followers.cmd_members_followers_follow(SimpleNamespace(member_id="member-2"), self._ctx())
        follow = json.loads(follow_buf.getvalue())

        unfollow_buf = io.StringIO()
        with redirect_stdout(unfollow_buf):
            unfollow_rc = members_followers.cmd_members_followers_unfollow(SimpleNamespace(member_id="member-2"), self._ctx())
        unfollow = json.loads(unfollow_buf.getvalue())

        self.assertEqual(follow_rc, 0)
        self.assertTrue(follow["dry_run"])
        self.assertEqual(follow["plan"]["request"]["method"], "POST")
        self.assertEqual(follow["plan"]["request"]["path"], "/members/v3/followers/member-2")
        self.assertNotIn("apply also requires --ack-irreversible", follow["plan"]["preconditions"])

        self.assertEqual(unfollow_rc, 0)
        self.assertTrue(unfollow["dry_run"])
        self.assertEqual(unfollow["plan"]["request"]["method"], "DELETE")
        self.assertEqual(unfollow["plan"]["request"]["path"], "/members/v3/followers/member-2")
        self.assertIn("apply also requires --ack-irreversible", unfollow["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_members_followers_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["members-followers", "follow", "--member-id", "member-1"], members_followers.cmd_members_followers_follow, True),
            (["members-followers", "unfollow", "--member-id", "member-1"], members_followers.cmd_members_followers_unfollow, True),
            (["members-followers", "list-followers", "--member-id", "member-1"], members_followers.cmd_members_followers_list_followers, False),
            (["members-followers", "list-following", "--member-id", "member-1"], members_followers.cmd_members_followers_list_following, False),
            (["members-followers", "list-my-followers"], members_followers.cmd_members_followers_list_my_followers, False),
            (["members-followers", "list-my-following"], members_followers.cmd_members_followers_list_my_following, False),
            (["members-followers", "query-connections", "--member-id", "member-1"], members_followers.cmd_members_followers_query_connections, False),
            (["members-followers", "query-my-connections"], members_followers.cmd_members_followers_query_my_connections, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
