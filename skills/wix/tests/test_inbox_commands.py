from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import inbox_conversations, inbox_messages
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestInboxCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli inbox",
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

    def test_parser_exposes_inbox_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["inbox-conversations", "get", "--conversation-id", "conversation-1"], "inbox_conversations_cmd", "get", False),
            (
                ["inbox-conversations", "get-or-create", "--request-json", '{"participantId":{"contactId":"contact-1"}}'],
                "inbox_conversations_cmd",
                "get-or-create",
                True,
            ),
            (["inbox-messages", "list"], "inbox_messages_cmd", "list", False),
            (
                ["inbox-messages", "send", "--request-json", '{"conversationId":"conversation-1","message":{"basic":{}}}'],
                "inbox_messages_cmd",
                "send",
                True,
            ),
        ]
        for argv, attr, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(getattr(args, attr), command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})
        cases = [
            (
                inbox_conversations.cmd_inbox_conversations_get,
                SimpleNamespace(conversation_id="conversation-1"),
                "GET",
                "/inbox/v2/conversations/conversation-1",
                None,
                None,
            ),
            (
                inbox_messages.cmd_inbox_messages_list,
                SimpleNamespace(params_json='{"conversationId":"conversation-1","paging":{"limit":30}}'),
                "GET",
                "/inbox/v2/messages",
                {"conversationId": "conversation-1", "paging": {"limit": 30}},
                None,
            ),
        ]
        for func, args, method, path, params, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_with_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                inbox_conversations.cmd_inbox_conversations_get_or_create,
                SimpleNamespace(request_json='{"participantId":{"contactId":"contact-1"}}'),
                "POST",
                "/inbox/v2/conversations",
                False,
            ),
            (
                inbox_messages.cmd_inbox_messages_send,
                SimpleNamespace(request_json='{"conversationId":"conversation-1","message":{"basic":{"text":"hello"}}}'),
                "POST",
                "/inbox/v2/messages",
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
                self.assertEqual("apply also requires --ack-irreversible" in payload["plan"]["preconditions"], requires_ack)
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_rejects_empty_send_body(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = inbox_messages.cmd_inbox_messages_send(SimpleNamespace(request_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
