from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_authentication
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class TestMemberAuthenticationCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        return {
            "cfg": SimpleNamespace(base_url="https://www.wixapis.com", timeout_s=30.0, access_token="token-abc"),
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli member-authentication send-set-password-email",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.member_authentication.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_authentication.HttpClient")
    def test_send_set_password_email_is_plan_first_and_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_authentication.cmd_member_authentication_send_set_password_email(
                SimpleNamespace(email_json='{"memberId":"member-1"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/wix-sm/api/v1/auth/v1/auth/members/send-set-password-email",
        )
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-authentication")
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_member_authentication_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["member-authentication", "send-set-password-email", "--email-json", "{}"])

        self.assertIs(args.func, member_authentication.cmd_member_authentication_send_set_password_email)
        self.assertTrue(args.write_capable)
