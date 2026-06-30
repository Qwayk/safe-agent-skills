from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_abouts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberAboutsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli member-abouts",
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

    @patch("wix_safe_agent_cli.commands.member_abouts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_abouts.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"memberAbout": {}})

        cases = [
            (member_abouts.cmd_member_abouts_get, SimpleNamespace(about_id="about-1"), "GET", "/members/v2/abouts/about-1", None),
            (
                member_abouts.cmd_member_abouts_query,
                SimpleNamespace(query_json='{"query":{"filter":{"memberId":{"$eq":"member-1"}}}}'),
                "POST",
                "/members/v2/abouts/query",
                {"query": {"filter": {"memberId": {"$eq": "member-1"}}}},
            ),
            (member_abouts.cmd_member_abouts_get_my, SimpleNamespace(), "GET", "/members/v2/abouts/my", None),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-abouts")

    @patch("wix_safe_agent_cli.commands.member_abouts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_abouts.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                member_abouts.cmd_member_abouts_create,
                SimpleNamespace(about_json='{"memberAbout":{"memberId":"member-1","content":{}}}'),
                "POST",
                "/members/v2/abouts",
                False,
            ),
            (
                member_abouts.cmd_member_abouts_update,
                SimpleNamespace(about_id="about-1", about_json='{"memberAbout":{"id":"about-1","revision":"3","content":{}}}'),
                "PATCH",
                "/members/v2/abouts/about-1",
                False,
            ),
            (
                member_abouts.cmd_member_abouts_delete,
                SimpleNamespace(about_id="about-1"),
                "DELETE",
                "/members/v2/abouts/about-1",
                True,
            ),
        ]
        for func, args, method, path, requires_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                preconditions = payload["plan"]["preconditions"]
                self.assertEqual("apply also requires --ack-irreversible" in preconditions, requires_ack)

        mock_client.return_value.request.assert_not_called()

    def test_update_requires_revision(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_abouts.cmd_member_abouts_update(
                SimpleNamespace(about_id="about-1", about_json='{"memberAbout":{"id":"about-1","content":{}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("memberAbout.revision", payload["error"])

    def test_parser_exposes_member_abouts_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["member-abouts", "create", "--about-json", "{}"], member_abouts.cmd_member_abouts_create, True),
            (["member-abouts", "get", "--about-id", "about-1"], member_abouts.cmd_member_abouts_get, False),
            (["member-abouts", "update", "--about-id", "about-1", "--about-json", "{}"], member_abouts.cmd_member_abouts_update, True),
            (["member-abouts", "delete", "--about-id", "about-1"], member_abouts.cmd_member_abouts_delete, True),
            (["member-abouts", "query"], member_abouts.cmd_member_abouts_query, False),
            (["member-abouts", "get-my"], member_abouts.cmd_member_abouts_get_my, False),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
