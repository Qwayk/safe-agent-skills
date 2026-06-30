from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import (
    ai_site_chat_conversations,
    ai_site_chat_messages,
    ai_site_chat_widget_settings,
    ai_site_chat_widget_settings_v2,
)
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAiSiteChatCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli ai-site-chat",
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

    def test_parser_exposes_ai_site_chat_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["ai-site-chat-widget-settings", "get"], "ai_site_chat_widget_settings_cmd", "get", False),
            (["ai-site-chat-widget-settings", "set", "--settings-json", '{"settings":{"enabled":true}}'], "ai_site_chat_widget_settings_cmd", "set", True),
            (["ai-site-chat-widget-settings-v2", "get"], "ai_site_chat_widget_settings_v2_cmd", "get", False),
            (["ai-site-chat-widget-settings-v2", "update", "--settings-json", '{"settings":{"enabled":true},"fieldMask":["enabled"]}'], "ai_site_chat_widget_settings_v2_cmd", "update", True),
            (["ai-site-chat-conversations", "get"], "ai_site_chat_conversations_cmd", "get", False),
            (["ai-site-chat-messages", "list"], "ai_site_chat_messages_cmd", "list", False),
            (["ai-site-chat-messages", "bulk-create", "--messages-json", '{"messages":[{"body":{"text":"Hi"}}]}'], "ai_site_chat_messages_cmd", "bulk-create", True),
            (["ai-site-chat-messages", "bulk-get-by-inbox", "--params-json", '{"conversationId":"inbox-1"}'], "ai_site_chat_messages_cmd", "bulk-get-by-inbox", False),
            (["ai-site-chat-messages", "media-upload-url"], "ai_site_chat_messages_cmd", "media-upload-url", False),
        ]
        for argv, dest, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(getattr(args, dest), command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        cases = [
            (ai_site_chat_widget_settings.cmd_ai_site_chat_widget_settings_get, SimpleNamespace(), "/wix-assistant-widget/v1/settings"),
            (ai_site_chat_widget_settings_v2.cmd_ai_site_chat_widget_settings_v2_get, SimpleNamespace(), "/wix-assistant-widget/v2/settings"),
            (ai_site_chat_conversations.cmd_ai_site_chat_conversations_get, SimpleNamespace(), "/wix-assistant-widget/v1/conversation"),
            (ai_site_chat_messages.cmd_ai_site_chat_messages_list, SimpleNamespace(params_json=None), "/wix-assistant-widget/v1/messages/list"),
            (ai_site_chat_messages.cmd_ai_site_chat_messages_bulk_get_by_inbox, SimpleNamespace(params_json='{"conversationId":"inbox-1"}'), "/wix-assistant-widget/v1/messages/get-by-inbox"),
            (ai_site_chat_messages.cmd_ai_site_chat_messages_media_upload_url, SimpleNamespace(), "/wix-assistant-widget/v1/messages/files/generate-upload-url"),
        ]
        for func, args, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], "GET")
                self.assertEqual(payload["request"]["path"], path)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_plan_first_writes_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                ai_site_chat_widget_settings.cmd_ai_site_chat_widget_settings_set,
                SimpleNamespace(settings_json='{"settings":{"enabled":true}}'),
                "POST",
                "/wix-assistant-widget/v1/settings",
                False,
            ),
            (
                ai_site_chat_widget_settings_v2.cmd_ai_site_chat_widget_settings_v2_update,
                SimpleNamespace(settings_json='{"settings":{"enabled":true},"fieldMask":["enabled"]}'),
                "PATCH",
                "/wix-assistant-widget/v2/settings",
                False,
            ),
            (
                ai_site_chat_messages.cmd_ai_site_chat_messages_bulk_create,
                SimpleNamespace(messages_json='{"messages":[{"body":{"text":"Hi"}}]}'),
                "POST",
                "/wix-assistant-widget/v1/bulk/messages/create",
                True,
            ),
        ]
        for func, args, http_method, path, needs_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if needs_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_bulk_create_validates_messages(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ai_site_chat_messages.cmd_ai_site_chat_messages_bulk_create(
                SimpleNamespace(messages_json='{"messages":[]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("messages", payload["error"])
        self.assertFalse(mock_client.return_value.request.called)
