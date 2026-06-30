from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import chat_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestChatSettingsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli chat-settings",
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

    def test_parser_exposes_chat_settings_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["chat-settings", "get", "--chat-settings-id", "form-1"], "get", False),
            (["chat-settings", "query", "--query-json", '{"cursorPaging":{"limit":10}}'], "query", False),
            (["chat-settings", "create", "--chat-settings-json", '{"chatSettings":{"id":"form-1"}}'], "create", True),
            (
                ["chat-settings", "update", "--chat-settings-json", '{"chatSettings":{"id":"form-1","revision":"1"}}'],
                "update",
                True,
            ),
            (["chat-settings", "delete", "--chat-settings-id", "form-1"], "delete", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.chat_settings_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.chat_settings.HttpClient")
    def test_chat_settings_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        read_cases = [
            (chat_settings.cmd_chat_settings_get, SimpleNamespace(chat_settings_id="form-1"), "GET", "/forms/ai/v1/chat-settings/form-1"),
            (
                chat_settings.cmd_chat_settings_query,
                SimpleNamespace(query_json='{"cursorPaging":{"limit":10}}'),
                "POST",
                "/forms/ai/v1/chat-settings/query",
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

    @patch("wix_safe_agent_cli.commands.chat_settings.HttpClient")
    def test_chat_settings_writes_are_plan_first_with_expected_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        write_cases = [
            (
                chat_settings.cmd_chat_settings_create,
                SimpleNamespace(chat_settings_json='{"chatSettings":{"id":"form-1"}}'),
                "POST",
                "/forms/ai/v1/chat-settings",
                False,
            ),
            (
                chat_settings.cmd_chat_settings_update,
                SimpleNamespace(chat_settings_json='{"chatSettings":{"id":"form-1","revision":"1"}}'),
                "PATCH",
                "/forms/ai/v1/chat-settings/form-1",
                False,
            ),
            (
                chat_settings.cmd_chat_settings_delete,
                SimpleNamespace(chat_settings_id="form-1"),
                "DELETE",
                "/forms/ai/v1/chat-settings/form-1",
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

    @patch("wix_safe_agent_cli.commands.chat_settings.HttpClient")
    def test_chat_settings_update_requires_revision(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = chat_settings.cmd_chat_settings_update(
                SimpleNamespace(chat_settings_json='{"chatSettings":{"id":"form-1"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
