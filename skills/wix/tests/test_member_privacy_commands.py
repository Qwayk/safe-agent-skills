from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_privacy
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberPrivacyCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli member-privacy",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.member_abouts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_abouts.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"settings": {}})

        cases = [
            (member_privacy.cmd_member_privacy_get_default, "GET", "/members/v1/default-privacy-status"),
            (member_privacy.cmd_member_privacy_get_settings, "GET", "/members/v1/privacy-settings"),
        ]
        for func, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(SimpleNamespace(), self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-privacy")

    @patch("wix_safe_agent_cli.commands.member_abouts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_abouts.HttpClient")
    def test_writes_are_plan_first(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                member_privacy.cmd_member_privacy_set_default,
                SimpleNamespace(privacy_json='{"defaultPrivacyStatus":"PUBLIC"}'),
                "PATCH",
                "/members/v1/default-privacy-status",
            ),
            (
                member_privacy.cmd_member_privacy_set_settings,
                SimpleNamespace(settings_json='{"memberPrivacySettings":{"revision":"1","publicMemberCandidates":"ALL_MEMBERS"}}'),
                "POST",
                "/members/v1/privacy-settings",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    def test_set_settings_requires_revision(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_privacy.cmd_member_privacy_set_settings(
                SimpleNamespace(settings_json='{"memberPrivacySettings":{"publicMemberCandidates":"ALL_MEMBERS"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("memberPrivacySettings.revision", payload["error"])

    def test_parser_exposes_member_privacy_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["member-privacy", "get-default"], member_privacy.cmd_member_privacy_get_default, False),
            (["member-privacy", "set-default", "--privacy-json", "{}"], member_privacy.cmd_member_privacy_set_default, True),
            (["member-privacy", "get-settings"], member_privacy.cmd_member_privacy_get_settings, False),
            (["member-privacy", "set-settings", "--settings-json", "{}"], member_privacy.cmd_member_privacy_set_settings, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
