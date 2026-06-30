from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_social_media
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltySocialMediaCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-social-media",
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

    def test_parser_exposes_loyalty_social_media_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-social-media", "list"], "list", False),
            (
                ["loyalty-social-media", "create", "--followed-channel-json", '{"followedChannel":{"channel":"X"}}'],
                "create",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_social_media_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_uses_official_get_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"followedChannels": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_social_media.cmd_loyalty_social_media_list(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/loyalty-social-media/v1/followed-channels")

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_is_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        args = SimpleNamespace(followed_channel_json='{"followedChannel":{"channel":"X"}}')
        with redirect_stdout(buf):
            rc = loyalty_social_media.cmd_loyalty_social_media_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/loyalty-social-media/v1/followed-channels")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_requires_channel(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        args = SimpleNamespace(followed_channel_json='{"followedChannel":{}}')
        with redirect_stdout(buf):
            rc = loyalty_social_media.cmd_loyalty_social_media_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
